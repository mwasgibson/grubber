from pathlib import Path

from PIL import Image

from fileconv.converters.image import PillowImageConverter


def test_pillow_image_converter_round_trip(tmp_path: Path):
    source = tmp_path / "input.png"
    target = tmp_path / "output.jpg"

    image = Image.new("RGBA", (10, 10), (255, 0, 0, 128))
    image.save(source)

    converter = PillowImageConverter()
    result = converter.convert(source, target)

    assert result == target
    assert target.exists()
    with Image.open(target) as out:
        assert out.format == "JPEG"