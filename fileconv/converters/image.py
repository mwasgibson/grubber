from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image

from ..core import converter


@converter(name="pillow")
class PillowImageConverter:
    name: str = "pillow"
    priority: int = 20

    supported_input_mimes = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/bmp",
        "image/gif",
        "image/tiff",
    }

    supported_output_mimes = {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/bmp",
        "image/gif",
        "image/tiff",
    }

    @classmethod
    def supports(cls, input_mime: str, output_mime: str) -> bool:
        return input_mime in cls.supported_input_mimes and output_mime in cls.supported_output_mimes

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
        output_ext = output_path.suffix.lower().lstrip(".")
        with Image.open(input_path) as img:
            img = self._apply_mode_rules(img, output_ext, options)
            save_kwargs = self._build_save_kwargs(output_ext, options)
            img.save(output_path, **save_kwargs)
        return output_path

    def _apply_mode_rules(self, img: Image.Image, output_ext: str, options: dict[str, Any]) -> Image.Image:
        requested_mode = options.get("mode")
        if requested_mode:
            return img.convert(str(requested_mode))

        if output_ext in {"jpg", "jpeg"} and img.mode in {"RGBA", "LA", "P"}:
            return img.convert("RGB")

        return img

    def _build_save_kwargs(self, output_ext: str, options: dict[str, Any]) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}

        if output_ext in {"jpg", "jpeg", "webp"} and "quality" in options:
            kwargs["quality"] = int(options["quality"])

        if "optimize" in options:
            kwargs["optimize"] = bool(options["optimize"])

        if "progressive" in options and output_ext in {"jpg", "jpeg"}:
            kwargs["progressive"] = bool(options["progressive"])

        return kwargs