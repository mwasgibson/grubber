from __future__ import annotations

from .detection import detect_format
from pathlib import Path
from typing import Any
from tqdm import tqdm

from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import entry_points
from pathlib import Path
from shutil import which
from sys import version_info
from typing import Any, Callable

from .errors import UnsupportedConversionError
from .types import ConverterProtocol


@dataclass(frozen=True)
class ConverterSpec:
    name: str
    cls: type[ConverterProtocol]
    priority: int


class ConverterRegistry:
    def __init__(self) -> None:
        self._by_name: dict[str, ConverterSpec] = {}
        self._items: list[ConverterSpec] = []
        self._loaded_entry_points = False
        self._entry_point_group = "fileconv.converters"

    def register(self, converter_cls: type[ConverterProtocol]) -> type[ConverterProtocol]:
        name = getattr(converter_cls, "name", converter_cls.__name__.lower())
        priority = int(getattr(converter_cls, "priority", 100))
        spec = ConverterSpec(name=name, cls=converter_cls, priority=priority)
        self._by_name[name] = spec
        self._items = [item for item in self._items if item.name != name]
        self._items.append(spec)
        self._items.sort(key=lambda item: item.priority)
        return converter_cls

    def get(self, name: str) -> type[ConverterProtocol]:
        return self._by_name[name].cls

    def list(self) -> list[type[ConverterProtocol]]:
        return [item.cls for item in self._items]

    def list_specs(self) -> list[ConverterSpec]:
        return list(self._items)

    def find(self, input_mime: str, output_mime: str) -> type[ConverterProtocol] | None:
        self.load_entry_points()
        for item in self._items:
            if item.cls.supports(input_mime, output_mime):
                return item.cls
        return None

    def load_entry_points(self, group: str | None = None) -> None:
        if self._loaded_entry_points:
            return

        group_name = group or self._entry_point_group
        for ep in entry_points(group=group_name):
            converter_cls = ep.load()
            self.register(converter_cls)

        self._loaded_entry_points = True

    def loaded_entry_points(self) -> bool:
        return self._loaded_entry_points


REGISTRY = ConverterRegistry()


def converter(
    *,
    name: str | None = None,
    priority: int = 100,
) -> Callable[[type[ConverterProtocol]], type[ConverterProtocol]]:
    def decorator(converter_cls: type[ConverterProtocol]) -> type[ConverterProtocol]:
        converter_cls.name = name or converter_cls.__name__.lower()
        converter_cls.priority = priority
        return REGISTRY.register(converter_cls)

    return decorator

class ConversionManager:
    def __init__(self, registry: ConverterRegistry | None = None) -> None:
        self.registry = registry or REGISTRY

    def convert(
        self,
        input_path: Path,
        output_format: str,
        *,
        output_path: Path | None = None,
        options: dict[str, Any] | None = None,
    ) -> Path:
        input_mime = self._guess_input_mime(input_path)
        output_mime = self._guess_output_mime(output_format)

        converter_cls = self.registry.find(input_mime, output_mime)
        if converter_cls is None:
            raise UnsupportedConversionError(f"No converter for {input_mime} -> {output_mime}")

        output_path = output_path or input_path.with_suffix(f".{output_format.lstrip('.')}")
        converter = converter_cls()
        return converter.convert(input_path, output_path, options=options or {})

    def dry_run(self, input_path: Path, output_format: str) -> str:
        input_mime = self._guess_input_mime(input_path)
        output_mime = self._guess_output_mime(output_format)

        converter_cls = self.registry.find(input_mime, output_mime)
        if converter_cls is None:
            raise UnsupportedConversionError(f"No converter for {input_mime} -> {output_mime}")
        return converter_cls.name

