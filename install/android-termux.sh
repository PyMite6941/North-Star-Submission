#!/data/data/com.termux/files/usr/bin/bash
# North Star (Polaris) installer for Android via Termux.
#
# Android can run the local LLM on-device through Termux, but phones are RAM- and
# CPU-limited, so this script defaults to SMALL models. Install Termux from
# F-Droid (https://f-droid.org/packages/com.termux/) — NOT the Play Store build.
#
# Usage (inside Termux):
#   pkg install git -y && git clone <repo> && cd "North Star Submission"
#   bash install/android-termux.sh
#
# Override models:  CHAT_MODEL=qwen2.5:0.5b bash install/android-termux.sh
set -euo pipefail

# Small defaults that fit typical phone RAM (4–8 GB).
CHAT_MODEL="${CHAT_MODEL:-qwen2.5:1.5b}"
EMBED_MODEL="${EMBED_MODEL:-all-minilm}"
SKIP_MODELS="${SKIP_MODELS:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

echo "==> North Star installer (Android / Termux)"
echo "    Repo: $REPO_ROOT"

have() { command -v "$1" >/dev/null 2>&1; }

# --- 1. System packages ------------------------------------------------------
echo "==> Updating Termux packages..."
pkg update -y && pkg upgrade -y
# python + build tooling (rust/clang needed for some wheels), ollama, git
pkg install -y python python-pip git clang rust binutils ollama || {
    echo "    NOTE: 'ollama' may not be in your Termux repo. If so, you can still run" >&2
    echo "    the cloud-fallback mode (set GROQ_API_KEY/OPENROUTER_API_KEY in .env)." >&2
}

# --- 2. Virtual environment + install ----------------------------------------
if [ ! -d .venv ]; then
    echo "==> Creating virtual environment (.venv)..."
    python -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip wheel

echo "==> Installing the project (editable)..."
echo "    (If chromadb/onnxruntime fails to build on your device, install the study"
echo "     LLM + fitness components only — see install/README.md for the lite path.)"
python -m pip install -e . || {
    echo "    Full install failed — retrying without the RAG vector-DB stack..." >&2
    python -m pip install \
        langgraph langgraph-checkpoint-sqlite langchain-core langchain-ollama \
        pydantic pydantic-settings python-dotenv typer rich httpx \
        fitparse gpxpy pandas numpy
    echo "    Installed core without chromadb. The study-LLM and fitness components work;"
    echo "    the RAG component needs chromadb (see install/README.md)."
}

# --- 3. .env -----------------------------------------------------------------
if [ ! -f .env ]; then
    cp .env.example .env
    # default to the smaller mobile models
    sed -i "s/^POLARIS_CHAT_MODEL=.*/POLARIS_CHAT_MODEL=$CHAT_MODEL/" .env
    sed -i "s/^POLARIS_EMBED_MODEL=.*/POLARIS_EMBED_MODEL=$EMBED_MODEL/" .env
    echo "==> Created .env (mobile models: $CHAT_MODEL / $EMBED_MODEL)"
fi

# --- 4. Ollama daemon + models ----------------------------------------------
if have ollama; then
    if ! curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "==> Starting 'ollama serve' in the background..."
        (ollama serve >"$PREFIX/tmp/ollama.log" 2>&1 &) || true
        sleep 4
    fi
    if [ "$SKIP_MODELS" != "1" ]; then
        echo "==> Pulling small models for mobile..."
        ollama pull "$CHAT_MODEL" || echo "    (pull $CHAT_MODEL later)"
        ollama pull "$EMBED_MODEL" || echo "    (pull $EMBED_MODEL later)"
    fi
else
    echo "==> Ollama not installed; configure cloud fallback keys in .env to run."
fi

echo ""
echo "==> Done!"
echo "    Run:    source .venv/bin/activate && polaris-study doctor"
echo "    Tip:    keep models small on phones; close other apps while running."
