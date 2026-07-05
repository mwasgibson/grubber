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
