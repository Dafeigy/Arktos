"""Custom exception hierarchy for Arktos."""


class ArktosError(Exception):
    """Base exception for all Arktos errors."""


class DetectorError(ArktosError):
    """Raised when a detector fails to execute."""

    def __init__(self, detector_name: str, message: str = ""):
        self.detector_name = detector_name
        super().__init__(f"Detector '{detector_name}' failed: {message}")


class ConfigurationError(ArktosError):
    """Raised when configuration is invalid."""


class TextTooLongError(ArktosError):
    """Raised when input text exceeds the configured maximum length."""


class RuleLoadError(ArktosError):
    """Raised when rule files cannot be loaded or parsed."""
