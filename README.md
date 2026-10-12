# FileConv

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/mwasgibson/grubber)

**FileConv** (package: `grubber-fileconv`) is a lightweight, extensible command-line tool for converting files between supported formats using pluggable backends such as LibreOffice, pdf2docx, and Pillow.

## Highlights (v1.5)

- MIME-based converter registry with priority resolution
- LibreOffice for office ↔ PDF / HTML / ODT / etc.
- pdf2docx for high-quality PDF → DOCX
- Pillow for raster image conversions
- Recursive batch conversion that **preserves folder structure**
- Parallel workers (`--jobs`)
- Include / exclude globs
- Dry-run + JSON export for scripting
- Rich `doctor` and `inspect` commands
- Optional user config (`~/.config/fileconv/config.toml`)
- Entry-point plugin system for third-party converters

## Installation

```bash
pip install grubber-fileconv
```

For local development:

```bash
pip install -e ".[dev]"
```

**System dependency:** LibreOffice (`libreoffice` / `soffice`) must be on `PATH` for office conversions.

## Quickstart

```bash
# Single file
fileconv convert report.docx --to pdf
fileconv convert scan.pdf --to docx -o ./out
fileconv convert photo.png --to jpg --overwrite

# Batch (recursive, parallel, filtered)
fileconv batch ./photos --to webp --out-dir ./converted -r -j 4 \
  --include "*.png" --include "*.jpg" --exclude "*_thumb*"

# Dry-run as JSON (pipeable)
fileconv batch ./docs --to pdf --out-dir ./out -r --dry-run --format json

# Environment check
fileconv doctor
fileconv doctor --json

# Inspect a file
fileconv inspect invoice.pdf
fileconv inspect invoice.pdf --json
```

## CLI reference

### `convert`

```bash
fileconv convert <input> --to <format> [--output PATH] [--out-dir DIR] [--overwrite]
```

### `batch`

```bash
fileconv batch <input> --to <format> --out-dir <dir>
  [--recursive] [--overwrite] [--jobs N]
  [--include GLOB] [--exclude GLOB]
  [--dry-run] [--format text|json] [--no-progress]
```

- Recursive mode mirrors the input directory tree under `--out-dir`.
- Existing outputs are skipped unless `--overwrite` is set.
- `--jobs` > 1 enables parallel conversion (ThreadPoolExecutor).

### `doctor`

Reports binaries, Python packages, registered converters, and config defaults.

### `inspect`

Reports detected MIME, confidence, and recommended converters for a file.

## Supported converters

| Name         | Typical use                          | Priority |
|--------------|--------------------------------------|----------|
| `pdf2docx`   | PDF → DOCX                           | 20       |
| `libreoffice`| Office docs ↔ PDF / HTML / ODT / …   | 10       |
| `pillow`     | PNG / JPG / WebP / BMP / GIF / TIFF  | 5        |

Priority decides which converter wins when several claim the same MIME pair.

## Configuration

Optional file: `~/.config/fileconv/config.toml`

```toml
[fileconv]
default_output_dir = "~/Documents/FileConv"
jobs = 2
overwrite = false
show_progress = true
recursive = false
```

## Architecture

1. **Registry** – stores converters (built-in + entry points).
2. **Resolver** – picks the highest-priority converter whose `supports(in, out)` is true.
3. **Converter class** – performs the conversion.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Plugin entry points

Third-party packages can register converters under the group `fileconv.converters`:

```toml
[project.entry-points."fileconv.converters"]
myconv = "mypkg.converters:MyConverter"
```

## Development

```bash
pip install -e ".[dev]"
pytest -q
fileconv --version   # → 1.5.0
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE).
