from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..core import converter
from ..errors import DependencyMissingError, FileConvError

def find_libreoffice_binary() -> str | None:
        for candidate in ("libreoffice", "soffice", "soffice.com"):
            path = shutil.which(candidate)
            if path:
                return path
        return None

@converter(name="libreoffice")
class LibreOfficeConverter:
    name = "libreoffice"
    priority = 0

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
        binary = find_libreoffice_binary()
        if binary is None:
            raise DependencyMissingError("LibreOffice binary not found")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        out_ext = output_path.suffix.lower().lstrip(".")

        import tempfile
        profile_dir = tempfile.mkdtemp(prefix="fileconv-lo-profile-")

        cmd = [
            binary,
            "--headless",
            "--norestore",
            f"-env:UserInstallation=file://{profile_dir}",
            "--convert-to",
            out_ext,
            "--outdir",
            str(output_path.parent),
            str(input_path),
        ]

        # Special handling: PDF → DOC/DOCX often needs the PDF import filter
        if input_path.suffix.lower() == ".pdf" and out_ext in {"doc", "docx"}:
            cmd.insert(2, "--infilter=writer_pdf_import")

        subprocess.run(cmd, check=True)

        # LibreOffice writes to <stem>.<out_ext> in the outdir
        produced = output_path.parent / f"{input_path.stem}.{out_ext}"
        if produced.exists() and produced != output_path:
            produced.replace(output_path)

        if not output_path.exists():
            raise FileConvError(f"LibreOffice did not create output file: {output_path}")

        return output_path