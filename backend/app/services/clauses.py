"""Clause extraction: reuse structural section parsing, classify each section
with the LLM, then store clauses with embeddings for the compare feature."""

import math
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import CLAUSE_TYPES, Clause, Document
from app.services.chunking import parse_sections
from app.services.extraction import extract_pages
from app.services.llm import ChatMessage, ask_json, get_provider
from pathlib import Path

_MIN_SECTION_CHARS = 150
_MAX_SECTION_CHARS = 12000
_SNIPPET_CHARS = 700
_EMBED_TEXT_CHARS = 1500


class ClassifiedSection(BaseModel):
    index: int
    is_clause: bool = False
    clause_type: str = "other"
    title: str = ""


class ClassificationBatch(BaseModel):
    sections: list[ClassifiedSection] = Field(default_factory=list)


def _prompt(sections: list) -> str:
    lines = [
        "Classify which of the following numbered document sections are substantive "
        "contract clauses. Ignore boilerplate like tables of contents, signature "
        "blocks, or recitals (set is_clause=false for those).\n"
        f"Allowed clause_type values: {', '.join(CLAUSE_TYPES)}. Pick the closest "
        "match; use 'other' only when nothing fits.\n"
    ]
    for i, s in enumerate(sections):
        header = s.section_path or "Preamble"
        snippet = s.text.strip()[:_SNIPPET_CHARS]
        lines.append(f"### SECTION {i}\nHeader: {header}\n{snippet}\n")
    lines.append(
        'Reply with ONLY JSON: {"sections": [{"index": <the section number>, '
        '"is_clause": true/false, "clause_type": "<type>", "title": "<short title>"}]} '
        "- include an entry for every section."
    )
    return "\n".join(lines)


def _batched(sections: list, max_chars: int) -> list[list]:
    batches: list[list] = []
    buf: list = []
    size = 0
    for s in sections:
        if buf and size + len(s.text) > max_chars:
            batches.append(buf)
            buf, size = [], 0
        buf.append(s)
        size += len(s.text)
    if buf:
        batches.append(buf)
    return batches


def extract_clauses(session: Session, doc: Document, *, refresh: bool = False) -> list[Clause]:
    existing = session.query(Clause).filter(Clause.document_id == doc.id).all()
    if existing and not refresh:
        return existing

    provider = get_provider()
    pages = extract_pages(Path(doc.file_path), doc.mime)
    sections = [
        s
        for s in parse_sections(pages)
        if _MIN_SECTION_CHARS <= len(s.text.strip()) <= _MAX_SECTION_CHARS
    ]
    clauses: list[Clause] = []
    seq = 0
    for batch in _batched(sections, 10000):
        result = ask_json(
            provider,
            [
                ChatMessage(
                    role="system",
                    content=(
                        "You classify sections of legal documents. Reply with ONLY "
                        "the requested JSON."
                    ),
                ),
                ChatMessage(role="user", content=_prompt(batch)),
            ],
            ClassificationBatch,
        )
        by_index = {c.index: c for c in result.sections}
        for i, s in enumerate(batch):
            classified = by_index.get(i)
            if not classified or not classified.is_clause:
                continue
            clause_type = classified.clause_type if classified.clause_type in CLAUSE_TYPES else "other"
            clauses.append(
                Clause(
                    document_id=doc.id,
                    seq=seq,
                    clause_type=clause_type,
                    title=classified.title or s.section_path,
                    page_start=s.page_start,
                    page_end=s.page_end,
                    section_path=s.section_path,
                    text=s.text.strip()[:6000],
                )
            )
            seq += 1

    if clauses:
        embeddings = provider.embed(
            [f"{c.title}\n{c.text[:_EMBED_TEXT_CHARS]}" for c in clauses]
        )
        for clause, vec in zip(clauses, embeddings):
            clause.embedding = vec

    session.query(Clause).filter(Clause.document_id == doc.id).delete()
    for clause in clauses:
        session.add(clause)
    session.commit()
    return session.query(Clause).filter(Clause.document_id == doc.id).order_by(Clause.seq).all()


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _clause_dict(c: Clause, text_limit: int = 800) -> dict[str, Any]:
    return {
        "id": str(c.id),
        "clause_type": c.clause_type,
        "title": c.title,
        "page_start": c.page_start,
        "page_end": c.page_end,
        "section_path": c.section_path,
        "text": c.text[:text_limit],
    }
