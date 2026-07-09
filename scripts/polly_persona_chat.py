"""Standalone Groq test harness for the Polly persona prompt.

Loads the system prompt straight from ``docs/polly-persona-prompt.md`` and chats
with it via Groq's free OpenAI-compatible API — independent of the app's normal
local-first/Ollama chain, so you can iterate on the persona wording against a real
model without standing up anything else.

Setup:
    pip install -e ".[cloud]"          # installs langchain-openai
    export GROQ_API_KEY=gsk_your_key_here   # free key: console.groq.com/keys

Usage:
    python scripts/polly_persona_chat.py                  # interactive chat
    python scripts/polly_persona_chat.py -m "hey Polly!"   # one-shot message
    python scripts/polly_persona_chat.py --model llama-3.1-8b-instant
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import typer

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages"))

PROMPT_FILE = REPO_ROOT / "docs" / "polly-persona-prompt.md"
DEFAULT_MODEL = "llama-3.3-70b-versatile"

app = typer.Typer(add_completion=False, help=__doc__)


def _load_system_prompt(path: Path = PROMPT_FILE) -> str:
    """Pull the fenced ```text``` system prompt block out of the persona markdown file."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```text\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise RuntimeError(f"No ```text``` system-prompt block found in {path}")
    return match.group(1)


def _groq_chat_model(*, model: str, temperature: float):
    """Build a Groq-backed chat model directly, bypassing the Ollama-first fallback chain."""
    from polaris_core.config import get_settings

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            'Groq testing needs langchain-openai: pip install -e ".[cloud]"'
        ) from exc

    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at console.groq.com/keys, then "
            "export GROQ_API_KEY=... (or add it to .env)."
        )
    return ChatOpenAI(
        model=model,
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
        temperature=temperature,
    )


@app.command()
def main(
    message: str = typer.Option(
        None, "--message", "-m", help="Send one message and print the reply, then exit."
    ),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Groq model id."),
    temperature: float = typer.Option(0.6, "--temperature", help="Sampling temperature."),
) -> None:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    system_prompt = _load_system_prompt()
    llm = _groq_chat_model(model=model, temperature=temperature)
    history: list = [SystemMessage(content=system_prompt)]

    if message is not None:
        history.append(HumanMessage(content=message))
        reply = llm.invoke(history)
        print(reply.content)
        return

    print(f"Polly persona chat (Groq: {model}) — type 'exit' to quit.\n")
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"exit", "quit"}:
            break
        if not user:
            continue
        history.append(HumanMessage(content=user))
        reply = llm.invoke(history)
        history.append(AIMessage(content=reply.content))
        print(f"polly> {reply.content}\n")


if __name__ == "__main__":
    app()
