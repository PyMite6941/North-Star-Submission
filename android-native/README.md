# PolarisStudyKit (Android) — on-device, the Android counterpart to `ios-native/`

Android has no built-in system model the way iOS 26+ has Apple Intelligence, so there is no
truly zero-download on-device option here. This package runs the study LLM **entirely on
the phone** via **Google's [MediaPipe LLM Inference API](https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference/android)**,
using a small, bundled quantized model — still no server, no account, and no network once
the model file is on the device.

## Why MediaPipe LLM Inference (and its real limits)

| Option | On-device | Bring your own model | Effort | Notes |
|--------|:---:|:---:|--------|-------|
| **MediaPipe LLM Inference** ✅ used here | ✅ | ✅ (any small GGUF/`.task`-convertible model) | low | Documented, Kotlin-native, works on today's flagship-class Android hardware. |
| **LiteRT-LM** | ✅ | ✅ | unclear | Google's forward-looking replacement — see "Roadmap" below; not documented enough yet to build against with confidence. |
| llama.cpp (JNI) | ✅ | ✅ (GGUF) | higher | Maximum control, works on older/lower-end hardware too; more native-build work. |
| Thin client (LAN/desktop Ollama) | ❌ | ✅ | low | The existing fallback for Android in `install/android-termux.sh` / `install/README.md`. |

**Be honest about the trade-off**: per Google's own docs, MediaPipe's LLM Inference API is
"optimized for high-end Android devices, such as Pixel 8 and Samsung S23 or later, and does
not reliably support device emulators" — and it's currently in **maintenance-only mode**,
with Google recommending eventual migration to **LiteRT-LM**. It's still the right choice
*today* because it's real, documented, and Kotlin-native — but on a budget/older phone, the
existing Termux + Ollama path (RAM-limited, but broader hardware support) remains the
better fit. Use [`PowerMode`](polaris-study-kit/src/main/java/com/polaris/studykit/PowerMode.kt)
to push a struggling device as far as it'll go before falling back to that path.

## What's here

```
android-native/
├── settings.gradle.kts / build.gradle.kts / gradle.properties
├── polaris-study-kit/            # the library module (mirrors ios-native/Sources/PolarisStudyKit)
│   └── src/main/java/com/polaris/studykit/
│       ├── PolarisArea.kt        # the 6 areas + prompts (mirrors polaris_core/polaris.py)
│       ├── PowerMode.kt          # NORMAL / LOW_POWER / SAVE_MEMORY tuning
│       └── PolarisStudy.kt       # router → area handler, on-device
│   └── src/test/...              # pure JVM unit tests (no device/emulator needed)
└── example/                      # minimal Jetpack Compose usage example
```

No Gradle wrapper is checked in (avoids committing a binary jar) — CI provisions Gradle
directly (see `.github/workflows/ci.yml`); for local development, install Gradle 8.9+
yourself or run `gradle wrapper` once to generate one.

## Getting a model file

MediaPipe's LLM Inference API takes a `.task` model file. Google's recommendation: **Gemma
3 1B, 4-bit quantized**, from Hugging Face. Push it to the device once:

```bash
adb push gemma3-1b-it-int4.task /data/local/tmp/gemma3-1b-it-int4.task
```

The example app points at that exact path — see `MainActivity.kt`.

## Use it

```kotlin
val polaris = PolarisStudy(
    context = applicationContext,
    modelPath = "/data/local/tmp/gemma3-1b-it-int4.task",
    powerMode = PowerMode.LOW_POWER,   // or NORMAL / SAVE_MEMORY
)
val result = polaris.answer("Quiz me on the French Revolution")   // call off the main thread
println(result.area.title)   // "Quizzing"
println(result.text)
polaris.close()
```

See `example/src/main/java/com/polaris/studykit/example/MainActivity.kt` for a minimal
Compose screen (uses Kotlin's `use {}` to close the session automatically).

## Requirements

- Android 8.0+ (`minSdk 26`), but realistically a **high-end device from the last few
  years** (Pixel 8 / Galaxy S23-class or newer) for acceptable performance — see the
  trade-off note above.
- Does **not** reliably run on emulators (per MediaPipe's own docs) — test on a real device.
- A `.task` model file pushed to the device (not bundled in the repo — see above).

## Roadmap

- Migrate to **LiteRT-LM** once Google's Android documentation for it is complete enough
  to build against confidently (it's explicitly the recommended successor to LLM
  Inference).
- **RAG on-device**: mirrors the iOS roadmap item — pair with a small on-device embedding
  model + vector index to bring Study RAG to Android too.
- **Fitness agents**: reuse the parsers via a small Kotlin port, same `PolarisStudy`-style
  wrapper around MediaPipe/LiteRT-LM.
