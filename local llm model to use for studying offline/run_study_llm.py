"""Thin runner so the study LLM can be launched from this component folder directly.

Equivalent to the installed `polaris-study` entry point:

    python "local llm model to use for studying offline/run_study_llm.py" chat
"""

from study_llm.cli import app

if __name__ == "__main__":
    app()
