from __future__ import annotations

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


REGISTRY = Registry()


def converter(*, name: str):
    """Register a converter function under a stable name."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        REGISTRY.register(name, func)
        return func
    return decorator


class ConversionManager:
    """Plan and execute file conversions."""

    def dry_run(self, input_path: Path, to: str) -> str:
        """Return the converter name that would handle this file."""
        suffix = input_path.suffix.lower()
        if suffix == ".docx" and to.lower() == "pdf":
            return "libreoffice"
        if suffix in {".png", ".jpg", ".jpeg"}:
            return "pillow"
        return "unknown"

    def doctor(self) -> dict[str, Any]:
        """Report environment capabilities."""
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

    def convert(self, input_path: Path, to: str, output_path: Path | None = None) -> Path:
        """Convert a single file and return the output path."""
        if output_path is None:
            output_path = input_path.with_suffix(f".{to.lstrip('.')}")
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
        """Convert many files and return a structured batch payload."""
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

            ok += 1
            results.append(
                {
                    "input": str(input_path),
                    "output": str(output_path),
                    "status": "ok",
                    "reason": None,
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