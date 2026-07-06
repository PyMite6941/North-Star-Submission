# Backend container for Cloud Run — serverless-friendly (no Ollama).
# Chat uses the free Groq API (cloud fallback); embeddings use fastembed (ONNX, in-image).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # Serverless config: fastembed embeddings + cloud chat, all writable paths under /tmp.
    POLARIS_EMBED_BACKEND=fastembed \
    POLARIS_ALLOW_CLOUD_FALLBACK=true \
    POLARIS_CHROMA_DIR=/tmp/chroma \
    POLARIS_FITNESS_DB=/tmp/fitness.sqlite \
    POLARIS_CHECKPOINT_DB=/tmp/checkpoints.sqlite \
    POLARIS_COLLEGE_DB=/tmp/college.sqlite \
    POLARIS_CORS_ORIGINS=*

WORKDIR /app

# Build tooling for any wheels that need compiling (chromadb/onnxruntime deps).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install the project + serve + fastembed + cloud extras.
COPY pyproject.toml requirements.txt README.md ./
COPY packages ./packages
RUN pip install -U pip \
    && pip install -e ".[serve,offline-embeddings,cloud]"

# Bake the fastembed model into the image so cold starts don't download it.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"

# Cloud Run provides $PORT (default 8080). Bind 0.0.0.0.
ENV PORT=8080
CMD exec uvicorn polaris_api.app:app --host 0.0.0.0 --port ${PORT}
