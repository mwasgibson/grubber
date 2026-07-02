# Architecture

## Overview

FileConv uses Typer for the CLI layer and a conversion core for file processing. The CLI is modular: each command group lives in its own module, while the root app handles global flags and subcommand registration.

## Module layout

- `cli.py` wires the root app and registers command groups.
- `version.py` stores the package version.
- `commands/batch.py` handles batch conversion, dry-run, and JSON output.
- `commands/convert.py` handles single-file conversion.
- `commands/doctor.py` performs environment diagnostics.
- `commands/inspect.py` is reserved for future inspection/reporting.
- `core.py` handles discovery, planning, and conversion work.

## Execution flow

1. Typer parses the root command and global options.
2. `--version` exits early through a root callback.
3. Completion flags are available from Typer’s built-in support.
4. `batch` calls `convert_many()` and emits either JSON or text.
5. `convert` calls `convert()` for single-file execution.
6. `doctor` checks environment readiness.
7. `inspect` will report file details once defined.

## Output contract

Batch JSON payloads include:

- `mode`
- `format`
- `counts`
- `elapsed_seconds`
- `results`

Each result item includes:

- `input`
- `output`
- `status`
- `reason`

## Path behavior

Recursive batch output mirrors nested input folders under the output root. Dry-run calculates output paths without writing files.

## Testing

- Test JSON mode with `CliRunner`.
- Test the root `--version` flag.
- Test doctor output for missing and present dependencies.
- Test that recursive output paths are preserved.
- Test that completion flags appear in help.