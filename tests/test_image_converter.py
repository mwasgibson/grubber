"""Pillow converter tests."""

from pathlib import Path

from fileconv.converters.image import PillowImageConverter


def _tiny_png(path: Path) -> None:
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01"
        b"\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def test_png_to_jpeg(tmp_path: Path):
    src = tmp_path / "in.png"
    dst = tmp_path / "out.jpg"
    _tiny_png(src)
    result = PillowImageConverter().convert(src, dst)
    assert result.exists()
    assert result.suffix == ".jpg"


def test_supports_image_mimes():
    assert PillowImageConverter.supports("image/png", "image/jpeg")
    assert not PillowImageConverter.supports("application/pdf", "image/png")
