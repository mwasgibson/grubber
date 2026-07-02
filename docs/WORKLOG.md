# FileConv Worklog

## 2026-07-01

### Goal

Build a local, cross-platform, universal file converter for personal use.

### Design decisions

- Use a Python plugin + registry architecture.
- Keep a small core and add converters as plugins.
- Support lazy plugin loading through Python entry points.
- Start with LibreOffice for office-document conversions.

### What was added

- Project skeleton.
- Core registry and conversion manager design.
- CLI entry point.
- LibreOffice converter plugin.
- Test scaffold.

### Notes

- Third-party plugins will register under the `fileconv.converters` entry-point group.
- Built-in converters self-register via the decorator.
- Future plugins can be added without changing the core.

## 2026-07-01 - Doctor command upgrade

### Goal

Add real dependency checks for the local conversion environment.

### What will change

- `doctor()` will verify installed binaries like `libreoffice` and `soffice`.
- `doctor()` will report the Python package environment.
- `doctor()` will show registered converters.
- `doctor()` will produce a clear pass/fail summary.

### Reason

We need a reliable way to confirm the machine can run conversions before trying to convert files.

## 2026-07-01 - Doctor dependency check

### What changed

- Added real binary detection for LibreOffice, ffmpeg, and magick.
- Added a structured doctor report.
- Added an overall status flag.

### Impact

- The app can now verify whether the local machine is ready for conversions before any file is processed.

## 2026-07-01 - Format detection helper

### Goal

Improve input format detection so converters are chosen more reliably.

### What will change

- Add a dedicated `detect_format()` helper.
- Use file extension detection first as a fallback.
- Use `python-magic` when available for content-based MIME detection.
- Return a structured result with mime type, extension, and confidence/source.

### Why

Registry lookup is cleaner when format detection is centralized instead of duplicated in the manager.

## 2026-07-01 - Format detection helper

### What changed

- Added `detect_format()` to centralize format detection.
- Used `python-magic` when available.
- Kept extension fallback for portability.
- Improved doctor output to show detection capability.

## 2026-07-01 - ImageConverter design

### Goal

Add an image format conversion plugin for raster formats like PNG, JPG, WebP, BMP, and GIF.

### Design decisions

- Use Pillow as the conversion engine.
- Keep the plugin interface aligned with the registry contract.
- Convert via `Image.open()` and `Image.save()`.
- Add explicit handling for mode conversion, transparency, and multi-frame images later.

### Scope

- Start with single-frame raster conversions.
- Keep PDFs, SVGs, and vector workflows out of this plugin for now.

## 2026-07-01 - ImageConverter implementation

### What changed

- Added a Pillow-based image conversion plugin.
- Supported raster inputs include PNG, JPG, WebP, BMP, GIF, and TIFF.
- Added output handling for JPEG alpha flattening.
- Added optional save parameters like quality and optimize.

### Notes

- This plugin only handles raster image format conversion.
- Animated and multi-frame edge cases are not fully handled yet.

## 2026-07-01 - Batch CLI for images

### What changed

- Added folder-based batch conversion support.
- Added recursive file discovery.
- Added per-file conversion results and summary output.
- Designed the batch flow so each file converts independently.

### Notes

- Default behavior is safe and non-destructive.
- Batch mode should continue past failures unless fail-fast is requested.

## 2026-07-01 - Batch image CLI

### What changed

- Added a batch command for folder-based conversion.
- Added recursive scanning support.
- Added per-file result reporting.
- Added a summary count for ok/skipped/failed files.

### Notes

- Batch mode is folder-friendly and suitable for image collections.
- Future improvement: add filtering by allowed extensions and optional progress bars.

## 2026-07-02 - Batch filtering and progress

### What changed

- Added supported-file filtering for batch conversion.
- Added tqdm progress feedback for folder runs.
- Kept batch conversion per-file and non-blocking on individual failures.

### Notes

- Progress should reflect actual files being processed.
- Unsupported files should be skipped before conversion starts.

## 2026-07-02 - Progress and filtering

### What changed

- Added supported-file filtering to batch traversal.
- Added tqdm-based progress display.
- Added `--no-progress` to disable the bar in scripts.

### Notes

- Progress bar uses prefiltered files only.
- Unsupported files are not converted or counted.

## 2026-07-02 - Preserve subfolder structure in batch

### What changed

- Batch output now mirrors the input folder structure under the chosen output root.
- Relative paths are computed from the input root to each source file.
- Output filenames keep the same stem with a new extension.

### Notes

- This avoids filename collisions for different subfolders.
- Makes it easier to map converted files back to their originals.

## 2026-07-02 - Preserve directory structure in batch output

### What changed

- Batch conversion now mirrors the input folder structure under the output directory.
- Output paths use the source file’s path relative to the batch input root.
- Filenames keep the same stem and only change the extension.

### Notes

- Avoids collisions when different subfolders contain files with the same name.
- Makes it easy to match converted files back to originals.

## 2026-07-02 - Document batch path mirroring

### What changed

- Added a code comment explaining why relative paths are used in batch output.
- Documented how `relative_to()` helps recreate the input folder tree under the output directory.

### Notes

- This keeps batch output organized and avoids filename collisions.
- The output path is derived from the source file’s subpath under the input root.

## 2026-07-02 - Dry-run mode

### What changed

- Added a dry-run mode for batch conversion.
- Dry-run prints the planned output tree without writing files.
- Dry-run is useful for checking recursive batch runs before executing them.

### Notes

- Output should mirror the real batch layout.
- No files should be created in dry-run mode.

## 2026-07-02 - JSON dry-run export

### What changed

- Added JSON output for dry-run results.
- Dry-run can now be piped into scripts and automation tools.
- Structured output mirrors the planned conversion tree.

### Notes

- JSON output should be machine-readable and stable.
- Plain text output remains available for interactive use.

## 2026-07-02 - Refine JSON script output

### What changed

- JSON output now goes to stdout without decorative text.
- Progress, summaries, and diagnostics stay on stderr.
- Dry-run JSON output is structured for piping into scripts.

### Notes

- Keep stdout reserved for data.
- Keep stderr for human-facing status.

## 2026-07-02 - Format switch for output

### What changed

- Added a `--format` switch for batch output.
- Supported values are `text` and `json`.
- JSON output is kept machine-readable for scripts.

### Notes

- Text remains the default for interactive use.
- JSON is intended for piping into automation.

## 2026-07-02 - JSON metadata enrichment

### What changed

- Added timing metadata to JSON export.
- Added summary counts to the top-level payload.
- Kept per-file results in a stable results array.

### Notes

- Use monotonic timing for elapsed duration.
- JSON should remain stable for scripts and automation.

## 2026-07-02 - Batch JSON tests

### What changed

- Added tests for dry-run JSON export.
- Added tests for stdout/stderr separation.
- Added tests for mirrored subfolder output paths.

### Notes

- JSON output must stay stable for scripts.
- Text mode should remain human-readable.

## 2026-07-02 - Output mode cleanup

### What changed

- Simplified output-mode branching in the batch command.
- Centralized formatting logic for text and json output.
- Kept JSON output clean for scripts and pipelines.

### Notes

- Use one path for result collection.
- Use one path for final emission.

## 2026-07-02 - Documentation update

### What changed

- Documented dry-run and JSON output usage.
- Added examples for piping JSON into scripts.
- Documented output-stream behavior.
- Added architecture notes for CLI flow and payload shapes.
- Documented stdout/stderr separation.

### Notes

- README should match the final CLI contract.
- Keep docs aligned with `--format` and dry-run JSON behavior.
