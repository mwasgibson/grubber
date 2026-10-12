"""Single-file conversion command."""

from __future__ import annotations

from pathlib import Path

import typer

from ..core import ConversionManager
from ..errors import FileConvError

manager = ConversionManager()


def convert(
    input_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        help="Input file to convert.",
    ),
    to: str = typer.Option(
        ...,
        "--to",
        "-t",
        help="Target format / extension (e.g. pdf, docx, png).",
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Explicit output file path. Overrides --out-dir.",
    ),
    out_dir: Path | None = typer.Option(
        None,
        "--out-dir",
        help="Directory for the output file (filename derived from input).",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Replace an existing output file.",
    ),
) -> None:
    """Convert a single file to another format."""
    try:
        output_path: Path | None = output
        if output_path is None and out_dir is not None:
            output_path = out_dir / f"{input_path.stem}.{to.lstrip('.')}"

        result = manager.convert(
            input_path,
            to,
            output_path=output_path,
            overwrite=overwrite,
        )
        typer.echo(str(result))
    except FileConvError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
