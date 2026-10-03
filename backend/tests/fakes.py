"""Deterministic in-memory LLM provider for tests.

- embed(): bag-of-words hashing vectors (identical text -> identical vector,
  overlapping vocabulary -> similar vectors), sized to EMBEDDING_DIM.
- chat(): dispatches on the prompt shape and returns canned JSON for the
  structured endpoints, prose otherwise.
"""

import hashlib
import json
import math
import re

from app.core.config import settings
from app.services.llm.base import ChatMessage, Provider


class FakeProvider(Provider):
    name = "fake"
    llm_model = "fake-llm"
    embed_model = "fake-embed"

    def __init__(self) -> None:
        self.chat_calls: list[list[ChatMessage]] = []

    # -- embeddings ---------------------------------------------------------
    def embed(self, texts: list[str]) -> list[list[float]]:
        dim = settings.EMBEDDING_DIM
        vectors: list[list[float]] = []
        for text in texts:
            vec = [0.0] * dim
            for word in re.findall(r"[a-z0-9]+", text.lower()):
                digest = int(hashlib.md5(word.encode()).hexdigest(), 16)
                vec[digest % dim] += 1.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vectors.append([x / norm for x in vec])
        return vectors

    # -- chat ---------------------------------------------------------------
    def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> str:
        self.chat_calls.append(messages)
        return self._respond(messages[-1].content)

    def stream_chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ):
        for word in self._respond(messages[-1].content).split(" "):
            yield word + " "

    # -- canned replies ------------------------------------------------------
    def _respond(self, prompt: str) -> str:
        if "### SECTION" in prompt and '"sections"' in prompt:
            indices = [int(n) for n in re.findall(r"### SECTION (\d+)", prompt)]
            sections = [
                {
                    "index": i,
                    "is_clause": True,
                    "clause_type": "termination" if i % 2 == 0 else "confidentiality",
                    "title": f"Clause {i}",
                }
                for i in indices
            ]
            return json.dumps({"sections": sections})
        if "Extract the following" in prompt or "Fill in ONLY these fields" in prompt:
            return json.dumps(
                {
                    "agreement_type": "Mutual Non-Disclosure Agreement",
                    "parties": [{"name": "Acme Corp", "role": "Disclosing Party"}],
                    "effective_date": "January 1, 2024",
                    "term": "Two years",
                    "governing_law": "Delaware",
                    "payment_terms": None,
                    "termination": "30 days written notice",
                    "renewal": None,
                    "confidentiality": "Standard mutual obligations for 3 years",
                    "indemnification": None,
                    "dispute_resolution": "Arbitration in New York",
                    "obligations": ["Protect confidential information"],
                    "special_notes": [],
                }
            )
        if "### PAIR" in prompt:
            indices = [int(n) for n in re.findall(r"### PAIR (\d+)", prompt)]
            return json.dumps(
                {
                    "pairs": [
                        {
                            "index": i,
                            "change_level": "moderate",
                            "change_summary": "The clause wording changed materially.",
                        }
                        for i in indices
                    ]
                }
            )
        if '{"summary"' in prompt:
            return json.dumps(
                {"summary": "The payment clause changed materially between the versions."}
            )
        return (
            "Based on the provided context [1], either party may terminate with "
            "30 days' written notice."
        )
