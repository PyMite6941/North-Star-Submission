# North Star Challenge — Submission Brief

**Track:** Access & Equity — *"The student with no tutor, no counselor, no Wi-Fi at home."*
**Entry type:** Solo.

This doc is the problem brief + AI-usage note the Challenge asks for. It maps directly to
the published rubric so a judge can find each criterion without hunting through the code.

## The problem (who it hurts, how often, why it matters)

Most of the tools students are told to use for studying — AI tutors, flashcard apps, essay
helpers, even Polaris Student itself — are cloud services. They need a live internet
connection and, usually, an account. That's a fine default for a student with home
broadband and a laptop. It's a wall for the student who:

- doesn't have reliable Wi-Fi at home and only gets connected time at school or a library,
- shares one family device and can't count on always-on data,
- can't afford (or whose family can't afford) a private tutor or test-prep subscription,
- is wary of putting their essays, grades, or personal details into a cloud account.

That student still has the same homework, the same college applications, and the same
need for a study partner at 9pm on a Tuesday with no signal. Every time the only answer is
"use this web app," they're the one left out — which is exactly the student the Access &
Equity track calls out.

## The solution, and why a student team can actually build & run it

North Star (Polaris) is four small, offline helpers that run entirely on a student's
own device through [Ollama](https://ollama.com) — no account, no API key, no internet
after setup:

1. **Study LLM** — the 6 areas: Flashcard Creation, Quizzing, CV Builder, Advisor, Citation
   Generator, Essay Helper. One local model, routed by a small LangGraph classifier. Also
   includes **Study Packs** (bundle decks into one portable file for a group to share with
   no server) and **Group Quiz** (pass-the-device multiplayer with a leaderboard) — built
   for a study group in one room with no internet and often one shared device.
2. **Study RAG** — point it at your own notes folder; it answers questions from *your*
   material with cited sources, entirely from a local vector DB (Chroma) — no upload, no
   cloud retrieval.
3. **Fitness Agents** — a bonus component (progress tracking / growth plans from workout
   files), included because "Wellbeing & Motivation" and "Learning & Focus" both touch the
   same student, but not the focus of this track entry.
4. **College Planner** — an offline college-application tracker (deadlines, status, notes)
   and a 4-year course/credit map, in a local file — the exact "Course Map" / "College
   List" job a cloud platform does, done with no account and no connectivity required.

It's feasible for a solo student build because every piece is a thin, well-scoped layer
over existing free tools (Ollama for the model, LangGraph for orchestration, Chroma for
retrieval, plain SQLite for local records) rather than new infrastructure — see
[ARCHITECTURE.md](ARCHITECTURE.md).

## Traction / evidence it works

This isn't a slide — it's a working prototype with tests that don't need a model running
to verify the scaffolding:

- One-command installers for Windows, macOS/Linux, Android (Termux), and a native iOS
  package (Apple Foundation Models) — see [`install/`](install/) and
  [`ios-native/`](ios-native).
- 24 automated tests (`pytest`, CI on 3.11/3.12/3.13 — see
  [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) covering config, the 6 areas,
  file parsing, exports, Study Packs, and College Planner storage — none require a live
  model.
- Every export is a format usable with or without North Star installed on the other end:
  flashcards → Anki `.apkg` or CSV
  ([`flashcards.py`](packages/study_llm/flashcards.py)), a résumé → PDF or Markdown
  ([`cv.py`](packages/study_llm/cv.py)), a quiz → a printable Markdown handout
  ([`quiz.py`](packages/study_llm/quiz.py)), college deadlines → `.ics` for any calendar
  app ([`calendar_export.py`](packages/college_planner/calendar_export.py)).
- A Streamlit web UI and a FastAPI service so the same graphs are usable from a browser or
  another app, not just a terminal.

## Impact & equity — who it helps, and why it reaches students who are usually left out

The entire design constraint is **works with zero ongoing cost and zero connectivity**:
once installed, nothing here calls out to the internet or an account. That means it
reaches the student a cloud-only tool structurally can't:

- No recurring cost — no subscription, no per-token API bill.
- No account/login, so no data leaves the device by default (cloud fallback is
  admin-gated and off unless a family explicitly opts in — see `ROADMAP.md`).
- Works at school-issued-Chromebook-with-no-data-plan levels of connectivity, once set up
  on any Wi-Fi (library, school lab) the student passes through.
- Complements, rather than competes with, cloud platforms like Polaris Student itself:
  those are excellent for tracking grades/deadlines/college lists across devices, but they
  assume connectivity. College Planner does the same deadline/course-map job entirely
  offline, so a student isn't blocked the moment that assumption breaks.
- Built for groups, not just individuals: Study Packs and Group Quiz assume the realistic
  case for an under-resourced student — studying with friends off one shared device,
  because a laptop or data plan per person isn't a given.

## How we used AI

Built with **Claude Code** (Anthropic's CLI coding agent) as a pair-programmer for the
full engineering pass — architecture, the LangGraph graphs, the CLI/API/web surfaces, the
test suite, and this brief. Every change was directed, reviewed, and run by the student
author; the product idea, the track/problem framing, and the choice to go offline-first
are the student's own.
