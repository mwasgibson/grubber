from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConversionResult:
    input: str
    output: str
    status: str
    reason: str | None = None


class ConversionManager:
    """Plan and execute file conversions."""

    def convert(self, input_path: Path, to: str, output_path: Path | None = None) -> Path:
        """Convert a single file and return the output path."""
        if output_path is None:
            output_path = input_path.with_suffix(f".{to.lstrip('.')}")
        # Real conversion work would go here; for now we just return the planned path.
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
            # For now, keep path logic simple; you can expand this to preserve subfolders later.
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

            # Real conversion work would go here; for now, pretend conversion succeeded.
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