# Install

North Star is **offline-first**: on desktop it runs a local LLM via [Ollama](https://ollama.com)
with no API keys. Mobile platforms are more constrained — the table below is honest about what
runs where.

## Platform support matrix

| Platform | On-device LLM | Installer | Notes |
|----------|:---:|-----------|-------|
| **Windows** | ✅ full | `install\install.ps1` | Auto-installs Python + Ollama via winget if missing. |
| **macOS** | ✅ full | `install/install.sh` | Apple Silicon runs local models very well. |
| **Linux** | ✅ full | `install/install.sh` | Uses the official Ollama install script. |
| **Android** | ⚠️ limited | `install/android-termux.sh` | Via **Termux**; small models only (RAM/CPU limited). |
| **iOS / iPadOS** (native) | ✅ on-device | [`ios-native/`](../ios-native) | **Recommended.** Runs on-device via Apple Foundation Models (iOS 26+). No Ollama needed. |
| **iOS / iPadOS** (scripted) | ❌ not on-device | `install/ios-setup.sh` | Fallback: Python sandbox blocks Ollama, so it runs as a **thin client** (LAN or cloud). |

Legend: ✅ full local LLM · ⚠️ works but constrained · ❌ no on-device daemon.

> **iOS note:** you cannot run Ollama (or the Python RAG stack) on-device. The proper
> on-device path is the native Swift package in [`ios-native/`](../ios-native), which uses
> Apple's Foundation Models framework. The `ios-setup.sh` script below is the no-native-build
> fallback (thin client to a desktop or the cloud).

---

## Windows

```powershell
# from the repo root
powershell -ExecutionPolicy Bypass -File install\install.ps1
# options:
#   -ChatModel qwen2.5:3b   -EmbedModel nomic-embed-text   -SkipModels
```
Then:
```powershell
.\.venv\Scripts\Activate.ps1
polaris-study doctor
```

## macOS / Linux

```bash
chmod +x install/install.sh
./install/install.sh
# options via env: CHAT_MODEL=qwen2.5:3b SKIP_MODELS=1 ./install/install.sh
source .venv/bin/activate
polaris-study doctor
```

## Android (Termux)

Install **Termux from F-Droid** (the Play Store build is outdated). Then:

```bash
pkg install git -y
git clone <your-repo-url>
cd "North Star Submission"
bash install/android-termux.sh
```

- Defaults to small models (`qwen2.5:1.5b`, `all-minilm`) that fit phone RAM.
- If `chromadb`/`onnxruntime` won't build on your device, the script falls back to a
  **lite install** (study-LLM + fitness components). The RAG component needs `chromadb`;
  on unsupported devices, run RAG against a desktop instead (set `OLLAMA_BASE_URL`).
- Keep other apps closed while a model runs.

## iOS / iPadOS

### Recommended: native on-device (`ios-native/`)

iOS **cannot** run Ollama, but it *can* run a model on-device through Apple's **Foundation
Models** framework (iOS 26+). The Swift package in [`ios-native/`](../ios-native) implements the
6 Polaris areas locally — no Ollama, no network, no download. Add it to an iOS 26 app target:

```swift
import PolarisStudyKit
let result = try await PolarisStudy().answer(to: "Quiz me on the French Revolution")
```

See [`ios-native/README.md`](../ios-native/README.md) (also covers MLX Swift / MLC / llama.cpp
if you need to run your own model instead of Apple's).

### Fallback: thin client (`ios-setup.sh`)

If you can't ship a native build, the Python app runs as a **thin client** in one of two modes,
configured from the **a-Shell** app:

**(A) LAN mode** — use Ollama on your Mac/PC over Wi-Fi:
```sh
# on the desktop, expose Ollama to the network:
OLLAMA_HOST=0.0.0.0 ollama serve
# in a-Shell on the iPhone, from the repo folder:
REMOTE_HOST=192.168.1.50 sh install/ios-setup.sh
```

**(B) Cloud mode** — use a free hosted model:
```sh
USE_CLOUD=1 sh install/ios-setup.sh
# then edit .env: set GROQ_API_KEY or OPENROUTER_API_KEY
```

> **Shipping a real iOS app?** Bundle a small model on-device with
> [MLC LLM](https://llm.mlc.ai/) or [llama.cpp](https://github.com/ggerganov/llama.cpp)
> in a native Swift app. That's a build target, not a script — this scaffold's Python
> graphs would back the LAN/cloud client or be ported to the native runtime.

---

## What every installer does

1. Ensures Python 3.11+ (and Ollama, where supported).
2. Creates a `.venv` and installs the monorepo editable (`pip install -e .`).
3. Copies `.env.example` → `.env` (tailoring model names on mobile).
4. Pulls the default models (skippable).

All are **idempotent** — re-running them is safe.
