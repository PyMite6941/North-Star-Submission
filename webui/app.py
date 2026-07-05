"""Polaris — Streamlit web UI (a single front-end for all three components).

Run:  streamlit run webui/app.py    (install with:  pip install -e ".[ui]")

Calls the same package functions the CLIs use, so behaviour is identical and it works
fully offline against local Ollama.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st
from langchain_core.messages import HumanMessage
from polaris_core.config import get_settings
from polaris_core.llm import check_ollama
from polaris_core.polaris import POLARIS_AREAS, PolarisArea

st.set_page_config(page_title="Polaris", page_icon="⭐", layout="wide")
st.title("North Star ⭐ (Polaris)")

# NOTE: this UI is an admin / site-manager tool for locally testing the stack,
# not something end users (students) are meant to see — there is no student-
# facing login here.
_SECRET_SETTINGS = {"groq_api_key", "openrouter_api_key"}

# --- sidebar: local stack status ---------------------------------------------
with st.sidebar:
    st.header("Local stack")
    status = check_ollama()
    if status.reachable:
        st.success(f"Ollama reachable — {len(status.models)} models")
        st.caption(", ".join(status.models) or "(none)")
    else:
        st.error("Ollama not reachable")
        st.caption("Start it with `ollama serve` and pull a model.")

    st.divider()
    st.header("Admin / testing")
    settings = get_settings()
    if settings.has_cloud_fallback:
        use_cloud = st.toggle(
            "Use cloud AI fallback",
            value=settings.allow_cloud_fallback,
            help=(
                "A cloud key (Groq/OpenRouter) is configured server-side. Flip this on to "
                "let this session fail over to it when Ollama is unreachable — the key itself "
                "is never shown here or handed to students."
            ),
        )
        if use_cloud != settings.allow_cloud_fallback:
            os.environ["POLARIS_ALLOW_CLOUD_FALLBACK"] = "true" if use_cloud else "false"
            get_settings.cache_clear()
            st.rerun()
    else:
        st.caption("Cloud AI fallback isn't configured (no GROQ/OPENROUTER key set in `.env`).")

    with st.expander("Resolved settings"):
        for name, field in type(settings).model_fields.items():
            value = getattr(settings, name)
            if name in _SECRET_SETTINGS:
                value = "***set***" if value else "(not set)"
            st.text(f"{field.alias or name.upper()} = {value}")

study_tab, rag_tab, fitness_tab = st.tabs(["📚 Study LLM", "🔎 Study RAG", "🏃 Fitness"])

# --- Study LLM ---------------------------------------------------------------
with study_tab:
    st.subheader("Ask (6 areas)")
    prompt = st.text_area("Your request", "Make 5 flashcards on the Krebs cycle")
    area_names = ["auto"] + [a.value for a in POLARIS_AREAS]
    area_choice = st.selectbox("Area", area_names, index=0)
    if st.button("Ask", key="study_ask"):
        from study_llm.graph import build_graph

        state: dict = {"messages": [HumanMessage(content=prompt)]}
        if area_choice != "auto":
            state["area"] = PolarisArea(area_choice)
        with st.spinner("Thinking…"):
            result = build_graph().invoke(state)
        st.caption(f"area: {result.get('area')}")
        st.markdown(result["messages"][-1].content)

    st.divider()
    st.subheader("Flashcards → CSV")
    fc_topic = st.text_input("Topic", "Photosynthesis")
    fc_n = st.slider("Cards", 3, 20, 8)
    if st.button("Generate deck", key="fc"):
        from study_llm.flashcards import generate_deck

        with st.spinner("Generating…"):
            deck = generate_deck(fc_topic, count=fc_n)
        rows = [{"Q": c.question, "A": c.answer} for c in deck.cards]
        st.dataframe(rows, use_container_width=True)

# --- Study RAG ---------------------------------------------------------------
with rag_tab:
    st.subheader("Ingest notes")
    path = st.text_input("File or folder", "study local notes with vector db/sample_notes")
    if st.button("Ingest", key="ingest"):
        from study_rag.ingest import ingest_path

        with st.spinner("Embedding…"):
            n = ingest_path(path)
        st.success(f"Indexed {n} new/updated chunks.")

    st.divider()
    st.subheader("Ask your notes")
    q = st.text_input("Question", "Explain the light-dependent reactions.")
    if st.button("Ask notes", key="rag_ask"):
        from study_rag.graph import build_graph

        with st.spinner("Retrieving + answering…"):
            result = build_graph().invoke(
                {"question": q, "original_question": q, "attempts": 0}
            )
        st.markdown(result.get("answer", "(no answer)"))
        srcs = sorted({d.metadata.get("source", "?") for d in result.get("documents", [])})
        if srcs:
            st.caption("Sources: " + ", ".join(Path(s).name for s in srcs))

# --- Fitness -----------------------------------------------------------------
with fitness_tab:
    st.subheader("Analyze activity")
    uploads = st.file_uploader(
        "Upload .fit / .tcx / .gpx / .csv / .json",
        type=["fit", "tcx", "gpx", "csv", "json"],
        accept_multiple_files=True,
    )
    goal = st.text_input("Goal", "Run a sub-25 minute 5K")
    log_it = st.checkbox("Log to progress history", value=False)
    if st.button("Analyze", key="fit") and uploads:
        tmpdir = Path(tempfile.mkdtemp())
        paths = []
        for up in uploads:
            p = tmpdir / up.name
            p.write_bytes(up.getbuffer())
            paths.append(str(p))
        from fitness_agents.graph import build_graph

        with st.spinner("Running the agent pipeline…"):
            result = build_graph().invoke({"files": paths, "goal": goal})
        if result.get("trend_text"):
            st.info(result["trend_text"])
        st.markdown("### Analysis")
        st.markdown(result.get("analysis", "(none)"))
        st.markdown("### Growth Plan")
        st.markdown(result.get("review") or result.get("plan", "(none)"))
        if log_it:
            from fitness_agents.history import log_session
            from fitness_agents.metrics import summarize
            from fitness_agents.parsers import parse_file

            for p in paths:
                recs = parse_file(p)
                dates = [r.timestamp for r in recs if r.timestamp]
                log_session(summarize(recs), source=Path(p).name, when=dates[0] if dates else None)
            st.success("Logged to history.")

    st.divider()
    st.subheader("Progress trend")
    if st.button("Show trend", key="trend"):
        from fitness_agents.history import compute_trends

        trends = compute_trends()
        st.text(trends.to_prompt() if trends else "No history yet.")
