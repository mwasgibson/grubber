# FileConv

[![Release](https://img.shields.io/github/v/tag/your-username/fileconv?label=release)](https://github.com/your-username/fileconv/releases)
[![License](https://img.shields.io/github/license/your-username/fileconv)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/your-username/fileconv)

FileConv is a lightweight command-line tool for converting files between supported formats using pluggable backends such as LibreOffice, pdf2docx, and Pillow.

## Highlights

- Routes conversions through a MIME-based registry.
- Uses LibreOffice for office document conversions.
- Uses pdf2docx for PDF to DOCX conversion.
- Supports image conversions through Pillow.
- Includes a doctor command for environment validation.

## Installation

Install from PyPI:

```bash
pip install grubber
```

For local development:

```bash
pip install -e .
```

## Quickstart

Convert a PDF to DOCX:

```bash
fileconv convert input.pdf --to docx
```

Convert a DOCX to PDF:

```bash
fileconv convert input.docx --to pdf
```

Check your setup:

```bash
fileconv doctor
```

## CLI options

### convert

```bash
fileconv convert <input-file> --to <format> [--output <path>]
```

Common options:

- `--to`: output format to convert into.
- `--output`: optional output file path.
- `--overwrite`: replace an existing output file when supported.
- `--dry-run`: show what would be converted without writing files.
- `--recursive`: process files recursively from a directory when supported.

### doctor

```bash
fileconv doctor
```

Use this command to check whether FileConv can find the installed conversion tools and dependencies.

## Supported converters

- `libreoffice`: Office-to-office conversions such as DOCX to PDF.
- `pdf2docx`: PDF to DOCX conversion.
- `pillow`: Image conversions.

## How it works

FileConv uses three layers:

1. The **registry** stores available converters.
2. The **resolver** matches input and output MIME types.
3. The **converter class** performs the conversion.

This keeps routing separate from implementation and makes it easier to add new backends later.

## Release notes

### v0.1.0

- Initial release of FileConv.
- Added converter registry and MIME-based routing.
- Added LibreOffice-based conversion support.
- Added pdf2docx support for PDF to DOCX.
- Added doctor command for environment validation.

For full release history, see [CHANGELOG.md](CHANGELOG.md).

## Contributing

Contributions are welcome. Please open an issue before larger changes, keep pull requests focused, and update tests or docs when behavior changes. New converters must be imported so they register correctly.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Released under the MIT License. See [LICENSE](LICENSE).