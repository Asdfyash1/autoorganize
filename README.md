# AutoOrganize

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blueviolet.svg)](#ai-powered-features)

**A smart CLI tool to automatically organize files in any directory — by type, date, custom rules, or AI-powered content analysis.**

Tired of messy Downloads folders? AutoOrganize sorts your files into clean, categorized folders — instantly or in real-time with a built-in file watcher. With AI mode, it reads file contents and suggests intelligent categorizations beyond simple extension matching.

## Features

- **Smart Categorization** — Sorts files into Images, Videos, Audio, Documents, Code, Data, Archives, and more
- **Custom Rules** — Define your own organization rules via YAML config
- **Watch Mode** — Monitors a directory and organizes files as they appear in real-time
- **Date Organization** — Sort files into `YYYY/MM/` folders by modification date
- **Dry Run** — Preview what would happen before moving anything
- **Undo** — Revert the last organization with one command
- **Copy Mode** — Copy files instead of moving them
- **Size Filters** — Rules can filter by minimum/maximum file size

### AI-Powered Features

- **AI Smart Categorize** — Uses AI to read file contents and suggest intelligent folder organization
- **AI Rename Suggestions** — Get better, more descriptive filename suggestions based on file content
- **Multi-Provider** — Works with OpenAI, Google Gemini, and NVIDIA APIs

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

AI-powered smart categorization:

```bash
export OPENAI_API_KEY="your-key"   # or GEMINI_API_KEY or NVIDIA_API_KEY
autoorganize smart ~/Downloads           # preview
autoorganize smart ~/Downloads --execute  # actually move files
```

AI rename suggestions:

```bash
autoorganize suggest-names ~/Documents
```

Watch a directory for new files:

```bash
autoorganize watch ~/Downloads
```

## AI Setup

Set one of these environment variables to enable AI features:

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Google Gemini | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| NVIDIA | `NVIDIA_API_KEY` | `meta/llama-3.1-8b-instruct` |

## Commands

| Command | Description |
|---------|-------------|
| `run` | Organize files by extension rules |
| `dry-run` | Preview organization without moving |
| `watch` | Watch directory and auto-organize new files |
| `by-date` | Organize by modification date (YYYY/MM) |
| `undo` | Revert the last organization |
| `init` | Generate default config file |
| `smart` | AI-powered content-based categorization |
| `suggest-names` | AI-powered file rename suggestions |

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

rules:
  - folder: Images
    extensions: [.jpg, .jpeg, .png, .gif, .svg, .webp]
  - folder: Documents
    extensions: [.pdf, .doc, .docx, .xlsx, .pptx]
  - folder: LargeFiles
    extensions: [.iso, .dmg]
    min_size: 104857600  # 100MB
  - folder: Screenshots
    patterns: ["Screenshot*", "Screen Shot*"]
```

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

## Development

```bash
git clone https://github.com/Asdfyash1/autoorganize.git
cd autoorganize
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/ -v
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Yashwanth** — [GitHub](https://github.com/Asdfyash1)
