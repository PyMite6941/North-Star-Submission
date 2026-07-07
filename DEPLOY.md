# Deployment

Live:
- **Frontend** (Vercel): https://frontend-h8e7r5jyn-matt-gs-projects-e73d6b76.vercel.app
- **Backend** (Cloud Run): https://polaris-api-425677098314.us-central1.run.app

Architecture: static React SPA on Vercel → FastAPI on Cloud Run. The backend is
**serverless** (no Ollama): chat uses the free **Groq** API (cloud fallback), embeddings use
**fastembed** (ONNX, baked into the image). The vector store (Chroma) persists to a **GCS
bucket mounted into Cloud Run**, so all feature data survives cold starts.

## Backend — Google Cloud Run

Project `project-3758abef-d8d2-488a-b35`, region `us-central1`. (A new project could not be
used: the billing account is at its 5-project cap.)

```bash
# 1. Enable APIs (once)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  --project project-3758abef-d8d2-488a-b35

# 2. Build + deploy from the Dockerfile
gcloud run deploy polaris-api --source . \
  --project project-3758abef-d8d2-488a-b35 --region us-central1 \
  --allow-unauthenticated --memory 2Gi --cpu 2 --timeout 300 --max-instances 1

# 3. Durable vector store: mount a GCS bucket at /data
gcloud storage buckets create gs://polaris-store-4edac7 \
  --project project-3758abef-d8d2-488a-b35 --location us-central1 --uniform-bucket-level-access
gcloud storage buckets add-iam-policy-binding gs://polaris-store-4edac7 \
  --member serviceAccount:425677098314-compute@developer.gserviceaccount.com --role roles/storage.objectAdmin
gcloud run services update polaris-api --project project-3758abef-d8d2-488a-b35 --region us-central1 \
  --add-volume=name=store,type=cloud-storage,bucket=polaris-store-4edac7 \
  --add-volume-mount=volume=store,mount-path=/data \
  --update-env-vars=POLARIS_CHROMA_DIR=/data/chroma,POLARIS_FITNESS_DB=/data/fitness.sqlite,POLARIS_COLLEGE_DB=/data/college.sqlite,POLARIS_CHECKPOINT_DB=/data/checkpoints.sqlite \
  --max-instances 1
```

> `--max-instances 1` keeps a single writer so Chroma's SQLite over gcsfuse stays consistent.

### Enable chat (free Groq key — required for study/quiz/flashcards/planner/assistant)
```bash
gcloud run services update polaris-api --project project-3758abef-d8d2-488a-b35 --region us-central1 \
  --set-env-vars GROQ_API_KEY=gsk_your_key_here   # get one free at console.groq.com/keys
```

The Dockerfile already sets `POLARIS_EMBED_BACKEND=fastembed`, `POLARIS_ALLOW_CLOUD_FALLBACK=true`,
and `POLARIS_CORS_ORIGINS=*`.

## Frontend — Vercel

`frontend/.env.production` points `VITE_API_BASE` at the Cloud Run URL and is committed, so a
build anywhere produces a working bundle.

**Deploy (CLI):**
```bash
cd frontend
vercel --prod        # first run links the project; subsequent runs redeploy
```

**Auto-deploy on git push (one-time, dashboard):**
1. Vercel → project **frontend** → Settings → **Git** → connect `PyMite6941/North-Star-Submission`
   (installs the Vercel GitHub app — requires your approval).
2. Set **Root Directory** to `frontend`.
3. Deployment Protection is already **off** (public site).

After that, every push to `master` redeploys the frontend automatically.

## Scaling the vector store (managed DB)
The GCS-mounted Chroma persists but pins writes to one instance. For higher scale, switch to
**Upstash Vector** (managed, serverless) — the backend is already implemented
(`polaris_core/store_upstash.py`); activation is config-only:

1. Create a free index at **console.upstash.com** → Vector → new index, **dimension 384**,
   **metric cosine** (matches the fastembed `BAAI/bge-small-en-v1.5` embeddings).
2. Point the backend at it and drop the single-instance pin:
   ```bash
   gcloud run services update polaris-api --project project-3758abef-d8d2-488a-b35 --region us-central1 \
     --set-env-vars POLARIS_VECTOR_BACKEND=upstash,UPSTASH_VECTOR_REST_URL=...,UPSTASH_VECTOR_REST_TOKEN=... \
     --clear-volume-mounts --clear-volumes --max-instances 3
   ```

Chroma remains the default (`POLARIS_VECTOR_BACKEND=chroma`), so nothing changes until you flip it.

## Frontend auto-deploy (GitHub Actions)
`.github/workflows/deploy-frontend.yml` redeploys the frontend to Vercel on every push to
`master` that touches `frontend/**` — using repo secrets `VERCEL_TOKEN`, `VERCEL_ORG_ID`,
`VERCEL_PROJECT_ID` (already set). No Vercel GitHub App required.
