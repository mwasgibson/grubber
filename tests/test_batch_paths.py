"""Batch path discovery and mirroring tests."""

from pathlib import Path

from fileconv.core import collect_files, relative_output_path, ConversionManager


def test_collect_files_non_recursive(tmp_path: Path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.png").write_bytes(b"y")
    files = collect_files(tmp_path, recursive=False)
    assert len(files) == 1
    assert files[0].name == "a.png"


def test_collect_files_recursive(tmp_path: Path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.png").write_bytes(b"y")
    files = collect_files(tmp_path, recursive=True)
    assert len(files) == 2


def test_collect_files_include_exclude(tmp_path: Path):
    (tmp_path / "keep.png").write_bytes(b"x")
    (tmp_path / "skip.jpg").write_bytes(b"y")
    files = collect_files(tmp_path, include=["*.png"])
    assert [f.name for f in files] == ["keep.png"]
    files = collect_files(tmp_path, exclude=["*.jpg"])
    assert [f.name for f in files] == ["keep.png"]


def test_relative_output_path_mirrors_tree(tmp_path: Path):
    src_root = tmp_path / "src"
    (src_root / "nested").mkdir(parents=True)
    src = src_root / "nested" / "photo.png"
    src.write_bytes(b"x")
    out_root = tmp_path / "out"
    result = relative_output_path(src, src_root, out_root, "jpg")
    assert result == out_root / "nested" / "photo.jpg"


def test_convert_many_dry_run(tmp_path: Path):
    src = tmp_path / "img.png"
    src.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01"
        b"\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    out = tmp_path / "out"
    manager = ConversionManager()
    payload = manager.convert_many(
        [src],
        "jpg",
        output_root=out,
        dry_run=True,
    )
    assert payload["counts"]["planned"] == 1
    assert payload["counts"]["total"] == 1
    assert payload["results"][0]["status"] == "planned"


def test_convert_many_excludes_output_tree(tmp_path: Path):
    """Files already under output_root must not be picked up as inputs."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.png").write_bytes(b"x")
    out = src / "converted"
    out.mkdir()
    (out / "prior.jpg").write_bytes(b"y")

    manager = ConversionManager()
    payload = manager.convert_many(
        [src],
        "jpg",
        output_root=out,
        recursive=True,
        dry_run=True,
    )
    inputs = [r["input"] for r in payload["results"]]
    assert any(Path(i).name == "a.png" for i in inputs)
    assert not any("prior.jpg" in i for i in inputs)
    assert not any("converted" in Path(i).parts and Path(i).name == "prior.jpg" for i in inputs)


def test_is_under_helper(tmp_path: Path):
    from fileconv.core import is_under

    root = tmp_path / "out"
    root.mkdir()
    nested = root / "nested" / "f.jpg"
    nested.parent.mkdir(parents=True)
    nested.write_bytes(b"z")
    outside = tmp_path / "other.jpg"
    outside.write_bytes(b"z")
    assert is_under(nested, root) is True
    assert is_under(root, root) is True
    assert is_under(outside, root) is False
