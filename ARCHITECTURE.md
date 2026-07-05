# Architecture

North Star is a **monorepo of three LangGraph applications** sharing one core library.
Design goals, in order: **offline-first**, **robust** (typed config, health checks,
graceful failover), and **easy to extend** (add an agent = add a file).

## Why this layout

Python packages cannot have spaces in their import names, but the brief uses descriptive
folder names with spaces (`fitness agents for use/`, etc.). To get both clean imports and
the descriptive structure, we split concerns:

- **`packages/`** — all importable library code, in space-free package dirs. One editable
  install (`pip install -e .`) exposes `polaris_core`, `study_llm`, `study_rag`,
  `fitness_agents` everywhere, and registers the `polaris-*` CLI entry points.
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

### 2. Study RAG — `study_rag`
A **corrective-RAG** topology for accuracy.

```
ingest (offline, one-time):  load → split → embed → Chroma
query:  START → retrieve → grade_docs → generate (cited) → END
                              └─ (if weak) → rewrite_query → retrieve
```
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

## Interfaces (CLI / API / UI)

The graphs are the single source of truth; every interface is a thin wrapper over them:
- **`polaris_cli`** — the unified `polaris` command mounts each component's Typer app
  (`study` / `rag` / `fitness`) plus `doctor`, `version`, `serve`.
- **`polaris_api`** — a FastAPI app (`[serve]` extra) exposing `/study`, `/rag`, `/fitness`,
  `/health`. Run with `polaris serve`.
- **`webui/app.py`** — a Streamlit UI (`[ui]` extra) calling the same package functions.

Because all three call the identical functions, behaviour is consistent across CLI, HTTP,
and UI.

## Data flow & persistence

- **Vector DB:** Chroma, embedded, on local disk — no server.
- **Conversation memory:** LangGraph SQLite checkpointer (`.data/checkpoints.sqlite`).
- **User uploads:** kept under `uploads/` (git-ignored); only `sample_*` data is committed.

## Failover & robustness

- `check_ollama()` runs before graph execution; CLIs print actionable guidance if the
  daemon or a model is missing.
- If `GROQ_API_KEY` / `OPENROUTER_API_KEY` are set, `get_chat_model(allow_cloud=True)`
  can fall back to a hosted free model when Ollama is unreachable. Default is **local-only**.
- All config is typed and validated at startup (pydantic), so misconfiguration fails fast
  with a clear message rather than deep in a graph run.
