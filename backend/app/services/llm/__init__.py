from functools import lru_cache
from typing import Iterator, TypeVar

from pydantic import BaseModel

from app.core.config import settings
from app.services.json_utils import extract_json
from app.services.llm.base import ChatMessage, Provider, ProviderError
from app.services.llm.ollama import OllamaProvider
from app.services.llm.zai import ZaiProvider

T = TypeVar("T", bound=BaseModel)

__all__ = [
    "ChatMessage",
    "Provider",
    "ProviderError",
    "get_provider",
    "provider_info",
    "ask_json",
]


@lru_cache
def get_provider() -> Provider:
    name = settings.LLM_PROVIDER.strip().lower()
    if name == "zai":
        return ZaiProvider()
    if name == "ollama":
        return OllamaProvider()
    raise ProviderError(f"Unknown LLM_PROVIDER '{name}' (expected 'zai' or 'ollama')")


def provider_info() -> dict:
    try:
        p = get_provider()
        return {
            "provider": p.name,
            "llm_model": p.llm_model,
            "embed_model": p.embed_model,
            "embedding_dim": settings.EMBEDDING_DIM,
            "available": True,
            "error": None,
        }
    except ProviderError as exc:
        return {
            "provider": settings.LLM_PROVIDER,
            "llm_model": None,
            "embed_model": None,
            "embedding_dim": settings.EMBEDDING_DIM,
            "available": False,
            "error": str(exc),
        }


def ask_json(
    provider: Provider,
    messages: list[ChatMessage],
    schema_cls: type[T],
    *,
    temperature: float = 0.1,
    max_retries: int = 1,
) -> T:
    """Chat + parse a pydantic-validated JSON reply, retrying once on bad output."""
    msgs = list(messages)
    last_error: Exception | None = None
    for _ in range(max_retries + 1):
        text = provider.chat(msgs, temperature=temperature)
        try:
            return schema_cls.model_validate(extract_json(text))
        except Exception as exc:  # noqa: BLE001 - any parse/validation failure retries
            last_error = exc
            msgs = msgs + [
                ChatMessage(role="assistant", content=text),
                ChatMessage(
                    role="user",
                    content=(
                        f"Your previous reply could not be parsed as JSON matching the "
                        f"requested schema ({exc}). Reply again with ONLY the JSON, "
                        f"no prose and no code fences."
                    ),
                ),
            ]
    raise ProviderError(f"LLM failed to produce valid JSON: {last_error}")
