package com.polaris.studykit

import kotlin.math.roundToInt

/**
 * Offline, deterministic writing checker (grammar / style / clarity) — no AI.
 *
 * The on-device, works-offline tier of the writing assistant, mirroring
 * `packages/writing/rules.py`. The AI coach ("Polly") is an **online-only** feature — call its
 * API only when the device has connectivity (see [PolarisStudy] docs); this checker always works.
 */
data class WritingIssue(
    val start: Int,
    val end: Int,
    val type: String,          // grammar | style | clarity | punctuation
    val message: String,
    val suggestion: String? = null,
    val matched: String = "",
)

object WritingChecker {

    private val wordiness = mapOf(
        "in order to" to "to", "due to the fact that" to "because", "in the event that" to "if",
        "at this point in time" to "now", "a large number of" to "many", "a majority of" to "most",
        "for the purpose of" to "to", "has the ability to" to "can", "with regard to" to "about",
        "each and every" to "every", "in spite of the fact that" to "although",
    )
    private val weasel = setOf(
        "very", "really", "quite", "rather", "somewhat", "fairly", "actually", "basically",
        "clearly", "obviously", "simply", "just", "totally", "extremely",
    )
    private val confusables = mapOf(
        "its" to "it's", "it's" to "its", "their" to "there/they're", "there" to "their/they're",
        "your" to "you're", "you're" to "your", "affect" to "effect", "effect" to "affect",
        "then" to "than", "than" to "then", "loose" to "lose",
    )
    private val passive = Regex("\\b(is|are|was|were|be|been|being|get|got)\\s+\\w+ed\\b", RegexOption.IGNORE_CASE)
    private val wordRe = Regex("[A-Za-z']+")

    /** Analyze [text] and return located issues, sorted by position. */
    fun check(text: String): List<WritingIssue> {
        val issues = mutableListOf<WritingIssue>()
        val lower = text.lowercase()

        for ((phrase, repl) in wordiness) {
            var i = lower.indexOf(phrase)
            while (i >= 0) {
                issues.add(WritingIssue(i, i + phrase.length, "clarity", "Wordy — tighten this",
                    repl, text.substring(i, i + phrase.length)))
                i = lower.indexOf(phrase, i + phrase.length)
            }
        }

        val tokens = wordRe.findAll(text).toList()
        tokens.forEachIndexed { idx, m ->
            val w = m.value.lowercase()
            if (w in weasel) {
                issues.add(WritingIssue(m.range.first, m.range.last + 1, "style",
                    "Weak intensifier “${m.value}” — cut or strengthen", "(delete)", m.value))
            } else if (w in confusables) {
                issues.add(WritingIssue(m.range.first, m.range.last + 1, "grammar",
                    "Commonly confused: check “${m.value}” vs “${confusables[w]}”", null, m.value))
            }
            if (idx > 0 && tokens[idx - 1].value.lowercase() == w) {
                val s = tokens[idx - 1].range.first
                val e = m.range.last + 1
                issues.add(WritingIssue(s, e, "grammar", "Repeated word “${m.value}”",
                    m.value, text.substring(s, e)))
            }
        }

        for (m in passive.findAll(text)) {
            issues.add(WritingIssue(m.range.first, m.range.last + 1, "clarity",
                "Passive voice — prefer an active subject", null, m.value))
        }
        for (m in Regex("  +").findAll(text)) {
            issues.add(WritingIssue(m.range.first, m.range.last + 1, "punctuation", "Extra space", " ", m.value))
        }
        for (s in sentences(text)) {
            val n = wordRe.findAll(s.substring).count()
            if (n > 30) {
                issues.add(WritingIssue(s.start, s.end, "clarity",
                    "Long sentence ($n words) — consider splitting", null,
                    s.substring.trim().let { if (it.length <= 40) it else it.take(40) + "…" }))
            }
        }

        return issues.sortedBy { it.start }
    }

    /** A 0–100 quality score from the issue mix (matches the Python scoring). */
    fun score(text: String, issues: List<WritingIssue>): Int {
        val words = wordRe.findAll(text).count().coerceAtLeast(1)
        val weights = mapOf("grammar" to 4, "clarity" to 3, "style" to 2, "punctuation" to 1)
        val penalty = issues.sumOf { (weights[it.type] ?: 2).toDouble() }
        val density = penalty / (words / 100.0 + 1)
        return (100 - density).roundToInt().coerceIn(0, 100)
    }

    private data class Span(val start: Int, val end: Int, val substring: String)

    private fun sentences(text: String): List<Span> {
        val out = mutableListOf<Span>()
        var start = 0
        for (i in text.indices) {
            if (text[i] in ".!?") {
                out.add(Span(start, i + 1, text.substring(start, i + 1))); start = i + 1
            }
        }
        if (start < text.length) out.add(Span(start, text.length, text.substring(start)))
        return out
    }
}
