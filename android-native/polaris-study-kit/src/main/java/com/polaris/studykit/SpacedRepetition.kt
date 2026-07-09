package com.polaris.studykit

import kotlin.math.max
import kotlin.math.roundToInt

/**
 * SM-2 (SuperMemo 2) spaced-repetition scheduling — the algorithm behind flashcards.
 *
 * No AI: given a card's current state and a recall grade 0–5, it deterministically computes
 * the next review interval, ease factor, and due day. Mirrors `packages/recall/sm2.py`.
 *
 * Dates are epoch-day integers (days since 1970) to keep it dependency-free and trivially
 * testable; convert to/from [java.time.LocalDate.toEpochDay] at the UI edge.
 */
data class Sm2State(
    val ease: Double = 2.5,
    val interval: Int = 0,
    val repetitions: Int = 0,
    val dueDay: Long = 0L,
) {
    fun isDue(today: Long): Boolean = dueDay <= today

    companion object {
        fun new(today: Long): Sm2State = Sm2State(dueDay = today)
    }
}

object SpacedRepetition {

    /**
     * Advance an SM-2 state by a review graded 0–5 (>= 3 is a pass).
     * - grade < 3: lapse — repetitions reset, review again tomorrow.
     * - grade >= 3: interval grows (1, 6, then × ease); ease adjusts per SM-2.
     */
    fun schedule(state: Sm2State, grade: Int, today: Long): Sm2State {
        val g = grade.coerceIn(0, 5)

        val repetitions: Int
        val interval: Int
        if (g < 3) {
            repetitions = 0
            interval = 1
        } else {
            repetitions = state.repetitions + 1
            interval = when (repetitions) {
                1 -> 1
                2 -> 6
                else -> (state.interval * state.ease).roundToInt()
            }
        }

        // SM-2 ease update, floored at 1.3.
        val delta = 0.1 - (5 - g) * (0.08 + (5 - g) * 0.02)
        val ease = max(1.3, state.ease + delta)

        return Sm2State(
            ease = (ease * 1000).roundToInt() / 1000.0,
            interval = interval,
            repetitions = repetitions,
            dueDay = today + interval,
        )
    }

    /** Cards due today or earlier, soonest-due first. */
    fun <T> due(cards: List<T>, today: Long, state: (T) -> Sm2State): List<T> =
        cards.filter { state(it).dueDay <= today }.sortedBy { state(it).dueDay }
}
