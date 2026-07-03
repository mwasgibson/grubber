"""Root CLI entrypoint for FileConv."""

from __future__ import annotations

import typer

from .commands.batch import batch
from .commands.convert import convert
from .commands.doctor import doctor
from .commands.inspect import inspect
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


app.command(name="batch")(batch)
app.command(name="convert")(convert)
app.command(name="doctor")(doctor)
app.command(name="inspect")(inspect)