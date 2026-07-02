from __future__ import annotations

import typer

from .commands.batch import app as batch_app
from .commands.convert import app as convert_app
from .commands.doctor import app as doctor_app
from .commands.inspect import app as inspect_app
from .version import __version__

app = typer.Typer(add_completion=True, no_args_is_help=True)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show the installed version and exit.",
    ),
):
    """FileConv: batch file conversion with dry-run, JSON export, and environment checks."""
    pass


app.add_typer(batch_app, name="batch", help="Batch conversion commands.")
app.add_typer(convert_app, name="convert", help="Single-file conversion commands.")
app.add_typer(doctor_app, name="doctor", help="Environment checks.")
app.add_typer(inspect_app, name="inspect", help="Inspect input files and planned outputs.")