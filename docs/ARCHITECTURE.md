# FileConv Architecture

## Core pieces
- `ConverterRegistry`: stores and resolves converter plugins.
- `ConversionManager`: detects formats and runs conversions.
- `@converter`: decorator for registering built-in plugins.
- `entry_points`: mechanism for loading third-party plugins lazily.

## Plugin contract
Each converter must expose:
- `name`
- `priority`
- `supports(input_mime, output_mime)`
- `supported_inputs()`
- `supported_outputs()`
- `convert(input_path, output_path, options=None)`

## Loading strategy
1. Import built-in converter modules.
2. Register them through the decorator.
3. Load external plugins through `importlib.metadata.entry_points()`.

## First supported engine
LibreOffice headless mode for documents.