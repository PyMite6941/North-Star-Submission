# Contributing

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (POSIX: source .venv/bin/activate)
pip install -e ".[dev,serve,offline-embeddings]"
cp .env.example .env
```

Pull the local models once:

```bash
ollama serve
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Conventions

- **Packages live in `packages/`** (space-free names). Spaced folders hold docs, runners,
  agent markdown, and sample data only.
- **Each component depends only on `polaris_core`**, never on a sibling component.
- **Config goes through `polaris_core.config.Settings`** — read settings, don't call
  `os.getenv` scattered around.
- **Graphs are pure where possible:** nodes take state, return a partial state dict. Side
  effects (disk, network) live in clearly named helper modules.
- Type everything that crosses a module boundary. Run `ruff check packages` and `pytest`
  before opening a PR.

## Adding things

### A new study area (component 1)
1. Add a member to `PolarisArea` in `packages/polaris_core/polaris.py` with its metadata.
2. Add a handler node in `packages/study_llm/nodes.py` and wire it in `graph.py`.

### A new fitness agent (component 3)
1. Drop a markdown file in `fitness agents for use/agent mds/` (frontmatter + prompt body).
2. Reference it from a node in `packages/fitness_agents/graph.py` via `load_agent("name")`.

### A new file format (component 3)
Add a parser function in `packages/fitness_agents/parsers.py` returning `list[ActivityRecord]`
and register its extension in `PARSERS`.

## Tests

`pytest` lives in `tests/`. Unit tests should not require a running Ollama daemon — mock
`get_chat_model` / `get_embeddings`. Integration tests that need Ollama are marked and
skipped when the daemon is unreachable.
