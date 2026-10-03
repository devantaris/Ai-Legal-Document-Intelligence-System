import shutil
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, owned_document
from app.models import Chunk, Clause, Document, User
from app.schemas import DocumentOut
from app.services.extraction import is_supported
from app.services.ingestion import run_ingestion

router = APIRouter(prefix="/documents", tags=["documents"])


def _doc_out(db: Session, doc: Document) -> DocumentOut:
    chunk_count = db.scalar(
        select(func.count(Chunk.id)).where(Chunk.document_id == doc.id)
    )
    clause_count = db.scalar(
        select(func.count(Clause.id)).where(Clause.document_id == doc.id)
    )
    return DocumentOut(
        id=doc.id,
        filename=doc.filename,
        mime=doc.mime,
        status=doc.status,
        page_count=doc.page_count,
        size_bytes=doc.size_bytes,
        error=doc.error,
        has_summary=bool(doc.summary_md),
        has_key_terms=bool(doc.key_terms),
        clause_count=clause_count or 0,
        chunk_count=chunk_count or 0,
        created_at=doc.created_at,
    )


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentOut:
    if not file.filename or not is_supported(file.filename):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Unsupported file type. Upload a PDF, DOCX, TXT or MD document.",
        )
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    data = file.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            f"File exceeds the {settings.MAX_UPLOAD_MB} MB limit",
        )
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is empty")

    doc = Document(
        user_id=user.id,
        filename=Path(file.filename).name,
        file_path="",
        mime=file.content_type or "application/octet-stream",
        size_bytes=len(data),
        status="uploaded",
    )
    db.add(doc)
    db.flush()

    target_dir = settings.storage_path / str(user.id) / str(doc.id)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / Path(file.filename).name
    target.write_bytes(data)
    doc.file_path = str(target)
    db.commit()
    db.refresh(doc)

    background.add_task(run_ingestion, doc.id)
    return _doc_out(db, doc)


@router.get("", response_model=list[DocumentOut])
def list_documents(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[DocumentOut]:
    docs = (
        db.query(Document)
        .filter(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [_doc_out(db, d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentOut:
    return _doc_out(db, owned_document(doc_id, user, db))


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    doc = owned_document(doc_id, user, db)
    target_dir = (settings.storage_path / str(user.id) / str(doc.id)).resolve()
    storage_root = settings.storage_path.resolve()
    if target_dir.is_relative_to(storage_root) and target_dir.is_dir():
        shutil.rmtree(target_dir, ignore_errors=True)
    db.delete(doc)
    db.commit()
