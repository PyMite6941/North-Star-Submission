# North Star ⭐ (Polaris)

**Offline-first, local-LLM agents for studying and fitness — built on [LangGraph](https://langchain-ai.github.io/langgraph/) + [Ollama](https://ollama.com).**

> **North Star Challenge judges:** start with [SUBMISSION.md](SUBMISSION.md) — the
> problem brief, track (Access & Equity), evidence of traction, and AI-usage note, mapped
> to the published rubric.

North Star (Polaris Student) is a privacy-preserving, offline-first study & fitness platform.
The AI parts run on a local LLM through Ollama (or a free cloud model); the everyday tools run
on **classical algorithms** so they work instantly, offline, and free — including on the native
mobile apps, which are **fully AI-free**. It ships as a **web app** (React + Vite), a **CLI**, a
**FastAPI** service, and **native iOS + Android** kits.

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

## Core components (AI / LangGraph)

| # | Component | Folder | Library package | What it does |
|---|-----------|--------|-----------------|--------------|
| 1 | **Study LLM** | `local llm model to use for studying offline/` | `study_llm` | A local LLM that fulfils the **6 areas of Polaris**: Flashcard Creation, Quizzing, CV Builder, Advisor, Citation Generator, Essay Helper. A LangGraph router classifies the request and dispatches it to the matching area. Also has **Study Packs** and **Group Quiz** for studying together offline (below). |
| 2 | **Study RAG** | `study local notes with vector db/` | `study_rag` | Ingests a user's notes into a local Chroma vector DB and answers study questions with **retrieval-augmented, cited** responses — accurate, works offline. |
| 3 | **Fitness Agents** | `fitness agents for use/` | `fitness_agents` | Parses uploaded fitness files (`.fit`, `.tcx`, `.gpx`, `.csv`, `.json`), computes metrics, and runs **markdown-defined agents** to analyze progress and produce a personalized growth plan. |
| 4 | **College Planner** | `packages/college_planner/` | `college_planner` | An offline college-application tracker (deadlines, status, notes) and a 4-year course/credit map, stored locally — no account needed. Deadlines export to `.ics` for any calendar app. |

> Agent prompts for the fitness pipeline live as markdown in `fitness agents for use/agent mds/`
> — edit a file to change an agent, no code change required.

## Student-life tools (algorithm-backed, offline-capable)

| Tool | Package | What it does |
|------|---------|--------------|
| **Recall** | `recall` | Free, Quizlet-style **SM-2 spaced repetition** — AI-generate decks or add your own, review exactly what's due. |
| **Writing** | `writing` | A grammar/style/clarity checker (wordiness, weasel words, passive voice, confusables) + Flesch–Kincaid readability + 0–100 score — **runs offline, no AI**. Plus **Polly** (online-only AI coach) that shows where to **fix and add** content, each with a reason, and can rewrite the whole piece. All free. |
| **Syllabus** | `syllabus` | Import a syllabus (PDF/DOCX/PPTX/MD) → extracted courses, assignments, and due dates. |
| **Planner** | `planner` | **Workload detection** (assignments bucketed by week, heavy-week flags) + an AI weekly study plan. |
| **Pomodoro** | `pomodoro` | Focus timer with a persistent streak and focus stats. |
| **Clubs** | `clubs` | Club hub — discover/create/join with semantic search. |
| **Assistant** | `assistant` | A free-API interpreter that reasons across everything in the vector store. |

Feature data lives in one local **Chroma** vector collection (`polaris_core/store.py`), with a
drop-in **Upstash Vector** managed backend for scale (`POLARIS_VECTOR_BACKEND=upstash`).

## Native mobile apps — algorithms, not AI

`ios-native/` (Swift) and `android-native/` (Kotlin) implement the study features with
**deterministic algorithms** — no on-device LLM, no model download, no network:

| Feature | Algorithm |
|---------|-----------|
| Flashcards | **SM-2** spaced repetition + cloze/definition generation |
| Quizzing | MCQ generation + **Levenshtein** grading + **Leitner** boxes |
| Citations | Rule-table formatter (APA / MLA / Chicago) |
| Essay / Writing | **Flesch–Kincaid** readability + rule-based grammar/style checker |
| CV Builder | Template rendering |
| Advisor | Rule-based deadline + spacing scheduler |

The only online feature is **Polly** (the AI writing coach), which the apps call only when
connected. See [`ios-native/README.md`](ios-native/README.md) / [`android-native/README.md`](android-native/README.md).

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
| **Android — native app** | Kotlin study kit — see [`android-native/`](android-native) (**algorithms, any device, no AI**) |
| **iOS — native app** | Swift study kit — see [`ios-native/`](ios-native) (**algorithms, iOS 15+, no AI**) |
| **Web** | Deployed on Vercel; or `cd frontend && npm run dev` — see [`frontend/README.md`](frontend/README.md) |

Each desktop installer sets up Python + the venv, installs the project, copies `.env`, and
installs Ollama + pulls the models. See [`install/README.md`](install/README.md) for the full
platform support matrix and per-OS details.

**Platform notes:**
- **Windows / macOS / Linux** — full local LLM via Ollama, no API keys. Set
  `POLARIS_LOW_POWER=true` / `POLARIS_SAVE_MEMORY=true` in `.env` on an older machine to trade
  quality for less CPU/battery/RAM.
- **Android & iOS** — the native kits (`android-native/` Kotlin, `ios-native/` Swift) implement
  the study features with **classical algorithms, not AI** (SM-2, Levenshtein, Flesch–Kincaid,
  rule-table citations). No model download, no network, runs on **any** device. The only online
  feature is **Polly** (the AI writing coach), which the app calls only when connected.
- **Web** — the React app is live on Vercel and talks to the Cloud Run backend (see
  [DEPLOY.md](DEPLOY.md)).

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
│   ├── polaris_core/       # shared: config, LLM, embeddings, vector store, documents, the 6 areas
│   ├── study_llm/          # Study LLM: graph + flashcards + quiz + CV + CLI
│   ├── study_rag/          # Study RAG: graph + ingest (pdf/docx/pptx) + CLI
│   ├── fitness_agents/     # Fitness: graph + parsers + metrics + history + schedule + CLI
│   ├── college_planner/    # College tracker: SQLite storage + .ics export + CLI
│   ├── recall/             # SM-2 spaced repetition (decks/cards/review)
│   ├── writing/            # writing checker (rules, offline) + Polly AI coach (online)
│   ├── syllabus/           # syllabus import → courses/assignments
│   ├── planner/            # workload detection + AI weekly plan
│   ├── pomodoro/ clubs/    # focus stats/streak · club hub
│   ├── assistant/          # free-API interpreter over the vector store
│   ├── polaris_cli/        # unified `polaris` command
│   └── polaris_api/        # FastAPI service ([serve] extra) — mounts every feature router
├── frontend/               # React + Vite web app (deployed to Vercel)
├── webui/                  # Streamlit web UI ([ui] extra)
├── tests/                  # tests (run without Ollama)
├── docs/ · .github/workflows/   # docs · CI (ruff+pytest 3.11-3.13 + Android Gradle + iOS Swift)
├── install/                # cross-platform installers + support matrix
├── Dockerfile · DEPLOY.md  # Cloud Run backend (fastembed + Groq) + deploy guide
├── ios-native/             # iOS app (Swift) — ALGORITHMS, not AI (SM-2, Levenshtein, Flesch…)
├── android-native/         # Android app (Kotlin) — ALGORITHMS, not AI
├── local llm model to use for studying offline/   # Study LLM docs + runners + Modelfile
├── study local notes with vector db/              # Study RAG docs + sample notes + runners
└── fitness agents for use/                        # Fitness docs + agent mds + sample data
```

## Documentation map

| Doc | What's in it |
|-----|--------------|
| [SUBMISSION.md](SUBMISSION.md) | North Star Challenge problem brief, track, traction, and AI-usage note. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, why the layout, each component's LangGraph topology. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Setup, conventions, how to add an area / agent / file format. |
| [ROADMAP.md](ROADMAP.md) | Status of each feature and what's next. |
| [DEPLOY.md](DEPLOY.md) | Live deployment — Cloud Run backend (fastembed + Groq, GCS-backed store) + Vercel frontend. |
| [THEME.md](THEME.md) | Brand tokens (colors/fonts) matched to polarisstudent.com. |
| [install/README.md](install/README.md) | Per-platform install + the support matrix. |
| [frontend/README.md](frontend/README.md) | The React + Vite web app. |
| [ios-native/README.md](ios-native/README.md) | iOS study kit — the classical algorithms (no AI). |
| [android-native/README.md](android-native/README.md) | Android study kit — the classical algorithms (no AI). |
| [docs/discord-announcements-sync.md](docs/discord-announcements-sync.md) | Pull the official Polaris Student `#announcements` channel into Study RAG — read-only, one-way, and exactly what has to be set up on the Discord side first. |
| [docs/polly-persona-prompt.md](docs/polly-persona-prompt.md) | Candidate system prompt for the Polly Bot AI study companion persona, plus a `scripts/polly_persona_chat.py` harness for testing it against Groq. |

## Status

**Deployed and live**: frontend on **Vercel** (public), backend on **Google Cloud Run**
(fastembed embeddings + free Groq chat, GCS-backed persistent vector store) — see
[DEPLOY.md](DEPLOY.md). Frontend auto-deploys on push via GitHub Actions.

Verified: all packages install (`pip install -e .`), **37 tests pass**, ruff clean, and the
LangGraph pipelines run end-to-end. **CI is green on every push** — Python (3.11–3.13),
Android (Gradle, incl. the Kotlin algorithm tests), and iOS (Swift). The native mobile kits are
**AI-free** (classical algorithms). Live desktop LLM output needs Ollama running; the deployed
backend uses the free Groq fallback (set `GROQ_API_KEY` for chat). See [ROADMAP.md](ROADMAP.md).
