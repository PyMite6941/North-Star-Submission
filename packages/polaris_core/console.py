"""Shared Rich console that is safe on Windows.

When output is piped/redirected on Windows, Python's stdout defaults to the legacy
locale encoding (cp1252), which can't encode glyphs like ✓/✗ and raises
``UnicodeEncodeError``. We reconfigure stdout/stderr to UTF-8 (best-effort) so the
CLIs behave identically in a terminal and when piped.
"""

from __future__ import annotations

import sys

from rich.console import Console


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - never fail just setting up output
                pass


_force_utf8()

# Single shared console for all CLIs.
console = Console()
