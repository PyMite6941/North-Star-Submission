# Component 1 — Study LLM (the 6 areas of Polaris)

A local LLM (via Ollama) that fulfils the **6 areas of Polaris**, intended to ship inside
a **downloadable app** so it runs on any device with no API keys.

| Area | Key |
|------|-----|
| Flashcard Creation | `flashcards` |
| Quizzing | `quizzing` |
| CV Builder | `cv_builder` |
| Advisor | `advisor` |
| Citation Generator | `citation` |
| Essay Helper | `essay` |

A LangGraph **router** classifies each request and dispatches it to the matching area
handler. The library lives in `packages/study_llm`; this folder holds the runnable entry
point and the Ollama `Modelfile`.

## Run

```bash
polaris-study areas            # list the 6 areas
polaris-study doctor           # verify Ollama + model
polaris-study ask "make flashcards about the Krebs cycle"
polaris-study chat             # interactive, memory-backed

# or without installing entry points:
python "local llm model to use for studying offline/run_study_llm.py" chat
```

## Modelfile

`Modelfile` defines an optional pre-tuned Ollama model (`polaris-study`) with a system
prompt and parameters baked in. Build it with:

```bash
ollama create polaris-study -f "local llm model to use for studying offline/Modelfile"
# then set POLARIS_CHAT_MODEL=polaris-study in .env
```
