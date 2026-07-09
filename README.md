# North Star ⭐ (Polaris)

**Offline-first, local-LLM agents for studying and fitness — built on [LangGraph](https://langchain-ai.github.io/langgraph/) + [Ollama](https://ollama.com).**

> **North Star Challenge judges:** start with [SUBMISSION.md](SUBMISSION.md) — the
> problem brief, track (Access & Equity), evidence of traction, and AI-usage note, mapped
> to the published rubric.

North Star is a set of four downloadable, privacy-preserving AI components that run
entirely on a user's own device (no API keys required). Everything is orchestrated with
LangGraph state machines and powered by a local LLM through Ollama.

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                                North Star (Polaris)                               │
├────────────────┬──────────────────────┬───────────────────────┬───────────────────┤
│   Study LLM    │      Study RAG       │    Fitness Agents     │  College Planner  │
│   (6 areas)    │  (vector-DB notes)   │  (MD file analysis)   │ (app tracker)     │
│                │                      │                       │                   │
│ Flashcards     │ ingest → embed →     │ parse .fit/.tcx/.gpx  │ colleges: deadline│
│ Quizzing       │ store → retrieve →   │ → analyze metrics →   │ / status / notes  │
│ CV Builder     │ grade → generate     │ growth plan → review  │ courses: 4-year   │
│ Advisor        │ (cited)              │                       │ credit map        │
│ Citation Gen   │                      │ markdown-defined      │ deadlines → .ics  │
│ Essay Helper   │ Chroma (local disk)  │ agents (`agent mds/`) │                   │
└────────────────┴──────────────────────┴───────────────────────┴───────────────────┘
                shared core: polaris_core (LLM, embeddings, config, memory)
```

## The four components

| # | Component | Folder | Library package | What it does |
|---|-----------|--------|-----------------|--------------|
| 1 | **Study LLM** | `local llm model to use for studying offline/` | `study_llm` | A local LLM that fulfils the **6 areas of Polaris**: Flashcard Creation, Quizzing, CV Builder, Advisor, Citation Generator, Essay Helper. A LangGraph router classifies the request and dispatches it to the matching area. Also has **Study Packs** and **Group Quiz** for studying together offline (below). |
| 2 | **Study RAG** | `study local notes with vector db/` | `study_rag` | Ingests a user's notes into a local Chroma vector DB and answers study questions with **retrieval-augmented, cited** responses — accurate, works offline. |
| 3 | **Fitness Agents** | `fitness agents for use/` | `fitness_agents` | Parses uploaded fitness files (`.fit`, `.tcx`, `.gpx`, `.csv`, `.json`), computes metrics, and runs **markdown-defined agents** to analyze progress and produce a personalized growth plan. |
| 4 | **College Planner** | `packages/college_planner/` | `college_planner` | An offline college-application tracker (deadlines, status, notes) and a 4-year course/credit map, stored locally — no account needed. Deadlines export to `.ics` for any calendar app. |

> Agent prompts for the fitness pipeline live as markdown in `fitness agents for use/agent mds/`
> — edit a file to change an agent, no code change required.

## The 6 areas of Polaris (Study LLM)

| Area | Purpose |
|------|---------|
| **Flashcard Creation** | Turn material into Q/A flashcards (Anki-style). |
| **Quizzing** | Generate quizzes and grade answers with feedback. |
| **CV Builder** | Draft and refine a CV / résumé. |
| **Advisor** | General study / academic advice and planning. |
| **Citation Generator** | Produce citations (APA/MLA/Chicago). |
| **Essay Helper** | Outline, draft, and improve essays. |

## Study together, still offline

Two features built for a group of students in one room with no internet and often one
shared device between them:

| Feature | What it does |
|---------|--------------|
| **Study Pack** | Bundle several decks/quizzes into one portable JSON file (`pack create`); anyone can `pack import` it — shared by USB, AirDrop, email, or any messaging app, no server or account. |
| **Group Quiz** | Pass-the-device multiplayer (`group-quiz`): each named player answers the same quiz, individually graded, with a leaderboard at the end. |

Every export is a format you can use with or without North Star installed: flashcards →
Anki `.apkg` or CSV, a résumé → PDF or Markdown, a quiz → a printable Markdown handout,
college deadlines → `.ics` for any calendar app.

## Quick start

### Easiest — one-command installers

| Platform | Command |
|----------|---------|
| **Windows** | `powershell -ExecutionPolicy Bypass -File install\install.ps1` |
| **macOS / Linux** | `./install/install.sh` |
| **Android — on-device (high-end devices)** | Native Kotlin package — see [`android-native/`](android-native) (MediaPipe LLM Inference) |
| **Android — Termux (broader hardware support)** | `bash install/android-termux.sh` |
| **iOS — on-device (recommended)** | Native Swift package — see [`ios-native/`](ios-native) (Apple Foundation Models, iOS 26+) |
| **iOS — thin client (fallback)** | `REMOTE_HOST=<desktop-ip> sh install/ios-setup.sh` |

Each installer sets up Python + the venv, installs the project, copies `.env`, and (on
desktop) installs Ollama and pulls the models. See [`install/README.md`](install/README.md)
for the full platform support matrix and per-OS details.

**Platform notes:**
- **Windows / macOS / Linux** — full local LLM via Ollama, no API keys. Set
  `POLARIS_LOW_POWER=true` and/or `POLARIS_SAVE_MEMORY=true` in `.env` on an older machine
  to trade quality for less CPU/battery/RAM use.
- **Android** — two tiers, same trade-off as iOS below: the **native Kotlin package in
  [`android-native/`](android-native)** runs fully on-device via MediaPipe's LLM Inference
  API, but per Google's own docs it's optimized for high-end devices (Pixel 8 / Galaxy
  S23-class or newer) and doesn't reliably run on emulators. On a budget/older phone,
  **Termux** remains the broader-hardware-support fallback (small models, RAM-limited); the
  RAG component may need a desktop if `chromadb` won't build.
- **iOS / iPadOS** — the Python stack can't run Ollama on-device, so the proper path is the
  **native Swift package in [`ios-native/`](ios-native)**, which runs the 6 areas on-device with
  Apple's Foundation Models framework (iOS 26+). The `ios-setup.sh` script is a thin-client fallback.

### Manual

```bash
# 1. Install Ollama and pull models (https://ollama.com)
ollama serve            # in one terminal
ollama pull llama3.2
ollama pull nomic-embed-text

# 2. Set up the Python environment
python -m venv .venv
.venv\Scripts\activate         # Windows  (POSIX: source .venv/bin/activate)
pip install -e .
cp .env.example .env           # (Windows: copy .env.example .env)
```

### Run each component

One unified command mounts all four (or use the `polaris-study` / `polaris-rag` /
`polaris-fitness` / `polaris-college` shortcuts):

```bash
polaris doctor                     # check Ollama + models for all components
polaris version
polaris serve                      # run the FastAPI service (needs [serve] extra)

# Study LLM (the 6 areas)
polaris study chat                                   # interactive, memory-backed (streamed)
polaris study ask "Explain osmosis" --area advisor   # force an area, skip the router
polaris study flashcards "the Krebs cycle" -n 8 --export deck.csv  # or deck.apkg (Anki)
polaris study quiz "the French Revolution" -n 5      # interactive, LLM-graded quiz
polaris study cv "junior year, 3.8 GPA, robotics club captain..." --export resume.pdf  # or .md

# Study together (Study Packs + Group Quiz — see "Study together, still offline" above)
polaris study pack create "Bio final" -t "Krebs cycle" -t "Photosynthesis" -e pack.json
polaris study pack import pack.json --export-dir out/     # -> out/*.apkg for each deck
polaris study group-quiz "the French Revolution" -p Ana -p Sam -p Lee

# Study RAG (vector-DB notes; supports .md/.txt/.pdf/.docx/.pptx, incremental)
polaris rag ingest "study local notes with vector db/sample_notes"
polaris rag ask "Explain the light-dependent reactions." --show-sources
polaris rag stats                                    # chunks stored
polaris rag reset                                    # clear the vector DB
polaris rag sync-discord                             # optional: see docs/discord-announcements-sync.md

# Fitness agents
polaris fitness parse activity.gpx                   # metrics incl. HR zones + training load
polaris fitness analyze activity.gpx --goal "sub-25 5K" --save report.md --log
polaris fitness trend                                # fitness/fatigue/form over time
polaris fitness schedule --goal "sub-25 5K" --export-ics plan.ics  # weekly plan → calendar

# College Planner (offline application tracker + course map)
polaris college add "MIT" --deadline 2027-01-01 --type "Early Action"
polaris college list
polaris college deadlines --export deadlines.ics     # -> any calendar app
polaris college course add Math "AP Calculus BC" --credits 1 --year 12 --grade A
polaris college course list
```

### Web UI

```bash
pip install -e ".[ui]"
streamlit run webui/app.py         # one front-end for all three components
```

Themed to match **[polarisstudent.com](https://polarisstudent.com)** (firebrick→orange brand,
constellation-navy header, Plus Jakarta Sans + Inter). Brand tokens live in [THEME.md](THEME.md).

### HTTP API

```bash
pip install -e ".[serve]"
polaris serve                      # → http://127.0.0.1:8000  (interactive docs at /docs)
```

Everything runs locally. No `.env` values are required unless you opt into the cloud
fallback (`GROQ_API_KEY` / `OPENROUTER_API_KEY`). Set an athlete profile
(`POLARIS_ATHLETE_AGE` / `_MAX_HR` / `_RESTING_HR`) for true %HRmax zones.

## Repository layout

```
North Star Submission/
├── README.md / ARCHITECTURE.md / CONTRIBUTING.md / ROADMAP.md
├── root.md                 # the original spec (3 components + the 6 areas)
├── pyproject.toml          # single editable install, packages live in packages/
├── .env.example
├── packages/               # importable libraries (no spaces → clean imports)
│   ├── polaris_core/       # shared: config, LLM, embeddings, memory, console, the 6 areas
│   ├── study_llm/          # component 1: graph + flashcards + quiz + CLI
│   ├── study_rag/          # component 2: graph + ingest (pdf/docx/pptx) + CLI
│   ├── fitness_agents/     # component 3: graph + parsers + metrics + history + schedule + CLI
│   ├── college_planner/    # component 4: models + SQLite storage + .ics export + CLI
│   ├── polaris_cli/        # unified `polaris` command
│   └── polaris_api/        # FastAPI service ([serve] extra)
├── webui/                  # Streamlit web UI ([ui] extra)
├── tests/                  # smoke tests (run without Ollama)
├── docs/                   # discord-announcements-sync.md, etc.
├── .github/workflows/      # CI: ruff+pytest (3.11-3.13) + android-native (Gradle) + ios-native (Swift)
├── install/                # cross-platform installers + support matrix
│   ├── install.ps1         # Windows
│   ├── install.sh          # macOS / Linux
│   ├── android-termux.sh   # Android (Termux)
│   └── ios-setup.sh        # iOS thin-client fallback
├── ios-native/             # iOS ON-DEVICE app (Swift, Apple Foundation Models, iOS 26+)
│   └── Sources/PolarisStudyKit/   # the 6 areas, on-device (mirrors study_llm)
├── android-native/         # Android ON-DEVICE app (Kotlin, MediaPipe LLM Inference)
│   └── polaris-study-kit/  # the 6 areas + PowerMode, on-device (mirrors study_llm)
├── local llm model to use for studying offline/   # component 1 docs + runners + Modelfile
├── study local notes with vector db/              # component 2 docs + sample notes + runners
└── fitness agents for use/                        # component 3 docs + agent mds + sample data
    ├── agent mds/          # markdown agent definitions
    └── core programs/      # runnable entry scripts
```

## Documentation map

| Doc | What's in it |
|-----|--------------|
| [SUBMISSION.md](SUBMISSION.md) | North Star Challenge problem brief, track, traction, and AI-usage note. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, why the layout, each component's LangGraph topology. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Setup, conventions, how to add an area / agent / file format. |
| [ROADMAP.md](ROADMAP.md) | Status of each component and what's next. |
| [THEME.md](THEME.md) | Brand tokens (colors/fonts) matched to polarisstudent.com. |
| [install/README.md](install/README.md) | Per-platform install + the support matrix. |
| [ios-native/README.md](ios-native/README.md) | On-device iOS via Foundation Models (+ MLX / MLC / llama.cpp options). |
| [android-native/README.md](android-native/README.md) | On-device Android via MediaPipe LLM Inference — the device-tiering trade-offs and the LiteRT-LM migration note. |
| [docs/discord-announcements-sync.md](docs/discord-announcements-sync.md) | Pull the official Polaris Student `#announcements` channel into Study RAG — read-only, one-way, and exactly what has to be set up on the Discord side first. |
| [docs/polly-persona-prompt.md](docs/polly-persona-prompt.md) | Candidate system prompt for the Polly Bot AI study companion persona, plus a `scripts/polly_persona_chat.py` harness for testing it against Groq. |

## Status

Scaffolded and verified: all packages install (`pip install -e .`), 26 smoke tests pass, ruff
clean, and all three LangGraph pipelines (Study LLM, Study RAG, Fitness Agents) run
end-to-end — College Planner is a fourth, graph-free component (local storage + exports,
no LLM call needed). Live LLM output needs Ollama running (`ollama serve` + the two
models). CI also builds `android-native/` (Gradle) and `ios-native/` (Swift) so the
on-device mobile packages can't silently bit-rot. See [ROADMAP.md](ROADMAP.md) for what's
stubbed vs. complete.
