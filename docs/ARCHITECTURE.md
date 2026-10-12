# Architecture (v1.5)

## Overview

FileConv uses Typer for the CLI layer and a conversion core for file processing.
The CLI is modular: each command lives in its own module; the root app handles
global flags and subcommand registration.

## Module layout

| Module | Role |
|--------|------|
| `cli.py` | Root Typer app, version flag, command registration |
| `version.py` | Package version (`1.5.0`) |
| `config.py` | Optional TOML user config |
| `core.py` | Registry, ConversionManager, file discovery, parallel execution |
| `detection.py` | MIME / format detection (magic + extension) |
| `errors.py` | Domain exceptions |
| `types.py` | `ConverterProtocol` |
| `commands/convert.py` | Single-file conversion |
| `commands/batch.py` | Batch, dry-run, JSON, filters, jobs |
| `commands/doctor.py` | Environment diagnostics |
| `commands/inspect.py` | Format detection + recommendations |
| `converters/*` | Built-in backends (LibreOffice, pdf2docx, Pillow) |

## Execution flow

1. Typer parses the root command and global options.
2. `--version` exits early through a root callback.
3. `batch` calls `ConversionManager.convert_many()` and emits text or JSON.
4. `convert` calls `ConversionManager.convert()`.
5. `doctor` / `inspect` use detection + registry introspection.

## Registry & resolution

- Converters self-register with `@converter(name=..., priority=...)`.
- Entry points under group `fileconv.converters` are loaded on first use.
- `Registry.resolve(input_mime, output_mime)` selects the highest-priority
  converter whose `supports()` returns true.

## Batch path behaviour

- `collect_files()` walks the input (optionally recursive) and applies
  include / exclude globs.
- `relative_output_path()` mirrors the input tree under the output root so
  nested folders do not collide.
- Dry-run computes the same paths without writing files.
- `--jobs N` uses a `ThreadPoolExecutor` for parallel conversion.

## Output contract (batch JSON)

```json
{
  "mode": "batch" | "dry_run",
  "format": "json",
  "counts": { "planned", "ok", "skipped", "failed", "total" },
  "elapsed_seconds": 1.234,
  "results": [
    {
      "input": "...",
      "output": "...",
      "status": "ok|skipped|failed|planned",
      "reason": null | "string",
      "converter": "pillow" | null
    }
  ]
}
```

## Testing

- Registry resolution and priorities
- Path collection / mirroring / filters
- Dry-run JSON shape
- CLI `--version`, `doctor`, batch dry-run
- Individual converter `supports()` contracts

## Extensibility

Third-party packages register converters via the `fileconv.converters`
entry-point group. Built-in converters remain import-time registered so the
tool works without entry-point discovery.
