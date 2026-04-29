"""AI-powered smart file categorization."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .ai_client import query_ai, get_provider_name

console = Console()

SYSTEM_PROMPT = """\
You are AutoOrganize AI, a file organization expert. Given a list of filenames (with optional content previews),
suggest the best folder for each file. Return ONLY valid JSON — no markdown, no explanation.
Use descriptive folder names like "Python-Projects", "Config-Files", "Reports", "Design-Assets", etc.
Be smarter than just sorting by extension — consider the actual purpose of the file."""


def _read_preview(filepath: Path, max_chars: int = 500) -> str:
    """Read a short preview of a file's content."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(max_chars)
        return content.strip()
    except (OSError, UnicodeDecodeError):
        return ""


def ai_categorize(directory: Path, dry_run: bool = True) -> list[dict[str, str]]:
    """Use AI to intelligently categorize files in a directory."""
    provider = get_provider_name()
    if provider == "none":
        console.print("[red]No AI API key found.[/red]")
        console.print("Set one of: [bold]OPENAI_API_KEY[/bold], [bold]GEMINI_API_KEY[/bold], or [bold]NVIDIA_API_KEY[/bold]")
        return []

    header = Text()
    header.append("  AI ORGANIZE  ", style="bold white on bright_magenta")
    header.append(f"  powered by {provider}", style="bold bright_white")
    console.print(Panel(header, border_style="bright_magenta", padding=(0, 1)))
    console.print()

    files_info = []
    for item in sorted(directory.iterdir()):
        if item.is_dir() or item.name.startswith("."):
            continue
        preview = _read_preview(item, max_chars=300)
        files_info.append({
            "name": item.name,
            "size": item.stat().st_size,
            "ext": item.suffix,
            "preview": preview[:200] if preview else "(binary or empty)",
        })

    if not files_info:
        console.print("[dim]No files to organize.[/dim]")
        return []

    file_list = "\n".join(
        f"- {f['name']} (ext: {f['ext']}, size: {f['size']}B, preview: {f['preview'][:100]})"
        for f in files_info
    )

    prompt = f"""Categorize these files into appropriate folders. Return JSON array of objects with "file" and "folder" keys.

Files in: {directory}
{file_list}

Return format: [{{"file": "example.py", "folder": "Python-Scripts"}}, ...]
Return ONLY the JSON array, nothing else."""

    with console.status(f"[bold magenta]AI analyzing {len(files_info)} files...", spinner="dots"):
        response = query_ai(prompt, system_prompt=SYSTEM_PROMPT)

    try:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0]
        categorizations = json.loads(response)
    except (json.JSONDecodeError, IndexError):
        console.print("[red]Error parsing AI response. Try again.[/red]")
        return []

    table = Table(
        title="AI Categorization" + (" (Dry Run)" if dry_run else ""),
        border_style="bright_magenta",
        header_style="bold bright_white",
    )
    table.add_column("File", style="white")
    table.add_column("Suggested Folder", style="bold bright_magenta")

    for item in categorizations:
        table.add_row(item.get("file", "?"), item.get("folder", "?"))

    console.print(table)
    console.print(f"\n[bold]{len(categorizations)} file(s)[/bold] categorized by AI")

    if not dry_run:
        import shutil
        moved = 0
        for item in categorizations:
            src = directory / item["file"]
            dest_dir = directory / item["folder"]
            if src.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / item["file"]
                if not dest.exists():
                    shutil.move(str(src), str(dest))
                    moved += 1
        console.print(f"\n[bold green]Moved {moved} file(s)[/bold green]")

    return categorizations


def ai_rename_suggestions(directory: Path) -> list[dict[str, str]]:
    """Use AI to suggest better file names."""
    provider = get_provider_name()
    if provider == "none":
        console.print("[red]No AI API key found.[/red]")
        console.print("Set one of: [bold]OPENAI_API_KEY[/bold], [bold]GEMINI_API_KEY[/bold], or [bold]NVIDIA_API_KEY[/bold]")
        return []

    files = []
    for item in sorted(directory.iterdir()):
        if item.is_dir() or item.name.startswith("."):
            continue
        preview = _read_preview(item, max_chars=500)
        files.append({"name": item.name, "preview": preview[:300]})

    if not files:
        console.print("[dim]No files found.[/dim]")
        return []

    file_list = "\n".join(f"- {f['name']}: {f['preview'][:150]}" for f in files)

    prompt = f"""Suggest better, more descriptive filenames for these files based on their content.
Keep the same extension. Only suggest renames where the current name is unclear or generic.
Return JSON: [{{"old": "current.txt", "new": "suggested.txt", "reason": "brief reason"}}]

Files:
{file_list}

Return ONLY the JSON array."""

    with console.status(f"[bold magenta]AI analyzing filenames...", spinner="dots"):
        response = query_ai(prompt, system_prompt=SYSTEM_PROMPT)

    try:
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1].rsplit("```", 1)[0]
        suggestions = json.loads(response)
    except (json.JSONDecodeError, IndexError):
        console.print("[red]Error parsing AI response.[/red]")
        return []

    if suggestions:
        table = Table(title="Rename Suggestions", border_style="bright_magenta", header_style="bold bright_white")
        table.add_column("Current Name", style="white")
        table.add_column("Suggested Name", style="bold bright_green")
        table.add_column("Reason", style="dim")

        for s in suggestions:
            table.add_row(s.get("old", ""), s.get("new", ""), s.get("reason", ""))

        console.print(table)
    else:
        console.print("[dim]All filenames look good![/dim]")

    return suggestions
