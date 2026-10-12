"""FileConv – extensible local file converter."""

from .core import ConversionManager, Registry, REGISTRY
from . import converters  # registers built-in converters via @converter
from .version import __version__

__all__ = ["ConversionManager", "Registry", "REGISTRY", "converters", "__version__"]
