# Roadmap

Status legend: ✅ done · 🚧 scaffolded (stub logic, ready to flesh out) · ⬜ planned

## On-device LLM everywhere + power modes + Discord sync

- ✅ Global `POLARIS_LOW_POWER` / `POLARIS_SAVE_MEMORY` settings — swap to a smaller model
  and/or shrink the context window + capped output tokens on constrained devices
- ⬜ `android-native/` — on-device Android package (MediaPipe LLM Inference, mirrors
  `ios-native/`'s role), with its own low-power/save-memory config
- ⬜ CI builds `android-native/` (Gradle) and `ios-native/` (Swift) alongside the Python
  ruff+pytest matrix, so a broken mobile build fails the same way a broken Python change
  does
- ✅ **Discord announcements sync** — read-only, one-way pull of the official Polaris
  Student `#announcements` channel into Study RAG (`polaris rag sync-discord`); see
  [docs/discord-announcements-sync.md](docs/discord-announcements-sync.md) for the
  (Discord-side, admin-only) setup this depends on
- ⬜ On-device RAG for Android (mirrors the iOS roadmap item below)

## Group study + college planning + portable exports

Ties directly to the Access & Equity pitch in [SUBMISSION.md](SUBMISSION.md): a group of
students studying together with no internet, and a student tracking college applications
without a cloud account.

- ✅ Flashcards: Anki `.apkg` export (direct double-click import, no CSV step)
- ✅ CV Builder: PDF export (uploadable to any college/job portal, no Markdown viewer needed)
- ✅ Quiz: printable Markdown export (questions + answer key) as a group-study handout
- ✅ **Study Pack** — bundle decks + quizzes + notes into one portable JSON file a group
  can share by USB / AirDrop / email / messaging app, no server or account (`pack create` /
  `pack import`)
- ✅ **Group Quiz** — pass-the-device multiplayer: each named player answers the same
  quiz, individually graded, leaderboard at the end (`group-quiz`)
- ✅ **College Planner** (new component) — offline college-application tracker (deadlines,
  status, notes) + a 4-year course/credit map, with deadlines exportable to `.ics` so they
  show up in any calendar app
- ⬜ Study Pack: merge two members' packs into one without duplicate decks
- ⬜ College Planner: application-task checklists per college (not just status)

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
  projects) + Markdown/PDF export (`cv`)
- ✅ Offline Study Packs (`pack create`/`pack import`) + Group Quiz (`group-quiz`)
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

## Component 4 — College Planner
- ✅ Offline application tracker (college, deadline, type, status, notes) + a 4-year
  course/credit map, both in a local SQLite file (no account)
- ✅ Deadlines → `.ics` export (works in any calendar app)
- ⬜ Per-college application-task checklists
- ⬜ Import a course list from a transcript/CSV

## Cross-cutting
- ✅ Unified `polaris` CLI (mounts study / rag / fitness / college + `doctor`, `version`, `serve`)
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
