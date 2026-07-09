package com.polaris.studykit

import kotlin.math.abs
import kotlin.math.min

/**
 * Algorithmic quizzing — no AI.
 * - MCQ generation: distractors drawn from other cards' answers (nearest-length heuristic).
 * - Grading: fuzzy free-text match via normalized Levenshtein edit distance.
 * - Adaptive review: Leitner box system (promote on correct, reset on wrong).
 */
data class QuizQuestion(val prompt: String, val options: List<String>, val answer: String)

object QuizEngine {

    fun multipleChoice(cards: List<Flashcard>, choices: Int = 4): List<QuizQuestion> {
        val answers = cards.map { it.answer }
        return cards.map { card ->
            val distractors = answers
                .filter { it != card.answer }
                .sortedBy { abs(it.length - card.answer.length) }
                .take((choices - 1).coerceAtLeast(0))
            val options = (distractors + card.answer).shuffled()
            QuizQuestion(card.question, options, card.answer)
        }
    }

    /** Accepts near-matches (default 80% similarity — tolerant of typos / singular-plural). */
    fun isCorrect(given: String, answer: String, threshold: Double = 0.80): Boolean =
        similarity(normalize(given), normalize(answer)) >= threshold

    /** 1 - edit distance / max length. 1.0 == identical. */
    fun similarity(a: String, b: String): Double {
        if (a.isEmpty() && b.isEmpty()) return 1.0
        val dist = levenshtein(a, b)
        return 1.0 - dist.toDouble() / maxOf(a.length, b.length)
    }

    /** Leitner: correct promotes (max maxBox), wrong resets to 0. */
    fun leitner(box: Int, correct: Boolean, maxBox: Int = 5): Int =
        if (correct) min(maxBox, box + 1) else 0

    private fun normalize(s: String): String =
        s.lowercase().split(Regex("[^a-z0-9]+")).filter { it.isNotEmpty() }.joinToString(" ")

    private fun levenshtein(a: String, b: String): Int {
        if (a.isEmpty()) return b.length
        if (b.isEmpty()) return a.length
        var prev = IntArray(b.length + 1) { it }
        var cur = IntArray(b.length + 1)
        for (i in 1..a.length) {
            cur[0] = i
            for (j in 1..b.length) {
                val cost = if (a[i - 1] == b[j - 1]) 0 else 1
                cur[j] = minOf(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            }
            val tmp = prev; prev = cur; cur = tmp
        }
        return prev[b.length]
    }
}
