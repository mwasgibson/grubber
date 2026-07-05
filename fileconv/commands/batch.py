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


def emit_batch_output(*, payload: dict[str, Any], dry_run: bool, output_format: OutputFormat) -> None:
    if output_format == OutputFormat.json:
        export = build_batch_payload(mode="dry_run" if dry_run else "batch", payload=payload)
        sys.stdout.write(json.dumps(export, indent=2) + "\n")
        return

    for item in payload["results"]:
        typer.echo(
            f"{item['status'].upper()}: {item['input']} -> {item['output']} {item['reason'] or ''}".rstrip(),
            err=True,
        )

    counts = payload["counts"]
    if dry_run:
        typer.echo(f"Dry run summary: planned={counts['planned']} total={counts['total']}", err=True)
    else:
        typer.echo(
            f"Summary: ok={counts['ok']} skipped={counts['skipped']} failed={counts['failed']} total={counts['total']}",
            err=True,
        )


def batch(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
    to: str = typer.Option(..., "--to", "-t"),
    out_dir: Path = typer.Option(..., "--out-dir", "-o"),
    recursive: bool = typer.Option(False, "--recursive", "-r"),
    overwrite: bool = typer.Option(False, "--overwrite"),
    no_progress: bool = typer.Option(False, "--no-progress"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    output_format: OutputFormat = typer.Option(OutputFormat.text, "--format"),
):
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
        )
        emit_batch_output(payload=payload, dry_run=dry_run, output_format=output_format)
    except FileConvError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc