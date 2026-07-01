"""Load markdown-defined agents from ``fitness agents for use/agent mds/``.

Each agent is a markdown file with optional YAML-ish frontmatter::

    ---
    name: fitness_analyst
    description: Analyzes activity metrics and trends.
    ---
    <system prompt body…>

Editing a file changes the agent — no code change required.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

from polaris_core.logging import get_logger

logger = get_logger(__name__)


def _agent_dir() -> Path:
    """Resolve the spaced ``agent mds`` folder relative to the repo root."""
    # packages/fitness_agents/agents.py → parents[2] == repo root
    return Path(__file__).resolve().parents[2] / "fitness agents for use" / "agent mds"


@dataclass(frozen=True)
class Agent:
    name: str
    description: str
    system_prompt: str


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split simple ``key: value`` frontmatter from the body. Tolerant of no frontmatter."""
    meta: dict[str, str] = {}
    body = text
    if text.lstrip().startswith("---"):
        _, _, rest = text.lstrip().partition("---")
        fm, sep, body = rest.partition("---")
        if sep:
            for line in fm.strip().splitlines():
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip().lower()] = v.strip()
    return meta, body.strip()


@cache
def load_agent(name: str) -> Agent:
    """Load and cache an agent by file stem (e.g. ``"fitness_analyst"``)."""
    path = _agent_dir() / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(
            f"Agent markdown not found: {path}. Available: {', '.join(list_agents()) or '(none)'}"
        )
    meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
    return Agent(
        name=meta.get("name", name),
        description=meta.get("description", ""),
        system_prompt=body,
    )


def list_agents() -> list[str]:
    """List available agent file stems."""
    d = _agent_dir()
    return sorted(p.stem for p in d.glob("*.md")) if d.exists() else []
