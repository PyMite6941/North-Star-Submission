package com.polaris.studykit

import java.time.LocalDate
import java.time.temporal.ChronoUnit
import kotlin.math.roundToInt

/**
 * PolarisStudy — the on-device study toolkit, powered entirely by **classical algorithms,
 * not AI**. Every feature is deterministic, offline, instant, and unit-tested:
 *
 * | Area        | Algorithm |
 * |-------------|-----------|
 * | Flashcards  | SM-2 spaced repetition + cloze/definition generation |
 * | Quizzing    | MCQ generation + Levenshtein grading + Leitner boxes |
 * | Citation    | Rule-table formatter (APA / MLA / Chicago) |
 * | Essay       | Flesch–Kincaid readability + structural heuristics |
 * | CV Builder  | Template rendering |
 * | Advisor     | Rule-based deadline + spacing study scheduler |
 *
 * No model file, no MediaPipe, no network — nothing to download and it runs on any device.
 * All calls are cheap and synchronous (no [AutoCloseable], no background thread required).
 */
class PolarisStudy {

    // Flashcards (SM-2)
    fun makeFlashcards(text: String, limit: Int = 20): List<Flashcard> =
        FlashcardGenerator.generate(text, limit)

    fun review(state: Sm2State, grade: Int, today: Long = LocalDate.now().toEpochDay()): Sm2State =
        SpacedRepetition.schedule(state, grade, today)

    // Quizzing
    fun makeQuiz(cards: List<Flashcard>, choices: Int = 4): List<QuizQuestion> =
        QuizEngine.multipleChoice(cards, choices)

    fun grade(given: String, answer: String): Boolean = QuizEngine.isCorrect(given, answer)

    // Citation
    fun citation(source: Source, style: CitationStyle): Pair<String, String> =
        Citations.reference(source, style) to Citations.inText(source, style)

    // Essay
    fun analyzeWriting(text: String): ReadabilityReport = Readability.analyze(text)

    // Writing checker (offline). The AI coach "Polly" is ONLINE-ONLY — call its API
    // (/writing/coach, /writing/polish) only when the device has connectivity; this rule-based
    // checker always works, on-device, with no network.
    fun checkWriting(text: String): Pair<List<WritingIssue>, Int> {
        val issues = WritingChecker.check(text)
        return issues to WritingChecker.score(text, issues)
    }

    // CV Builder (template)
    data class Resume(
        val name: String = "",
        val contact: String = "",
        val summary: String = "",
        val experience: List<String> = emptyList(),
        val education: List<String> = emptyList(),
        val skills: List<String> = emptyList(),
    )

    fun buildCV(r: Resume): String {
        val out = mutableListOf("# ${r.name}")
        if (r.contact.isNotEmpty()) out.add(r.contact)
        if (r.summary.isNotEmpty()) out.addAll(listOf("", "## Summary", r.summary))
        fun section(title: String, items: List<String>) {
            if (items.isEmpty()) return
            out.add(""); out.add("## $title"); out.addAll(items.map { "- $it" })
        }
        section("Experience", r.experience)
        section("Education", r.education)
        if (r.skills.isNotEmpty()) out.addAll(listOf("", "## Skills", r.skills.joinToString(" · ")))
        return out.joinToString("\n")
    }

    // Advisor (rule-based scheduler)
    data class Deadline(val title: String, val due: LocalDate, val weightPct: Double = 0.0)
    data class PlanItem(val title: String, val start: LocalDate, val priority: Double)

    /**
     * Prioritize upcoming work by urgency × importance — no AI.
     * priority = weight / max(1, days-until-due); heavier items start sooner (front-loading).
     */
    fun advise(deadlines: List<Deadline>, now: LocalDate = LocalDate.now()): List<PlanItem> =
        deadlines.map { d ->
            val days = ChronoUnit.DAYS.between(now, d.due).coerceAtLeast(1)
            val priority = (if (d.weightPct > 0) d.weightPct else 10.0) / days
            val lead = ((d.weightPct / 20).roundToInt() + 1).toLong().coerceAtMost(days)
            val start = maxOf(now, d.due.minusDays(lead))
            PlanItem(d.title, start, priority)
        }.sortedByDescending { it.priority }
}
