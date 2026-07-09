"""Orchestrate the rules + readability into a single report with an overall score."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from writing.rules import Issue, run_all

_WORD = re.compile(r"[A-Za-z']+")
_SENTENCE = re.compile(r"[^.!?]+[.!?]")
_VOWELS = set("aeiouy")


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    words: int = 0
    sentences: int = 0
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    score: int = 100                 # 0–100 writing-quality score
    counts: dict[str, int] = field(default_factory=dict)


def _syllables(word: str) -> int:
    w = "".join(c for c in word.lower() if c.isalpha())
    if not w:
        return 0
    count, prev_vowel = 0, False
    for c in w:
        v = c in _VOWELS
        if v and not prev_vowel:
            count += 1
        prev_vowel = v
    if w.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def check(text: str) -> Report:
    """Run the full deterministic writing check on ``text``. No AI."""
    issues = run_all(text)
    words = _WORD.findall(text)
    sentences = _SENTENCE.findall(text) or [text]
    n_words = max(1, len(words))
    n_sent = max(1, len(sentences))
    n_syll = sum(_syllables(w) for w in words)

    wps = n_words / n_sent
    spw = n_syll / n_words
    ease = round(206.835 - 1.015 * wps - 84.6 * spw, 1)
    grade = round(0.39 * wps + 11.8 * spw - 15.59, 1)

    # Score: start at 100, subtract weighted penalties per issue density.
    weights = {"grammar": 4, "clarity": 3, "style": 2, "punctuation": 1, "spelling": 4}
    penalty = sum(weights.get(i.type, 2) for i in issues)
    density_penalty = penalty / (n_words / 100 + 1)   # per ~100 words
    score = max(0, min(100, round(100 - density_penalty)))

    counts: dict[str, int] = {}
    for i in issues:
        counts[i.type] = counts.get(i.type, 0) + 1

    return Report(
        issues=issues, words=n_words, sentences=n_sent,
        flesch_reading_ease=ease, flesch_kincaid_grade=grade, score=score, counts=counts,
    )
