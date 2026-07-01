"""polaris_api — FastAPI service exposing the three components over HTTP.

Install with the extra:  pip install -e ".[serve]"
Run:                     polaris serve   (or: uvicorn polaris_api.app:app --reload)
"""

from polaris_api.app import app

__all__ = ["app"]
