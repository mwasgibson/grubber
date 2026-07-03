"""Single-file conversion command for FileConv."""

from __future__ import annotations

from pathlib import Path

import typer

from ..core import ConversionManager
from ..errors import FileConvError

manager = ConversionManager()


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