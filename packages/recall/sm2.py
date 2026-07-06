"""SM-2 spaced-repetition algorithm (SuperMemo 2).

Pure and dependency-free so it's easy to unit-test. Given a card's current state and a
recall grade 0–5, returns the next state (ease factor, repetition count, interval in days,
and due date).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class SM2State:
    ease: float = 2.5  # ease factor (>= 1.3)
    interval: int = 0  # days until next review
    repetitions: int = 0  # consecutive correct reviews
    due: str = ""  # ISO date the card is next due

    @classmethod
    def new(cls, today: date | None = None) -> SM2State:
        today = today or date.today()
        return cls(due=today.isoformat())


def schedule(state: SM2State, grade: int, today: date | None = None) -> SM2State:
    """Advance an SM-2 state by a review graded 0–5 (>=3 is a pass).

    - grade < 3: lapse — repetitions reset, review again tomorrow.
    - grade >= 3: interval grows (1, 6, then ×ease); ease adjusts per SM-2.
    """
    today = today or date.today()
    grade = max(0, min(5, int(grade)))

    if grade < 3:
        repetitions = 0
        interval = 1
    else:
        repetitions = state.repetitions + 1
        if repetitions == 1:
            interval = 1
        elif repetitions == 2:
            interval = 6
        else:
            interval = round(state.interval * state.ease)

    # SM-2 ease update, floored at 1.3.
    ease = state.ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
    ease = max(1.3, ease)

    return SM2State(
        ease=round(ease, 3),
        interval=interval,
        repetitions=repetitions,
        due=(today + timedelta(days=interval)).isoformat(),
    )
