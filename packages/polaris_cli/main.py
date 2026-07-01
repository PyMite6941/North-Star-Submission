"""The unified `polaris` command — mounts each component as a subcommand group."""

from __future__ import annotations

import typer
from fitness_agents.cli import app as fitness_app
from polaris_core import __version__
from polaris_core.console import console
from polaris_core.llm import check_ollama
from study_llm.cli import app as study_app
from study_rag.cli import app as rag_app

app = typer.Typer(
    help="Polaris — offline study & fitness AI (LangGraph + Ollama).",
    no_args_is_help=True,
)

app.add_typer(study_app, name="study", help="The 6-area study LLM.")
app.add_typer(rag_app, name="rag", help="Vector-DB study agent (RAG).")
app.add_typer(fitness_app, name="fitness", help="Fitness file analysis + growth plan.")


@app.command()
def version() -> None:
    """Show the Polaris version."""
    console.print(f"Polaris {__version__}")


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Bind host."),
    port: int = typer.Option(8000, help="Bind port."),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload (dev)."),
) -> None:
    """Run the FastAPI service (requires the [serve] extra)."""
    try:
        import uvicorn
    except ImportError:
        console.print('[red]Install the serve extra:[/] pip install -e ".[serve]"')
        raise typer.Exit(1) from None
    console.print(f"[green]Polaris API →[/] http://{host}:{port}  (docs at /docs)")
    uvicorn.run("polaris_api.app:app", host=host, port=port, reload=reload)


@app.command()
def doctor() -> None:
    """Check the local stack (Ollama + models) for all components."""
    status = check_ollama()
    if status.reachable:
        console.print(f"[green]✓ Ollama reachable[/] — {len(status.models)} model(s) installed.")
        console.print(f"  {', '.join(status.models) or '(none)'}")
    else:
        console.print(f"[red]✗ Ollama not reachable[/]: {status.detail}")
        console.print("  Start it with [bold]ollama serve[/] and pull a model.")


if __name__ == "__main__":
    app()
