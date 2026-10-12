"""Format detection helpers."""

from __future__ import annotations

from dataclasses import dataclass
from mimetypes import guess_type
from pathlib import Path
from typing import Literal

DetectionSource = Literal["magic", "extension", "unknown"]

# Common extension → MIME map used as a reliable fallback.
_EXTENSION_TO_MIME: dict[str, str] = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".html": "text/html",
    ".htm": "text/html",
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".rtf": "application/rtf",
}

_MIME_TO_EXTENSION: dict[str, str] = {v: k for k, v in _EXTENSION_TO_MIME.items()}
# Prefer the most common extension when multiple map to the same MIME.
_MIME_TO_EXTENSION.update(
    {
        "image/jpeg": ".jpg",
        "text/html": ".html",
        "image/tiff": ".tiff",
    }
)


@dataclass(frozen=True)
class FormatDetection:
    path: Path
    mime: str
    extension: str
    source: DetectionSource
    confidence: float


def mime_for(path: Path) -> str:
    """Return the best-effort MIME type for a path."""
    ext = path.suffix.lower()
    if ext in _EXTENSION_TO_MIME:
        return _EXTENSION_TO_MIME[ext]
    guessed, _ = guess_type(str(path))
    return guessed or "application/octet-stream"


def extension_for_mime(mime: str, fallback: str = "") -> str:
    """Return a conventional file extension for a MIME type."""
    return _MIME_TO_EXTENSION.get(mime, fallback.lower() if fallback else "")


def detect_format(path: Path) -> FormatDetection:
    """Detect format using magic (if available) then extension fallback."""
    mime_from_magic = _detect_mime_with_magic(path)
    if mime_from_magic:
        return FormatDetection(
            path=path,
            mime=mime_from_magic,
            extension=extension_for_mime(mime_from_magic, path.suffix),
            source="magic",
            confidence=0.95,
        )

    ext = path.suffix.lower()
    if ext in _EXTENSION_TO_MIME:
        return FormatDetection(
            path=path,
            mime=_EXTENSION_TO_MIME[ext],
            extension=ext,
            source="extension",
            confidence=0.85,
        )

    mime_from_extension, _ = guess_type(str(path))
    if mime_from_extension:
        return FormatDetection(
            path=path,
            mime=mime_from_extension,
            extension=ext or extension_for_mime(mime_from_extension),
            source="extension",
            confidence=0.70,
        )

    return FormatDetection(
        path=path,
        mime="application/octet-stream",
        extension=ext,
        source="unknown",
        confidence=0.10,
    )


def _detect_mime_with_magic(path: Path) -> str | None:
    try:
        import magic
    except Exception:
        return None

    try:
        detector = magic.Magic(mime=True)
        result = detector.from_file(str(path))
        return str(result) if result else None
    except Exception:
        return None
