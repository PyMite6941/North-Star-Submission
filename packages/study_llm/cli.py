"""CLI for the study LLM (the 6 Polaris areas).

    polaris-study chat                 # interactive, memory-backed session
    polaris-study ask "make flashcards about the Krebs cycle"
    polaris-study ask "..." --area essay   # force an area, skip the router
    polaris-study flashcards "Krebs cycle" -n 8 --export deck.csv   # or deck.apkg (Anki)
    polaris-study cv "rising senior, 3.8 GPA, ..." --export resume.md   # or resume.pdf
    polaris-study quiz "the French Revolution" -n 5 --export handout.md --no-interactive
    polaris-study pack create "Bio final" -t "Krebs cycle" -t "Photosynthesis" -e pack.json
    polaris-study pack import pack.json --export-dir out/     # -> out/*.apkg for each deck
    polaris-study group-quiz "the French Revolution" -p Ana -p Sam -p Lee
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

from study_llm.cv import export_resume, generate_resume
from study_llm.flashcards import export_deck, generate_deck
from study_llm.graph import build_graph
from study_llm.groups import PlayerResult, build_pack, export_pack, import_pack, leaderboard
from study_llm.quiz import export_markdown as export_quiz_markdown
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
pack_app = typer.Typer(help="Offline Study Packs — bundle decks to share with a group.")
app.add_typer(pack_app, name="pack")


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
        None, "--export", "-e", help="Write to this path — .csv or .apkg (Anki package)."
    ),
) -> None:
    """Generate a structured flashcard deck (and optionally export to CSV or Anki .apkg)."""
    deck = generate_deck(topic, count=count)
    table = Table(title=f"Flashcards — {deck.topic}")
    table.add_column("#", style="dim", width=3)
    table.add_column("Q", style="cyan")
    table.add_column("A")
    for i, card in enumerate(deck.cards, 1):
        table.add_row(str(i), card.question, card.answer)
    console.print(table)
    if export is not None:
        path = export_deck(deck, export)
        console.print(f"[green]✓ Exported {len(deck.cards)} cards →[/] {path}")


@app.command()
def cv(
    details: str = typer.Argument(
        ..., help="Free-form details: name, background, experience, education, skills..."
    ),
    export: Path | None = typer.Option(
        None, "--export", "-e", help="Write to this path — .pdf or Markdown."
    ),
) -> None:
    """Generate a structured résumé (and optionally export to PDF or Markdown)."""
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
        path = export_resume(resume, export)
        console.print(f"[green]✓ Exported résumé →[/] {path}")


@app.command()
def quiz(
    topic: str,
    count: int = typer.Option(5, "--count", "-n", help="How many questions."),
    difficulty: str = typer.Option("medium", "--difficulty", "-d", help="easy | medium | hard."),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", help="Prompt for answers and grade them."
    ),
    export: Path | None = typer.Option(
        None, "--export", "-e", help="Write a printable Markdown handout (questions + answer key)."
    ),
) -> None:
    """Generate a quiz and (interactively) grade your answers."""
    quiz_obj = generate_quiz(topic, count=count, difficulty=difficulty)

    if export is not None:
        path = export_quiz_markdown(quiz_obj, export)
        console.print(f"[green]✓ Exported {len(quiz_obj.questions)} questions →[/] {path}")

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


@pack_app.command("create")
def pack_create(
    name: str,
    topic: list[str] = typer.Option(
        ..., "--topic", "-t", help="A topic to generate a deck for (repeat per member/subtopic)."
    ),
    count: int = typer.Option(10, "--count", "-n", help="Cards per deck."),
    export: Path = typer.Option(..., "--export", "-e", help="Write the pack to this JSON path."),
) -> None:
    """Generate one deck per --topic and bundle them into a single, shareable Study Pack."""
    pack = build_pack(name, topics=topic, cards_per_deck=count)
    path = export_pack(pack, export)
    console.print(
        f"[green]✓ Built study pack[/] {pack.name!r} — {len(pack.decks)} deck(s) → {path}"
    )
    console.print("[dim]Share this file with your group (USB, AirDrop, email, chat app).[/]")


@pack_app.command("import")
def pack_import(
    path: Path,
    export_dir: Path | None = typer.Option(
        None, "--export-dir", help="Also export every deck in the pack as .apkg into this folder."
    ),
) -> None:
    """Load a Study Pack a group member shared with you, and optionally export every deck."""
    pack = import_pack(path)
    console.print(f"[bold]{pack.name}[/]")
    if pack.notes:
        console.print(pack.notes)
    table = Table(title="Decks in this pack")
    table.add_column("Topic", style="cyan")
    table.add_column("Cards", justify="right")
    for deck in pack.decks:
        table.add_row(deck.topic, str(len(deck.cards)))
    console.print(table)
    if export_dir is not None:
        export_dir.mkdir(parents=True, exist_ok=True)
        for deck in pack.decks:
            safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in deck.topic)
            out = export_deck(deck, export_dir / f"{safe_name}.apkg")
            console.print(f"[green]✓[/] {out}")


@app.command("group-quiz")
def group_quiz(
    topic: str,
    player: list[str] = typer.Option(
        ..., "--player", "-p", help="A player's name (repeat once per person)."
    ),
    count: int = typer.Option(5, "--count", "-n", help="How many questions."),
    difficulty: str = typer.Option("medium", "--difficulty", "-d", help="easy | medium | hard."),
) -> None:
    """Pass-the-device quiz: everyone answers the same quiz, one at a time; ends with a
    leaderboard. Built for a study group in one room with no internet and one device."""
    quiz_obj = generate_quiz(topic, count=count, difficulty=difficulty)
    results: list[PlayerResult] = []

    for name in player:
        console.rule(f"{name}'s turn")
        try:
            console.input(f"[dim]Pass the device to[/] [bold]{name}[/][dim] — press enter> [/]")
        except (EOFError, KeyboardInterrupt):
            console.print("\nAborted.")
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
        results.append(PlayerResult(name=name, score=score, total=len(quiz_obj.questions)))
        console.print(f"[green]{name}: {score}/{len(quiz_obj.questions)}[/]")

    console.rule("Leaderboard")
    table = Table()
    table.add_column("#", style="dim")
    table.add_column("Player", style="bold")
    table.add_column("Score", justify="right")
    for i, r in enumerate(leaderboard(results), 1):
        table.add_row(str(i), r.name, f"{r.score}/{r.total}")
    console.print(table)


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
