"""Batch conversion command with recursion, filters, parallel jobs, and JSON export."""

from __future__ import annotations

import json
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import typer

from ..core import ConversionManager
from ..errors import FileConvError

manager = ConversionManager()


class OutputFormat(str, Enum):
    text = "text"
    json = "json"


def build_batch_payload(*, mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": mode,
        "format": "json",
        "counts": payload["counts"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "results": payload["results"],
    }


def emit_batch_output(
    *,
    payload: dict[str, Any],
    dry_run: bool,
    output_format: OutputFormat,
) -> None:
    if output_format == OutputFormat.json:
        export = build_batch_payload(
            mode="dry_run" if dry_run else "batch", payload=payload
        )
        sys.stdout.write(json.dumps(export, indent=2) + "\n")
        return

    for item in payload["results"]:
        reason = f" ({item['reason']})" if item.get("reason") else ""
        converter = f" [{item['converter']}]" if item.get("converter") else ""
        typer.echo(
            f"{item['status'].upper()}: {item['input']} -> {item['output']}{converter}{reason}",
            err=True,
        )

    counts = payload["counts"]
    if dry_run:
        typer.echo(
            f"Dry-run summary: planned={counts['planned']} total={counts['total']}",
            err=True,
        )
    else:
        typer.echo(
            f"Summary: ok={counts['ok']} skipped={counts['skipped']} "
            f"failed={counts['failed']} total={counts['total']} "
            f"({payload['elapsed_seconds']}s)",
            err=True,
        )


def batch(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input file or directory.",
    ),
    to: str = typer.Option(
        ...,
        "--to",
        "-t",
        help="Target format / extension.",
    ),
    out_dir: Path = typer.Option(
        ...,
        "--out-dir",
        "-o",
        help="Root directory for converted files (mirrors input tree when recursive).",
    ),
    recursive: Optional[bool] = typer.Option(
        None,
        "--recursive/--no-recursive",
        "-r",
        help="Process files under subdirectories. Default: config or false.",
    ),
    overwrite: Optional[bool] = typer.Option(
        None,
        "--overwrite/--no-overwrite",
        help="Replace existing output files. Default: config or false.",
    ),
    jobs: Optional[int] = typer.Option(
        None,
        "--jobs",
        "-j",
        min=1,
        help="Number of parallel conversion workers. Default: config or 1.",
    ),
    include: list[str] = typer.Option(
        None,
        "--include",
        "-i",
        help="Only process files matching these globs (repeatable).",
    ),
    exclude: list[str] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Skip files matching these globs (repeatable).",
    ),
    no_progress: Optional[bool] = typer.Option(
        None,
        "--no-progress/--progress",
        help="Disable/enable the progress bar. Default: config or enabled for text.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show planned conversions without writing files.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.text,
        "--format",
        "-f",
        help="Output format: text (default) or json.",
    ),
) -> None:
    """Convert many files. Supports recursion, filters, parallel jobs, and JSON export.

    Unspecified flags (recursive, overwrite, jobs, progress) inherit from
    ~/.config/fileconv/config.toml when present.
    """
    try:
        out_dir.mkdir(parents=True, exist_ok=True)

        # Resolve progress: explicit CLI wins; otherwise leave None for config
        # (JSON mode still forces progress off for clean stdout).
        if output_format == OutputFormat.json:
            show_progress: bool | None = False
        elif no_progress is True:
            show_progress = False
        elif no_progress is False:
            show_progress = True
        else:
            show_progress = None

        payload = manager.convert_many(
            [input_path],
            to,
            output_root=out_dir,
            recursive=recursive,
            overwrite=overwrite,
            show_progress=show_progress,
            dry_run=dry_run,
            jobs=jobs,
            include=include or None,
            exclude=exclude or None,
        )
        emit_batch_output(
            payload=payload, dry_run=dry_run, output_format=output_format
        )
        if payload["counts"]["failed"] > 0 and not dry_run:
            raise typer.Exit(code=1)
    except FileConvError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
