"""Executive summary generation (single-pass for short docs, map-reduce for long)."""

from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.services.llm import ChatMessage, get_provider

_SYSTEM_PROMPT = (
    "You are a senior legal analyst. Write clear, neutral executive summaries "
    "of legal documents in GitHub-flavored markdown. Where the provided text "
    "carries page markers like (p. 4), keep those citations in your summary."
)

_FINAL_INSTRUCTIONS = (
    "Write an executive summary with these markdown sections:\n"
    "## Overview\n## Parties\n## Scope & Purpose\n## Key Obligations\n"
    "## Financial Terms\n## Duration & Termination\n## Notable Provisions\n"
    "Keep each section to 1-4 bullet points. Use only information present in "
    "the text; write 'Not specified in the document.' under any empty section."
)

_BATCH_CHARS = 12000
_SINGLE_PASS_LIMIT = 20000


def _chunks_with_markers(session: Session, doc: Document) -> list[str]:
    rows = (
        session.query(Chunk)
        .filter(Chunk.document_id == doc.id)
        .order_by(Chunk.seq)
        .all()
    )
    marked = []
    for c in rows:
        pages = f"(p. {c.page_start})" if c.page_start else ""
        prefix = f"[{c.section_path}] " if c.section_path else ""
        marked.append(f"{prefix}{pages}\n{c.text}")
    return marked


def _batch(items: list[str], max_chars: int) -> list[list[str]]:
    batches: list[list[str]] = []
    buf: list[str] = []
    size = 0
    for item in items:
        if buf and size + len(item) > max_chars:
            batches.append(buf)
            buf, size = [], 0
        buf.append(item)
        size += len(item)
    if buf:
        batches.append(buf)
    return batches


def generate_summary(session: Session, doc: Document, *, refresh: bool = False) -> str:
    if doc.summary_md and not refresh:
        return doc.summary_md

    provider = get_provider()
    marked = _chunks_with_markers(session, doc)

    if sum(len(m) for m in marked) <= _SINGLE_PASS_LIMIT:
        reply = provider.chat(
            [
                ChatMessage(role="system", content=_SYSTEM_PROMPT),
                ChatMessage(
                    role="user",
                    content=(
                        f"Summarize this legal document.\n\n{_FINAL_INSTRUCTIONS}\n\n"
                        f"---\n\nDocument text:\n\n" + "\n\n".join(marked)
                    ),
                ),
            ],
            temperature=0.2,
        )
    else:
        partials: list[str] = []
        for i, batch in enumerate(_batch(marked, _BATCH_CHARS), start=1):
            partials.append(
                provider.chat(
                    [
                        ChatMessage(role="system", content=_SYSTEM_PROMPT),
                        ChatMessage(
                            role="user",
                            content=(
                                "This is part "
                                f"{i} of a long legal document. Extract the key facts, "
                                "obligations, dates, amounts and unusual terms in terse "
                                "bullets. Keep page citations.\n\n"
                                + "\n\n".join(batch)
                            ),
                        ),
                    ],
                    temperature=0.2,
                )
            )
        reply = provider.chat(
            [
                ChatMessage(role="system", content=_SYSTEM_PROMPT),
                ChatMessage(
                    role="user",
                    content=(
                        "These are section-by-section notes from one long legal "
                        f"document.\n\n{_FINAL_INSTRUCTIONS}\n\n---\n\nNotes:\n\n"
                        + "\n\n".join(partials)
                    ),
                ),
            ],
            temperature=0.2,
        )

    doc.summary_md = reply
    session.commit()
    return reply
