"""Environment diagnostics command."""

from __future__ import annotations

import json

import typer

from ..core import ConversionManager

manager = ConversionManager()


def doctor(
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Emit machine-readable JSON.",
    ),
) -> None:
    """Check whether the local environment is ready for FileConv."""
    report = manager.doctor()

    if as_json:
        typer.echo(json.dumps(report, indent=2))
        return

    typer.echo(f"FileConv doctor  (v{report['version']})")
    typer.echo("")

    typer.echo("Binaries")
    for name, path in report["binaries"].items():
        status = path or "not found"
        typer.echo(f"  {name}: {status}")

    typer.echo("")
    typer.echo("Python packages")
    for name, ver in report["packages"].items():
        typer.echo(f"  {name}: {ver or 'not installed'}")

    typer.echo("")
    magic = report["format_detection"]["magic_available"]
    typer.echo(f"Format detection (python-magic): {'yes' if magic else 'no (extension fallback)'}")

    typer.echo("")
    typer.echo("Registered converters")
    for c in report["converters"]:
        typer.echo(
            f"  {c['name']} (priority={c['priority']})  "
            f"in={len(c['inputs'])} out={len(c['outputs'])}"
        )

    typer.echo("")
    cfg = report["config"]
    typer.echo("Config defaults")
    typer.echo(f"  default_output_dir: {cfg['default_output_dir']}")
    typer.echo(f"  jobs: {cfg['jobs']}")
    typer.echo(f"  overwrite: {cfg['overwrite']}")
    typer.echo("")
    typer.echo("Done.")
