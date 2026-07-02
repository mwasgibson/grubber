from __future__ import annotations

import shutil
from pathlib import Path

import typer

app = typer.Typer(add_completion=False)


def _check_binary(name: str) -> str:
    path = shutil.which(name)
    return path if path else "not found"


@app.command()
def run() -> None:
    """Check whether the local environment is ready for FileConv."""
    typer.echo("FileConv doctor")
    typer.echo(f"LibreOffice soffice: {_check_binary('soffice')}")
    typer.echo(f"LibreOffice libreoffice: {_check_binary('libreoffice')}")
    typer.echo(f"Current directory exists: {'yes' if Path('.').exists() else 'no'}")
    typer.echo("Done.")