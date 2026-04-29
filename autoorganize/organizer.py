"""Core file organization engine."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .rules import OrganizeConfig, match_file


@dataclass
class MoveAction:
    source: Path
    destination: Path
    folder: str
    size: int
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class OrganizeResult:
    moved: list[MoveAction] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    total_size_moved: int = 0


UNDO_FILE = ".autoorganize_undo.json"


def plan_moves(directory: Path, config: OrganizeConfig) -> list[MoveAction]:
    """Plan file moves without executing them (dry run)."""
    actions: list[MoveAction] = []

    for item in sorted(directory.iterdir()):
        if item.is_dir():
            continue
        if item.name.startswith(".autoorganize"):
            continue

        target_folder = match_file(item, config)
        if target_folder is None:
            continue

        dest_dir = directory / target_folder
        dest = dest_dir / item.name

        if dest == item:
            continue

        actions.append(MoveAction(
            source=item,
            destination=dest,
            folder=target_folder,
            size=item.stat().st_size,
        ))

    return actions


def execute_moves(
    directory: Path,
    actions: list[MoveAction],
    *,
    copy_mode: bool = False,
) -> OrganizeResult:
    """Execute planned file moves."""
    result = OrganizeResult()

    for action in actions:
        try:
            action.destination.parent.mkdir(parents=True, exist_ok=True)

            final_dest = action.destination
            if final_dest.exists():
                stem = final_dest.stem
                suffix = final_dest.suffix
                counter = 1
                while final_dest.exists():
                    final_dest = final_dest.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                action.destination = final_dest

            if copy_mode:
                shutil.copy2(action.source, action.destination)
            else:
                shutil.move(str(action.source), str(action.destination))

            result.moved.append(action)
            result.total_size_moved += action.size

        except OSError as e:
            result.errors.append(f"Failed to move {action.source.name}: {e}")

    _save_undo(directory, result.moved)
    return result


def undo_last(directory: Path) -> OrganizeResult:
    """Undo the last organization operation."""
    undo_path = directory / UNDO_FILE
    if not undo_path.exists():
        return OrganizeResult(errors=["No undo history found."])

    with open(undo_path) as f:
        data = json.load(f)

    result = OrganizeResult()
    for entry in reversed(data):
        src = Path(entry["destination"])
        dst = Path(entry["source"])
        try:
            if src.exists():
                shutil.move(str(src), str(dst))
                result.moved.append(MoveAction(
                    source=src,
                    destination=dst,
                    folder="(undo)",
                    size=entry.get("size", 0),
                ))
        except OSError as e:
            result.errors.append(f"Failed to undo {src.name}: {e}")

    undo_path.unlink(missing_ok=True)

    # Clean up empty directories
    for entry in data:
        dest = Path(entry["destination"])
        parent = dest.parent
        if parent.exists() and parent != directory and not any(parent.iterdir()):
            try:
                parent.rmdir()
            except OSError:
                pass

    return result


def _save_undo(directory: Path, actions: list[MoveAction]) -> None:
    undo_path = directory / UNDO_FILE
    data = [
        {
            "source": str(a.source),
            "destination": str(a.destination),
            "folder": a.folder,
            "size": a.size,
            "timestamp": a.timestamp,
        }
        for a in actions
    ]
    with open(undo_path, "w") as f:
        json.dump(data, f, indent=2)


def organize_by_date(directory: Path) -> OrganizeResult:
    """Organize files into YYYY/MM folders based on modification date."""
    result = OrganizeResult()

    for item in sorted(directory.iterdir()):
        if item.is_dir() or item.name.startswith("."):
            continue

        try:
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            dest_dir = directory / str(mtime.year) / f"{mtime.month:02d}"
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / item.name

            if dest == item:
                continue

            shutil.move(str(item), str(dest))
            result.moved.append(MoveAction(
                source=item,
                destination=dest,
                folder=f"{mtime.year}/{mtime.month:02d}",
                size=item.stat().st_size if item.exists() else 0,
            ))
        except OSError as e:
            result.errors.append(f"Failed: {item.name}: {e}")

    _save_undo(directory, result.moved)
    return result
