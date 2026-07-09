package com.polaris.studykit

/**
 * The six areas of Polaris — each fulfilled on-device by a classical algorithm (no AI).
 *
 * The desktop/Python build uses an LLM for these; the mobile kits (iOS + Android) deliberately
 * swap in deterministic algorithms so they run instantly, offline, on any device. See [algorithm].
 */
enum class PolarisArea(val key: String, val title: String, val summary: String) {
    FLASHCARDS(
        key = "flashcards",
        title = "Flashcard Creation",
        summary = "Turn study material into clear question/answer flashcards.",
    ),
    QUIZZING(
        key = "quizzing",
        title = "Quizzing",
        summary = "Generate quizzes and grade answers with feedback.",
    ),
    CV_BUILDER(
        key = "cv_builder",
        title = "CV Builder",
        summary = "Draft and refine a CV / résumé.",
    ),
    ADVISOR(
        key = "advisor",
        title = "Advisor",
        summary = "General study and academic advice and planning.",
    ),
    CITATION(
        key = "citation",
        title = "Citation Generator",
        summary = "Produce citations in APA / MLA / Chicago.",
    ),
    ESSAY(
        key = "essay",
        title = "Essay Helper",
        summary = "Outline, draft, and improve essays.",
    ),
    ;

    /** The deterministic algorithm powering this area (no AI). */
    val algorithm: String
        get() = when (this) {
            FLASHCARDS -> "SM-2 spaced repetition + cloze/definition generation"
            QUIZZING -> "MCQ generation + Levenshtein grading + Leitner boxes"
            CV_BUILDER -> "Template rendering"
            ADVISOR -> "Rule-based deadline + spacing scheduler"
            CITATION -> "Rule-table formatter (APA / MLA / Chicago)"
            ESSAY -> "Flesch–Kincaid readability + structural heuristics"
        }

    companion object {
        /** Lookup by routing key (matches the Python/iOS `PolarisArea` string values). */
        fun fromKey(key: String): PolarisArea? = entries.find { it.key == key.lowercase() }
    }
}
