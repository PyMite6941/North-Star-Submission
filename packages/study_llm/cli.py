"""CLI for the study LLM (the 6 Polaris areas).

    polaris-study chat                 # interactive, memory-backed session
    polaris-study ask "make flashcards about the Krebs cycle"
    polaris-study ask "..." --area essay   # force an area, skip the router
    polaris-study flashcards "Krebs cycle" -n 8 --export deck.csv
    polaris-study cv "rising senior, 3.8 GPA, ..." --export resume.md
    polaris-study areas                # list the 6 areas
    polaris-study doctor               # check Ollama + model availability
"""

from __future__ import annotations

import uuid
from pathlib import Path

import typer
from langchain_core.messages import HumanMessage
from polaris_core.console import console
from polaris_core.llm import check_ollama
from polaris_core.memory import sqlite_checkpointer
from polaris_core.polaris import POLARIS_AREAS, PolarisArea
from rich.table import Table

from study_llm.cv import export_markdown, generate_resume
from study_llm.flashcards import export_csv, generate_deck
from study_llm.graph import build_graph
from study_llm.quiz import generate_quiz, grade_quiz


def _stream_answer(graph, state: dict, config: dict | None = None):
    """Stream tokens from the area handler as they arrive; return the chosen area.

    Router-node tokens are filtered out so only the final answer streams to the user.
    """
    area = None
    for mode, data in graph.stream(state, config=config, stream_mode=["updates", "messages"]):
        if mode == "messages":
            chunk, meta = data
            if meta.get("langgraph_node") != "route" and getattr(chunk, "content", ""):
                console.print(chunk.content, end="", markup=False, soft_wrap=True)
        elif mode == "updates":
            for update in data.values():
                if update and update.get("area") is not None:
                    area = update["area"]
    console.print()
    return area

app = typer.Typer(help="Offline study LLM — the 6 areas of Polaris.", no_args_is_help=True)


@app.command()
def areas() -> None:
    """List the six Polaris areas."""
    table = Table(title="The 6 Areas of Polaris")
    table.add_column("Key", style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("Description")
    for info in POLARIS_AREAS.values():
        table.add_row(info.area.value, info.title, info.description)
    console.print(table)


@app.command()
def doctor() -> None:
    """Check that Ollama is reachable and the chat model is available."""
    status = check_ollama()
    if status.reachable:
        models = ", ".join(status.models) or "(none)"
        console.print(f"[green]✓ Ollama reachable[/]. Models: {models}")
    else:
        console.print(f"[red]✗ Ollama not reachable[/]: {status.detail}")
        console.print("  Start it with [bold]ollama serve[/] and pull a model.")


@app.command()
def ask(
    prompt: str,
    area: PolarisArea | None = typer.Option(
        None, "--area", "-a", help="Force an area and skip the router."
    ),
) -> None:
    """One-shot: route (or force an area) and answer a single request (streamed)."""
    graph = build_graph()
    state: dict = {"messages": [HumanMessage(content=prompt)]}
    if area is not None:
        state["area"] = area
    chosen = _stream_answer(graph, state)
    console.print(f"[dim](area: {chosen})[/]")


@app.command()
def flashcards(
    topic: str,
    count: int = typer.Option(10, "--count", "-n", help="How many cards to generate."),
    export: Path | None = typer.Option(
        None, "--export", "-e", help="Write an Anki-importable CSV to this path."
    ),
) -> None:
    """Generate a structured flashcard deck (and optionally export to CSV)."""
    deck = generate_deck(topic, count=count)
    table = Table(title=f"Flashcards — {deck.topic}")
    table.add_column("#", style="dim", width=3)
    table.add_column("Q", style="cyan")
    table.add_column("A")
    for i, card in enumerate(deck.cards, 1):
        table.add_row(str(i), card.question, card.answer)
    console.print(table)
    if export is not None:
        path = export_csv(deck, export)
        console.print(f"[green]✓ Exported {len(deck.cards)} cards →[/] {path}")


@app.command()
def cv(
    details: str = typer.Argument(
        ..., help="Free-form details: name, background, experience, education, skills..."
    ),
    export: Path | None = typer.Option(
        None, "--export", "-e", help="Write the résumé as Markdown to this path."
    ),
) -> None:
    """Generate a structured résumé (and optionally export to Markdown)."""
    resume = generate_resume(details)
    console.print(f"[bold]{resume.contact.name}[/]")
    if resume.summary:
        console.print(resume.summary)
    for section, entries in (
        ("Experience", resume.experience),
        ("Education", resume.education),
        ("Projects", resume.projects),
    ):
        if entries:
            console.rule(section)
            for entry in entries:
                console.print(entry)
    if resume.skills:
        console.rule("Skills")
        console.print(", ".join(resume.skills))
    if export is not None:
        path = export_markdown(resume, export)
        console.print(f"[green]✓ Exported résumé →[/] {path}")


@app.command()
def quiz(
    topic: str,
    count: int = typer.Option(5, "--count", "-n", help="How many questions."),
    difficulty: str = typer.Option("medium", "--difficulty", "-d", help="easy | medium | hard."),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for answers and grade them."
    ),
) -> None:
    """Generate a quiz and (interactively) grade your answers."""
    quiz_obj = generate_quiz(topic, count=count, difficulty=difficulty)

    if not interactive:
        for i, q in enumerate(quiz_obj.questions, 1):
            console.print(f"[bold]{i}. {q.question}[/]")
            for j, opt in enumerate(q.options):
                console.print(f"   {chr(97 + j)}) {opt}")
            console.print(f"   [dim]answer:[/] {q.answer}  [dim]— {q.explanation}[/]\n")
        return

    answers: list[str] = []
    for i, q in enumerate(quiz_obj.questions, 1):
        console.print(f"\n[bold]{i}. {q.question}[/]")
        for j, opt in enumerate(q.options):
            console.print(f"   {chr(97 + j)}) {opt}")
        try:
            answers.append(console.input("[cyan]your answer> [/]").strip())
        except (EOFError, KeyboardInterrupt):
            console.print("\nAborted.")
            return

    graded = grade_quiz(quiz_obj, answers)
    score = sum(1 for g in graded if g.correct)
    console.rule(f"Score: {score}/{len(quiz_obj.questions)}")
    for i, (q, g) in enumerate(zip(quiz_obj.questions, graded, strict=False), 1):
        mark = "[green]✓[/]" if g.correct else "[red]✗[/]"
        console.print(f"{mark} [bold]{i}.[/] correct answer: {q.answer}")
        console.print(f"   [dim]{g.feedback}[/]")


@app.command()
def chat() -> None:
    """Interactive, memory-backed chat (streamed). Type 'exit' to quit."""
    thread_id = str(uuid.uuid4())
    console.print("[bold]Polaris study chat[/] — type 'exit' to quit.\n")
    with sqlite_checkpointer() as cp:
        graph = build_graph(checkpointer=cp)
        config = {"configurable": {"thread_id": thread_id}}
        while True:
            try:
                user = console.input("[cyan]you> [/]").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if user.lower() in {"exit", "quit"}:
                break
            if not user:
                continue
            console.print("[green]polaris>[/] ", end="")
            chosen = _stream_answer(graph, {"messages": [HumanMessage(content=user)]}, config)
            console.print(f"[dim](area: {chosen})[/]\n")


if __name__ == "__main__":
    app()
