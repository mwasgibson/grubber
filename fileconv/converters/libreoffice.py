"""LibreOffice-backed office document converter."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
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


@converter(name="libreoffice", priority=10)
class LibreOfficeConverter:
    """Convert office documents via headless LibreOffice."""

    name = "libreoffice"
    priority = 10

    supported_input_mimes = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.ms-powerpoint",
        "application/rtf",
        "text/plain",
        "text/html",
        "application/pdf",  # PDF import filter for PDF → office
    }

    supported_output_mimes = {
        "application/pdf",
        "text/plain",
        "text/html",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
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
            raise DependencyMissingError(
                "LibreOffice binary not found (install libreoffice or ensure soffice is on PATH)"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        out_ext = output_path.suffix.lower().lstrip(".")

        profile_dir = tempfile.mkdtemp(prefix="fileconv-lo-profile-")
        try:
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

            # PDF → DOC/DOCX benefits from the PDF import filter
            if input_path.suffix.lower() == ".pdf" and out_ext in {"doc", "docx"}:
                cmd.insert(2, "--infilter=writer_pdf_import")

            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout or "").strip()
                raise FileConvError(
                    f"LibreOffice failed (exit {result.returncode}): {detail or 'no output'}"
                )

            produced = output_path.parent / f"{input_path.stem}.{out_ext}"
            if produced.exists() and produced != output_path:
                produced.replace(output_path)

            if not output_path.exists():
                raise FileConvError(f"LibreOffice did not create output file: {output_path}")

            return output_path
        finally:
            shutil.rmtree(profile_dir, ignore_errors=True)
