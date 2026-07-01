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