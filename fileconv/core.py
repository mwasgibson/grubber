from __future__ import annotations

import mimetypes
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class ConverterSpec:
    """Describe one registered converter."""

    name: str
    handler: Callable[..., Any]


class Registry:
    """Registry of available converters."""

    def __init__(self) -> None:
        self._items: dict[str, ConverterSpec] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> ConverterSpec:
        spec = ConverterSpec(name=name, handler=handler)
        self._items[name] = spec
        return spec

    def list(self) -> list[ConverterSpec]:
        return list(self._items.values())

    def get(self, name: str) -> ConverterSpec:
        return self._items[name]

    def resolve(self, input_mime: str, output_mime: str) -> ConverterSpec | None:
        if (
            input_mime
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            and output_mime == "application/pdf"
        ):
            return self._items.get("libreoffice")
        if input_mime.startswith("image/") and output_mime.startswith("image/"):
            return self._items.get("pillow")
        return None


REGISTRY = Registry()


def converter(*, name: str):
    """Register a converter class or function under a stable name."""
    def decorator(obj: Callable[..., Any]) -> Callable[..., Any]:
        REGISTRY.register(name, obj)
        return obj
    return decorator

_EXTENSION_TO_MIME={

".png":"image/png",
".jpg":"image/jpeg",
".jpeg":"image/jpeg",
".gif":"image/gif",
".bmp":"image/bmp",
".webp":"image/webp",
".tiff":"image/tiff",

".pdf":"application/pdf",

".doc":"application/msword",

".docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",

".odt":"application/vnd.oasis.opendocument.text",

".txt":"text/plain",

".html":"text/html",

".htm":"text/html",

}


def mime_for(path:Path)->str:

    ext=path.suffix.lower()

    if ext in _EXTENSION_TO_MIME:
        return _EXTENSION_TO_MIME[ext]

    guessed,_=mimetypes.guess_type(path)

    return guessed or "application/octet-stream"

class ConversionManager:
    """Plan and execute file conversions."""
    
    def __init__(self)->None:
        self.registry = REGISTRY
        self.default_output_dir = Path.home()/"Documents"/"FileConv"
    
    def _pick_converter(self, input_path: Path, to: str) -> str:
        suffix = input_path.suffix.lower()
        target = to.lower().lstrip(".")
        if suffix == ".docx" and target == "pdf":
            return "libreoffice"
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}:
            return "pillow"
        return "unknown"

    def dry_run(self, input_path: Path, to: str) -> str:
        return self._pick_converter(input_path, to)

    def doctor(self) -> dict[str, Any]:
        try:
            import magic  # type: ignore
            magic_available = True
        except Exception:
            magic_available = False

        return {
            "format_detection": {
                "magic_available": magic_available,
            },
            "entry_points": {
                "group": "fileconv.converters",
            },
        }
    
    def _build_output_path(
        self,
        input_path: Path,
        output_path: Path | None,
        to: str,
    ) -> Path:
        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            return output_path

        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        return self.default_output_dir / f"{input_path.stem}.{to.lstrip('.')}"

    def _find_converter(
        self,
        input_path: Path,
        output_path: Path,
    ) -> ConverterSpec:
        input_mime = mime_for(input_path)
        output_mime = mime_for(output_path)

        converter = self.registry.resolve(
            input_mime,
            output_mime,
        )
        if converter is None:
            raise RuntimeError(
                f"No converter found for {input_mime} -> {output_mime}"
            )
        return converter

    def convert(
        self,
        input_path: Path,
        to: str,
        output_path: Path | None = None,
    ) -> Path:
        output_path = self._build_output_path(
            input_path,
            output_path,
            to,
        )

        converter = self._find_converter(
            input_path,
            output_path,
        )

        handler: Any = converter.handler
        if isinstance(handler, type):
            handler = handler()

        if hasattr(handler, "convert"):
            handler.convert(input_path, output_path)
        else:
            handler(input_path, output_path)

        return output_path

    def convert_many(
        self,
        input_paths: list[Path],
        to: str,
        *,
        output_root: Path,
        recursive: bool = False,
        overwrite: bool = False,
        show_progress: bool = False,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        results: list[dict[str, Any]] = []
        planned = ok = skipped = failed = 0

        for input_path in input_paths:
            output_path = output_root / f"{input_path.stem}.{to.lstrip('.')}"
            if dry_run:
                planned += 1
                results.append(
                    {
                        "input": str(input_path),
                        "output": str(output_path),
                        "status": "planned",
                        "reason": None,
                    }
                )
                continue

            try:
                final_output = self.convert(input_path, to, output_path=output_path)
                ok += 1
                results.append(
                    {
                        "input": str(input_path),
                        "output": str(final_output),
                        "status": "ok",
                        "reason": None,
                    }
                )
            except Exception as exc:
                failed += 1
                results.append(
                    {
                        "input": str(input_path),
                        "output": str(output_path),
                        "status": "failed",
                        "reason": str(exc),
                    }
                )

        elapsed = time.perf_counter() - started
        return {
            "elapsed_seconds": round(elapsed, 4),
            "counts": {
                "planned": planned,
                "ok": ok,
                "skipped": skipped,
                "failed": failed,
                "total": len(results),
            },
            "results": results,
        }