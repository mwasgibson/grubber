"""PDF → DOCX converter using the pdf2docx library."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from ..core import converter
from ..errors import DependencyMissingError, FileConvError


@converter(name="pdf2docx", priority=20)
class Pdf2DocxConverter:
    """Convert PDF files to DOCX using pdf2docx (higher priority than LibreOffice for this pair)."""

    name = "pdf2docx"
    priority = 20

    supported_input_mimes = {"application/pdf"}
    supported_output_mimes = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
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
        if input_path.suffix.lower() != ".pdf":
            raise FileConvError("pdf2docx only supports PDF input")

        try:
            pdf2docx_module = importlib.import_module("pdf2docx")
            converter_cls = getattr(pdf2docx_module, "Converter")
        except ImportError as exc:
            raise DependencyMissingError("pdf2docx is not installed") from exc

        output_path.parent.mkdir(parents=True, exist_ok=True)

        cv: Any = converter_cls(str(input_path))
        try:
            cv.convert(str(output_path), start=0, end=None)
        finally:
            cv.close()

        if not output_path.exists():
            raise FileConvError(f"pdf2docx did not create output file: {output_path}")

        return output_path
