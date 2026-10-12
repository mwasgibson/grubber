"""CLI-level batch tests using Typer CliRunner."""

from pathlib import Path

from typer.testing import CliRunner

from fileconv.cli import app

runner = CliRunner()


def _tiny_png(path: Path) -> None:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01"
        b"\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "1.5.0" in result.stdout


def test_batch_dry_run_json(tmp_path: Path):
    src = tmp_path / "a.png"
    _tiny_png(src)
    out = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "batch",
            str(src),
            "--to",
            "jpg",
            "--out-dir",
            str(out),
            "--dry-run",
            "--format",
            "json",
            "--no-progress",
        ],
    )
    assert result.exit_code == 0
    assert '"mode": "dry_run"' in result.stdout
    assert '"planned": 1' in result.stdout


def test_doctor_runs():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "FileConv doctor" in result.stdout
    assert "1.5.0" in result.stdout
