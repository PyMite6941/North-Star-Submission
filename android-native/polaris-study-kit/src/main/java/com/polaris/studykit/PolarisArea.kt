package com.polaris.studykit

/**
 * The six areas of Polaris fulfilled by the on-device study LLM.
 *
 * Mirrors `packages/polaris_core/polaris.py` and `ios-native`'s `PolarisArea.swift` so all
 * three builds (Python/desktop, iOS, Android) behave identically — same areas, same
 * specialized system prompts.
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

    /** The specialized system prompt for this area (kept in sync with the Python build). */
    val systemPrompt: String
        get() = when (this) {
            FLASHCARDS ->
                "You are a flashcard-creation expert. Convert the user's material into " +
                    "concise, atomic Q/A flashcards (one fact per card). Prefer active " +
                    "recall. Return a numbered list of 'Q:' / 'A:' pairs. Keep answers " +
                    "short and precise."
            QUIZZING ->
                "You are a quiz master. Create well-formed quiz questions (mix of multiple " +
                    "choice and short answer) at an appropriate difficulty. Always provide " +
                    "an answer key with brief explanations. If the user supplies answers, " +
                    "grade them and give targeted, encouraging feedback."
            CV_BUILDER ->
                "You are a professional CV/résumé writer. Produce strong, ATS-friendly " +
                    "content with action verbs and quantified impact. Ask for missing " +
                    "essentials only when necessary; otherwise draft with sensible " +
                    "placeholders the user can fill in. Use clear sections: Summary, " +
                    "Experience, Education, Skills, Projects."
            ADVISOR ->
                "You are a thoughtful academic advisor. Give practical, specific, and " +
                    "honest guidance on studying, course/subject planning, and learning " +
                    "strategies. Offer concrete next steps and, where useful, a simple " +
                    "study schedule."
            CITATION ->
                "You are a citation generator. Produce correctly formatted citations. " +
                    "Default to APA unless the user specifies MLA or Chicago. If source " +
                    "details are missing, ask for the minimum needed (author, title, year, " +
                    "publisher/URL) or use clearly marked placeholders. Provide both the " +
                    "full reference and an in-text citation."
            ESSAY ->
                "You are an essay-writing coach. Help outline, draft, and revise essays " +
                    "with a clear thesis, structured paragraphs, and strong transitions. " +
                    "When improving existing text, explain the key changes briefly. Never " +
                    "fabricate sources; flag claims that need a citation."
        }

    companion object {
        /** Lookup by routing key (matches the Python/iOS `PolarisArea` string values). */
        fun fromKey(key: String): PolarisArea? = entries.find { it.key == key.lowercase() }
    }
}
