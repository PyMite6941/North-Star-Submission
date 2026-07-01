"""fitness_agents — analyze uploaded fitness files and build a growth plan.

Parses .fit/.tcx/.gpx/.csv/.json into a common schema, computes metrics, then runs a
pipeline of markdown-defined agents (analyze → plan → review) via LangGraph.
"""

from fitness_agents.graph import build_graph
from fitness_agents.parsers import ActivityRecord, parse_file

__all__ = ["build_graph", "parse_file", "ActivityRecord"]
