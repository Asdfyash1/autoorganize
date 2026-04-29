"""File organization rules engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


DEFAULT_RULES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".heic"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".rtf", ".epub"],
    "Archives": [".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar", ".tar.gz"],
    "Code": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".go", ".rs", ".rb", ".php", ".swift", ".kt"],
    "Data": [".json", ".csv", ".xml", ".yaml", ".yml", ".toml", ".sql", ".db", ".sqlite"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "Executables": [".exe", ".msi", ".dmg", ".app", ".deb", ".rpm", ".AppImage"],
    "Text": [".txt", ".md", ".log", ".cfg", ".ini", ".conf"],
}


@dataclass
class OrganizeRule:
    folder: str
    extensions: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    min_size: Optional[int] = None
    max_size: Optional[int] = None


@dataclass
class OrganizeConfig:
    rules: list[OrganizeRule] = field(default_factory=list)
    ignore_dotfiles: bool = True
    ignore_patterns: list[str] = field(default_factory=list)

    @classmethod
    def default(cls) -> OrganizeConfig:
        rules = [
            OrganizeRule(folder=folder, extensions=exts)
            for folder, exts in DEFAULT_RULES.items()
        ]
        return cls(rules=rules)

    @classmethod
    def from_yaml(cls, path: Path) -> OrganizeConfig:
        with open(path) as f:
            data = yaml.safe_load(f)

        if not data or "rules" not in data:
            return cls.default()

        rules = []
        for item in data["rules"]:
            rules.append(OrganizeRule(
                folder=item["folder"],
                extensions=item.get("extensions", []),
                patterns=item.get("patterns", []),
                min_size=item.get("min_size"),
                max_size=item.get("max_size"),
            ))

        return cls(
            rules=rules,
            ignore_dotfiles=data.get("ignore_dotfiles", True),
            ignore_patterns=data.get("ignore_patterns", []),
        )

    def to_yaml(self, path: Path) -> None:
        data = {
            "ignore_dotfiles": self.ignore_dotfiles,
            "ignore_patterns": self.ignore_patterns,
            "rules": [
                {
                    "folder": rule.folder,
                    "extensions": rule.extensions,
                    **({"patterns": rule.patterns} if rule.patterns else {}),
                    **({"min_size": rule.min_size} if rule.min_size else {}),
                    **({"max_size": rule.max_size} if rule.max_size else {}),
                }
                for rule in self.rules
            ],
        }
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def match_file(filepath: Path, config: OrganizeConfig) -> Optional[str]:
    """Determine which folder a file should be moved to based on rules."""
    if config.ignore_dotfiles and filepath.name.startswith("."):
        return None

    import fnmatch
    for pattern in config.ignore_patterns:
        if fnmatch.fnmatch(filepath.name, pattern):
            return None

    ext = filepath.suffix.lower()
    size = filepath.stat().st_size if filepath.exists() else 0

    for rule in config.rules:
        if rule.extensions and ext in rule.extensions:
            if rule.min_size and size < rule.min_size:
                continue
            if rule.max_size and size > rule.max_size:
                continue
            return rule.folder

        if rule.patterns:
            for pattern in rule.patterns:
                if fnmatch.fnmatch(filepath.name, pattern):
                    if rule.min_size and size < rule.min_size:
                        continue
                    if rule.max_size and size > rule.max_size:
                        continue
                    return rule.folder

    return None
