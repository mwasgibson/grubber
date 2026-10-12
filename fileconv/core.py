"""Core registry, conversion manager, and plugin loading."""

from __future__ import annotations

import fnmatch
import importlib.metadata
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from .config import FileConvConfig
from .detection import detect_format, mime_for
from .errors import FileConvError, UnsupportedConversionError

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None  # type: ignore[assignment, misc]


@dataclass(frozen=True)
class ConverterSpec:
    """Describe one registered converter."""

    name: str
    handler: Any
    priority: int = 0


class Registry:
    """Registry of available converters."""

    def __init__(self) -> None:
        self._items: dict[str, ConverterSpec] = {}
        self._entry_points_loaded = False

    def register(self, name: str, handler: Any, priority: int = 0) -> ConverterSpec:
        spec = ConverterSpec(name=name, handler=handler, priority=priority)
        self._items[name] = spec
        return spec

    def list(self) -> list[ConverterSpec]:
        return sorted(self._items.values(), key=lambda s: (-s.priority, s.name))

    def get(self, name: str) -> ConverterSpec:
        if name not in self._items:
            raise KeyError(f"Unknown converter: {name}")
        return self._items[name]

    def names(self) -> list[str]:
        return [s.name for s in self.list()]

    def resolve(self, input_mime: str, output_mime: str) -> ConverterSpec | None:
        """Pick the highest-priority converter that supports the MIME pair."""
        candidates: list[ConverterSpec] = []
        for spec in self._items.values():
            handler = spec.handler
            cls = handler if isinstance(handler, type) else type(handler)
            supports = getattr(cls, "supports", None)
            if callable(supports) and supports(input_mime, output_mime):
                candidates.append(spec)
                continue
            if hasattr(handler, "can_handle"):
                pass
        if not candidates:
            return None
        candidates.sort(key=lambda s: (-s.priority, s.name))
        return candidates[0]

    def recommend(self, input_mime: str) -> list[tuple[str, str]]:
        """Return list of (converter_name, output_mime) pairs for an input MIME."""
        results: list[tuple[str, str]] = []
        for spec in self.list():
            handler = spec.handler
            cls = handler if isinstance(handler, type) else type(handler)
            outputs = getattr(cls, "supported_outputs", None)
            supports = getattr(cls, "supports", None)
            if not callable(outputs) or not callable(supports):
                continue
            for out in outputs():
                out_mime = out if "/" in out else _guess_mime_from_token(out)
                if supports(input_mime, out_mime):
                    results.append((spec.name, out_mime))
        return results

    def load_entry_points(self, group: str = "fileconv.converters") -> int:
        """Load third-party converters declared via entry points. Returns count loaded."""
        if self._entry_points_loaded:
            return 0
        loaded = 0
        try:
            eps = importlib.metadata.entry_points()
            selected = eps.select(group=group) if hasattr(eps, "select") else eps.get(group, [])
        except Exception:
            self._entry_points_loaded = True
            return 0

        for ep in selected:
            if ep.name in self._items:
                continue
            try:
                obj = ep.load()
                priority = getattr(obj, "priority", 0)
                self.register(ep.name, obj, priority=priority)
                loaded += 1
            except Exception:
                continue
        self._entry_points_loaded = True
        return loaded


def _guess_mime_from_token(token: str) -> str:
    token = token.lower().lstrip(".")
    mapping = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc": "application/msword",
        "odt": "application/vnd.oasis.opendocument.text",
        "txt": "text/plain",
        "html": "text/html",
        "htm": "text/html",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "gif": "image/gif",
        "tif": "image/tiff",
        "tiff": "image/tiff",
    }
    return mapping.get(token, f"application/{token}")


REGISTRY = Registry()


def converter(*, name: str, priority: int = 0):
    """Register a converter class or function under a stable name."""

    def decorator(obj: Any) -> Any:
        if not hasattr(obj, "priority"):
            try:
                obj.priority = priority
            except Exception:
                pass
        REGISTRY.register(name, obj, priority=priority)
        return obj

    return decorator


def collect_files(
    root: Path,
    *,
    recursive: bool = False,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Path]:
    """Collect files under root, optionally recursive, with include/exclude globs."""
    if root.is_file():
        files = [root]
    elif root.is_dir():
        if recursive:
            files = [p for p in root.rglob("*") if p.is_file()]
        else:
            files = [p for p in root.iterdir() if p.is_file()]
    else:
        return []

    include = include or []
    exclude = exclude or []

    def matches(path: Path, patterns: list[str]) -> bool:
        name = path.name
        rel = str(path)
        return any(fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel, pat) for pat in patterns)

    result: list[Path] = []
    for path in files:
        if include and not matches(path, include):
            continue
        if exclude and matches(path, exclude):
            continue
        result.append(path)
    return sorted(result)


