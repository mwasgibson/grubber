from pathlib import Path

import typer

from .core import ConversionManager
from .errors import FileConvError

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
):
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        results = manager.convert_many(
            [input_path],
            to,
            output_root=out_dir,
            recursive=recursive,
            overwrite=overwrite,
            show_progress=not no_progress,
            dry_run=dry_run,
        )
        
        for item in results:
            typer.echo(f"{item['status'].upper()}: {item['input']} -> {item['output']} {item['reason'] or ''}".rstrip())
            
        planned = sum(1 for item in results if item["status"] == "planned")
        ok = sum(1 for item in results if item["status"] == "ok")
        skipped = sum(1 for item in results if item["status"] == "skipped")
        failed = sum(1 for item in results if item["status"] == "failed")

        if dry_run:
            typer.echo(f"Dry run summary: planned={planned} total={len(results)}")
        else:
            typer.echo(f"Summary: ok={ok} skipped={skipped} failed={failed} total={len(results)}")
    except FileConvError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
        
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