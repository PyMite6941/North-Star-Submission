# Architecture

North Star is a **monorepo of three LangGraph applications plus one plain local-storage
component** (College Planner), sharing one core library. Design goals, in order:
**offline-first**, **robust** (typed config, health checks, graceful failover), and
**easy to extend** (add an agent = add a file).

## Why this layout

Python packages cannot have spaces in their import names, but the brief uses descriptive
folder names with spaces (`fitness agents for use/`, etc.). To get both clean imports and
the descriptive structure, we split concerns:

- **`packages/`** — all importable library code, in space-free package dirs. One editable
  install (`pip install -e .`) exposes `polaris_core`, `study_llm`, `study_rag`,
  `fitness_agents`, `college_planner` everywhere, and registers the `polaris-*` CLI
  entry points.
- **The spaced component folders** — documentation, runnable entry scripts, agent
  markdown, and sample/seed data. These import from the installed packages.

This is a conventional `src`-style layout (`where = ["packages"]` in `pyproject.toml`)
and avoids every spaced-path import headache on Windows.

## Shared core — `polaris_core`

| Module | Responsibility |
|--------|----------------|
| `config.py` | `Settings` (pydantic-settings) loaded from `.env` — the single source of truth. |
| `polaris.py` | The **6 areas** registry (`PolarisArea` enum + metadata) used by `study_llm`. |
| `llm.py` | `get_chat_model()` — builds a `ChatOllama`, plus `check_ollama()` health probe and optional cloud failover. |
| `embeddings.py` | `get_embeddings()` — Ollama embeddings by default, fastembed (ONNX) fallback. |
| `memory.py` | LangGraph SQLite checkpointer factory for resumable, persistent runs. |
| `logging.py` | Rich-backed structured logging configured from `POLARIS_LOG_LEVEL`. |
| `console.py` | Shared Rich console; forces UTF-8 stdout so Windows (cp1252) never crashes. |

`llm.py` also resolves a requested model to an installed tag (bare `llama3.2` →
`llama3.2:3b`). Every component depends only on `polaris_core` — never on each other.

## Component graphs (LangGraph)

All three are compiled `StateGraph`s with typed `TypedDict` state and a checkpointer, so
runs are resumable and conversations persist by `thread_id`.

### 1. Study LLM — `study_llm`
A **router → area-handler** topology.

```
START → route (classify into one of 6 areas) → <area node> → END
areas: flashcards | quizzing | cv_builder | advisor | citation | essay
```
`route` uses the LLM (structured output) to pick the area; each area node owns a focused
system prompt. Adding a 7th area = add an enum member + a node.

`study_llm` also has two group-study modules that sit beside the graph rather than in it
(no routing needed — they call `flashcards.generate_deck` / `quiz.generate_quiz` directly):
`groups.py` (`StudyPack` — bundle decks/quizzes into one portable JSON file; `PlayerResult`
+ `leaderboard()` for pass-the-device Group Quiz scoring).

### 2. Study RAG — `study_rag`
A **corrective-RAG** topology for accuracy.

```
ingest (offline, one-time):  load → split → embed → Chroma
query:  START → retrieve → grade_docs → generate (cited) → END
                              └─ (if weak) → rewrite_query → retrieve
```

`study_rag` also has `discord_sync.py` — a read-only, one-way pull of a single Discord
channel's messages (via the official REST API, a scoped bot token) into a Markdown note
that feeds straight into the same ingest pipeline. Not part of the query graph; it's a
separate, occasional "add a source" step. See
[docs/discord-announcements-sync.md](docs/discord-announcements-sync.md).
Chroma persists to disk (`.data/chroma`), so retrieval works fully offline once ingested.
Ingestion reads `.md/.txt/.rst/.pdf/.docx/.pptx` and is **incremental**: each file's content
is hashed, so re-ingesting skips unchanged files and upserts (re-indexes) changed ones.

### 3. Fitness Agents — `fitness_agents`
A **pipeline of markdown-defined agents**.

