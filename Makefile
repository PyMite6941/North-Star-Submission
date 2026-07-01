# North Star (Polaris) — developer shortcuts.
# On Windows, run these targets with `make` (Git Bash) or run the commands
# directly. POSIX paths shown; adjust venv activation per shell.

PY ?= python
VENV ?= .venv

.PHONY: help venv install dev models lint test clean \
        study rag-ingest rag-ask fitness

help:
	@echo "Targets:"
	@echo "  venv        Create the virtual environment"
	@echo "  install     Editable install of the monorepo"
	@echo "  dev         Install with dev + serve + offline-embeddings extras"
	@echo "  models      Pull the default Ollama models"
	@echo "  lint        Ruff lint"
	@echo "  test        Run pytest"
	@echo "  study       Launch the study-LLM CLI (6 Polaris areas)"
	@echo "  rag-ingest  Ingest sample notes into the vector DB"
	@echo "  rag-ask     Ask the RAG study agent a question"
	@echo "  fitness     Run the fitness agent pipeline on a file"
	@echo "  clean       Remove caches and runtime data"

venv:
	$(PY) -m venv $(VENV)

install:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e .

dev:
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e ".[dev,serve,offline-embeddings]"

models:
	ollama pull llama3.2
	ollama pull nomic-embed-text

lint:
	ruff check packages

test:
	pytest

study:
	polaris-study chat

rag-ingest:
	polaris-rag ingest "study local notes with vector db/sample_notes"

rag-ask:
	polaris-rag ask "Explain the light-dependent reactions of photosynthesis."

fitness:
	polaris-fitness analyze --help

clean:
	rm -rf .data .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
