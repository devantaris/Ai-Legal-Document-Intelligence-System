"""Bridge from LegalIQ's chunking + hybrid retrieval to the LegalBench-RAG
protocol.

Ingestion deliberately deviates from the app path in one documented way: each
corpus file is chunked as a *single page*, so the chunker's character offsets
are original-file offsets (the app's virtual ~3.5k-page split for .txt exists
for page-citation purposes and is orthogonal to retrieval quality). Everything
else — structure-aware chunking parameters, embedding model, hybrid fusion —
is exactly the system users run.

Ingestion is idempotent: documents already present with a matching chunk count
are reused (no re-embedding), so k-sweeps and channel ablations re-run cheaply.
"""

import time
import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Chunk, Document, User
from app.services.chunking import build_chunks
from app.services.llm import get_provider
from app.services.retrieval import ALL_CHANNELS, Retrieved, retrieve

EVAL_USER_EMAIL = "eval@legaliq.local"
_EMBED_BATCH = 64


class LegalIQRetrieval:
    """Ingest a corpus once, then answer ranked-span queries against it."""

    def __init__(self, channels: set[str] | None = None) -> None:
        if channels is not None and not channels <= set(ALL_CHANNELS):
            raise ValueError(f"unknown channels: {channels}")
        self.channels = channels
        self.user_id: uuid.UUID | None = None
        self._span_by_chunk: dict[uuid.UUID, tuple[int, int]] = {}

    def ensure_user(self, db: Session) -> None:
        user = db.scalar(select(User).where(User.email == EVAL_USER_EMAIL))
        if user is None:
            user = User(email=EVAL_USER_EMAIL, password_hash="!eval-no-login")
            db.add(user)
            db.commit()
        self.user_id = user.id

    def ingest_corpus(
        self, corpus: dict[str, str], *, fresh: bool = False
    ) -> dict[str, int]:
        stats = {"docs": len(corpus), "reused_docs": 0, "embedded_chunks": 0}
        provider = get_provider()
        started = time.perf_counter()

        for file_path in sorted(corpus):
            content = corpus[file_path]
            chunks_data = build_chunks(
                [content],
                max_tokens=settings.CHUNK_TOKENS,
                overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
            )
            db: Session = SessionLocal()
            try:
                doc = db.scalar(
                    select(Document).where(
                        Document.user_id == self.user_id,
                        Document.filename == file_path,
                    )
                )
                if doc is not None and not fresh:
                    existing = (
                        db.execute(
                            select(Chunk)
                            .where(Chunk.document_id == doc.id)
                            .order_by(Chunk.seq)
                        )
                        .scalars()
                        .all()
                    )
                    if len(existing) == len(chunks_data):
                        for row in existing:
                            cd = chunks_data[row.seq]
                            self._span_by_chunk[row.id] = (cd.char_start, cd.char_end)
                        stats["reused_docs"] += 1
                        continue

                if doc is None:
                    doc = Document(
                        user_id=self.user_id,
                        filename=file_path,
                        file_path="",  # corpus content is ingested from memory
                        mime="text/plain",
                        size_bytes=len(content.encode("utf-8")),
                        status="ready",
                    )
                    db.add(doc)
                    db.flush()
                else:
                    db.execute(delete(Chunk).where(Chunk.document_id == doc.id))
                    db.flush()

                embeddings: list[list[float]] = []
                for i in range(0, len(chunks_data), _EMBED_BATCH):
                    batch = [c.text for c in chunks_data[i : i + _EMBED_BATCH]]
                    embeddings.extend(provider.embed(batch))
                stats["embedded_chunks"] += len(chunks_data)

                for seq, (cd, vec) in enumerate(zip(chunks_data, embeddings)):
                    chunk = Chunk(
                        document_id=doc.id,
                        seq=seq,
                        page_start=cd.page_start,
                        page_end=cd.page_end,
                        section_path=cd.section_path,
                        text=cd.text,
                        embedding=vec,
                    )
                    db.add(chunk)
                    db.flush()
                    self._span_by_chunk[chunk.id] = (cd.char_start, cd.char_end)
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

        stats["embed_seconds"] = round(time.perf_counter() - started, 1)
        return stats

    def ranked_spans(self, query: str, *, top_k: int) -> list[Retrieved]:
        db: Session = SessionLocal()
        try:
            return retrieve(
                db,
                self.user_id,
                query,
                top_k=top_k,
                channels=self.channels,
            )
        finally:
            db.close()

    def span_of(self, retrieved: Retrieved) -> tuple[int, int] | None:
        """Character span of a retrieved chunk in its original corpus file."""
        return self._span_by_chunk.get(retrieved.chunk_id)
