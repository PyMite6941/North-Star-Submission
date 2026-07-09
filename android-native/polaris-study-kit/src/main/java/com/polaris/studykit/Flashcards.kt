package com.polaris.studykit

/** A generated flashcard. */
data class Flashcard(val question: String, val answer: String)

/**
 * Algorithmic flashcard generation from study text — no AI.
 *  1. Definition extraction via "X is/are/means Y" patterns → Q/A cards.
 *  2. Cloze deletion: blank the most salient term (longest non-stopword) in a sentence.
 */
object FlashcardGenerator {

    private val stopwords = setOf(
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "is", "are",
        "was", "were", "be", "been", "being", "that", "this", "these", "those", "it", "its",
        "as", "by", "with", "from", "at", "which", "who", "whom", "into", "than", "then",
    )

    fun generate(text: String, limit: Int = 20): List<Flashcard> {
        val cards = mutableListOf<Flashcard>()
        val seen = mutableSetOf<String>()
        for (sentence in sentences(text)) {
            if (cards.size >= limit) break
            val card = definitionCard(sentence) ?: clozeCard(sentence) ?: continue
            if (seen.add(card.answer.lowercase())) cards.add(card)
        }
        return cards
    }

    private fun definitionCard(sentence: String): Flashcard? {
        for (verb in listOf(" is ", " are ", " means ", " refers to ", " is defined as ")) {
            val idx = sentence.indexOf(verb)
            if (idx < 0) continue
            val subject = sentence.substring(0, idx).trim()
            val predicate = sentence.substring(idx + verb.length).trim().trimEnd('.')
            if (subject.isEmpty() || predicate.isEmpty()) continue
            if (subject.split(" ").size > 5) continue
            val plural = verb.contains("are")
            return Flashcard("What ${if (plural) "are" else "is"} $subject?", predicate)
        }
        return null
    }

    private fun clozeCard(sentence: String): Flashcard? {
        val words = sentence.split(Regex("[^A-Za-z-]+")).filter { it.isNotEmpty() }
        if (words.size < 5) return null
        val key = words
            .filter { it.length >= 4 && it.lowercase() !in stopwords }
            .maxByOrNull { it.length } ?: return null
        return Flashcard(sentence.replace(key, "_____"), key)
    }

    fun sentences(text: String): List<String> =
        text.split(Regex("[.!?\\n]"))
            .map { it.trim() }
            .filter { it.split(" ").size >= 4 }
}
