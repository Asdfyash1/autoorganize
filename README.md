# AutoOrganize

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A smart CLI tool to automatically organize files in any directory by type, date, or custom rules.**

Tired of messy Downloads folders? AutoOrganize sorts your files into clean, categorized folders — instantly or in real-time with a built-in file watcher.

## Features

- **Smart Categorization** — Sorts files into Images, Videos, Audio, Documents, Code, Data, Archives, and more
- **Custom Rules** — Define your own organization rules via YAML config
- **Watch Mode** — Monitors a directory and organizes files as they appear in real-time
- **Date Organization** — Sort files into `YYYY/MM/` folders by modification date
- **Dry Run** — Preview what would happen before moving anything
- **Undo** — Revert the last organization with one command
- **Copy Mode** — Copy files instead of moving them
- **Size Filters** — Rules can filter by minimum/maximum file size
- **Beautiful Output** — Rich terminal output with tables and colors

## Installation

```bash
git clone https://github.com/Asdfyash1/autoorganize.git
cd autoorganize
pip install -e .
```

## Quick Start

Organize your Downloads folder:

```bash
autoorganize run ~/Downloads
```

Preview first (dry run):

```bash
autoorganize dry-run ~/Downloads
```

Watch a directory for new files:

```bash
autoorganize watch ~/Downloads
```

Organize by date:

```bash
autoorganize by-date ~/Downloads
```

Undo the last operation:

```bash
autoorganize undo ~/Downloads
```

## Custom Rules

Generate a default config:

```bash
autoorganize init
```

This creates `autoorganize.yml`:

```yaml
ignore_dotfiles: true
ignore_patterns:
  - "*.tmp"
  - "*.partial"

rules:
  - folder: Images
    extensions:
      - .jpg
      - .jpeg
      - .png
      - .gif
      - .svg
      - .webp

  - folder: Documents
    extensions:
      - .pdf
      - .doc
      - .docx
      - .xlsx
      - .pptx

  - folder: LargeFiles
    extensions:
      - .iso
      - .dmg
    min_size: 104857600  # 100MB

  - folder: Screenshots
    patterns:
      - "Screenshot*"
      - "Screen Shot*"
```

Use custom rules:

```bash
autoorganize run ~/Downloads --config autoorganize.yml
```

## Commands

| Command | Description |
|---------|-------------|
| `run` | Organize files in a directory |
| `dry-run` | Preview organization without moving files |
| `watch` | Watch directory and auto-organize new files |
| `by-date` | Organize files by modification date (YYYY/MM) |
| `undo` | Revert the last organization |
| `init` | Generate default config file |

## Default Categories

| Category | Extensions |
|----------|-----------|
| Images | .jpg, .jpeg, .png, .gif, .svg, .webp, .ico, .bmp |
| Videos | .mp4, .mkv, .avi, .mov, .wmv, .webm |
| Audio | .mp3, .wav, .flac, .aac, .ogg, .m4a |
| Documents | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx |
| Archives | .zip, .tar, .gz, .7z, .rar |
| Code | .py, .js, .ts, .java, .c, .cpp, .go, .rs |
| Data | .json, .csv, .xml, .yaml, .sql, .db |
| Text | .txt, .md, .log, .cfg, .ini |
| Fonts | .ttf, .otf, .woff, .woff2 |
| Executables | .exe, .msi, .dmg, .deb, .AppImage |

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Yashwanth** — [GitHub](https://github.com/Asdfyash1)
