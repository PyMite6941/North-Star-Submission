"""CLI for the RAG study agent.

    polaris-rag ingest "study local notes with vector db/sample_notes"
    polaris-rag ask "Explain the light-dependent reactions of photosynthesis."
    polaris-rag ask "..." --show-sources    # also list the cited chunks
    polaris-rag stats                        # how many chunks are stored
    polaris-rag reset                        # clear the vector DB
    polaris-rag sync-discord                 # pull #announcements -> local notes -> ingest
    polaris-rag doctor
"""

from __future__ import annotations

from pathlib import Path

import typer
from polaris_core.config import get_settings
from polaris_core.console import console
from polaris_core.llm import check_ollama

from study_rag.discord_sync import DiscordSyncError, sync_channel
from study_rag.graph import build_graph
from study_rag.ingest import ingest_path
from study_rag.store import collection_count, reset_collection

app = typer.Typer(help="Local RAG study agent (vector DB).", no_args_is_help=True)


@app.command()
def ingest(path: str) -> None:
    """Ingest a file or directory of notes into the vector DB."""
    n = ingest_path(path)
    if n:
        console.print(f"[green]✓ Ingested {n} chunks[/] from {path}")
        console.print(f"[dim]Collection now holds {collection_count()} chunks.[/]")
    else:
        console.print(f"[yellow]No supported text files found under[/] {path}")


@app.command()
def ask(
    question: str,
    show_sources: bool = typer.Option(
        False, "--show-sources", "-s", help="List the source chunks used for the answer."
    ),
) -> None:
    """Ask a question, answered with cited, retrieval-grounded context."""
    graph = build_graph()
    result = graph.invoke({"question": question, "original_question": question, "attempts": 0})
    console.print(result.get("answer", "(no answer)"))

    if show_sources:
        docs = result.get("documents", [])
        if docs:
            console.print("\n[bold]Sources:[/]")
            seen: set[str] = set()
            for i, doc in enumerate(docs, 1):
                src = doc.metadata.get("source", "?")
                key = f"{src}#{doc.metadata.get('start_index', i)}"
                if key in seen:
                    continue
                seen.add(key)
                snippet = doc.page_content[:120].replace("\n", " ")
                console.print(f"  [{i}] [cyan]{src}[/] — {snippet}…")
        else:
            console.print("\n[dim]No sources retrieved.[/]")


@app.command()
def stats() -> None:
    """Show how many chunks are stored in the vector DB."""
    console.print(f"Stored chunks: [bold]{collection_count()}[/]")


@app.command()
def reset(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip the confirmation prompt."),
) -> None:
    """Clear the vector DB (delete all ingested chunks)."""
    n = collection_count()
    if not yes:
        confirm = typer.confirm(f"Delete all {n} chunks from the collection?")
        if not confirm:
            console.print("Aborted.")
            return
    reset_collection()
    console.print("[green]✓ Collection cleared.[/]")


@app.command("sync-discord")
def sync_discord(
    export: Path = typer.Option(
        Path("study local notes with vector db/discord_sync/announcements.md"),
        "--export",
        "-e",
        help="Where to write the synced Markdown note.",
    ),
    ingest_after: bool = typer.Option(
        True, "--ingest/--no-ingest", help="Run `rag ingest` on the synced note afterward."
    ),
    limit: int = typer.Option(200, "--limit", help="Max recent messages to fetch."),
) -> None:
    """Pull recent messages from the configured Discord announcements channel (read-only,
    one-way — never posts) into a local Markdown note, then ingest it for offline, cited
    Q&A. Requires DISCORD_BOT_TOKEN + DISCORD_ANNOUNCEMENTS_CHANNEL_ID — see
    docs/discord-announcements-sync.md for what has to be set up first."""
    settings = get_settings()
    try:
        path = sync_channel(
            settings.discord_announcements_channel_id,
            settings.discord_bot_token,
            export,
            limit=limit,
        )
    except DiscordSyncError as exc:
        console.print(f"[red]✗ {exc}[/]")
        raise typer.Exit(1) from None
    console.print(f"[green]✓ Synced →[/] {path}")
    if ingest_after:
        n = ingest_path(path)
        console.print(f"[green]✓ Ingested {n} chunks[/] — ask about it with `polaris rag ask`.")


@app.command()
def doctor() -> None:
    """Check Ollama availability (needed for embeddings + generation)."""
    status = check_ollama()
    state = "[green]✓ reachable[/]" if status.reachable else f"[red]✗ {status.detail}[/]"
    console.print(f"Ollama: {state}")


if __name__ == "__main__":
    app()
