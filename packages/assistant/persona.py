"""Load Polly's persona system prompt from ``docs/polly-persona-prompt.md``.

Keeping the persona in a markdown file (not code) lets it be tweaked without a code change —
the same file the `scripts/polly_persona_chat.py` test harness uses. The app's conversational
Polly (the ``assistant`` interpreter) reads it here so both stay in sync.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from polaris_core.logging import get_logger

logger = get_logger(__name__)

_PERSONA_FILE = Path(__file__).resolve().parents[2] / "docs" / "polly-persona-prompt.md"

# Fallback identity if the md file is ever missing, so the assistant never breaks.
_FALLBACK = (
    "You are Polly, a warm, encouraging academic advisor for a student. Be friendly, concrete, "
    "and honest; point students to the right Polaris feature by name when relevant."
)


@lru_cache(maxsize=1)
def load_polly_persona(path: Path | None = None) -> str:
    """Return Polly's system prompt from the persona markdown's ```text``` block."""
    p = path or _PERSONA_FILE
    try:
        match = re.search(r"```text\n(.*?)\n```", p.read_text(encoding="utf-8"), re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
        logger.warning("No ```text``` block in %s; using fallback persona", p)
    except OSError as exc:
        logger.warning("Could not read persona file %s (%s); using fallback", p, exc)
    return _FALLBACK
