# Roadmap

Status legend: ✅ done · 🚧 scaffolded (stub logic, ready to flesh out) · ⬜ planned

## Foundation
- ✅ Monorepo layout, single editable install, `.env.example`, docs
- ✅ `polaris_core`: typed config, Ollama LLM factory + health check, embeddings, memory
- ✅ The 6 Polaris areas registry

## Component 1 — Study LLM
- ✅ Router graph + 6 area nodes (Flashcards, Quizzing, CV Builder, Advisor, Citation, Essay)
- ✅ `--area` override to pin an area and skip the router
- ✅ Structured flashcard deck (typed output) + Anki-importable CSV export (`flashcards`)
- ✅ Interactive quiz mode — generate → answer → LLM-graded feedback (`quiz`)
- ✅ Token streaming in `ask` / `chat`
- ✅ Structured CV Builder — typed sections (contact/summary/experience/education/skills/
  projects) + Markdown export (`cv`)
- ⬜ CV export to PDF, Anki `.apkg`
- ⬜ Packaging as a downloadable desktop app (the brief's "apps that can be downloaded")

## Component 2 — Study RAG
- ✅ Ingest pipeline (load → split → embed → Chroma) + corrective-RAG query graph
- ✅ `--show-sources` (cited chunk list), `stats`, and `reset` commands
- ✅ PDF / DOCX / PPTX loaders (beyond Markdown/txt)
- ✅ Incremental ingest — content-hash dedupe/upsert (skips unchanged, re-indexes changed)
- ⬜ Citation spans + source highlighting in answers
- ⬜ Per-subject collections

## Component 3 — Fitness Agents
- ✅ Parsers (.fit/.tcx/.gpx/.csv/.json) → `ActivityRecord`, metrics, 4 markdown agents
- ✅ HR zone distribution + training-load metric; `--save` Markdown report export
- ✅ Athlete profile (age / resting / max HR) → true %HRmax zones + HRR-based load
- ✅ Progress tracking — SQLite history + CTL/ATL/TSB trends (`log`, `trend`, `history`)
- ✅ Structured weekly schedule → `.ics` calendar export (`schedule`)
- ⬜ Power zones, VO2 trend, richer PR tracking

## Cross-cutting
- ✅ Unified `polaris` CLI (mounts study / rag / fitness + `doctor`, `version`, `serve`)
- ✅ Model-tag auto-resolution (bare `llama3.2` → installed `llama3.2:3b`)
- ✅ UTF-8-safe output on Windows (CLIs + runner scripts)
- ✅ FastAPI service layer (`[serve]` extra) exposing all three graphs
- ✅ Streamlit web UI (`[ui]` extra) — single front-end for all three, with an admin-only
  sidebar (resolved settings + a gated cloud-fallback toggle)
- ✅ `polaris config show` — inspect resolved settings (secrets masked)
- ✅ Fail-fast settings validation (`POLARIS_EMBED_BACKEND` typos reject at startup)
- ✅ `POLARIS_UNITS` (metric/imperial) for fitness output
- ✅ `POLARIS_ALLOW_CLOUD_FALLBACK` admin switch — a configured key alone no longer enables cloud use
- ✅ GitHub Actions CI (ruff + pytest on 3.11/3.12/3.13)
- ⬜ Expanded test suite with mocked LLM + Ollama integration tests
- ⬜ Packaged release artifacts
