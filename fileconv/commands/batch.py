"""Batch conversion command with recursion, filters, parallel jobs, and JSON export."""

from __future__ import annotations

import json
import sys
from enum import Enum
from pathlib import Path
from typing import Any

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
    recursive: bool = typer.Option(
        False,
        "--recursive",
        "-r",
        help="Process files under subdirectories.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Replace existing output files.",
    ),
    jobs: int = typer.Option(
        1,
        "--jobs",
        "-j",
        min=1,
        help="Number of parallel conversion workers.",
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
    no_progress: bool = typer.Option(
        False,
        "--no-progress",
        help="Disable the progress bar.",
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
    """Convert many files. Supports recursion, filters, parallel jobs, and JSON export."""
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = manager.convert_many(
            [input_path],
            to,
            output_root=out_dir,
            recursive=recursive,
            overwrite=overwrite,
            show_progress=not no_progress and output_format == OutputFormat.text,
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
