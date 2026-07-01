from pathlib import Path

from PIL import Image

from fileconv.converters.image import PillowImageConverter


def test_pillow_converter_supports_png_to_jpeg():
    assert PillowImageConverter.supports("image/png", "image/jpeg")


def test_pillow_converter_converts_png_to_jpeg(tmp_path: Path):
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.jpg"

    image = Image.new("RGBA", (32, 32), (255, 0, 0, 128))
    image.save(input_path)

    converter = PillowImageConverter()
    result = converter.convert(input_path, output_path, options={"quality": 85, "optimize": True})

    assert result == output_path
    assert output_path.exists()