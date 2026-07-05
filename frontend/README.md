# Polaris Student — web front-end (React + Vite)

A single-page React app that puts **all three Polaris components** on one branded site,
styled to match [polarisstudent.com](https://polarisstudent.com) (see [../THEME.md](../THEME.md)).
It talks to the Polaris **FastAPI backend** (`polaris_api`).

## Pages

- **Home** — branded landing (constellation hero, feature cards).
- **Study** — ask across the 6 areas (auto-routed or pinned), flashcard decks (+ CSV export),
  and quizzes (with reveal).
- **Notes** — upload documents (.md/.txt/.pdf/.docx/.pptx) → cited RAG answers + collection stats.
- **Fitness** — upload activities → metrics, trends, AI growth plan; weekly schedule → `.ics` export.

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
