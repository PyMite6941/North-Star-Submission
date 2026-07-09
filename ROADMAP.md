# Roadmap

Status legend: ✅ done · 🚧 scaffolded (stub logic, ready to flesh out) · ⬜ planned

## Native mobile — classical algorithms, not AI

- ✅ Both native kits (`ios-native/` Swift, `android-native/` Kotlin) implement every study
  feature with **deterministic algorithms** — no on-device LLM, no model download, no network,
  no Apple-Intelligence requirement. Instant, private, and free on any device.
- ✅ Flashcards **SM-2** · Quizzing **Levenshtein** grading + **Leitner** · Citations rule-table
  (APA/MLA/Chicago) · Essay/Writing **Flesch–Kincaid** + rule-based checker · CV template ·
  Advisor rule-based scheduler
- ✅ Offline **WritingChecker** on both platforms; the AI coach **Polly** is called only when online
- ✅ CI builds `android-native/` (Gradle, incl. Kotlin algorithm tests) and `ios-native/` (Swift)
  alongside the Python ruff+pytest matrix, so a broken mobile build fails like a Python change does
- ✅ **Discord announcements sync** — read-only, one-way pull of the official Polaris
  Student `#announcements` channel into Study RAG; see
  [docs/discord-announcements-sync.md](docs/discord-announcements-sync.md)
- ⬜ On-device RAG (semantic notes search) for Android + iOS

## Student-life tools (algorithm-backed + optional AI)

- ✅ **Recall** — SM-2 spaced repetition (decks/cards/review), AI-generated or manual decks
- ✅ **Writing** — offline rule checker (grammar/style/clarity + readability + score) **+ Polly**,
  the online-only AI coach that shows where to **fix and add** content with reasons + full rewrite
- ✅ **Syllabus** import (PDF/DOCX/PPTX) → courses/assignments in the vector store
- ✅ **Planner** — workload detection (heavy-week flags) + AI weekly plan
- ✅ **Pomodoro** (focus stats/streak) · **Clubs** hub (semantic search) · **Assistant** interpreter
- ✅ Shared **Chroma** vector store (`polaris_core/store.py`) + drop-in **Upstash Vector** backend
- ⬜ Notes/notifications sync across devices

## Web app + deployment

- ✅ **React + Vite** web app (`frontend/`) — lazy-code-split pages for every feature, themed to
  polarisstudent.com, with offline detection (`useOnline`) that gates Polly
- ✅ **Deployed**: frontend on **Vercel** (public), backend on **Cloud Run** (fastembed + Groq,
  GCS-backed persistent store); frontend **auto-deploys on push** via GitHub Actions
- ⬜ Custom domain + backend behind it

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
- ✅ FastAPI service layer (`[serve]` extra) — mounts every feature router (study, rag, fitness,
  recall, writing, syllabus, planner, pomodoro, clubs, assistant)
- ✅ Streamlit web UI (`[ui]` extra) — admin sidebar with resolved settings + gated cloud toggle
- ✅ `polaris config show` — inspect resolved settings (secrets masked)
- ✅ Fail-fast settings validation (`POLARIS_EMBED_BACKEND` typos reject at startup)
- ✅ `POLARIS_UNITS` (metric/imperial) for fitness output
- ✅ `POLARIS_ALLOW_CLOUD_FALLBACK` admin switch — a configured key alone no longer enables cloud use
- ✅ GitHub Actions CI (ruff + pytest on 3.11/3.12/3.13)
- ⬜ Expanded test suite with mocked LLM + Ollama integration tests
- ⬜ Packaged release artifacts
