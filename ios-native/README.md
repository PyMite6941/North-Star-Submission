# PolarisStudyKit — on-device iOS (the real alternative to the thin client)

The Python install path treats iOS as a **thin client** because the sandbox can't run Ollama.
This package is the **on-device alternative**: it runs the study LLM entirely on the iPhone/iPad
using **Apple's [Foundation Models](https://developer.apple.com/documentation/FoundationModels)
framework** (iOS 26+). No Ollama, no network, no download — it uses the same on-device model that
powers Apple Intelligence.

## Why Foundation Models (vs. the other options)

| Option | On-device | Bring your own model | Effort | Notes |
|--------|:---:|:---:|--------|-------|
| **Apple Foundation Models** ✅ recommended | ✅ | ❌ (Apple's model) | low | Native Swift, built into iOS 26, free, structured output + tool calling. |
| **MLX Swift** ([mlx-swift-examples](https://github.com/ml-explore/mlx-swift-examples)) | ✅ | ✅ (Qwen/Llama, MLX format) | medium | Run your own models on Apple Silicon; bigger download. |
| **MLC LLM** ([llm.mlc.ai](https://llm.mlc.ai/)) | ✅ | ✅ (GGUF/MLC) | medium | Cross-platform, also covers older devices. |
| **llama.cpp** | ✅ | ✅ (GGUF) | higher | Maximum control; C++ wrapper work. |
| Thin client (LAN/cloud) | ❌ | — | low | The fallback in `install/ios-setup.sh`. |

This kit uses **Foundation Models** because it needs zero model download, matches the 6-area
design via guided generation, and is the lowest-friction true on-device path. The other rows are
listed so you can swap the runtime if you need a specific model or older-device support.

## What's here

```
ios-native/
├── Package.swift
├── Sources/PolarisStudyKit/
│   ├── PolarisArea.swift     # the 6 areas + prompts (mirrors polaris_core/polaris.py)
│   └── PolarisStudy.swift    # router → area handler, on-device (mirrors study_llm graph)
├── Tests/PolarisStudyKitTests/
└── Example/ContentView.swift # SwiftUI usage example
```

The router uses Foundation Models' **guided generation** (`@Generable` + `@Guide(.anyOf(...))`) to
constrain the choice to the six area keys, then answers with that area's specialized prompt —
the same router→handler flow as the Python LangGraph build, executed locally.

## Use it

Add the package to an iOS 26 app target, then:

```swift
import PolarisStudyKit

let polaris = PolarisStudy()
guard await polaris.isAvailable() else { /* show "needs Apple Intelligence device" */ return }

let result = try await polaris.answer(to: "Quiz me on the French Revolution")
print(result.area.title)  // "Quizzing"
print(result.text)
```

See `Example/ContentView.swift` for a minimal SwiftUI screen.

## Requirements

- iOS / iPadOS / macOS / visionOS **26+**
- An **Apple-Intelligence-capable device** (model availability is checked at runtime via
  `SystemLanguageModel.default.availability`; the API degrades gracefully when unavailable).
- Xcode 26+ to build.

## Roadmap

- **RAG on-device**: pair with on-device embeddings + a small vector index (e.g. `NLEmbedding`
  or Core ML) to bring the study-RAG component on-device too.
- **Fitness agents**: reuse the parsers via a small Swift port (or a shared file-format lib) and
  drive the analyst/planner/reviewer prompts through the same `LanguageModelSession` pattern,
  using the `Tool` protocol for metric computation.
