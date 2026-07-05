from pathlib import Path
import import link
import pytest

def test_pdf2docx_converter_requires_optional_dependency(tmp_path: Path, monkeypatch):
    import fileconv.converters.pdf2docx as mod

    def fake_import(name, *args, **kwargs):
        if name == "pdf2docx":
            raise ImportError("simulated missing dependency")
        return importlib.import_module(name, *args, **kwargs)

    monkeypatch.setattr(mod.importlib, "import_module", fake_import)

    converter = mod.Pdf2DocxConverter()
    ...
    with pytest.raises(mod.DependencyMissingError, match="pdf2docx"):
        converter.convert(input_path, output_path)