```
START → parse_files → compute_metrics → analyze (agent) → plan (agent) → review (agent) → END
```
Agent system prompts are markdown files in `fitness agents for use/agent mds/`, loaded at
runtime by `agents.py`. Parsers (`parsers.py`) normalize `.fit/.tcx/.gpx/.csv/.json` into a
common `ActivityRecord` schema; `metrics.py` computes distance/pace/HR-zone/load summaries
that ground the agents in real numbers.

Two extra fitness modules build on this:
- `history.py` — a SQLite session store; `compute_trends()` derives CTL/ATL/TSB
  (fitness/fatigue/form) and PRs, which the analyst node reads for progress context.
- `schedule.py` — structured-output weekly plan (`WeeklySchedule`) with `.ics` export.

### 4. College Planner — `college_planner`

No LLM, no graph — plain typed records over local SQLite, the same pattern as the
Fitness Agents history:

```
models.py (CollegeEntry, CourseEntry)  →  storage.py (SQLite CRUD)  →  cli.py
                                        →  calendar_export.py (deadlines → .ics)
```

`storage.py` mirrors `fitness_agents/history.py`'s connection pattern (one SQLite file at
`POLARIS_COLLEGE_DB`, row-factory dicts mapped back to pydantic models).
`calendar_export.py` writes the same hand-rolled RFC 5545 text as
`fitness_agents/schedule.py`'s `.ics` export, duplicated rather than shared to keep every
component depending only on `polaris_core`.

### Student-life features (vector-store-backed) — `syllabus`, `planner`, `pomodoro`, `clubs`, `recall`

These newer packages share one Chroma collection (`POLARIS_APP_COLLECTION`) via
`polaris_core/store.py`, storing each item as an embedded document with structured metadata
(dates, weights, SM-2 state). This gives every feature semantic search *and* exact
metadata filtering, and lets the free-API interpreter reason across all of them.

## Interfaces (CLI / API / UI)

The graphs and services are the single source of truth; every interface is a thin wrapper:
- **`polaris_cli`** — the unified `polaris` command mounts each component's Typer app
  (`study` / `rag` / `fitness` / `college`) plus `doctor`, `version`, `serve`.
- **`polaris_api`** — a FastAPI app (`[serve]` extra) exposing `/study`, `/rag`, `/fitness`,
  the student-life feature routers, and `/health`. Run with `polaris serve`.
- **`webui/app.py`** — a Streamlit UI (`[ui]` extra); **`frontend/`** — a React + Vite site,
  both calling the same package functions / API.

Because every interface calls the identical functions, behaviour is consistent across CLI,
HTTP, and UI.

## Data flow & persistence

- **Vector DB:** Chroma, embedded, on local disk — no server.
- **Conversation memory:** LangGraph SQLite checkpointer (`.data/checkpoints.sqlite`).
- **Fitness / college history:** each its own local SQLite file (`.data/fitness.sqlite`,
  `.data/college.sqlite`) — no shared server, no sync.
- **Study Packs:** a single portable JSON file (no DB) — the whole point is that it's one
  file a group can pass around.
- **User uploads:** kept under `uploads/` (git-ignored); only `sample_*` data is committed.

## Failover & robustness

- `check_ollama()` runs before graph execution; CLIs print actionable guidance if the
  daemon or a model is missing.
- If `GROQ_API_KEY` / `OPENROUTER_API_KEY` are set, `get_chat_model(allow_cloud=True)`
  can fall back to a hosted free model when Ollama is unreachable. Default is **local-only**.
- All config is typed and validated at startup (pydantic), so misconfiguration fails fast
  with a clear message rather than deep in a graph run.
- `POLARIS_LOW_POWER` / `POLARIS_SAVE_MEMORY` (`polaris_core/llm.py`'s
  `_effective_model_and_options`) trade quality for less CPU/battery/RAM on constrained
  devices: low power swaps in a smaller chat model, save memory shrinks the context
  window and caps generated tokens. Both are opt-in and off by default.
