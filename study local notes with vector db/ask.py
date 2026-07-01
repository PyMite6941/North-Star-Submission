"""Thin runner: ask the RAG study agent a question.

    python "study local notes with vector db/ask.py" "your question here"
"""

import sys

from study_rag.graph import build_graph

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python ask.py "your question"')
        raise SystemExit(1)
    question = " ".join(sys.argv[1:])
    graph = build_graph()
    result = graph.invoke({"question": question, "original_question": question, "attempts": 0})
    print(result.get("answer", "(no answer)"))
