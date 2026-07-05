from pathlib import Path

import pytest

from fileconv.converters.pdf2docx import Pdf2DocxConverter
from fileconv.errors import DependencyMissingError


def test_pdf2docx_converter_requires_optional_dependency(tmp_path: Path):
    converter = Pdf2DocxConverter()
    input_path = tmp_path / "sample.pdf"
    # Create a minimal but valid PDF file
    input_path.write_bytes(
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/Resources<<>>>>endobj\n"
        b"xref\n"
        b"0 4\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000058 00000 n\n"
        b"0000000115 00000 n\n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n"
        b"190\n"
        b"%%EOF\n"
    )
    output_path = tmp_path / "sample.docx"

    with pytest.raises(DependencyMissingError, match="pdf2docx"):
        converter.convert(input_path, output_path)
