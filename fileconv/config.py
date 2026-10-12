"""Optional user configuration for FileConv."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import ConfigError


def default_config_path() -> Path:
    return Path.home() / ".config" / "fileconv" / "config.toml"


@dataclass
class FileConvConfig:
    """Runtime configuration loaded from TOML or defaults."""

    default_output_dir: Path = field(
        default_factory=lambda: Path.home() / "Documents" / "FileConv"
    )
    jobs: int = 1
    overwrite: bool = False
    show_progress: bool = True
    recursive: bool = False

    @classmethod
    def load(cls, path: Path | None = None) -> FileConvConfig:
        cfg_path = path or default_config_path()
        if not cfg_path.is_file():
            return cls()

        try:
            with cfg_path.open("rb") as fh:
                data: dict[str, Any] = tomllib.load(fh)
        except Exception as exc:
            raise ConfigError(f"Failed to read config {cfg_path}: {exc}") from exc

        section = data.get("fileconv", data)
        default_out = section.get("default_output_dir")
        return cls(
            default_output_dir=Path(default_out).expanduser()
            if default_out
            else Path.home() / "Documents" / "FileConv",
            jobs=int(section.get("jobs", 1)),
            overwrite=bool(section.get("overwrite", False)),
            show_progress=bool(section.get("show_progress", True)),
            recursive=bool(section.get("recursive", False)),
        )
