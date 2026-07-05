"""Typed application settings, loaded once from the environment / `.env`.

Every component reads configuration through :func:`get_settings` rather than
touching ``os.environ`` directly, so misconfiguration fails fast and loudly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    """Repo root = three levels up from this file (packages/polaris_core/config.py)."""
    return Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Central configuration. Field names map to ``POLARIS_*`` env vars below."""

    model_config = SettingsConfigDict(
        env_file=(_repo_root() / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Ollama / LLM ---
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    chat_model: str = Field(default="llama3.2", alias="POLARIS_CHAT_MODEL")
    embed_model: str = Field(default="nomic-embed-text", alias="POLARIS_EMBED_MODEL")
    temperature: float = Field(default=0.2, alias="POLARIS_TEMPERATURE")
    num_ctx: int = Field(default=8192, alias="POLARIS_NUM_CTX")
    request_timeout: int = Field(default=120, alias="POLARIS_REQUEST_TIMEOUT")

    # --- Embeddings backend ---
    embed_backend: Literal["ollama", "fastembed"] = Field(
        default="ollama", alias="POLARIS_EMBED_BACKEND"
    )
    fastembed_model: str = Field(
        default="BAAI/bge-small-en-v1.5", alias="POLARIS_FASTEMBED_MODEL"
    )

    # --- Vector DB (Chroma) ---
    chroma_dir: str = Field(default=".data/chroma", alias="POLARIS_CHROMA_DIR")
    rag_collection: str = Field(default="study_notes", alias="POLARIS_RAG_COLLECTION")
    rag_chunk_size: int = Field(default=1000, alias="POLARIS_RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=150, alias="POLARIS_RAG_CHUNK_OVERLAP")
    rag_top_k: int = Field(default=4, alias="POLARIS_RAG_TOP_K")

    # --- LangGraph persistence ---
    checkpoint_db: str = Field(default=".data/checkpoints.sqlite", alias="POLARIS_CHECKPOINT_DB")

    # --- Fitness athlete profile (optional; improves HR zones + training load) ---
    athlete_age: int | None = Field(default=None, alias="POLARIS_ATHLETE_AGE")
    athlete_resting_hr: int | None = Field(default=None, alias="POLARIS_ATHLETE_RESTING_HR")
    athlete_max_hr: int | None = Field(default=None, alias="POLARIS_ATHLETE_MAX_HR")
    fitness_db: str = Field(default=".data/fitness.sqlite", alias="POLARIS_FITNESS_DB")
    units: Literal["metric", "imperial"] = Field(default="metric", alias="POLARIS_UNITS")

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="POLARIS_LOG_LEVEL")

    # --- Optional cloud fallback (blank = stay fully local) ---
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    # Master switch: the admin sets the key above AND flips this on before any
    # component is allowed to fail over to the cloud when Ollama is unreachable.
    allow_cloud_fallback: bool = Field(default=False, alias="POLARIS_ALLOW_CLOUD_FALLBACK")

    @field_validator("embed_backend", "units", mode="before")
    @classmethod
    def _normalize_choice(cls, v: object) -> object:
        """Lowercase/trim string choices so ``Fastembed`` and ``fastembed`` both work."""
        return v.strip().lower() if isinstance(v, str) else v

    # ------------------------------------------------------------------ helpers
    @property
    def has_cloud_fallback(self) -> bool:
        return bool(self.groq_api_key or self.openrouter_api_key)

    @property
    def cloud_fallback_active(self) -> bool:
        """True only when the admin has both configured a key AND flipped the switch on."""
        return self.allow_cloud_fallback and self.has_cloud_fallback

    def abspath(self, relative: str) -> Path:
        """Resolve a configured relative path against the repo root and ensure parent dirs."""
        p = Path(relative)
        if not p.is_absolute():
            p = _repo_root() / p
        return p

    def chroma_path(self) -> Path:
        p = self.abspath(self.chroma_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def checkpoint_path(self) -> Path:
        p = self.abspath(self.checkpoint_db)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def fitness_path(self) -> Path:
        p = self.abspath(self.fitness_db)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def max_hr_estimate(self) -> int | None:
        """Configured max HR, else the age-based estimate (208 − 0.7·age), else None."""
        if self.athlete_max_hr:
            return self.athlete_max_hr
        if self.athlete_age:
            return round(208 - 0.7 * self.athlete_age)
        return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide, cached settings instance."""
    return Settings()
