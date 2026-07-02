import json
from pathlib import Path

from typer.testing import CliRunner

from fileconv.cli import app


runner = CliRunner()


def test_batch_json_dry_run(tmp_path: Path):
    input_root = tmp_path / "images"
    out_root = tmp_path / "out"
    (input_root / "cats").mkdir(parents=True)
    (input_root / "cats" / "kitten.png").write_bytes(b"fake-image")
    (input_root / "dogs").mkdir(parents=True)
    (input_root / "dogs" / "puppy.png").write_bytes(b"fake-image")

    result = runner.invoke(
        app,
        [
            "batch",
            str(input_root),
            "--to",
            "webp",
            "--out-dir",
            str(out_root),
            "--recursive",
            "--dry-run",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)

    assert payload["mode"] == "dry_run"
    assert payload["format"] == "json"
    assert payload["counts"]["planned"] == 2
    assert payload["counts"]["total"] == 2
    assert len(payload["results"]) == 2
    assert payload["results"][0]["status"] == "planned"
    assert payload["results"][0]["output"].startswith(str(out_root))


def test_batch_preserves_structure(tmp_path: Path):
    input_root = tmp_path / "images"
    out_root = tmp_path / "out"
    (input_root / "cats").mkdir(parents=True)
    (input_root / "cats" / "kitten.png").write_bytes(b"fake-image")

    result = runner.invoke(
        app,
        [
            "batch",
            str(input_root),
            "--to",
            "webp",
            "--out-dir",
            str(out_root),
            "--recursive",
            "--dry-run",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    planned = payload["results"][0]["output"]
    assert planned == str(out_root / "cats" / "kitten.webp")
    
def test_batch_text_mode(tmp_path: Path):
    input_root = tmp_path / "images"
    out_root = tmp_path / "out"
    input_root.mkdir()
    (input_root / "kitten.png").write_bytes(b"fake-image")

    result = runner.invoke(
        app,
        [
            "batch",
            str(input_root),
            "--to",
            "webp",
            "--out-dir",
            str(out_root),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "PLANNED:" in result.stdout or "PLANNED:" in result.stderr    