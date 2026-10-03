import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, owned_document
from app.models import Document, User
from app.schemas import ClauseOut, KeyTermsOut, SummaryOut
from app.services.clauses import extract_clauses
from app.services.key_terms import generate_key_terms
from app.services.summarization import generate_summary

router = APIRouter(tags=["analysis"])


def _ready_document(doc_id: uuid.UUID, user: User, db: Session) -> Document:
    doc = owned_document(doc_id, user, db)
    if doc.status != "ready":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Document is not ready (status: {doc.status}). Wait for ingestion to finish.",
        )
    return doc


@router.get("/documents/{doc_id}/summary", response_model=SummaryOut)
def get_summary(
    doc_id: uuid.UUID,
    refresh: bool = Query(default=False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SummaryOut:
    doc = _ready_document(doc_id, user, db)
    return SummaryOut(summary_md=generate_summary(db, doc, refresh=refresh))


@router.get("/documents/{doc_id}/key-terms", response_model=KeyTermsOut)
def get_key_terms(
    doc_id: uuid.UUID,
    refresh: bool = Query(default=False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KeyTermsOut:
    doc = _ready_document(doc_id, user, db)
    return KeyTermsOut(data=generate_key_terms(db, doc, refresh=refresh))


@router.get("/documents/{doc_id}/clauses", response_model=list[ClauseOut])
def get_clauses(
    doc_id: uuid.UUID,
    refresh: bool = Query(default=False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ClauseOut]:
    doc = _ready_document(doc_id, user, db)
    clauses = extract_clauses(db, doc, refresh=refresh)
    return [ClauseOut.model_validate(c) for c in clauses]
