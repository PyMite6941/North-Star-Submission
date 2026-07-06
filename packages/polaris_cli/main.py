"""The unified `polaris` command — mounts each component as a subcommand group."""

from __future__ import annotations

import typer
from college_planner.cli import app as college_app
from fitness_agents.cli import app as fitness_app
from polaris_core import __version__
from polaris_core.config import get_settings
from polaris_core.console import console
from polaris_core.llm import check_ollama
from study_llm.cli import app as study_app
from study_rag.cli import app as rag_app

app = typer.Typer(
    help="Polaris — offline study & fitness AI (LangGraph + Ollama).",
    no_args_is_help=True,
)

config_app = typer.Typer(help="Inspect the resolved configuration.", no_args_is_help=True)

app.add_typer(study_app, name="study", help="The 6-area study LLM.")
app.add_typer(rag_app, name="rag", help="Vector-DB study agent (RAG).")
app.add_typer(fitness_app, name="fitness", help="Fitness file analysis + growth plan.")
app.add_typer(college_app, name="college", help="College-application tracker + course map.")
app.add_typer(config_app, name="config", help="Inspect the resolved configuration.")

_SECRET_FIELDS = {"groq_api_key", "openrouter_api_key", "discord_bot_token"}


@config_app.command("show")
def config_show() -> None:
    """Print every resolved setting (from `.env` / environment / defaults). Secrets are masked."""
    settings = get_settings()
    console.print("[bold]Polaris settings[/] (env var → value):\n")
    for name, field in type(settings).model_fields.items():
        value = getattr(settings, name)
        if name in _SECRET_FIELDS:
            value = "***set***" if value else "(not set)"
        console.print(f"  [cyan]{field.alias or name.upper()}[/] = {value}")


@app.command()
def version() -> None:
    """Show the Polaris version."""
    console.print(f"Polaris {__version__}")


@app.command()
def serve(
    host: str | None = typer.Option(None, help="Bind host (default: POLARIS_API_HOST)."),
    port: int | None = typer.Option(None, help="Bind port (default: POLARIS_API_PORT)."),
    reload: bool = typer.Option(False, "--reload", help="Auto-reload (dev)."),
) -> None:
    """Run the FastAPI service (requires the [serve] extra)."""
    try:
        import uvicorn
    except ImportError:
        console.print('[red]Install the serve extra:[/] pip install -e ".[serve]"')
        raise typer.Exit(1) from None
    from polaris_core.config import get_settings

    settings = get_settings()
    host = host or settings.api_host
    port = port or settings.api_port
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
