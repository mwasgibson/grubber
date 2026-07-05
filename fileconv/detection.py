from __future__ import annotations

from dataclasses import dataclass
from mimetypes import guess_type
from pathlib import Path
from typing import Literal

DetectionSource = Literal["magic", "extension", "unknown"]


@dataclass(frozen=True)
class FormatDetection:
    path: Path
    mime: str
    extension: str
    source: DetectionSource
    confidence: float


def detect_format(path: Path) -> FormatDetection:
    mime_from_magic = _detect_mime_with_magic(path)
    if mime_from_magic:
        return FormatDetection(
            path=path,
            mime=mime_from_magic,
            extension=_extension_from_mime(mime_from_magic, path.suffix),
            source="magic",
            confidence=0.95,
        )

    mime_from_extension, _ = guess_type(str(path))
    if mime_from_extension:
        return FormatDetection(
            path=path,
            mime=mime_from_extension,
            extension=path.suffix.lower(),
            source="extension",
            confidence=0.70,
        )

    return FormatDetection(
        path=path,
        mime="application/octet-stream",
        extension=path.suffix.lower(),
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
        result = detector.from_file(str(path))  # type: ignore[reportUnknownMemberType]
        return str(result) if result else None
    except Exception:
        return None


def _extension_from_mime(mime: str, fallback_suffix: str) -> str:
    mapping = {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/msword": ".doc",
        "application/pdf": ".pdf",
        "application/vnd.oasis.opendocument.text": ".odt",
        "text/plain": ".txt",
        "text/html": ".html",
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }
    return mapping.get(mime, fallback_suffix.lower())