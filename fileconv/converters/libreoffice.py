from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..core import converter
from ..errors import DependencyMissingError


@converter(name="libreoffice", priority=10)
class LibreOfficeConverter:
    supported_input_mimes = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }

    supported_output_mimes = {
        "application/pdf",
        "text/plain",
        "text/html",
        "application/vnd.oasis.opendocument.text",
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
        binary = shutil.which("libreoffice") or shutil.which("soffice")
        if binary is None:
            raise DependencyMissingError("LibreOffice binary not found")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        outdir = output_path.parent
        target_ext = output_path.suffix.lstrip(".")

        subprocess.run(
            [
                binary,
                "--headless",
                "--convert-to",
                target_ext,
                "--outdir",
                str(outdir),
                str(input_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        produced = outdir / f"{input_path.stem}.{target_ext}"
        if produced != output_path and produced.exists():
            produced.replace(output_path)

        return output_path