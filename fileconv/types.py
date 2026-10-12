"""Shared types and protocols for FileConv."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ConverterProtocol(Protocol):
    """Contract every converter must satisfy."""

    name: str
    priority: int

    @classmethod
    def supports(cls, input_mime: str, output_mime: str) -> bool: ...

    @classmethod
    def supported_inputs(cls) -> set[str]: ...

    @classmethod
    def supported_outputs(cls) -> set[str]: ...

    def convert(
        self,
        input_path: Path,
        output_path: Path,
        *,
        options: dict[str, Any] | None = None,
    ) -> Path: ...
