package com.polaris.studykit

/**
 * On-device power/memory tuning, mirroring `polaris_core.config`'s `POLARIS_LOW_POWER` /
 * `POLARIS_SAVE_MEMORY` — trade quality for less CPU/battery/RAM, which matters far more on
 * a phone than a desktop.
 *
 * There's no system-provided model on Android the way Apple Intelligence provides one on
 * iOS 26+ — the model file is bundled/downloaded once (see the module README). Power mode
 * controls *how* that model is driven (shorter generations, narrower sampling), not which
 * model; on a device that still struggles in [SAVE_MEMORY], swap in a smaller quantization
 * of the model file itself.
 */
enum class PowerMode(val maxTokens: Int, val topK: Int, val temperature: Float) {
    /** Full quality: longer answers, larger sampling pool. Best on high-end devices. */
    NORMAL(maxTokens = 512, topK = 40, temperature = 0.8f),

    /** Low power: shorter generations use less CPU/battery per request. */
    LOW_POWER(maxTokens = 256, topK = 20, temperature = 0.7f),

    /** Save memory: the smallest footprint — short generations, narrow sampling. */
    SAVE_MEMORY(maxTokens = 128, topK = 10, temperature = 0.6f),
}
