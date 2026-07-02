from pathlib import Path
from typing import Any

import typer
import json
import sys

from .core import ConversionManager
from .errors import FileConvError
from enum import Enum

class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"

app = typer.Typer(add_completion=False)
manager = ConversionManager()

@app.command()
def convert(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
    to: str = typer.Option(..., "--to", "-t"),
    out_dir: Path | None = typer.Option(None, "--out-dir", "-o"),
):
    try:
        output_path = None
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = out_dir / f"{input_path.stem}.{to.lstrip('.')}"
        result = manager.convert(input_path, to, output_path=output_path)
        typer.echo(str(result))
    except FileConvError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def batch(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
    to: str = typer.Option(..., "--to", "-t"),
    out_dir: Path = typer.Option(..., "--out-dir", "-o"),
    recursive: bool = typer.Option(False, "--recursive", "-r"),
    overwrite: bool = typer.Option(False, "--overwrite"),
    no_progress: bool = typer.Option(False, "--no-progress"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    format: OutputFormat = typer.Option(OutputFormat.TEXT, "--format"),
):
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        payload = manager.convert_many(
            [input_path],
            to,
            output_root=out_dir,
            recursive=recursive,
            overwrite=overwrite,
            show_progress=not no_progress and format == OutputFormat.TEXT,
            dry_run=dry_run,
        )

        if format == OutputFormat.JSON:
            export: dict[str, Any] = build_batch_payload(
                mode="dry_run" if dry_run else "batch",
                payload=payload,
            )
            sys.stdout.write(json.dumps(export, indent=2) + "\n")
            return

        emit_batch_output(payload=payload, dry_run=dry_run, output_format=format)
    except FileConvError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

def build_batch_payload(*, mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": mode,
        "format": "json",
        "counts": payload["counts"],
        "elapsed_seconds": payload["elapsed_seconds"],
        "results": payload["results"],
    }


def render_batch_text(payload: dict[str, Any], *, dry_run: bool) -> str:
    lines: list[str] = []
    for item in payload["results"]:
        lines.append(
            f"{item['status'].upper()}: {item['input']} -> {item['output']} {item['reason'] or ''}".rstrip()
        )

    counts = payload["counts"]
    if dry_run:
        lines.append(f"Dry run summary: planned={counts['planned']} total={counts['total']}")
    else:
        lines.append(
            f"Summary: ok={counts['ok']} skipped={counts['skipped']} failed={counts['failed']} total={counts['total']}"
        )
    return "\n".join(lines)

def emit_batch_output(*, payload: dict[str, Any], dry_run: bool, output_format: OutputFormat) -> None:
    if output_format == OutputFormat.JSON:
        export: dict[str, Any] = {
            "mode": "dry_run" if dry_run else "batch",
            "format": "json",
            "counts": payload["counts"],
            "elapsed_seconds": payload["elapsed_seconds"],
            "results": payload["results"],
        }
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
        
@app.command()
def doctor():
    checks = manager.doctor()

    typer.echo("FileConv doctor report")
    typer.echo(f"Python: {checks['python']['version']} | ok={checks['python']['ok']}")
    typer.echo(f"Entry points loaded: {checks['entry_points']['ok']} | group={checks['entry_points']['group']}")
    typer.echo(f"Registered converters: {', '.join(checks['registry']['converters']) or 'none'}")
    typer.echo("Binaries:")

    for name, data in checks["binaries"].items():
        typer.echo(f"  - {name}: ok={data['ok']} path={data['path']}")

    typer.echo(f"Overall: {'ok' if checks['overall_ok'] else 'needs attention'}")