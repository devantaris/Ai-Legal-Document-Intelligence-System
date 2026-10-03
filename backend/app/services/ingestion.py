"""Background ingestion: extract -> chunk -> embed -> store."""

import uuid
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Chunk, Document
from app.services.chunking import build_chunks
from app.services.extraction import extract_pages
from app.services.llm import ProviderError, get_provider

_EMBED_BATCH = 64


def run_ingestion(document_id: uuid.UUID) -> None:
    """Runs in a FastAPI BackgroundTask with its own DB session."""
    db: Session = SessionLocal()
    try:
        doc = db.get(Document, document_id)
        if doc is None:
            return
        try:
            doc.status = "parsing"
            doc.error = None
            db.commit()

            pages = extract_pages(Path(doc.file_path), doc.mime)
            doc.page_count = len(pages)
            chunks_data = build_chunks(
                pages,
                max_tokens=settings.CHUNK_TOKENS,
                overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
            )
            if not chunks_data:
                raise ValueError("No text content could be extracted from the document")

            doc.status = "embedding"
            db.commit()

            provider = get_provider()
            db.execute(delete(Chunk).where(Chunk.document_id == doc.id))

            embeddings: list[list[float]] = []
            for i in range(0, len(chunks_data), _EMBED_BATCH):
                batch = [c.text for c in chunks_data[i : i + _EMBED_BATCH]]
                embeddings.extend(provider.embed(batch))

            for seq, (cd, vec) in enumerate(zip(chunks_data, embeddings)):
                db.add(
                    Chunk(
                        document_id=doc.id,
                        seq=seq,
                        page_start=cd.page_start,
                        page_end=cd.page_end,
                        section_path=cd.section_path,
                        text=cd.text,
                        embedding=vec,
                    )
                )
            doc.status = "ready"
            db.commit()
        except ProviderError as exc:
            db.rollback()
            _mark_failed(db, document_id, str(exc))
        except Exception as exc:  # noqa: BLE001 - background task must not raise
            db.rollback()
            _mark_failed(db, document_id, f"{type(exc).__name__}: {exc}")
    finally:
        db.close()


def _mark_failed(db: Session, document_id: uuid.UUID, message: str) -> None:
    doc = db.get(Document, document_id)
    if doc is not None:
        doc.status = "failed"
        doc.error = message[:2000]
        db.commit()
