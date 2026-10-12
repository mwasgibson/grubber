"""Config inheritance for batch options."""

from pathlib import Path

from fileconv.config import FileConvConfig
from fileconv.core import ConversionManager


def test_convert_many_inherits_recursive_from_config(tmp_path: Path):
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "top.png").write_bytes(b"x")
    (src / "sub" / "nested.png").write_bytes(b"y")
    out = tmp_path / "out"

    cfg = FileConvConfig(recursive=True, jobs=1, overwrite=False, show_progress=False)
    manager = ConversionManager(config=cfg)
    payload = manager.convert_many(
        [src],
        "jpg",
        output_root=out,
        recursive=None,
        dry_run=True,
        show_progress=False,
    )
    names = {Path(r["input"]).name for r in payload["results"]}
    assert "top.png" in names
    assert "nested.png" in names


def test_convert_many_cli_override_beats_config(tmp_path: Path):
    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "top.png").write_bytes(b"x")
    (src / "sub" / "nested.png").write_bytes(b"y")
    out = tmp_path / "out"

    cfg = FileConvConfig(recursive=True, jobs=1, show_progress=False)
    manager = ConversionManager(config=cfg)
    payload = manager.convert_many(
        [src],
        "jpg",
        output_root=out,
        recursive=False,
        dry_run=True,
        show_progress=False,
    )
    names = {Path(r["input"]).name for r in payload["results"]}
    assert "top.png" in names
    assert "nested.png" not in names
