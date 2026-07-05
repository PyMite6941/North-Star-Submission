package com.polaris.studykit

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

// These cover the pure logic (area registry / key mapping / power-mode tiering). The
// on-device model itself needs a real (and, per MediaPipe's docs, high-end) device, so
// generation is exercised via the example app, not a JVM unit test.

class PolarisAreaTest {

    @Test
    fun `six areas exist`() {
        assertEquals(6, PolarisArea.entries.size)
    }

    @Test
    fun `keys match the Python and iOS builds`() {
        assertEquals(PolarisArea.CV_BUILDER, PolarisArea.fromKey("cv_builder"))
        assertEquals(PolarisArea.FLASHCARDS, PolarisArea.fromKey("FLASHCARDS"))
        assertNull(PolarisArea.fromKey("nonsense"))
    }

    @Test
    fun `every area has a title and a system prompt`() {
        for (area in PolarisArea.entries) {
            assertTrue(area.title.isNotEmpty())
            assertTrue(area.systemPrompt.isNotEmpty())
        }
    }
}

class PowerModeTest {

    @Test
    fun `power modes shrink resource use in order`() {
        assertTrue(PowerMode.NORMAL.maxTokens > PowerMode.LOW_POWER.maxTokens)
        assertTrue(PowerMode.LOW_POWER.maxTokens > PowerMode.SAVE_MEMORY.maxTokens)
        assertTrue(PowerMode.NORMAL.topK > PowerMode.SAVE_MEMORY.topK)
    }
}
