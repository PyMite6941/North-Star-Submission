"""writing — Polaris Student's writing assistant (all free, no paywall).

- **check()** — a fast, deterministic, offline rule engine (grammar / style / clarity issues +
  readability). No AI. This is what also ships on the mobile kits.
- **Polly** (``coach`` / ``polish``) — the online AI writing coach: pinpoints where the text
  needs to be **fixed** *and* where content should be **added**, each with a reason, and can
  rewrite the whole piece. Free, powered by the local/free model.
"""

from writing.check import Report, check
from writing.polly import CoachNote, CoachReport, coach, polish
from writing.rules import Issue

__all__ = ["check", "Report", "Issue", "coach", "polish", "CoachNote", "CoachReport"]
