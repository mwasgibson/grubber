# FileConv

FileConv is a batch file conversion CLI with dry-run support, JSON export, and recursive output tree preservation.

## Features

- Convert files in batch.
- Preview planned output with dry-run.
- Export dry-run and batch results as JSON.
- Keep nested input folders mirrored in the output tree.
- Switch between human-readable and machine-readable output with `--format`.

## Usage

Convert one file:

```bash
fileconv convert input.png --to webp --out-dir out
```

Preview a batch run:

```bash
fileconv batch images --to webp --out-dir out --recursive --dry-run
```

Export the plan as JSON:

```bash
fileconv batch images --to webp --out-dir out --recursive --dry-run --format json
```

Pipe JSON into scripts:

```bash
fileconv batch images --to webp --out-dir out --recursive --dry-run --format json | jq '.counts'
```

Human-readable output is the default:

```bash
fileconv batch images --to webp --out-dir out --recursive --format text
```

## Output format

- `text` is for terminal use.
- `json` is for scripts and automation.
- In JSON mode, stdout contains only JSON.
- Progress, summaries, and diagnostics stay on stderr.

## JSON export

The JSON export includes:

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

## Behavior

- `--dry-run` calculates the planned output tree without writing files.
- `--recursive` preserves subfolder structure under the output directory.
- `--overwrite` allows replacing existing outputs.
