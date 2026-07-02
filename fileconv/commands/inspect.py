from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


@app.command()
def run(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
):
    """Inspect an input file or directory and report what FileConv sees."""
    typer.echo(f"Inspecting: {input_path}")