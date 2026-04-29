"""Directory watcher for real-time file organization."""

from __future__ import annotations

import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from watchdog.observers import Observer
from rich.console import Console

from .rules import OrganizeConfig, match_file
from .organizer import MoveAction, execute_moves

console = Console()


class OrganizeHandler(FileSystemEventHandler):
    """Handles file system events and organizes new files."""

    def __init__(self, directory: Path, config: OrganizeConfig) -> None:
        self.directory = directory
        self.config = config

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        self._handle_file(Path(event.src_path))

    def on_moved(self, event: FileMovedEvent) -> None:
        if event.is_directory:
            return
        self._handle_file(Path(event.dest_path))

    def _handle_file(self, filepath: Path) -> None:
        if filepath.parent != self.directory:
            return

        target = match_file(filepath, self.config)
        if target is None:
            return

        dest_dir = self.directory / target
        dest = dest_dir / filepath.name

        action = MoveAction(
            source=filepath,
            destination=dest,
            folder=target,
            size=filepath.stat().st_size if filepath.exists() else 0,
        )

        result = execute_moves(self.directory, [action])
        if result.moved:
            console.print(
                f"  [green]Moved[/green] {filepath.name} -> [bold]{target}/[/bold]"
            )
        for err in result.errors:
            console.print(f"  [red]Error[/red] {err}")


def watch_directory(directory: Path, config: OrganizeConfig) -> None:
    """Watch a directory and organize files as they appear."""
    handler = OrganizeHandler(directory, config)
    observer = Observer()
    observer.schedule(handler, str(directory), recursive=False)
    observer.start()

    console.print(f"\n[bold cyan]Watching[/bold cyan] {directory}")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[yellow]Stopped watching.[/yellow]")
    observer.join()
