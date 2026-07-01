"""Thin runner for the fitness pipeline.

    python "fitness agents for use/core programs/analyze.py" path/to/file.gpx [--goal "..."]
"""

from fitness_agents.cli import app

if __name__ == "__main__":
    # Default subcommand to `analyze` when the first arg looks like a file/option.
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in {"analyze", "parse", "agents", "--help"}:
        sys.argv.insert(1, "analyze")
    app()
