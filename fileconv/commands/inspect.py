"""Inspect a file and report what FileConv sees."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from ..core import ConversionManager, REGISTRY
from ..detection import detect_format

manager = ConversionManager()


def inspect(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="File (or directory) to inspect.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit machine-readable JSON.",
    ),
) -> None:
    """Inspect an input file and report format + recommended converters."""
    if input_path.is_dir():
        typer.echo(f"Directory: {input_path}", err=True)
        typer.echo("Pass a single file for detailed inspection.", err=True)
        raise typer.Exit(code=1)

    detection = detect_format(input_path)
    recommendations = REGISTRY.recommend(detection.mime)

    payload = {
        "path": str(input_path),
        "size_bytes": input_path.stat().st_size,
        "detection": {
            "mime": detection.mime,
            "extension": detection.extension,
            "source": detection.source,
            "confidence": detection.confidence,
        },
        "recommendations": [
            {"converter": name, "output_mime": out} for name, out in recommendations
        ],
    }

    if as_json:
        typer.echo(json.dumps(payload, indent=2))
        return

    typer.echo(f"File: {input_path}")
    typer.echo(f"Size: {payload['size_bytes']} bytes")
    typer.echo("")
    typer.echo("Detection")
    typer.echo(f"  MIME:       {detection.mime}")
    typer.echo(f"  Extension:  {detection.extension or '(none)'}")
    typer.echo(f"  Source:     {detection.source} (confidence {detection.confidence})")
    typer.echo("")
    if recommendations:
        typer.echo("Recommended conversions")
        for name, out in recommendations:
            typer.echo(f"  {name} → {out}")
    else:
        typer.echo("No registered converter supports this input MIME.")
