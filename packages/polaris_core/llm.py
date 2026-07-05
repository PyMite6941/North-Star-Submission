"""Local LLM factory + health checks, with optional cloud failover.

Default behaviour is **fully local** via Ollama. Cloud failover only engages when
``allow_cloud=True`` *and* an API key is configured.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama

from polaris_core.config import Settings, get_settings
from polaris_core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class OllamaStatus:
    reachable: bool
    models: list[str]
    detail: str = ""

    def has_model(self, name: str) -> bool:
        # Ollama tags include a ":tag"; match by bare name or exact tag.
        base = name.split(":")[0]
        return any(m == name or m.split(":")[0] == base for m in self.models)

    def resolve(self, name: str) -> str:
        """Map a requested model to an actually-installed tag.

        Ollama's API needs an exact ``name:tag`` (a bare ``llama3.2`` means
        ``llama3.2:latest``). If that exact tag isn't installed but a same-base
        tag is (e.g. ``llama3.2:3b``), use it so the call succeeds.
        """
        if name in self.models:
            return name
        base = name.split(":")[0]
        for m in self.models:
            if m.split(":")[0] == base:
                return m
        return name


def check_ollama(settings: Settings | None = None) -> OllamaStatus:
    """Probe the Ollama daemon and list installed models. Never raises."""
    settings = settings or get_settings()
    url = settings.ollama_base_url.rstrip("/") + "/api/tags"
    try:
        resp = httpx.get(url, timeout=5.0)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return OllamaStatus(reachable=True, models=models)
    except Exception as exc:  # noqa: BLE001 - report any failure as "unreachable"
        return OllamaStatus(reachable=False, models=[], detail=str(exc))


def _effective_model_and_options(
    settings: Settings, model: str | None
) -> tuple[str, int, int | None]:
    """Resolve (model, num_ctx, num_predict) from the low-power / save-memory settings.

    Pure and Ollama-free so it's unit-testable: low power swaps in a smaller model,
    save memory shrinks the context window and caps generated tokens — both aimed at
    constrained devices (old laptops, phones) rather than a beefy desktop.
    """
    if model is None:
        model = settings.low_power_chat_model if settings.low_power else settings.chat_model
    num_ctx = settings.save_memory_num_ctx if settings.save_memory else settings.num_ctx
    num_predict = settings.save_memory_max_tokens if settings.save_memory else None
    return model, num_ctx, num_predict


def get_chat_model(
    *,
    settings: Settings | None = None,
    model: str | None = None,
    temperature: float | None = None,
    allow_cloud: bool | None = None,
    **kwargs,
) -> BaseChatModel:
    """Return a chat model.

    Tries local Ollama first. If unreachable, falls back to a hosted free model via
    the OpenAI-compatible API — but only when cloud fallback is actually allowed:
    ``allow_cloud`` if explicitly passed, else the ``POLARIS_ALLOW_CLOUD_FALLBACK``
    admin setting (which itself requires a configured key; see ``Settings.cloud_fallback_active``).

    ``POLARIS_LOW_POWER`` / ``POLARIS_SAVE_MEMORY`` trade quality for less CPU/battery/RAM
    use on constrained devices — see :func:`_effective_model_and_options`.
    """
    settings = settings or get_settings()
    model, num_ctx, num_predict = _effective_model_and_options(settings, model)
    temperature = settings.temperature if temperature is None else temperature
    allow_cloud = settings.allow_cloud_fallback if allow_cloud is None else allow_cloud

    status = check_ollama(settings)
    if status.reachable:
        if not status.has_model(model):
            logger.warning(
                "Ollama is up but model %r is not pulled. Run: ollama pull %s", model, model
            )
        # Resolve to an installed tag (e.g. llama3.2 -> llama3.2:3b) so the call succeeds.
        model = status.resolve(model)
        ollama_kwargs: dict = {
            "model": model,
            "base_url": settings.ollama_base_url,
            "temperature": temperature,
            "num_ctx": num_ctx,
            "client_kwargs": {"timeout": settings.request_timeout},
        }
        if num_predict is not None:
            ollama_kwargs["num_predict"] = num_predict
        ollama_kwargs.update(kwargs)
        return ChatOllama(**ollama_kwargs)

    if allow_cloud and settings.has_cloud_fallback:
        logger.warning("Ollama unreachable (%s); falling back to cloud.", status.detail)
        return _cloud_chat_model(settings, temperature=temperature, **kwargs)

    raise RuntimeError(
        "Ollama is not reachable at "
        f"{settings.ollama_base_url}. Start it with `ollama serve` and "
        f"`ollama pull {model}`. ({status.detail})"
    )


def _cloud_chat_model(settings: Settings, *, temperature: float, **kwargs) -> BaseChatModel:
    """OpenAI-compatible free-model fallback (Groq, else OpenRouter)."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Cloud fallback requires langchain-openai: pip install langchain-openai"
        ) from exc

    if settings.groq_api_key:
        return ChatOpenAI(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=temperature,
            **kwargs,
        )
    return ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct:free",
        api_key=settings.openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
        **kwargs,
    )
