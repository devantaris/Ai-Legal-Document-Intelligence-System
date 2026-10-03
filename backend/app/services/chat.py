"""RAG chat: retrieve -> prompt with cited context -> stream the answer."""

import json
import uuid
from collections.abc import Iterator
from typing import Any

from sqlalchemy.orm import Session

from app.models import Conversation, Document, Message
from app.services import retrieval
from app.services.llm import ChatMessage, get_provider

_SYSTEM_PROMPT = (
    "You are a precise legal document assistant. Answer ONLY from the numbered "
    "context passages provided in the conversation. If the context does not "
    "contain the answer, say so plainly - never invent terms, dates or clauses. "
    "Cite sources inline using bracketed numbers like [1] or [2][3] that refer "
    "to the context passages. Quote exact clause language when it matters. Be "
    "concise and structured; use short markdown lists for multi-part answers."
)

_HISTORY_TURNS = 4  # pairs of (user, assistant) kept as chat history


def get_or_create_conversation(session: Session, doc: Document) -> Conversation:
    conv = session.query(Conversation).filter(Conversation.document_id == doc.id).first()
    if conv is None:
        conv = Conversation(document_id=doc.id)
        session.add(conv)
        session.commit()
    return conv


def build_context(retrieved: list[retrieval.Retrieved]) -> tuple[str, list[dict[str, Any]]]:
    blocks: list[str] = []
    citations: list[dict[str, Any]] = []
    for n, r in enumerate(retrieved, start=1):
        if r.page_start is not None:
            loc = f"{r.filename}, p. {r.page_start}" + (
                f"-{r.page_end}" if r.page_end and r.page_end != r.page_start else ""
            )
            if r.section_path:
                loc += f" ({r.section_path})"
        else:
            loc = f"{r.filename}" + (f" ({r.section_path})" if r.section_path else "")
        blocks.append(f"[{n}] {loc}\n{r.text}")
        citations.append(
            {
                "n": n,
                "chunk_id": str(r.chunk_id),
                "document_id": str(r.document_id),
                "filename": r.filename,
                "page": r.page_start,
                "section_path": r.section_path,
                "quote": r.text[:240],
            }
        )
    return "\n\n".join(blocks), citations


def _history_messages(session: Session, conversation: Conversation) -> list[ChatMessage]:
    rows = (
        session.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(_HISTORY_TURNS * 2)
        .all()
    )
    rows.reverse()
    return [ChatMessage(role=m.role, content=m.content) for m in rows]


def _compose_messages(
    history: list[ChatMessage], context: str, question: str
) -> list[ChatMessage]:
    user_msg = ChatMessage(
        role="user",
        content=(
            f"Context passages from the documents:\n\n{context}\n\n---\n\n"
            f"Question: {question}"
        ),
    )
    return [ChatMessage(role="system", content=_SYSTEM_PROMPT), *history, user_msg]


def answer(
    session: Session,
    doc: Document,
    question: str,
) -> dict[str, Any]:
    """Non-streaming answer; persists both messages and returns them."""
    provider = get_provider()
    conversation = get_or_create_conversation(session, doc)
    session.add(Message(conversation_id=conversation.id, role="user", content=question))
    session.commit()

    retrieved = retrieval.retrieve(session, doc.user_id, question, document_ids=[doc.id])
    context, citations = build_context(retrieved)
    messages = _compose_messages(_history_messages(session, conversation), context, question)
    text = provider.chat(messages, temperature=0.2)

    assistant = Message(
        conversation_id=conversation.id, role="assistant", content=text, citations=citations
    )
    session.add(assistant)
    session.commit()
    return {"content": text, "citations": citations}


def stream_answer(
    session: Session,
    doc: Document,
    question: str,
) -> Iterator[str]:
    """SSE event stream: citations -> answer deltas -> done. Persists messages."""
    provider = get_provider()
    conversation = get_or_create_conversation(session, doc)
    session.add(Message(conversation_id=conversation.id, role="user", content=question))
    session.commit()

    retrieved = retrieval.retrieve(session, doc.user_id, question, document_ids=[doc.id])
    context, citations = build_context(retrieved)
    messages = _compose_messages(_history_messages(session, conversation), context, question)

    def _event(payload: dict[str, Any]) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    yield _event({"type": "citations", "citations": citations})

    parts: list[str] = []
    try:
        for delta in provider.stream_chat(messages, temperature=0.2):
            parts.append(delta)
            yield _event({"type": "delta", "text": delta})
    except Exception as exc:  # noqa: BLE001 - surface mid-stream failures to the client
        yield _event({"type": "error", "error": str(exc)})
        return

    assistant = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="".join(parts),
        citations=citations,
    )
    session.add(assistant)
    session.commit()
    yield _event({"type": "done"})
