"""Raster image converter powered by Pillow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from ..core import converter
from ..errors import FileConvError

_EXT_TO_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}

_MIME_TO_EXT = {v: k for k, v in _EXT_TO_MIME.items()}
_MIME_TO_EXT["image/jpeg"] = ".jpg"


@converter(name="pillow", priority=5)
class PillowImageConverter:
    """Convert image files using Pillow."""

    name = "pillow"
    priority = 5

    supported_input_mimes = set(_EXT_TO_MIME.values())
    supported_output_mimes = set(_EXT_TO_MIME.values())

    @classmethod
    def supports(cls, input_mime: str, output_mime: str) -> bool:
        return (
            input_mime in cls.supported_input_mimes
            and output_mime in cls.supported_output_mimes
        )

    @classmethod
    def supported_inputs(cls) -> set[str]:
        return set(cls.supported_input_mimes)

    @classmethod
    def supported_outputs(cls) -> set[str]:
        return set(cls.supported_output_mimes)

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        *,
        options: dict[str, Any] | None = None,
    ) -> Path:
        options = options or {}
        output_path.parent.mkdir(parents=True, exist_ok=True)

        target_format = output_path.suffix.lstrip(".").upper()
        if target_format == "JPG":
            target_format = "JPEG"

        try:
            with Image.open(input_path) as image:
                # Flatten alpha when targeting JPEG
                if output_path.suffix.lower() in {".jpg", ".jpeg"} and image.mode in {
                    "RGBA",
                    "LA",
                    "P",
                }:
                    image = image.convert("RGB")

                save_kwargs: dict[str, Any] = {}
                if "quality" in options:
                    save_kwargs["quality"] = options["quality"]
                if "optimize" in options:
                    save_kwargs["optimize"] = options["optimize"]

                image.save(output_path, format=target_format, **save_kwargs)
        except Exception as exc:
            raise FileConvError(f"Pillow conversion failed: {exc}") from exc

        if not output_path.exists():
            raise FileConvError(f"Pillow did not create output file: {output_path}")

        return output_path
