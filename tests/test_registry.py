"""Registry and routing tests."""

from pathlib import Path

import importlib

importlib.import_module("fileconv.converters")
from fileconv.core import REGISTRY, ConversionManager
from fileconv.detection import mime_for


def test_registry_has_builtin_converters():
    names = set(REGISTRY.names())
    assert "pillow" in names
    assert "libreoffice" in names
    assert "pdf2docx" in names


def test_resolve_docx_to_pdf():
    manager = ConversionManager()
    assert manager.dry_run(Path("sample.docx"), "pdf") == "libreoffice"


def test_resolve_pdf_to_docx_prefers_pdf2docx():
    manager = ConversionManager()
    assert manager.dry_run(Path("sample.pdf"), "docx") == "pdf2docx"


def test_resolve_image():
    manager = ConversionManager()
    assert manager.dry_run(Path("photo.png"), "jpg") == "pillow"


def test_mime_for_known_extensions():
    assert mime_for(Path("a.docx")).endswith("wordprocessingml.document")
    assert mime_for(Path("a.pdf")) == "application/pdf"
    assert mime_for(Path("a.png")) == "image/png"


def test_doctor_reports_format_detection():
    manager = ConversionManager()
    doctor = manager.doctor()
    assert "format_detection" in doctor
    assert isinstance(doctor["format_detection"]["magic_available"], bool)
    assert doctor["entry_points"]["group"] == "fileconv.converters"
    assert "converters" in doctor
    assert len(doctor["converters"]) >= 3
    assert doctor["version"] == "1.5.0"
