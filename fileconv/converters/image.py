"""Image converter implementation for FileConv."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from ..core import converter


@converter(name="pillow")
class PillowImageConverter:
    """Convert image files using Pillow."""

    name = "pillow"
    priority = 0

    @classmethod
    def supported_inputs(cls) -> set[str]:
        return {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

    @classmethod
    def supported_outputs(cls) -> set[str]:
        return {"png", "jpg", "jpeg", "webp", "bmp", "gif", "tif", "tiff"}

    def can_handle(self, input_path: Path, to: str) -> bool:
        return input_path.suffix.lower() in self.supported_inputs() and to.lower().lstrip(".") in self.supported_outputs()

    def convert(self, input_path: Path, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_format = output_path.suffix.lstrip(".").upper()
        if target_format == "JPG":
            target_format = "JPEG"

        with Image.open(input_path) as image:
            if output_path.suffix.lower() in {".jpg", ".jpeg"} and image.mode in {"RGBA", "LA", "P"}:
                image = image.convert("RGB")
            image.save(output_path, format=target_format)

        return output_path