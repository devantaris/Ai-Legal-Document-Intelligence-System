import json
from typing import Any, Iterator

import httpx

from app.core.config import settings
from app.services.llm.base import ChatMessage, Provider, ProviderError

Timeout = httpx.Timeout(300.0, connect=10.0)


class OllamaProvider(Provider):
    """Local models via Ollama (https://ollama.com)."""

    name = "ollama"

    def __init__(self) -> None:
        self.llm_model = settings.OLLAMA_LLM_MODEL
        self.embed_model = settings.OLLAMA_EMBED_MODEL
        self._client = httpx.Client(
            base_url=settings.OLLAMA_BASE_URL.rstrip("/"), timeout=Timeout
        )

    def _payload(self, messages: list[ChatMessage], temperature: float, stream: bool) -> dict[str, Any]:
        return {
            "model": self.llm_model,
            "messages": [m.as_dict() for m in messages],
            "stream": stream,
            "options": {"temperature": temperature},
        }

    def _error(self, exc: httpx.HTTPError) -> ProviderError:
        return ProviderError(
            f"Ollama request failed: {exc}. Is Ollama running at "
            f"{settings.OLLAMA_BASE_URL} (try `ollama serve`)?"
        )

    def chat(self, messages, *, temperature=0.2, max_tokens=None) -> str:
        try:
            resp = self._client.post(
                "/api/chat", json=self._payload(messages, temperature, stream=False)
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise self._error(exc) from exc
        data = resp.json()
        try:
            return data["message"]["content"] or ""
        except KeyError as exc:
            raise ProviderError(f"Unexpected Ollama reply: {str(data)[:300]}") from exc

    def stream_chat(self, messages, *, temperature=0.2, max_tokens=None) -> Iterator[str]:
        try:
            with self._client.stream(
                "POST", "/api/chat", json=self._payload(messages, temperature, stream=True)
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    content = chunk.get("message", {}).get("content")
                    if content:
                        yield content
                    if chunk.get("done"):
                        break
        except httpx.HTTPError as exc:
            raise self._error(exc) from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            resp = self._client.post(
                "/api/embed", json={"model": self.embed_model, "input": texts}
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise self._error(exc) from exc
        data = resp.json()
        vectors = data.get("embeddings")
        if not isinstance(vectors, list) or len(vectors) != len(texts):
            raise ProviderError(f"Unexpected Ollama embedding reply: {str(data)[:300]}")
        return vectors
