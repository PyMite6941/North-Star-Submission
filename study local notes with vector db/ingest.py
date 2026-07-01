"""Thin runner: ingest notes from this component folder.

    python "study local notes with vector db/ingest.py" sample_notes
"""

import sys
from pathlib import Path

from study_rag.ingest import ingest_path

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "sample_notes")
    # Resolve relative paths against this folder for convenience.
    p = Path(target)
    if not p.is_absolute() and not p.exists():
        p = Path(__file__).parent / target
    n = ingest_path(p)
    print(f"Ingested {n} chunks from {p}")
