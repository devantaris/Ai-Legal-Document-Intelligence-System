"""Background ingestion: extract -> chunk -> embed -> store with real-time stage progress."""

import tempfile
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
from app.services.storage import LocalStorage, get_storage
from app.workers.queue import publish_task_progress

_EMBED_BATCH = 64


def run_ingestion(document_id: uuid.UUID) -> None:
    """Ingestion pipeline executing either in a distributed worker or FastAPI background task."""
    db: Session = SessionLocal()
    temp_file_path: Path | None = None
    try:
        doc = db.get(Document, document_id)
        if doc is None:
            return
        try:
            doc.status = "parsing"
            doc.error = None
            db.commit()

            publish_task_progress(
                document_id=doc.id,
                status="parsing",
                step="Extracting text and section structure",
                progress_pct=20,
            )

            # Resolve local file for extractor
            storage = get_storage()
            doc_path = Path(doc.file_path)
            if doc_path.is_file():
                local_path = doc_path
            elif not doc_path.is_absolute() and (settings.storage_path / doc_path).is_file():
                local_path = settings.storage_path / doc_path
            else:
                file_bytes = storage.read(doc.file_path)
                suffix = Path(doc.filename).suffix or ".pdf"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp.write(file_bytes)
                    local_path = Path(tmp.name)
                    temp_file_path = local_path

            pages = extract_pages(local_path, doc.mime)
            doc.page_count = len(pages)
            chunks_data = build_chunks(
                pages,
                max_tokens=settings.CHUNK_TOKENS,
                overlap_tokens=settings.CHUNK_OVERLAP_TOKENS,
            )
            if not chunks_data:
                raise ValueError("No text content could be extracted from the document")

            publish_task_progress(
                document_id=doc.id,
                status="parsing",
                step=f"Extracted {len(pages)} pages; structured into {len(chunks_data)} sections",
                progress_pct=45,
            )

            doc.status = "embedding"
            db.commit()

            publish_task_progress(
                document_id=doc.id,
                status="embedding",
                step="Computing sovereign dense vector representations",
                progress_pct=70,
            )

            provider = get_provider()
            db.execute(delete(Chunk).where(Chunk.document_id == doc.id))

            embeddings: list[list[float]] = []
            for i in range(0, len(chunks_data), _EMBED_BATCH):
                batch = [c.text for c in chunks_data[i : i + _EMBED_BATCH]]
                embeddings.extend(provider.embed(batch))

            publish_task_progress(
                document_id=doc.id,
                status="embedding",
                step="Indexing chunks & defined terms into database",
                progress_pct=90,
            )

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

            publish_task_progress(
                document_id=doc.id,
                status="ready",
                step="Ingestion complete. Contract ready for institutional review.",
                progress_pct=100,
            )

        except ProviderError as exc:
            db.rollback()
            _mark_failed(db, document_id, str(exc))
        except Exception as exc:  # noqa: BLE001 - background task must not raise
            db.rollback()
            _mark_failed(db, document_id, f"{type(exc).__name__}: {exc}")
    finally:
        if temp_file_path and temp_file_path.is_file():
            try:
                temp_file_path.unlink()
            except Exception:
                pass
        db.close()


def _mark_failed(db: Session, document_id: uuid.UUID, message: str) -> None:
    doc = db.get(Document, document_id)
    if doc is not None:
        doc.status = "failed"
        doc.error = message[:2000]
        db.commit()
    publish_task_progress(
        document_id=document_id,
        status="failed",
        step=f"Failed: {message[:120]}",
        progress_pct=0,
    )