# Preserve the source folder structure by computing the file's path
# relative to the batch input root, then recreating that subpath under
# the output directory. relative_parent = source.parent.relative_to(root)
    def convert_many(
        self,
        inputs: list[Path],
        output_format: str,
        *,
        output_root: Path,
        recursive: bool = False,
        overwrite: bool = False,
        options: dict[str, Any] | None = None,
        show_progress: bool = True,
        dry_run: bool = False,
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        options = options or {}

        # Build (input_root, source_file) tasks so we know what to be relative to
        tasks: list[tuple[Path, Path]] = []
        for input_item in inputs:
            files = self._expand_input(input_item, recursive=recursive)
            for f in files:
                tasks.append((input_item, f))

        iterator = tqdm(tasks, unit="file", desc="Converting") if show_progress else tasks

        for input_root, source in iterator:
            # Determine the true root to measure relativity from
            root = input_root if input_root.is_dir() else input_root.parent

            try:
                relative_parent = source.parent.relative_to(root)
            except ValueError:
                # If for some reason source is not under root, fall back to flat
                relative_parent = Path(".")

            output_path = (
                output_root
                / relative_parent
                / f"{source.stem}.{output_format.lstrip('.')}"
            )
            plan: dict[str, Any] = {
                "input": str(source),
                "output": str(output_path),
                "status": "planned" if dry_run else "pending",
                "reason": None,
            }

            if dry_run:
                results.append(plan)
                continue

            if output_path.exists() and not overwrite:
                results.append(
                    {
                        "input": str(source),
                        "output": str(output_path),
                        "status": "skipped",
                        "reason": "output exists",
                    }
                )
                continue

            output_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                produced = self.convert(
                    source,
                    output_format,
                    output_path=output_path,
                    options=options,
                )
                results.append(
                    {
                        "input": str(source),
                        "output": str(produced),
                        "status": "ok",
                        "reason": None,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "input": str(source),
                        "output": None,
                        "status": "failed",
                        "reason": str(exc),
                    }
                )

        return results

    def _build_batch_output_path(
        self,
        *,
        source: Path,
        input_root: Path,
        output_root: Path,
        output_format: str,
    ) -> Path:
        relative_parent = source.parent.relative_to(input_root) if source.parent != input_root else Path(".")
        return output_root / relative_parent / f"{source.stem}.{output_format.lstrip('.')}"
    
    def supported_extensions(self) -> set[str]:
        return {
            "doc", "docx", "odt", "xls", "xlsx", "ppt", "pptx",
            "png", "jpg", "jpeg", "webp", "bmp", "gif", "tif", "tiff",
        }

    def is_supported_file(self, path: Path) -> bool:
        if not path.is_file():
            return False
        suffix = path.suffix.lower().lstrip(".")
        return suffix in self.supported_extensions()

    def _expand_input(self, input_item: Path, *, recursive: bool, include_unsupported: bool = False) -> list[Path]:
        if input_item.is_file():
            return [input_item] if include_unsupported or self.is_supported_file(input_item) else []

        if input_item.is_dir():
            iterator = input_item.rglob("*") if recursive else input_item.iterdir()
            files = [p for p in iterator if p.is_file()]
            if include_unsupported:
                return files
            return [p for p in files if self.is_supported_file(p)]

        return []

    def doctor(self) -> dict[str, Any]:
        self.registry.load_entry_points()

        checks: dict[str, Any] = {
            "python": {
                "ok": version_info >= (3, 11),
                "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            },
            "registry": {
                "ok": len(self.registry.list_specs()) > 0,
                "converters": [spec.name for spec in self.registry.list_specs()],
            },
            "entry_points": {
                "ok": self.registry.loaded_entry_points(),
                "group": "fileconv.converters",
            },
            "format_detection": {
                "ok": True,
                "magic_available": self._magic_available(),
                "strategy": "magic-first, extension-fallback",
            },
            "binaries": {
                "libreoffice": {
                    "ok": which("libreoffice") is not None or which("soffice") is not None,
                    "path": which("libreoffice") or which("soffice"),
                },
                "ffmpeg": {
                    "ok": which("ffmpeg") is not None,
                    "path": which("ffmpeg"),
                },
                "magick": {
                    "ok": which("magick") is not None,
                    "path": which("magick"),
                },
            },
        }

        checks["overall_ok"] = (
            checks["python"]["ok"]
            and checks["registry"]["ok"]
            and checks["binaries"]["libreoffice"]["ok"]
        )
        return checks

    def _guess_input_mime(self, input_path: Path) -> str:
        return detect_format(input_path).mime

    def _guess_output_mime(self, output_format: str) -> str:
        suffix = output_format.lower().lstrip(".")
        return _EXT_TO_MIME.get(suffix, f"application/{suffix}")

    @staticmethod
    def _magic_available() -> bool:
        try:
            import_module("magic")
            return True
        except Exception:
            return False


_EXT_TO_MIME = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "pdf": "application/pdf",
    "odt": "application/vnd.oasis.opendocument.text",
    "txt": "text/plain",
    "html": "text/html",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "bmp": "image/bmp",
}
