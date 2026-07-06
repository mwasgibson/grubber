import importlib
from pathlib import Path

import pytest

from fileconv.converters.pdf2docx import Pdf2DocxConverter
from fileconv.errors import DependencyMissingError


def test_pdf2docx_converter_requires_optional_dependency(tmp_path: Path):
    converter = Pdf2DocxConverter()
    input_path = tmp_path / "sample.pdf"
    input_path.write_bytes(b"%PDF-1.4\n")
    output_path = tmp_path / "sample.docx"

    with pytest.raises(DependencyMissingError, match="pdf2docx"):
        converter.convert(input_path, output_path)


def test_repo_sample_pdf_is_valid():
    sample_pdf = Path(__file__).resolve().parents[1] / "sample.pdf"

    assert sample_pdf.exists()

    fitz = importlib.import_module("fitz")
    with fitz.open(sample_pdf) as doc:
        assert doc.page_count == 1

        text_parts: list[str] = []
        for page in doc:
            page_text = page.get_text()
            text_parts.append(page_text if isinstance(page_text, str) else str(page_text))

        text = " ".join(text_parts)

    assert "Hello" in text
