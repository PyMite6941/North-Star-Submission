"""pomodoro — log focus sessions and compute focus stats (today, streak, totals).

The timer runs in the UI; this backend records completed sessions in the shared vector
store and derives streaks/totals so progress persists across devices.
"""

from pomodoro.service import focus_stats, log_session

__all__ = ["log_session", "focus_stats"]
