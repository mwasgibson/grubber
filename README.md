# FileConv

A small, extensible local file conversion tool built around a registry and plugin pattern.

## What it does
- Detects input files
- Resolves the best converter plugin
- Runs conversions through a clean manager layer
- Supports built-in converters and external entry-point plugins

## Example
```bash
fileconv convert sample.docx --to pdf
fileconv doctor
```

## Dependencies
- Python dependencies are installed with `pip install -e '.[dev]'`
- LibreOffice is required for the built-in document converter and must be available on the system PATH (for example: `sudo apt-get install -y libreoffice`)