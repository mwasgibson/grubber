import importlib
from pathlib import Path

import pytest

from fileconv.converters.pdf2docx import Pdf2DocxConverter
from fileconv.errors import DependencyMissingError


def test_pdf2docx_converter_requires_optional_dependency(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import fileconv.converters.pdf2docx as mod

    def fake_import(name: str, *args: str, **kwargs: str):
        if name == "pdf2docx":
            raise ImportError("simulated missing dependency")
        return importlib.import_module(name, *args, **kwargs)

    monkeypatch.setattr(mod.importlib, "import_module", fake_import)

    converter = Pdf2DocxConverter()
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "output.docx"

    with pytest.raises(DependencyMissingError, match="pdf2docx"):
        converter.convert(input_path, output_path)
