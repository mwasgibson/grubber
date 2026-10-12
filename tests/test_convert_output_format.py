"""Enforce --to vs --output consistency."""

from pathlib import Path

import pytest

from fileconv.core import ConversionManager
from fileconv.errors import FileConvError


def test_explicit_output_must_match_to(tmp_path: Path):
    src = tmp_path / "photo.png"
    src.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01"
        b"\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    manager = ConversionManager()
    with pytest.raises(FileConvError, match="does not match"):
        manager.convert(src, "jpg", output_path=tmp_path / "result.webp")


def test_explicit_output_matching_to_ok(tmp_path: Path):
    src = tmp_path / "photo.png"
    src.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01"
        b"\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    out = tmp_path / "subdir" / "result.jpg"
    manager = ConversionManager()
    result = manager.convert(src, "jpg", output_path=out, overwrite=True)
    assert result == out
    assert result.exists()


def test_jpg_jpeg_equivalent(tmp_path: Path):
    src = tmp_path / "photo.png"
    src.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01"
        b"\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    out = tmp_path / "result.jpeg"
    manager = ConversionManager()
    result = manager.convert(src, "jpg", output_path=out, overwrite=True)
    assert result.exists()
