from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from fileconv.cli import app
from fileconv.core import ConversionManager

# Use mix_stderr=False so stdout/stderr can be asserted separately.
# This is the recommended pattern when testing Typer CLIs that separate JSON and logs. [web:422][web:500][web:654]
runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "0.1.0"


def test_doctor_command():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "FileConv doctor" in result.stdout


def test_batch_json_dry_run(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "a.txt").write_text("hello")

    out_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "batch",
            str(input_dir),
            "--to",
            "pdf",
            "--out-dir",
            str(out_dir),
            "--recursive",
            "--dry-run",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0

    # JSON should be clean on stdout. [web:422][web:458][web:646]
    payload = json.loads(result.stdout)
    assert payload["format"] == "json"
    assert payload["mode"] == "dry_run"
    assert payload["counts"]["planned"] == 1
    assert payload["results"][0]["status"] == "planned"


def test_batch_text_mode_stderr(tmp_path: Path):
    input_file = tmp_path / "a.txt"
    input_file.write_text("hello")
    out_dir = tmp_path / "out"

    result = runner.invoke(
        app,
        [
            "batch",
            str(input_file),
            "--to",
            "pdf",
            "--out-dir",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0

    # Text mode keeps JSON-clean stdout and sends human output to stderr. [web:422][web:458][web:631]
    assert result.stdout == ""
    assert "Summary:" in result.stderr


def test_convert_many_payload_shape(tmp_path: Path):
    manager = ConversionManager()
    input_file = tmp_path / "a.txt"
    input_file.write_text("hello")
    out_dir = tmp_path / "out"

    payload = manager.convert_many([input_file], "pdf", output_root=out_dir, dry_run=True)

    assert "elapsed_seconds" in payload
    assert "counts" in payload
    assert "results" in payload
    assert payload["counts"]["planned"] == 1
    assert len(payload["results"]) == 1
    assert payload["results"][0]["status"] == "planned"