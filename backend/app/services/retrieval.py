"""Hybrid retrieval: pgvector cosine search + PostgreSQL full-text search,
fused with Reciprocal Rank Fusion. Pure vector search is weak on legal text
(exact defined terms, section numbers), so both channels matter."""

import uuid
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Chunk, Document
from app.services.llm import get_provider

_RRF_K = 60
ALL_CHANNELS = frozenset({"vector", "fts"})


@dataclass
class Retrieved:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    seq: int
    text: str
    section_path: str
    page_start: int | None
    page_end: int | None
    score: float


def retrieve(
    session: Session,
    user_id: uuid.UUID,
    query: str,
    *,
    document_ids: list[uuid.UUID] | None = None,
    top_k: int | None = None,
    channels: AbstractSet[str] | None = None,
) -> list[Retrieved]:
    k = top_k or settings.RETRIEVAL_TOP_K
    pool = max(k * 4, 16)
    active = ALL_CHANNELS if channels is None else ALL_CHANNELS & channels

    base = (
        select(Chunk, Document.filename)
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.user_id == user_id)
    )
    if document_ids:
        base = base.where(Chunk.document_id.in_(document_ids))

    vec_rows: list = []
    if "vector" in active:
        provider = get_provider()
        qvec = provider.embed([query])[0]
        vec_rows = session.execute(
            base.order_by(Chunk.embedding.cosine_distance(qvec)).limit(pool)
        ).all()

    fts_rows: list = []
    if "fts" in active:
        tsq = func.plainto_tsquery("english", query)
        fts_rows = session.execute(
            base.where(Chunk.tsv.op("@@")(tsq))
            .order_by(func.ts_rank(Chunk.tsv, tsq).desc())
            .limit(pool)
        ).all()

    fused: dict[uuid.UUID, list] = {}  # id -> [score, chunk, filename]
    for rank, (chunk, filename) in enumerate(vec_rows, start=1):
        fused[chunk.id] = [1.0 / (_RRF_K + rank), chunk, filename]
    for rank, (chunk, filename) in enumerate(fts_rows, start=1):
        if chunk.id in fused:
            fused[chunk.id][0] += 1.0 / (_RRF_K + rank)
        else:
            fused[chunk.id] = [1.0 / (_RRF_K + rank), chunk, filename]

    ranked = sorted(fused.values(), key=lambda item: -item[0])[:k]
    return [
        Retrieved(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename=filename,
            seq=chunk.seq,
            text=chunk.text,
            section_path=chunk.section_path,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            score=score,
        )
        for score, chunk, filename in ranked
    ]
