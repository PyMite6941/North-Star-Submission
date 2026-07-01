"""Nodes for the fitness pipeline: parse → metrics → analyze → plan → review."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage
from polaris_core.llm import get_chat_model
from polaris_core.logging import get_logger

from fitness_agents.agents import load_agent
from fitness_agents.history import compute_trends
from fitness_agents.metrics import summarize
from fitness_agents.parsers import parse_file
from fitness_agents.state import FitnessState

logger = get_logger(__name__)


def parse_and_summarize(state: FitnessState) -> dict:
    """Parse every input file, build a combined metrics summary, and load trends."""
    all_records = []
    blocks: list[str] = []
    sessions: list[dict] = []
    for f in state.get("files", []):
        try:
            records = parse_file(f)
        except Exception as exc:  # noqa: BLE001 - report and skip bad files
            logger.warning("Could not parse %s: %s", f, exc)
            blocks.append(f"## {f}\n(could not parse: {exc})")
            continue
        all_records.extend(records)
        summary = summarize(records)
        blocks.append(f"## {f}\n{summary.to_prompt()}")
        # Activity date from the first timestamped record (falls back to None → now()).
        dates = [r.timestamp for r in records if r.timestamp]
        sessions.append(
            {"source": f, "date": dates[0].isoformat() if dates else None, "summary": summary}
        )

    # Read-only progress context from stored history (populated via `log` / `analyze --log`).
    trends = compute_trends()
    trend_text = trends.to_prompt() if trends else ""

    return {
        "metrics_text": "\n\n".join(blocks),
        "n_records": len(all_records),
        "sessions": sessions,
        "trend_text": trend_text,
    }


def _run_agent(agent_name: str, user_content: str, temperature: float = 0.3) -> str:
    """Invoke a markdown-defined agent with a user message."""
    agent = load_agent(agent_name)
    llm = get_chat_model(temperature=temperature)
    response = llm.invoke(
        [SystemMessage(content=agent.system_prompt), HumanMessage(content=user_content)]
    )
    return response.content


def analyze(state: FitnessState) -> dict:
    """Analyst agent interprets the metrics + progress trends."""
    goal = state.get("goal") or "(no specific goal provided)"
    trend = state.get("trend_text", "")
    trend_block = f"Progress trends from training history:\n{trend}\n\n" if trend else ""
    content = (
        f"User goal: {goal}\n\n"
        f"Activity metrics across uploaded files:\n{state.get('metrics_text', '(none)')}\n\n"
        f"{trend_block}"
        "Analyze the athlete's current fitness, strengths, and weaknesses. "
        "If progress trends are provided, comment on the trajectory (improving/declining) "
        "and current form."
    )
    return {"analysis": _run_agent("fitness_analyst", content)}


def plan(state: FitnessState) -> dict:
    """Planner agent builds a personalized growth plan from the analysis."""
    goal = state.get("goal") or "(no specific goal provided)"
    content = (
        f"User goal: {goal}\n\nAnalysis:\n{state.get('analysis', '')}\n\n"
        f"Metrics:\n{state.get('metrics_text', '')}\n\n"
        "Create a concrete, progressive growth plan."
    )
    return {"plan": _run_agent("growth_planner", content)}


def review(state: FitnessState) -> dict:
    """Reviewer agent sanity-checks the plan for safety and realism."""
    content = (
        f"Proposed plan:\n{state.get('plan', '')}\n\n"
        f"Analysis:\n{state.get('analysis', '')}\n\n"
        "Review for safety, realism, and progression. Return the final, improved plan."
    )
    return {"review": _run_agent("plan_reviewer", content, temperature=0.2)}
