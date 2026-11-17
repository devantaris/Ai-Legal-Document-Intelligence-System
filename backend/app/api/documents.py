import json
import shutil
import time
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import (
    get_current_member,
    get_current_org,
    get_current_user,
    get_current_workspace,
    owned_document,
)
from app.models import Chunk, Clause, Document, OrgRole, Organization, OrganizationMember, User, Workspace
from app.schemas import ChunkLite, DocumentContentOut, DocumentOut
from app.services.docx_export import generate_redline_docx
from app.services.extraction import is_supported
from app.services.ingestion import run_ingestion
from app.services.storage import get_storage
from app.workers.queue import enqueue_ingestion_task, get_task_progress

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
        org_id=doc.org_id,
        workspace_id=doc.workspace_id,
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
    org: Organization = Depends(get_current_org),
    workspace: Workspace = Depends(get_current_workspace),
    member: OrganizationMember = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> DocumentOut:
    if member.role == OrgRole.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot upload documents",
        )

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

    safe_filename = Path(file.filename).name
    mime_type = file.content_type or "application/octet-stream"

    doc = Document(
        user_id=user.id,
        org_id=org.id,
        workspace_id=workspace.id,
        filename=safe_filename,
        file_path="",
        mime=mime_type,
        size_bytes=len(data),
        status="uploaded",
    )
    db.add(doc)
    db.flush()

    # Save via unified StorageService (Local or S3)
    storage = get_storage()
    rel_path = f"{user.id}/{doc.id}/{safe_filename}"
    stored_path = storage.save(rel_path, data, mime=mime_type)
    doc.file_path = stored_path
    db.commit()
    db.refresh(doc)

    # Sovereign Worker Queue dispatch: Redis worker or fallback threadpool
    if getattr(settings, "ASYNC_WORKER_ENABLED", False):
        enqueued = enqueue_ingestion_task(doc.id)
        if not enqueued:
            background.add_task(run_ingestion, doc.id)
    else:
        background.add_task(run_ingestion, doc.id)

    return _doc_out(db, doc)


@router.get("", response_model=list[DocumentOut])
def list_documents(
    workspace_id: uuid.UUID | None = Query(None),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_org),
    db: Session = Depends(get_db),
) -> list[DocumentOut]:
    """List documents for the active organization, optionally filtered by workspace."""
    query = db.query(Document).filter(
        or_(
            Document.org_id == org.id,
            Document.user_id == user.id,
        )
    )
    if workspace_id:
        query = query.filter(Document.workspace_id == workspace_id)

    docs = query.order_by(Document.created_at.desc()).all()
    return [_doc_out(db, d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc: Document = Depends(owned_document),
    db: Session = Depends(get_db),
) -> DocumentOut:
    return _doc_out(db, doc)


@router.get("/{doc_id}/progress")
def get_progress(
    doc: Document = Depends(owned_document),
):
    """Retrieve real-time processing stage and percentage from worker pipeline."""
    prog = get_task_progress(doc.id)
    if prog:
        return prog
    return {
        "document_id": str(doc.id),
        "status": doc.status,
        "step": doc.error if doc.status == "failed" else ("Ready" if doc.status == "ready" else "Processing"),
        "progress_pct": 100 if doc.status == "ready" else (0 if doc.status == "failed" else 30),
    }


@router.get("/{doc_id}/progress-stream")
def stream_progress(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SSE stream yielding real-time ingestion stage updates."""
    doc = owned_document(doc_id, user, db)

    def event_generator():
        last_pct = -1
        while True:
            prog = get_task_progress(doc.id)
            if not prog:
                db.refresh(doc)
                prog = {
                    "document_id": str(doc.id),
                    "status": doc.status,
                    "step": "Processing in sovereign worker",
                    "progress_pct": 100 if doc.status == "ready" else (0 if doc.status == "failed" else 50),
                }
            if prog.get("progress_pct") != last_pct:
                last_pct = prog.get("progress_pct", 0)
                yield f"data: {json.dumps(prog)}\n\n"

            if prog.get("status") in ("ready", "failed"):
                break
            time.sleep(0.8)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{doc_id}/content", response_model=DocumentContentOut)
def get_document_content(
    doc: Document = Depends(owned_document),
    db: Session = Depends(get_db),
) -> DocumentContentOut:
    chunks = (
        db.query(Chunk)
        .filter(Chunk.document_id == doc.id)
        .order_by(Chunk.seq)
        .all()
    )
    return DocumentContentOut(
        id=doc.id,
        filename=doc.filename,
        page_count=doc.page_count,
        chunks=[ChunkLite.model_validate(c) for c in chunks],
    )


@router.get("/{doc_id}/export-redline-docx")
def export_redline_docx(
    doc: Document = Depends(owned_document),
    db: Session = Depends(get_db),
):
    buffer = generate_redline_docx(db, doc)
    safe_name = Path(doc.filename).stem
    filename = f"{safe_name}_LegalIQ_Redline.docx"
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc: Document = Depends(owned_document),
    member: OrganizationMember = Depends(get_current_member),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if member.role == OrgRole.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot delete documents",
        )

    storage = get_storage()
    try:
        storage.delete(doc.file_path)
    except Exception:
        pass

    db.delete(doc)
    db.commit()
