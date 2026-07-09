"""Deterministic writing-issue detection rules (no AI).

Each rule scans text with regular expressions / lookup tables and yields typed :class:`Issue`
spans with a message and (where possible) a concrete suggestion — the same approach used by
tools like proselint, write-good, and LanguageTool's simpler rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Issue:
    start: int
    end: int
    type: str          # grammar | style | clarity | spelling | punctuation
    message: str
    suggestion: str | None = None
    matched: str = ""


# --- lookup tables ----------------------------------------------------------
# Wordy phrase -> concise replacement.
WORDINESS = {
    "in order to": "to",
    "due to the fact that": "because",
    "in the event that": "if",
    "at this point in time": "now",
    "a large number of": "many",
    "a majority of": "most",
    "in spite of the fact that": "although",
    "for the purpose of": "to",
    "in the near future": "soon",
    "has the ability to": "can",
    "on a daily basis": "daily",
    "with regard to": "about",
    "in the process of": "",
    "each and every": "every",
    "first and foremost": "first",
}

# Vague intensifiers / hedges that usually weaken prose.
WEASEL = {
    "very", "really", "quite", "rather", "somewhat", "fairly", "actually", "basically",
    "literally", "clearly", "obviously", "simply", "just", "totally", "extremely",
}

# Redundant pairs where one word suffices.
REDUNDANCIES = {
    "absolutely essential": "essential",
    "advance planning": "planning",
    "past history": "history",
    "end result": "result",
    "final outcome": "outcome",
    "close proximity": "proximity",
    "unexpected surprise": "surprise",
    "free gift": "gift",
    "added bonus": "bonus",
}

CLICHES = {
    "at the end of the day", "think outside the box", "low-hanging fruit",
    "in this day and age", "needle in a haystack", "the fact of the matter",
}

# Commonly confused homophones — flagged for a human to verify (context-free).
CONFUSABLES = {
    "its": "it's", "it's": "its",
    "their": "there/they're", "there": "their/they're", "they're": "their/there",
    "your": "you're", "you're": "your",
    "affect": "effect", "effect": "affect",
    "then": "than", "than": "then",
    "loose": "lose", "lose": "loose",
    "complement": "compliment", "compliment": "complement",
}

_BE = r"(?:is|are|was|were|be|been|being|get|gets|got)"
_PASSIVE = re.compile(rf"\b{_BE}\s+(\w+ed|written|done|made|shown|seen|taken|given|known)\b", re.I)
_WORD = re.compile(r"[A-Za-z']+")
_SENTENCE = re.compile(r"[^.!?]+[.!?]?")


def _add(issues, m, type_, message, suggestion=None):
    issues.append(Issue(m.start(), m.end(), type_, message, suggestion, m.group(0)))


def run_all(text: str) -> list[Issue]:
    """Run every rule over ``text`` and return issues sorted by position."""
    issues: list[Issue] = []
    lower = text.lower()

    # Phrase tables (wordiness / redundancy / clichés).
    for table, type_, label in (
        (WORDINESS, "clarity", "Wordy — tighten this"),
        (REDUNDANCIES, "style", "Redundant — one word is enough"),
    ):
        for phrase, repl in table.items():
            for m in re.finditer(rf"\b{re.escape(phrase)}\b", lower):
                issues.append(Issue(m.start(), m.end(), type_, label,
                                    repl or "(delete)", text[m.start():m.end()]))
    for phrase in CLICHES:
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", lower):
            issues.append(Issue(m.start(), m.end(), "style", "Cliché — say it plainly",
                                None, text[m.start():m.end()]))

    # Weasel words / hedges.
    for m in _WORD.finditer(text):
        w = m.group(0).lower()
        if w in WEASEL:
            issues.append(Issue(m.start(), m.end(), "style",
                                f"Weak intensifier “{m.group(0)}” — cut or use a stronger word",
                                "(delete)", m.group(0)))
        elif w in CONFUSABLES:
            issues.append(Issue(m.start(), m.end(), "grammar",
                                f"Commonly confused: check “{m.group(0)}” vs “{CONFUSABLES[w]}”",
                                None, m.group(0)))

    # Passive voice.
    for m in _PASSIVE.finditer(text):
        _add(issues, m, "clarity", "Passive voice — prefer an active subject")

    # Repeated adjacent word ("the the").
    for m in re.finditer(r"\b(\w+)\s+\1\b", text, re.I):
        _add(issues, m, "grammar", f"Repeated word “{m.group(1)}”", m.group(1))

    # Punctuation: double space, space before punctuation.
    for m in re.finditer(r"  +", text):
        _add(issues, m, "punctuation", "Extra space", " ")
    for m in re.finditer(r"\s+([,.;:!?])", text):
        _add(issues, m, "punctuation", "Space before punctuation", m.group(1))

    # Overly long sentences.
    for m in _SENTENCE.finditer(text):
        n = len(_WORD.findall(m.group(0)))
        if n > 30:
            issues.append(Issue(m.start(), m.end(), "clarity",
                                f"Long sentence ({n} words) — consider splitting", None,
                                m.group(0).strip()[:40]))

    issues.sort(key=lambda i: (i.start, i.end))
    return issues
