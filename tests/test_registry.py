from pathlib import Path

from fileconv.core import ConversionManager, REGISTRY


def test_registry_has_builtin_converter():
    names = [cls.name for cls in REGISTRY.list()]
    assert "libreoffice" in names or "pillow" in names


def test_dry_run_for_docx_to_pdf():
    manager = ConversionManager()
    assert manager.dry_run(Path("sample.docx"), "pdf") == "libreoffice"
