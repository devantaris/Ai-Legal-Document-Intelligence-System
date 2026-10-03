import json
from typing import Any, Iterator

import httpx

from app.core.config import settings
from app.services.llm.base import ChatMessage, Provider, ProviderError

Timeout = httpx.Timeout(120.0, connect=15.0)


class ZaiProvider(Provider):
    """Z.ai (Zhipu GLM) via the OpenAI-compatible endpoint at api.z.ai."""

    name = "zai"

    def __init__(self) -> None:
        if not settings.ZAI_API_KEY:
            raise ProviderError(
                "ZAI_API_KEY is not set. Add it to your .env or set LLM_PROVIDER=ollama."
            )
        self.llm_model = settings.ZAI_LLM_MODEL
        self.embed_model = settings.ZAI_EMBED_MODEL
        self._client = httpx.Client(
            base_url=settings.ZAI_BASE_URL.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.ZAI_API_KEY}"},
            timeout=Timeout,
        )

    def _payload(self, messages: list[ChatMessage], temperature: float, max_tokens: int | None, stream: bool) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.llm_model,
            "messages": [m.as_dict() for m in messages],
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        return payload

    def _error(self, exc: httpx.HTTPStatusError) -> ProviderError:
        body = exc.response.text[:500]
        return ProviderError(f"Z.ai API error {exc.response.status_code}: {body}")

    def chat(self, messages, *, temperature=0.2, max_tokens=None) -> str:
        try:
            resp = self._client.post(
                "/chat/completions",
                json=self._payload(messages, temperature, max_tokens, stream=False),
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise self._error(exc) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Z.ai request failed: {exc}") from exc
        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Unexpected Z.ai reply shape: {str(data)[:300]}") from exc

    def stream_chat(self, messages, *, temperature=0.2, max_tokens=None) -> Iterator[str]:
        try:
            with self._client.stream(
                "POST",
                "/chat/completions",
                json=self._payload(messages, temperature, max_tokens, stream=True),
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0].get("delta", {})
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
                    content = delta.get("content")
                    if content:
                        yield content
        except httpx.HTTPStatusError as exc:
            raise self._error(exc) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Z.ai request failed: {exc}") from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        payload: dict[str, Any] = {
            "model": self.embed_model,
            "input": texts,
            "dimensions": settings.EMBEDDING_DIM,
        }
        try:
            resp = self._client.post("/embeddings", json=payload)
            if resp.status_code == 400:
                # some embedding endpoints reject the dimensions hint
                payload.pop("dimensions", None)
                resp = self._client.post("/embeddings", json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise self._error(exc) from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"Z.ai request failed: {exc}") from exc
        data = resp.json()
        try:
            items = sorted(data["data"], key=lambda d: d["index"])
            vectors = [item["embedding"] for item in items]
        except (KeyError, TypeError) as exc:
            raise ProviderError(f"Unexpected Z.ai embedding reply: {str(data)[:300]}") from exc
        if len(vectors) != len(texts):
            raise ProviderError(
                f"Embedding count mismatch: sent {len(texts)}, got {len(vectors)}"
            )
        return vectors
