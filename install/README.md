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
| **Android** (native) | ✅ any device | [`android-native/`](../android-native) | **Recommended.** Kotlin study kit — classical algorithms, **no AI**, no model, no network. |
| **iOS / iPadOS** (native) | ✅ any device | [`ios-native/`](../ios-native) | **Recommended.** Swift study kit — classical algorithms, **no AI**, iOS 15+. |
| **Web** | ✅ deployed | [`frontend/`](../frontend) | React app on Vercel → Cloud Run backend (fastembed + Groq). |
| **Android / iOS** (LLM via desktop) | ⚠️ optional | `install/android-termux.sh` · `install/ios-setup.sh` | Only if you want the *LLM* features on mobile: Termux runs Ollama on-device (RAM-limited); `ios-setup.sh` is a thin client to a desktop/cloud backend. |

Legend: ✅ full features · ⚠️ optional/constrained.

> **Mobile note:** the native apps are **AI-free** — every study feature is a deterministic
> algorithm (SM-2, Levenshtein, Flesch–Kincaid, rule-table citations), so they run instantly on
> any device with no model download. The only online feature is **Polly** (the AI writing coach),
> which the app calls over the network only when connected. The Termux / `ios-setup.sh` scripts
> are only needed if you specifically want the *LLM*-powered experience on a phone.

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

## Android

### Recommended: native app (`android-native/`)

The Kotlin study kit in [`android-native/`](../android-native) runs every study feature with
**classical algorithms — no AI, no model, no network** — so it works instantly on **any** device
(no high-end/NPU requirement, works on emulators). See that package's README for the algorithm
list (SM-2, Levenshtein, Flesch–Kincaid, rule-table citations) and usage.

### Optional: LLM features on-device via Termux

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
- Keep other apps closed while a model runs. On a low-RAM phone, also set
  `POLARIS_LOW_POWER=true` and `POLARIS_SAVE_MEMORY=true` in `.env`.

## iOS / iPadOS

### Recommended: native app (`ios-native/`)

The Swift study kit in [`ios-native/`](../ios-native) runs every study feature with **classical
algorithms — no AI, no network, no download** — on **iOS 15+** (no Apple-Intelligence requirement):

```swift
import PolarisStudyKit
let cards = PolarisStudy().makeFlashcards(from: notes)   // SM-2 + cloze generation, instant
```

See [`ios-native/README.md`](../ios-native/README.md) for the full algorithm list.

### Optional: LLM features via a desktop/cloud backend (`ios-setup.sh`)

If you specifically want the *LLM*-powered features on iOS, the Python app runs as a **thin
client** in one of two modes, configured from the **a-Shell** app:

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

> **Shipping a real mobile app?** Use the native kits (`ios-native/` / `android-native/`) — they're
> AI-free and need no model, so there's nothing to bundle. Add the online **Polly** coach via the
> `/writing/coach` API when the device has connectivity.

---

## What every installer does

1. Ensures Python 3.11+ (and Ollama, where supported).
2. Creates a `.venv` and installs the monorepo editable (`pip install -e .`).
3. Copies `.env.example` → `.env` (tailoring model names on mobile).
4. Pulls the default models (skippable).

All are **idempotent** — re-running them is safe.
