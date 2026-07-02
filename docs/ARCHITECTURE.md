# Architecture

## Overview

FileConv is structured as a small CLI layer on top of a conversion engine. The CLI handles argument parsing, output formatting, and stream separation. The core engine discovers inputs, computes output paths, and performs or simulates conversions.

## Execution flow

1. Parse CLI arguments with Typer.
2. Select output mode with `--format text|json`.
3. Run `convert_many()` once to collect a structured payload.
4. Emit JSON to stdout or text to stderr depending on the selected mode.

## Core data shape

The batch engine returns:

```json
{
  "elapsed_seconds": 0.8421,
  "counts": {
    "planned": 12,
    "ok": 0,
    "skipped": 0,
    "failed": 0,
    "total": 12
  },
  "results": [
    {
      "input": "images/cats/kitten.png",
      "output": "out/cats/kitten.webp",
      "status": "planned",
      "reason": null
    }
  ]
}
```

## Output rules

- JSON mode writes only JSON to stdout.
- Text mode writes readable lines and summaries to stderr.
- Progress output is disabled when JSON mode is selected.
- Dry-run never writes files.

## Path handling

Input paths are expanded recursively when requested. Output paths mirror the relative subfolder structure beneath the output root. This ensures planned and actual outputs stay consistent.

## Testing strategy

- Test the CLI with `CliRunner`.
- Validate stdout JSON parsing.
- Confirm stderr contains human summaries in text mode.
- Confirm dry-run does not create files.
- Confirm nested folders are preserved in output paths.
