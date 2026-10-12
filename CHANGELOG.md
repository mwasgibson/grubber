# Changelog

All notable changes to FileConv are documented in this file.

The format follows a simple release-first style:
- **Added** for new features.
- **Changed** for behavior updates.
- **Fixed** for bug fixes.
- **Removed** for deleted features.

## [1.5.0] - 2026-10-12

### Added
- Priority-based converter resolution via `supports()` instead of hard-coded MIME pairs.
- Real recursive batch conversion with folder-structure preservation.
- Parallel conversion workers (`--jobs N`).
- Include / exclude glob filters for batch.
- Working `--overwrite` / skip-existing logic.
- Full `doctor` command (binaries, packages, converters, config).
- Working `inspect` command (MIME detection + recommended converters).
- Optional user config at `~/.config/fileconv/config.toml`.
- Dynamic entry-point plugin loading (`fileconv.converters` group).
- Progress bar (tqdm) with `--no-progress` switch.
- Expanded test suite covering registry, paths, filters, CLI, and converters.

### Changed
- Version bumped to 1.5.0.
- CLI polish: clearer help text, consistent short flags, richer summaries.
- LibreOffice converter now cleans temporary user profiles and surfaces stderr on failure.
- pdf2docx preferred over LibreOffice for PDF → DOCX (higher priority).
- Package metadata, README, and architecture docs aligned with 1.5 behaviour.

### Fixed
- Batch previously ignored `--recursive` and did not mirror directory trees.
- Overwrite flag was accepted but not enforced.
- Doctor was a minimal stub; now reports actionable diagnostics.

## [0.1.0] - 2026-07-06

### Added
- Initial release of FileConv.
- Converter registry and MIME-based routing.
- LibreOffice-based office document conversion.
- pdf2docx support for PDF to DOCX conversion.
- Doctor command for environment validation.

### Changed
- Introduced a pluggable converter structure for future backends.
