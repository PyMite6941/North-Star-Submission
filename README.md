# North Star ⭐ (Polaris)

**Offline-first, local-LLM agents for studying and fitness — built on [LangGraph](https://langchain-ai.github.io/langgraph/) + [Ollama](https://ollama.com).**

North Star is a set of three downloadable, privacy-preserving AI components that run
entirely on a user's own device (no API keys required). Everything is orchestrated with
LangGraph state machines and powered by a local LLM through Ollama.

```
┌──────────────────────────────────────────────────────────────────────┐
│                          North Star (Polaris)                          │
├──────────────────┬───────────────────────────┬───────────────────────┤
│   Study LLM      │      Study RAG            │    Fitness Agents       │
│  (6 areas)       │   (vector-DB notes)       │   (MD file analysis)    │
│                  │                           │                         │
│ Flashcards       │  ingest → embed → store   │  parse .fit/.tcx/.gpx   │
│ Quizzing         │  retrieve → grade →       │  → analyze metrics →    │
│ CV Builder       │  generate (cited)         │  growth plan → review   │
│ Advisor          │                           │                         │
│ Citation Gen     │   Chroma (local disk)     │  markdown-defined        │
│ Essay Helper     │                           │  agents (`agent mds/`)  │
└──────────────────┴───────────────────────────┴───────────────────────┘
                   shared core: polaris_core (LLM, embeddings, config, memory)
```

## The three components

| # | Component | Folder | Library package | What it does |
|---|-----------|--------|-----------------|--------------|
| 1 | **Study LLM** | `local llm model to use for studying offline/` | `study_llm` | A local LLM that fulfils the **6 areas of Polaris**: Flashcard Creation, Quizzing, CV Builder, Advisor, Citation Generator, Essay Helper. A LangGraph router classifies the request and dispatches it to the matching area. |
| 2 | **Study RAG** | `study local notes with vector db/` | `study_rag` | Ingests a user's notes into a local Chroma vector DB and answers study questions with **retrieval-augmented, cited** responses — accurate, works offline. |
| 3 | **Fitness Agents** | `fitness agents for use/` | `fitness_agents` | Parses uploaded fitness files (`.fit`, `.tcx`, `.gpx`, `.csv`, `.json`), computes metrics, and runs **markdown-defined agents** to analyze progress and produce a personalized growth plan. |

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

## Quick start

### Easiest — one-command installers

| Platform | Command |
|----------|---------|
| **Windows** | `powershell -ExecutionPolicy Bypass -File install\install.ps1` |
| **macOS / Linux** | `./install/install.sh` |
| **Android (Termux)** | `bash install/android-termux.sh` |
| **iOS — on-device (recommended)** | Native Swift package — see [`ios-native/`](ios-native) (Apple Foundation Models, iOS 26+) |
| **iOS — thin client (fallback)** | `REMOTE_HOST=<desktop-ip> sh install/ios-setup.sh` |

Each installer sets up Python + the venv, installs the project, copies `.env`, and (on
desktop) installs Ollama and pulls the models. See [`install/README.md`](install/README.md)
for the full platform support matrix and per-OS details.

**Platform notes:**
- **Windows / macOS / Linux** — full local LLM via Ollama, no API keys.
- **Android** — works via Termux, but with small models (RAM-limited); the RAG component may
  need a desktop if `chromadb` won't build.
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

One unified command mounts all three (or use the `polaris-study` / `polaris-rag` /
`polaris-fitness` shortcuts):

```bash
polaris doctor                     # check Ollama + models for all components
polaris version
polaris serve                      # run the FastAPI service (needs [serve] extra)

# Study LLM (the 6 areas)
polaris study chat                                   # interactive, memory-backed (streamed)
polaris study ask "Explain osmosis" --area advisor   # force an area, skip the router
polaris study flashcards "the Krebs cycle" -n 8 --export deck.csv  # structured deck → Anki CSV
polaris study quiz "the French Revolution" -n 5      # interactive, LLM-graded quiz

# Study RAG (vector-DB notes; supports .md/.txt/.pdf/.docx/.pptx, incremental)
polaris rag ingest "study local notes with vector db/sample_notes"
polaris rag ask "Explain the light-dependent reactions." --show-sources
polaris rag stats                                    # chunks stored
polaris rag reset                                    # clear the vector DB

# Fitness agents
polaris fitness parse activity.gpx                   # metrics incl. HR zones + training load
polaris fitness analyze activity.gpx --goal "sub-25 5K" --save report.md --log
polaris fitness trend                                # fitness/fatigue/form over time
polaris fitness schedule --goal "sub-25 5K" --export-ics plan.ics  # weekly plan → calendar
```

### Web UI

```bash
pip install -e ".[ui]"
streamlit run webui/app.py         # one front-end for all three components
```

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
│   ├── polaris_cli/        # unified `polaris` command
│   └── polaris_api/        # FastAPI service ([serve] extra)
├── webui/                  # Streamlit web UI ([ui] extra)
├── tests/                  # smoke tests (run without Ollama)
├── .github/workflows/      # CI: ruff + pytest on 3.11/3.12/3.13
├── install/                # cross-platform installers + support matrix
│   ├── install.ps1         # Windows
│   ├── install.sh          # macOS / Linux
│   ├── android-termux.sh   # Android (Termux)
│   └── ios-setup.sh        # iOS thin-client fallback
├── ios-native/             # iOS ON-DEVICE app (Swift, Apple Foundation Models, iOS 26+)
│   └── Sources/PolarisStudyKit/   # the 6 areas, on-device (mirrors study_llm)
├── local llm model to use for studying offline/   # component 1 docs + runners + Modelfile
├── study local notes with vector db/              # component 2 docs + sample notes + runners
└── fitness agents for use/                        # component 3 docs + agent mds + sample data
    ├── agent mds/          # markdown agent definitions
    └── core programs/      # runnable entry scripts
```

## Documentation map

| Doc | What's in it |
|-----|--------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, why the layout, each component's LangGraph topology. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Setup, conventions, how to add an area / agent / file format. |
| [ROADMAP.md](ROADMAP.md) | Status of each component and what's next. |
| [install/README.md](install/README.md) | Per-platform install + the support matrix. |
| [ios-native/README.md](ios-native/README.md) | On-device iOS via Foundation Models (+ MLX / MLC / llama.cpp options). |

## Status

Scaffolded and verified: all packages install (`pip install -e .`), 5 smoke tests pass, ruff
clean, and all three graphs run end-to-end. Live LLM output needs Ollama running
(`ollama serve` + the two models). See [ROADMAP.md](ROADMAP.md) for what's stubbed vs. complete.
