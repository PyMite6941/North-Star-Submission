"""assistant — a free-API interpreter over the app's vector store.

Retrieves relevant items across every feature (syllabus, assignments, clubs, decks,
pomodoro, …) from the shared Chroma collection and answers with an LLM. Uses the free
cloud chain (Groq / OpenRouter :free) when ``POLARIS_ALLOW_CLOUD_FALLBACK`` is on, else
the local Ollama model — either way, free.
"""

from assistant.interpret import interpret

__all__ = ["interpret"]
