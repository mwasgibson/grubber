"""pdf2docx converter unit tests (no real PDF required for supports checks)."""

from fileconv.converters.pdf2docx import Pdf2DocxConverter


def test_supports_pdf_to_docx():
    assert Pdf2DocxConverter.supports(
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    assert not Pdf2DocxConverter.supports("image/png", "application/pdf")


def test_priority_higher_than_default():
    assert Pdf2DocxConverter.priority >= 10
