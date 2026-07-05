package com.polaris.studykit

import android.content.Context
import com.google.mediapipe.tasks.genai.llminference.LlmInference
import com.google.mediapipe.tasks.genai.llminference.LlmInference.LlmInferenceOptions

/**
 * On-device study assistant: routes a request to one of the six Polaris areas, then answers
 * with that area's specialized prompt — all running locally via MediaPipe's LLM Inference
 * API (see the module README for the model file this expects).
 *
 * Mirrors the LangGraph router→handler topology in `packages/study_llm` and iOS's
 * `PolarisStudy.swift`. Unlike the iOS build (Apple Foundation Models' schema-constrained
 * guided generation), this API has no structured-output mode, so routing asks the model to
 * reply with a single area key and validates it against [PolarisArea], falling back to
 * [PolarisArea.ADVISOR] on anything unparseable — the same safe default the Python router
 * uses when its own classification step fails.
 */
class PolarisStudy(
    context: Context,
    modelPath: String,
    powerMode: PowerMode = PowerMode.NORMAL,
) : AutoCloseable {

    data class Answer(val area: PolarisArea, val text: String)

    private val llm: LlmInference = LlmInference.createFromOptions(
        context,
        LlmInferenceOptions.builder()
            .setModelPath(modelPath)
            .setMaxTokens(powerMode.maxTokens)
            .setTopK(powerMode.topK)
            .setTemperature(powerMode.temperature)
            .build(),
    )

    private val routerPreamble = buildString {
        appendLine("You route a student's request to exactly one capability area.")
        appendLine("Reply with ONLY the area key, nothing else. Areas:")
        for (area in PolarisArea.entries) {
            appendLine("- ${area.key}: ${area.summary}")
        }
    }

    /**
     * Route the prompt to an area, then generate the answer — fully on-device, blocking.
     * Call this off the main thread (e.g. `Dispatchers.IO`) — inference is not instant.
     */
    fun answer(prompt: String): Answer {
        val routed = llm.generateResponse("$routerPreamble\nRequest: $prompt\nArea key:")
        val area = PolarisArea.fromKey(routed.trim().lowercase().substringBefore(' '))
            ?: PolarisArea.ADVISOR

        val response = llm.generateResponse("${area.systemPrompt}\n\n$prompt")
        return Answer(area, response)
    }

    /** Release the native LLM resources. Always call when done (or use Kotlin's `use {}`). */
    override fun close() {
        llm.close()
    }
}
