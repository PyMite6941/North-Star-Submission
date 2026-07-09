# Polaris Student — web front-end (React + Vite)

A single-page React app that puts **every Polaris feature** on one branded site, styled to match
[polarisstudent.com](https://polarisstudent.com) (see [../THEME.md](../THEME.md)). It talks to the
Polaris **FastAPI backend** (`polaris_api`); pages are lazy-code-split, and an `useOnline` hook
gates online-only features (Polly). **Deployed on Vercel** (auto-deploys on push to `master`).

## Pages

- **Home** — branded landing (constellation hero, feature cards).
- **Study** — ask across the 6 areas (auto-routed or pinned), flashcard decks (+ CSV export), quizzes.
- **Recall** — SM-2 spaced-repetition decks (AI-generate or manual) with a due-card review flow.
- **Writing** — offline grammar/style checker (issues + readability + score) **+ Polly**, the
  online AI coach (fix/add notes with reasons + rewrite); Polly disables when offline.
- **Notes** — upload documents (.md/.txt/.pdf/.docx/.pptx) → cited RAG answers + collection stats.
- **Planner** — import a syllabus → workload heatmap + AI weekly plan + the assistant.
- **Focus** — pomodoro timer with a persistent streak. **Clubs** — hub with semantic search.
- **Fitness** — upload activities → metrics, trends, AI growth plan; weekly schedule → `.ics`.

## Run it (two terminals)

```bash
# 1. Backend (from the repo root)
pip install -e ".[serve]"
polaris serve                 # → http://127.0.0.1:8000

# 2. Frontend (this folder)
cd frontend
npm install
npm run dev                   # → http://localhost:5173
```

The Vite dev server proxies `/api/*` → the backend (`http://127.0.0.1:8000` by default; override
with the `POLARIS_API` env var). Requires Ollama running (`ollama serve` + models) for real output.

## Build

```bash
npm run build                 # type-checks + bundles to dist/
npm run preview               # serve the production build
```

For a deployed backend, set `VITE_API_BASE` (e.g. `https://api.example.com`) at build time.

## Design tokens

Colors/fonts live in `src/theme.css`, mirroring the site's CSS variables (firebrick `#b22222`
→ orange `#f97316`, constellation navy, Plus Jakarta Sans + Inter). See [../THEME.md](../THEME.md).
