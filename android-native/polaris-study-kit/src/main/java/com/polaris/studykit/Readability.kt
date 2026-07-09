package com.polaris.studykit

import kotlin.math.roundToInt

/**
 * Deterministic writing analysis for the "Essay" feature — no AI.
 * Flesch Reading Ease + Flesch–Kincaid grade level (1975 formulas) plus structural signals.
 */
data class ReadabilityReport(
    val words: Int,
    val sentences: Int,
    val syllables: Int,
    val fleschReadingEase: Double,
    val fleschKincaidGrade: Double,
    val avgSentenceLength: Double,
    val longSentences: Int,
    val passiveHits: Int,
) {
    fun summary(): String =
        "Reading ease ${fleschReadingEase.roundToInt()} · grade $fleschKincaidGrade · " +
            "$words words, $sentences sentences (avg $avgSentenceLength/sentence)"
}

object Readability {

    fun analyze(text: String): ReadabilityReport {
        val sentenceList = text.split(Regex("[.!?]")).map { it.trim() }.filter { it.isNotEmpty() }
        val wordList = text.split(Regex("[^A-Za-z']+")).filter { it.isNotEmpty() }

        val nWords = wordList.size.coerceAtLeast(1)
        val nSentences = sentenceList.size.coerceAtLeast(1)
        val nSyll = wordList.sumOf { syllables(it) }

        val wps = nWords.toDouble() / nSentences
        val spw = nSyll.toDouble() / nWords
        val ease = 206.835 - 1.015 * wps - 84.6 * spw
        val grade = 0.39 * wps + 11.8 * spw - 15.59

        val longS = sentenceList.count { it.split(" ").size > 25 }
        val passive = passiveHeuristic(wordList)

        return ReadabilityReport(
            words = nWords, sentences = nSentences, syllables = nSyll,
            fleschReadingEase = round1(ease), fleschKincaidGrade = round1(grade),
            avgSentenceLength = round1(wps), longSentences = longS, passiveHits = passive,
        )
    }

    /** Heuristic English syllable count (vowel-group based, silent-'e' adjustment). */
    fun syllables(word: String): Int {
        val w = word.lowercase().filter { it.isLetter() }
        if (w.isEmpty()) return 0
        val vowels = "aeiouy".toSet()
        var count = 0
        var prevVowel = false
        for (ch in w) {
            val isVowel = ch in vowels
            if (isVowel && !prevVowel) count++
            prevVowel = isVowel
        }
        if (w.endsWith("e") && count > 1) count--
        return count.coerceAtLeast(1)
    }

    private fun passiveHeuristic(words: List<String>): Int {
        val be = setOf("is", "are", "was", "were", "be", "been", "being")
        var hits = 0
        for (i in 0 until (words.size - 1).coerceAtLeast(0)) {
            if (words[i].lowercase() in be && words[i + 1].lowercase().endsWith("ed")) hits++
        }
        return hits
    }

    private fun round1(x: Double): Double = (x * 10).roundToInt() / 10.0
}
