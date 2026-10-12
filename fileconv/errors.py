"""Domain errors for FileConv."""


class FileConvError(Exception):
    """Base error for the converter app."""


class UnsupportedConversionError(FileConvError):
    """Raised when no converter can handle the requested conversion."""


class DependencyMissingError(FileConvError):
    """Raised when an external binary or library is not available."""


class ConfigError(FileConvError):
    """Raised when configuration is invalid or missing."""
