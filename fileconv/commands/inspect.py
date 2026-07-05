from __future__ import annotations

from pathlib import Path

import typer


def inspect(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
):
    """Inspect an input file or directory and report what FileConv sees."""
    typer.echo(f"Inspecting: {input_path}")