from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator


class ProviderError(Exception):
    pass


@dataclass
class ChatMessage:
    role: str  # "system" | "user" | "assistant"
    content: str

    def as_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


class Provider(ABC):
    """LLM provider interface: chat + embeddings.

    Implementations are synchronous; FastAPI runs sync endpoints and
    background tasks in its threadpool, so this keeps the whole app simple.
    """

    name: str = "base"
    llm_model: str = ""
    embed_model: str = ""

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion and return the full reply text."""

    @abstractmethod
    def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """Yield reply text deltas as they arrive."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts; returns one vector per input text."""
