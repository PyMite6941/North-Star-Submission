#!/bin/sh
# North Star (Polaris) setup for iOS (iPhone / iPad).
#
# NOTE: The RECOMMENDED iOS path is the native on-device Swift package in ../ios-native
#       (Apple Foundation Models, iOS 26+) — no Ollama, no network. This script is the
#       thin-client FALLBACK for when you can't ship a native build.
#
# IMPORTANT: iOS is sandboxed — you CANNOT run the Ollama daemon on-device, and the
# heavy native deps (chromadb/onnxruntime) have no iOS wheels. So on iPhone the app
# runs as a THIN CLIENT in one of two modes:
#
#   (A) LAN mode  — talk to Ollama running on your Mac/PC on the same Wi-Fi.
#   (B) Cloud mode — use a free hosted model via GROQ_API_KEY / OPENROUTER_API_KEY.
#
# Run this inside the "a-Shell" app (free, App Store), which provides python3.
#
# Usage (in a-Shell, from the repo folder):
#   REMOTE_HOST=192.168.1.50 sh install/ios-setup.sh      # (A) LAN mode
#   USE_CLOUD=1 sh install/ios-setup.sh                   # (B) cloud mode
set -eu

REMOTE_HOST="${REMOTE_HOST:-}"
REMOTE_PORT="${REMOTE_PORT:-11434}"
USE_CLOUD="${USE_CLOUD:-0}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT"

echo "==> North Star setup (iOS / a-Shell)"

# --- Write a client .env -----------------------------------------------------
if [ ! -f .env ]; then
    cp .env.example .env
fi

if [ "$USE_CLOUD" = "1" ]; then
    echo "==> Cloud mode: edit .env and set GROQ_API_KEY or OPENROUTER_API_KEY."
    echo "    The app will fail over to a free hosted model (allow_cloud=True)."
elif [ -n "$REMOTE_HOST" ]; then
    BASE="http://$REMOTE_HOST:$REMOTE_PORT"
    # point the client at the desktop running 'ollama serve' (with OLLAMA_HOST=0.0.0.0)
    sed -i.bak "s|^OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=$BASE|" .env && rm -f .env.bak
    echo "==> LAN mode: OLLAMA_BASE_URL set to $BASE"
    echo "    On your Mac/PC, run Ollama bound to the network:"
    echo "      OLLAMA_HOST=0.0.0.0 ollama serve"
else
    echo "ERROR: choose a mode. Set REMOTE_HOST=<desktop-ip> (LAN) or USE_CLOUD=1 (cloud)." >&2
    exit 1
fi

# --- Lite, iOS-friendly Python deps (pure-Python only, no chromadb/onnx) -----
echo "==> Installing lite client deps (study LLM + fitness; no on-device RAG)..."
pip install --upgrade pip || true
pip install \
    langgraph langgraph-checkpoint-sqlite langchain-core langchain-ollama \
    pydantic pydantic-settings python-dotenv typer rich httpx \
    fitparse gpxpy || {
    echo "    Some deps may not have iOS wheels in a-Shell." >&2
    echo "    For a real shipped iOS app, bundle a model with MLC LLM / llama.cpp (see install/README.md)." >&2
}

echo ""
echo "==> Done (client configured)."
echo "    The study-LLM and fitness components work as a client."
echo "    On-device RAG (chromadb) is not supported on iOS — use LAN/cloud or a native build."
