# Component 2 — Study RAG (vector-DB notes)

Ingests a user's notes into a **local Chroma vector DB**, then answers study questions with
**retrieval-augmented, cited** responses. Increases study accuracy and works offline once
ingested — at the cost of some on-device storage. Intended to ship inside a downloadable app.

Library: `packages/study_rag`. Query topology is **corrective RAG**:

```
ingest (one-time):  load → split → embed → Chroma
query:  retrieve → grade docs → generate (cited)
                       └─ if weak → rewrite query → retrieve
```

## Run

```bash
# 1. Ingest the sample notes (or point at your own folder/file)
polaris-rag ingest "study local notes with vector db/sample_notes"

# 2. Ask
polaris-rag ask "Explain the light-dependent reactions of photosynthesis."

# without entry points:
python "study local notes with vector db/ingest.py" sample_notes
python "study local notes with vector db/ask.py" "your question"
```

Requires `ollama pull nomic-embed-text` for embeddings (or set
`POLARIS_EMBED_BACKEND=fastembed` for a pure-offline ONNX backend).

Supported note formats today: `.md`, `.markdown`, `.txt`, `.rst`. Add PDF/DOCX loaders in
`packages/study_rag/ingest.py` (see CONTRIBUTING).
