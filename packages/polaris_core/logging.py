"""Rich-backed logging configured from settings."""

from __future__ import annotations

import logging

from rich.logging import RichHandler

from polaris_core.config import get_settings

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Return a logger, configuring the root handler once at the settings log level."""
    global _CONFIGURED
    if not _CONFIGURED:
        level = get_settings().log_level.upper()
        logging.basicConfig(
            level=level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, show_path=False)],
        )
        _CONFIGURED = True
    return logging.getLogger(name)
