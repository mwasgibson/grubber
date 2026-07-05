from pathlib import Path

import importlib

importlib.import_module("fileconv.converters.image")
from fileconv.core import REGISTRY, ConversionManager


def test_registry_has_builtin_converter():
    names = [spec.name for spec in REGISTRY.list()]
    assert "pillow" in names


def test_dry_run_for_docx_to_pdf():
    manager = ConversionManager()
    assert manager.dry_run(Path("sample.docx"), "pdf") == "libreoffice"


def test_doctor_reports_format_detection():
    manager = ConversionManager()
    doctor = manager.doctor()

    assert "format_detection" in doctor
    assert isinstance(doctor["format_detection"]["magic_available"], bool)
    assert doctor["entry_points"]["group"] == "fileconv.converters"