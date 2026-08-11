class XAAError(Exception):
    """Expected application error that can be shown without a traceback."""


class ConfigError(XAAError):
    """Invalid or incomplete configuration."""


class GenerationError(XAAError):
    """Content or image generation failed."""


class PublishingError(XAAError):
    """Publishing to X failed."""
