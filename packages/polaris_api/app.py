"""FastAPI app exposing study / rag / fitness over HTTP.

Endpoints are thin wrappers over the same functions the CLIs use, so behaviour is
identical. This is the backbone for a web UI, the iOS thin-client, and mobile.
"""

from __future__ import annotations

from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from polaris_core import __version__
from polaris_core.llm import check_ollama
from pydantic import BaseModel

app = FastAPI(title="Polaris API", version=__version__)


# --------------------------------------------------------------------------- health
@app.get("/health")
def health() -> dict:
    status = check_ollama()
    return {"version": __version__, "ollama_reachable": status.reachable, "models": status.models}


# ---------------------------------------------------------------------------- study
class AskRequest(BaseModel):
    prompt: str
    area: str | None = None


@app.post("/study/ask")
def study_ask(req: AskRequest) -> dict:
    from polaris_core.polaris import PolarisArea
    from study_llm.graph import build_graph

    state: dict = {"messages": [HumanMessage(content=req.prompt)]}
    if req.area:
        state["area"] = PolarisArea(req.area)
    result = build_graph().invoke(state)
    area = result.get("area")
    return {"area": area.value if area else None, "answer": result["messages"][-1].content}


class FlashcardsRequest(BaseModel):
    topic: str
    count: int = 10


@app.post("/study/flashcards")
def study_flashcards(req: FlashcardsRequest) -> dict:
    from study_llm.flashcards import generate_deck

    deck = generate_deck(req.topic, count=req.count)
    return deck.model_dump()


class QuizRequest(BaseModel):
    topic: str
    count: int = 5
    difficulty: str = "medium"


@app.post("/study/quiz")
def study_quiz(req: QuizRequest) -> dict:
    from study_llm.quiz import generate_quiz

    return generate_quiz(req.topic, count=req.count, difficulty=req.difficulty).model_dump()


class CVRequest(BaseModel):
    details: str


@app.post("/study/cv")
def study_cv(req: CVRequest) -> dict:
    from study_llm.cv import generate_resume

    return generate_resume(req.details).model_dump()


# ------------------------------------------------------------------------------ rag
class IngestRequest(BaseModel):
    path: str


@app.post("/rag/ingest")
def rag_ingest(req: IngestRequest) -> dict:
    from study_rag.ingest import ingest_path

    return {"chunks_indexed": ingest_path(req.path)}


class RagAskRequest(BaseModel):
    question: str


@app.post("/rag/ask")
def rag_ask(req: RagAskRequest) -> dict:
    from study_rag.graph import build_graph

    result = build_graph().invoke(
        {"question": req.question, "original_question": req.question, "attempts": 0}
    )
    sources = sorted(
        {d.metadata.get("source", "?") for d in result.get("documents", [])}
    )
    return {"answer": result.get("answer", ""), "sources": sources}


@app.get("/rag/stats")
def rag_stats() -> dict:
    from study_rag.store import collection_count

    return {"chunks": collection_count()}


# -------------------------------------------------------------------------- fitness
class AnalyzeRequest(BaseModel):
    files: list[str]
    goal: str = ""
    log: bool = False


@app.post("/fitness/analyze")
def fitness_analyze(req: AnalyzeRequest) -> dict:
    from fitness_agents.graph import build_graph

    result = build_graph().invoke({"files": req.files, "goal": req.goal})
    if req.log:
        from fitness_agents.history import log_session
        from fitness_agents.metrics import summarize
        from fitness_agents.parsers import parse_file

        for f in req.files:
            recs = parse_file(f)
            dates = [r.timestamp for r in recs if r.timestamp]
            log_session(summarize(recs), source=f, when=dates[0] if dates else None)
    return {
        "metrics": result.get("metrics_text", ""),
        "trend": result.get("trend_text", ""),
        "analysis": result.get("analysis", ""),
        "plan": result.get("review") or result.get("plan", ""),
    }


@app.get("/fitness/trend")
def fitness_trend() -> dict:
    from fitness_agents.history import compute_trends

    trends = compute_trends()
    return trends.__dict__ if trends else {"message": "no history yet"}
