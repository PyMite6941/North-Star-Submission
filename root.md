# North Star ⭐ (Polaris) — project spec & status

Offline-first, local-LLM apps for studying and fitness, built on **LangGraph + Ollama**.
Everything runs on the user's own device with no API keys required.

> This is the canonical spec. For setup/usage see [README.md](README.md); for design see
> [ARCHITECTURE.md](ARCHITECTURE.md); for what's done vs. planned see [ROADMAP.md](ROADMAP.md).

## Features of this project

- **Local LLM Model** using Ollama that runs on any device when installed, to fulfil the
  6 areas of Polaris (below). **Aimed at apps that can be downloaded.**
  → implemented as `study_llm` (a LangGraph router → area handler).

- **Local RAG Study Agents** parse a vector DB to get accurate data for studying, offline or
  online — higher study accuracy at the cost of some device storage. **Aimed at downloadable
  apps.** → implemented as `study_rag` (Chroma + corrective-RAG graph).

- **Fitness MD Agents** look at uploaded files and data types to analyze a user's fitness
  progress and create a growth plan for their physical growth.
  → implemented as `fitness_agents` (parsers → metrics → markdown-defined agents).

## 6 Areas

| Area | Status | Notes |
|------|:------:|-------|
| **Flashcard Creation** | ✅ | Also a structured deck + Anki-importable CSV export. |
| **Quizzing** | ✅ | Interactive quiz mode: generate → answer → LLM-graded feedback. |
| **CV Builder** | ✅ | Specialized prompt; structured section export planned. |
| **Advisor** | ✅ | Study/academic planning. |
| **Citation Generator** | ✅ | APA / MLA / Chicago. |
| **Essay Helper** | ✅ | Outline / draft / revise. |

A LangGraph router classifies each request into one of the six areas (or you can pin one
with `--area`).

## Implementation status

### Component 1 — Study LLM (`packages/study_llm`)
- 6-area router graph; `--area` override; token **streaming** in `ask`/`chat`.
- **Flashcards** → structured deck + Anki CSV (`flashcards`).
- **Quiz** → interactive, LLM-graded (`quiz`).
- Memory-backed chat (SQLite checkpointer).

### Component 2 — Study RAG (`packages/study_rag`)
- Ingest **.md / .txt / .rst / .pdf / .docx / .pptx** → chunk → embed → Chroma.
- **Incremental**: content-hash dedupe (skips unchanged, re-indexes changed).
- Corrective-RAG query graph (retrieve → grade → generate, with rewrite loop).
- `ask --show-sources`, `stats`, `reset`.

### Component 3 — Fitness Agents (`packages/fitness_agents`)
- Parsers: **.fit / .tcx / .gpx / .csv / .json** → `ActivityRecord`.
- Metrics: distance/pace/HR, **HR zones + training load**; athlete profile
  (`POLARIS_ATHLETE_AGE` / `_MAX_HR` / `_RESTING_HR`) → true %HRmax zones + HRR load.
- **Progress tracking**: SQLite history + CTL/ATL/TSB trends (`log`, `trend`, `history`).
- Markdown-defined agents (analyst → planner → reviewer); `analyze --save report.md --log`.
- **Structured weekly schedule → `.ics`** calendar (`schedule --export-ics`).

### Student-life tools + Writing
- **Recall** (`recall`) — SM-2 spaced repetition; **Syllabus** import → courses/assignments;
  **Planner** — workload detection + AI weekly plan; **Pomodoro**, **Clubs**, **Assistant**.
- **Writing** (`writing`) — offline grammar/style/clarity checker + readability + score, plus
  **Polly**, the **online-only** AI coach that shows where to fix *and add* content (with reasons)
  and rewrites. All free.
- Shared **Chroma** vector store (`polaris_core/store.py`); drop-in **Upstash Vector** backend.

### College Planner (`college_planner`)
- Offline application tracker + 4-year course/credit map (local SQLite); deadlines → `.ics`.

### Cross-cutting
- Shared core `polaris_core` (config, LLM factory + health check + model-tag resolution,
  embeddings, vector store, the 6 areas, UTF-8-safe console).
- Unified **`polaris`** CLI + **FastAPI** service (`polaris_api`) + **Streamlit** UI + a
  **React + Vite** web app (`frontend/`).
- **GitHub Actions CI** (ruff + pytest 3.11–3.13, Android Gradle, iOS Swift); 37 tests.
- **Deployed**: frontend on Vercel, backend on Cloud Run (fastembed + free Groq, GCS store).
- Cloud fallback optional (`POLARIS_ALLOW_CLOUD_FALLBACK` + a key); default is fully local.

## Platforms (downloadable-app goal)

| Platform | Study features | How |
|----------|:---:|-----|
| Windows / macOS / Linux | ✅ full (AI + tools) | `install/` scripts (Python venv + Ollama), or the web app. |
| Android | ✅ native | `android-native/` (Kotlin) — **classical algorithms, no AI, any device**. |
| iOS / iPadOS | ✅ native | `ios-native/` (Swift) — **classical algorithms, no AI, iOS 15+**. |
| Web | ✅ deployed | React + Vite on Vercel → Cloud Run backend. |

See [install/README.md](install/README.md) for the full support matrix.
