package com.polaris.studykit

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// Every feature is a pure deterministic algorithm, so all of it runs as plain JVM unit tests
// (no device, no model file). This is the point of the AI-free mobile kit.

class PolarisAreaTest {

    @Test
    fun `six areas each have an algorithm`() {
        assertEquals(6, PolarisArea.entries.size)
        for (area in PolarisArea.entries) {
            assertTrue(area.title.isNotEmpty())
            assertTrue(area.algorithm.isNotEmpty())
        }
        assertEquals(PolarisArea.CV_BUILDER, PolarisArea.fromKey("cv_builder"))
        assertNull(PolarisArea.fromKey("nonsense"))
    }
}

class Sm2Test {

    @Test
    fun `passes grow the interval then a lapse resets it`() {
        val day = 20000L
        var s = Sm2State.new(day)
        s = SpacedRepetition.schedule(s, grade = 5, today = day)
        assertEquals(1, s.interval); assertEquals(1, s.repetitions)
        s = SpacedRepetition.schedule(s, grade = 5, today = day)
        assertEquals(6, s.interval); assertEquals(2, s.repetitions)
        val grown = SpacedRepetition.schedule(s, grade = 4, today = day)
        assertTrue(grown.interval > 6); assertEquals(3, grown.repetitions)
        val lapsed = SpacedRepetition.schedule(grown, grade = 1, today = day)
        assertEquals(0, lapsed.repetitions); assertEquals(1, lapsed.interval)
        assertTrue(lapsed.ease >= 1.3)
    }
}

class CitationTest {

    @Test
    fun `apa and in-text formatting`() {
        val src = Source(
            authors = listOf("Smith, John Paul"), title = "On Photosynthesis",
            year = "2020", container = "Journal of Biology",
        )
        val apa = Citations.reference(src, CitationStyle.APA)
        assertTrue(apa.contains("Smith, J. P."))
        assertTrue(apa.contains("(2020)"))
        assertEquals("(Smith, 2020)", Citations.inText(src, CitationStyle.APA))
        assertEquals("(Smith)", Citations.inText(src, CitationStyle.MLA))
    }
}

class QuizAndFlashcardTest {

    @Test
    fun `grading is fuzzy and leitner promotes`() {
        assertTrue(QuizEngine.isCorrect("mitochondrion", "mitochondria"))
        assertFalse(QuizEngine.isCorrect("nucleus", "mitochondria"))
        assertEquals(3, QuizEngine.leitner(2, correct = true))
        assertEquals(0, QuizEngine.leitner(3, correct = false))
    }

    @Test
    fun `flashcards and readability`() {
        val text = "Mitochondria are the powerhouse of the cell. " +
            "Photosynthesis converts light into chemical energy."
        assertTrue(FlashcardGenerator.generate(text).isNotEmpty())
        val r = Readability.analyze(text)
        assertEquals(2, r.sentences)
        assertTrue(r.words > 0)
    }
}

class WritingCheckerTest {

    @Test
    fun `flags wordiness, weasel words and repeats offline`() {
        val issues = WritingChecker.check("In order to win, be very very careful.")
        assertTrue(issues.any { it.matched.equals("in order to", true) && it.suggestion == "to" })
        assertTrue(issues.any { it.message.contains("Weak intensifier") })
        assertTrue(issues.any { it.message.contains("Repeated word") })
        assertTrue(issues.all { it.start in 0..it.end && it.end <= 39 })
    }

    @Test
    fun `clean prose scores higher than messy prose`() {
        val clean = "The cell makes energy. Light drives the reaction."
        val messy = "In order to make energy, the the cell is very very clearly used " +
            "due to the fact that light."
        val cleanScore = WritingChecker.check(clean).let { WritingChecker.score(clean, it) }
        val messyScore = WritingChecker.check(messy).let { WritingChecker.score(messy, it) }
        assertTrue(cleanScore > messyScore)
    }
}
