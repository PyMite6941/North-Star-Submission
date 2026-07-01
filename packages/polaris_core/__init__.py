"""polaris_core — shared foundation for the North Star (Polaris) components.

Exposes configuration, the 6-areas registry, and factories for the local LLM,
embeddings, and LangGraph persistence so every component depends only on this.
"""

# Import first, at package load, so stdout/stderr are reconfigured to UTF-8 before
# any logging handler or plain print() runs. This makes runner scripts and CLIs behave
# identically on Windows (whose default cp1252 console can't encode paths like ドキュメント).
from polaris_core.config import Settings, get_settings
from polaris_core.console import console
from polaris_core.polaris import POLARIS_AREAS, PolarisArea, area_info

__all__ = [
    "console",
    "Settings",
    "get_settings",
    "PolarisArea",
    "POLARIS_AREAS",
    "area_info",
]

__version__ = "0.1.0"
