"""polaris_cli — a single umbrella CLI that composes the three components.

    polaris study ...     # the 6-area study LLM
    polaris rag ...        # the vector-DB study agent
    polaris fitness ...    # the fitness agents
"""

from polaris_cli.main import app

__all__ = ["app"]
