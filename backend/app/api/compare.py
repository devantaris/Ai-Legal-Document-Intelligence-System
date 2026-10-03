from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, owned_document
from app.models import User
from app.schemas import CompareIn
from app.services.compare import compare_documents
from app.services.llm import provider_info

router = APIRouter(tags=["compare"])


@router.post("/compare")
def compare(
    payload: CompareIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if payload.document_a_id == payload.document_b_id:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Pick two different documents to compare"
        )
    doc_a = owned_document(payload.document_a_id, user, db)
    doc_b = owned_document(payload.document_b_id, user, db)
    return compare_documents(db, user.id, doc_a, doc_b)


@router.get("/settings/llm")
def llm_settings(user: User = Depends(get_current_user)) -> dict:
    return provider_info()