def relative_output_path(input_path: Path, input_root: Path, output_root: Path, to: str) -> Path:
    """Build an output path that mirrors the input tree under output_root."""
    try:
        rel = input_path.relative_to(input_root if input_root.is_dir() else input_path.parent)
    except ValueError:
        rel = Path(input_path.name)
    stem = rel.with_suffix("")
    return output_root / f"{stem}.{to.lstrip('.')}"


def is_under(path: Path, root: Path) -> bool:
    """Return True if path is root or a descendant of root (after resolve)."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (ValueError, OSError):
        return False


def normalize_ext(token: str) -> str:
    """Normalize an extension token (with or without dot) to lowercase '.ext'."""
    t = token.lower().lstrip(".")
    if t == "jpeg":
        t = "jpg"
    return f".{t}" if t else ""


def extensions_equivalent(a: str, b: str) -> bool:
    return normalize_ext(a) == normalize_ext(b)


def disambiguate_outputs(
    work: list[tuple[Path, Path]], to: str
) -> list[tuple[Path, Path]]:
    """Ensure each input maps to a unique output path.

    When multiple sources would write the same destination (e.g. photo.png and
    photo.webp both targeting jpg -> photo.jpg), rewrite colliding destinations
    to include the source extension: photo.png.jpg, photo.webp.jpg.
    """
    from collections import defaultdict

    by_out: dict[Path, list[Path]] = defaultdict(list)
    for src, out in work:
        by_out[out].append(src)

    if all(len(srcs) == 1 for srcs in by_out.values()):
        return work

    to_ext = to.lstrip(".")
    rewritten: dict[Path, Path] = {}
    for out, srcs in by_out.items():
        if len(srcs) == 1:
            continue
        for src in srcs:
            src_ext = src.suffix.lstrip(".") or "bin"
            new_name = f"{src.stem}.{src_ext}.{to_ext}"
            rewritten[src] = out.parent / new_name

    return [(src, rewritten.get(src, out)) for src, out in work]


class ConversionManager:
    """Plan and execute file conversions."""

    def __init__(self, config: FileConvConfig | None = None) -> None:
        self.registry = REGISTRY
        self.config = config or FileConvConfig.load()
        import fileconv.converters  # noqa: F401
        self.registry.load_entry_points()

    def _build_output_path(
        self,
        input_path: Path,
        to: str,
        *,
        output_path: Path | None = None,
        output_root: Path | None = None,
        input_root: Path | None = None,
    ) -> Path:
        """Compute the destination path without creating directories."""
        if output_path is not None:
            return output_path
        if output_root is not None:
            root = input_root or input_path.parent
            return relative_output_path(input_path, root, output_root, to)
        default_dir = self.config.default_output_dir
        return default_dir / f"{input_path.stem}.{to.lstrip('.')}"

    def _find_converter(self, input_path: Path, output_path: Path) -> ConverterSpec:
        input_mime = mime_for(input_path)
        output_mime = mime_for(output_path)
        converter = self.registry.resolve(input_mime, output_mime)
        if converter is None:
            raise UnsupportedConversionError(
                f"No converter found for {input_mime} -> {output_mime}"
            )
        return converter

    def dry_run(self, input_path: Path, to: str) -> str:
        input_mime = mime_for(input_path)
        dummy = Path(f"dummy.{to.lstrip('.')}")
        output_mime = mime_for(dummy)
        spec = self.registry.resolve(input_mime, output_mime)
        return spec.name if spec else "unknown"

    def doctor(self) -> dict[str, Any]:
        """Rich environment diagnostics."""
        import importlib
        import shutil

        def pkg_version(name: str) -> str | None:
            try:
                return importlib.metadata.version(name)
            except Exception:
                return None

        def binary(name: str) -> str | None:
            return shutil.which(name)

        magic_available = False
        try:
            import magic  # noqa: F401
            magic_available = True
        except Exception:
            pass

        converters = []
        for spec in self.registry.list():
            handler = spec.handler
            cls = handler if isinstance(handler, type) else type(handler)
            converters.append(
                {
                    "name": spec.name,
                    "priority": spec.priority,
                    "inputs": sorted(getattr(cls, "supported_inputs", lambda: set)()),
                    "outputs": sorted(getattr(cls, "supported_outputs", lambda: set)()),
                }
            )

        return {
            "version": __import__("fileconv.version", fromlist=["__version__"]).__version__,
            "format_detection": {"magic_available": magic_available},
            "binaries": {
                "libreoffice": binary("libreoffice"),
                "soffice": binary("soffice"),
            },
            "packages": {
                "Pillow": pkg_version("Pillow"),
                "pdf2docx": pkg_version("pdf2docx"),
                "python-magic": pkg_version("python-magic"),
                "typer": pkg_version("typer"),
                "tqdm": pkg_version("tqdm"),
            },
            "converters": converters,
            "entry_points": {"group": "fileconv.converters"},
            "config": {
                "default_output_dir": str(self.config.default_output_dir),
                "jobs": self.config.jobs,
                "overwrite": self.config.overwrite,
            },
        }

    def convert(
        self,
        input_path: Path,
        to: str,
        output_path: Path | None = None,
        *,
        overwrite: bool | None = None,
        options: dict[str, Any] | None = None,
    ) -> Path:
        overwrite = self.config.overwrite if overwrite is None else overwrite

        # Explicit --output must match the requested --to format.
        if output_path is not None and output_path.suffix:
            if not extensions_equivalent(output_path.suffix, to):
                raise FileConvError(
                    f"Output extension {output_path.suffix!r} does not match "
                    f"requested target format {to!r}. Use a matching suffix "
                    f"(e.g. --output result.{to.lstrip('.')}) or omit --output."
                )

        output_path = self._build_output_path(input_path, to, output_path=output_path)

        if output_path.exists() and not overwrite:
            raise FileConvError(
                f"Output already exists (use --overwrite): {output_path}"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        converter = self._find_converter(input_path, output_path)
        handler: Any = converter.handler
        if isinstance(handler, type):
            handler = handler()

        if hasattr(handler, "convert"):
            result = handler.convert(input_path, output_path, options=options)
        else:
            result = handler(input_path, output_path)

        final_path = result if isinstance(result, Path) else output_path
        if not final_path.exists():
            raise FileConvError(
                f"Converter {converter.name} did not write output file: {final_path}"
            )
        return final_path

    def _convert_one(
        self,
        input_path: Path,
        to: str,
        output_path: Path,
        *,
        overwrite: bool,
        dry_run: bool,
    ) -> dict[str, Any]:
        if dry_run:
            return {
                "input": str(input_path),
                "output": str(output_path),
                "status": "planned",
                "reason": None,
                "converter": self.dry_run(input_path, to),
            }

        if output_path.exists() and not overwrite:
            return {
                "input": str(input_path),
                "output": str(output_path),
                "status": "skipped",
                "reason": "exists",
                "converter": None,
            }

        try:
            final = self.convert(input_path, to, output_path=output_path, overwrite=overwrite)
            return {
                "input": str(input_path),
                "output": str(final),
                "status": "ok",
                "reason": None,
                "converter": self.dry_run(input_path, to),
            }
        except Exception as exc:
            return {
                "input": str(input_path),
                "output": str(output_path),
                "status": "failed",
                "reason": str(exc),
                "converter": None,
            }

    def convert_many(
        self,
        input_paths: list[Path] | Path,
        to: str,
        *,
        output_root: Path,
        recursive: bool | None = None,
        overwrite: bool | None = None,
        show_progress: bool | None = None,
        dry_run: bool = False,
        jobs: int | None = None,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        recursive = self.config.recursive if recursive is None else recursive
        overwrite = self.config.overwrite if overwrite is None else overwrite
        show_progress = self.config.show_progress if show_progress is None else show_progress
        jobs = jobs if jobs is not None else max(1, self.config.jobs)

        roots: list[Path] = []
        files: list[Path] = []
        if isinstance(input_paths, Path):
            input_paths = [input_paths]

        for src in input_paths:
            roots.append(src)
            files.extend(
                collect_files(src, recursive=recursive, include=include, exclude=exclude)
            )

        seen: set[Path] = set()
        unique_files: list[Path] = []
        for f in files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        files = unique_files

        output_root = output_root.resolve()
        if not dry_run:
            output_root.mkdir(parents=True, exist_ok=True)

        # Skip files already under the output tree so resumed recursive batches
        # do not re-ingest prior outputs (nested converted/converted/...).
        files = [f for f in files if not is_under(f, output_root)]

        work: list[tuple[Path, Path]] = []
        for f in files:
            input_root = f.parent
            for r in roots:
                try:
                    f.relative_to(r if r.is_dir() else r.parent)
                    input_root = r if r.is_dir() else r.parent
                    break
                except ValueError:
                    continue
            out = relative_output_path(f, input_root, output_root, to)
            work.append((f, out))

        work = disambiguate_outputs(work, to)

        results: list[dict[str, Any]] = []
        planned = ok = skipped = failed = 0

        def run_item(item: tuple[Path, Path]) -> dict[str, Any]:
            return self._convert_one(
                item[0], to, item[1], overwrite=overwrite, dry_run=dry_run
            )

        iterator: Iterable[dict[str, Any]]
        if jobs <= 1 or dry_run or len(work) <= 1:
            raw = (run_item(w) for w in work)
            if show_progress and tqdm is not None and not dry_run:
                raw = tqdm(raw, total=len(work), desc="Converting", unit="file")
            iterator = raw
            for item in iterator:
                results.append(item)
        else:
            with ThreadPoolExecutor(max_workers=jobs) as pool:
                futures = {pool.submit(run_item, w): w for w in work}
                completed = as_completed(futures)
                if show_progress and tqdm is not None:
                    completed = tqdm(
                        completed, total=len(futures), desc="Converting", unit="file"
                    )
                for fut in completed:
                    results.append(fut.result())

        for item in results:
            status = item["status"]
            if status == "planned":
                planned += 1
            elif status == "ok":
                ok += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed += 1

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
