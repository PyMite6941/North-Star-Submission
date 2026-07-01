#!/usr/bin/env bash
# North Star (Polaris) installer for macOS and Linux.
# Sets up the full offline stack: Python venv, the monorepo, Ollama, and models.
# Idempotent — safe to re-run.
#
# Usage:
#   ./install/install.sh                       # defaults
#   CHAT_MODEL=qwen2.5:3b ./install/install.sh # override chat model
#   SKIP_MODELS=1 ./install/install.sh         # skip pulling models
set -euo pipefail

CHAT_MODEL="${CHAT_MODEL:-llama3.2}"
EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"
SKIP_MODELS="${SKIP_MODELS:-0}"

# --- Move to repo root (this script lives in install/) -----------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

OS="$(uname -s)"
echo "==> North Star installer ($OS)"
echo "    Repo: $REPO_ROOT"

have() { command -v "$1" >/dev/null 2>&1; }

# --- 1. Python ---------------------------------------------------------------
if ! have python3; then
    echo "==> Python 3 not found."
    if [ "$OS" = "Darwin" ] && have brew; then
        echo "    Installing via Homebrew..."
        brew install python
    else
        echo "    Install Python 3.11+ (https://www.python.org/ or your package manager) and re-run." >&2
        exit 1
    fi
fi
echo "==> Using $(python3 --version)"

# --- 2. Ollama ---------------------------------------------------------------
if ! have ollama; then
    echo "==> Ollama not found. Installing..."
    if [ "$OS" = "Darwin" ]; then
        if have brew; then
            brew install ollama
        else
            echo "    Install Ollama from https://ollama.com/download then re-run." >&2
        fi
    else
        # Linux official installer
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# Make sure a daemon is reachable (Linux: start in background if needed).
if have ollama && ! curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
    if [ "$OS" = "Linux" ]; then
        echo "==> Starting 'ollama serve' in the background..."
        (ollama serve >/tmp/ollama.log 2>&1 &) || true
        sleep 3
    fi
fi

# --- 3. Virtual environment + editable install -------------------------------
if [ ! -d .venv ]; then
    echo "==> Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
echo "==> Installing the project (editable)..."
python -m pip install -U pip
python -m pip install -e .

# --- 4. .env -----------------------------------------------------------------
if [ ! -f .env ]; then
    cp .env.example .env
    echo "==> Created .env from .env.example"
fi

# --- 5. Models ---------------------------------------------------------------
if [ "$SKIP_MODELS" != "1" ] && have ollama; then
    echo "==> Pulling Ollama models (this can take a while)..."
    ollama pull "$CHAT_MODEL" || echo "    (pull $CHAT_MODEL later; is 'ollama serve' running?)"
    ollama pull "$EMBED_MODEL" || echo "    (pull $EMBED_MODEL later)"
fi

echo ""
echo "==> Done!"
echo "    Activate:  source .venv/bin/activate"
echo "    Verify:    polaris-study doctor"
echo '    Try:       polaris-study ask "make flashcards on the Krebs cycle"'
