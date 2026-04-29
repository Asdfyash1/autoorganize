"""CLI entry point for AutoOrganize."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .rules import OrganizeConfig
from .organizer import plan_moves, execute_moves, undo_last, organize_by_date

console = Console()


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _print_result(result, verb: str = "Moved") -> None:
    if result.moved:
        table = Table(border_style="green", header_style="bold bright_white")
        table.add_column("File", style="white")
        table.add_column("Destination", style="bold bright_green")
        table.add_column("Size", justify="right", style="dim")

        for action in result.moved:
            table.add_row(
                action.source.name,
                f"{action.folder}/",
                _format_size(action.size),
            )

        console.print(table)
        console.print(
            f"\n[bold green]{verb} {len(result.moved)} file(s)[/bold green] "
            f"({_format_size(result.total_size_moved)})"
        )

    if result.errors:
        for err in result.errors:
            console.print(f"[red]Error:[/red] {err}")

    if not result.moved and not result.errors:
        console.print("[dim]Nothing to do.[/dim]")


@click.group()
@click.version_option(package_name="autoorganize")
def main() -> None:
    """AutoOrganize - Smart file organization for your directories."""
    pass


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--config", "-c", "config_path", type=click.Path(exists=True), help="Custom rules YAML file.")
@click.option("--copy", "copy_mode", is_flag=True, help="Copy files instead of moving.")
def run(directory: str, config_path: str | None, copy_mode: bool) -> None:
    """Organize files in a directory based on rules."""
    target = Path(directory)
    config = OrganizeConfig.from_yaml(Path(config_path)) if config_path else OrganizeConfig.default()

    header = Text()
    header.append("  AUTOORGANIZE  ", style="bold white on green")
    header.append(f"  {target}", style="bold bright_white")
    console.print(Panel(header, border_style="green", padding=(0, 1)))
    console.print()

    actions = plan_moves(target, config)
    if not actions:
        console.print("[dim]No files to organize.[/dim]")
        return

    console.print(f"[bold]Found {len(actions)} file(s) to organize:[/bold]\n")
    for action in actions:
        console.print(f"  {action.source.name} -> [green]{action.folder}/[/green]")

    console.print()
    if click.confirm("Proceed?", default=True):
        verb = "Copied" if copy_mode else "Moved"
        result = execute_moves(target, actions, copy_mode=copy_mode)
        console.print()
        _print_result(result, verb)
    else:
        console.print("[yellow]Cancelled.[/yellow]")


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--config", "-c", "config_path", type=click.Path(exists=True), help="Custom rules YAML file.")
def dry_run(directory: str, config_path: str | None) -> None:
    """Preview what would be organized without moving files."""
    target = Path(directory)
    config = OrganizeConfig.from_yaml(Path(config_path)) if config_path else OrganizeConfig.default()

    actions = plan_moves(target, config)
    if not actions:
        console.print("[dim]No files to organize.[/dim]")
        return

    table = Table(title="Dry Run Preview", border_style="yellow", header_style="bold bright_white")
    table.add_column("File", style="white")
    table.add_column("Destination", style="bold bright_yellow")
    table.add_column("Size", justify="right", style="dim")

    total = 0
    for action in actions:
        table.add_row(action.source.name, f"{action.folder}/", _format_size(action.size))
        total += action.size

    console.print(table)
    console.print(f"\n[bold yellow]{len(actions)} file(s)[/bold yellow] would be organized ({_format_size(total)})")


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def undo(directory: str) -> None:
    """Undo the last organization operation."""
    target = Path(directory)
    result = undo_last(target)
    _print_result(result, "Restored")


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def by_date(directory: str) -> None:
    """Organize files into YYYY/MM folders by modification date."""
    target = Path(directory)
    result = organize_by_date(target)
    _print_result(result, "Organized")


@main.command()
@click.argument("directory", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--config", "-c", "config_path", type=click.Path(exists=True), help="Custom rules YAML file.")
def watch(directory: str, config_path: str | None) -> None:
    """Watch a directory and organize new files automatically."""
    from .watcher import watch_directory

    target = Path(directory)
    config = OrganizeConfig.from_yaml(Path(config_path)) if config_path else OrganizeConfig.default()
    watch_directory(target, config)


@main.command()
@click.argument("output", default="autoorganize.yml", type=click.Path())
def init(output: str) -> None:
    """Generate a default configuration YAML file."""
    config = OrganizeConfig.default()
    config.to_yaml(Path(output))
    console.print(f"[green]Created config file:[/green] {output}")
    console.print("[dim]Edit this file to customize your organization rules.[/dim]")


if __name__ == "__main__":
    main()
