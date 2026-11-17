import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_org, get_current_user, owned_document
from app.models import ClauseDecision, Document, Organization, Playbook, User
from app.schemas import (
    ClauseOut,
    KeyTermsOut,
    PlaybookReviewOut,
    PlaybookRule,
    SummaryOut,
)
from app.schemas.defined_terms import DefinedTermsSummaryOut
from app.services.clauses import extract_clauses
from app.services.defined_terms import extract_defined_terms
from app.services.key_terms import generate_key_terms
from app.services.playbook import DEFAULT_PLAYBOOK_RULES, review_document_playbook
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


@router.get("/documents/{doc_id}/playbook-review", response_model=PlaybookReviewOut)
def get_playbook_review(
    doc_id: uuid.UUID,
    playbook_id: uuid.UUID | None = Query(None),
    refresh: bool = Query(default=False),
    user: User = Depends(get_current_user),
    org: Organization = Depends(get_current_org),
    db: Session = Depends(get_db),
) -> PlaybookReviewOut:
    doc = _ready_document(doc_id, user, db)

    rules: dict[str, PlaybookRule] | None = None
    pb_name = "Institutional Commercial Standard"
    resolved_pb_id: uuid.UUID | None = None

    if playbook_id:
        pb = db.get(Playbook, playbook_id)
        if pb and pb.org_id == org.id:
            resolved_pb_id = pb.id
            pb_name = pb.name
            rules = {
                k: PlaybookRule.model_validate(v)
                for k, v in pb.rules.items()
                if isinstance(v, dict)
            }
    elif doc.org_id:
        default_pb = (
            db.query(Playbook)
            .filter(Playbook.org_id == doc.org_id, Playbook.is_default == True)
            .first()
        )
        if default_pb and default_pb.rules:
            resolved_pb_id = default_pb.id
            pb_name = default_pb.name
            rules = {
                k: PlaybookRule.model_validate(v)
                for k, v in default_pb.rules.items()
                if isinstance(v, dict)
            }

    review = review_document_playbook(db, doc, rules=rules, refresh=refresh)
    review.playbook_id = resolved_pb_id
    review.playbook_name = pb_name

    # Attach recorded attorney review decisions
    decisions = {
        d.clause_type: d
        for d in db.query(ClauseDecision).filter(ClauseDecision.document_id == doc.id).all()
    }
    for finding in review.findings:
        if finding.clause_type in decisions:
            d = decisions[finding.clause_type]
            finding.decision = d.decision
            finding.decision_notes = d.notes

    return review


@router.get("/documents/{doc_id}/defined-terms", response_model=DefinedTermsSummaryOut)
def get_defined_terms(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DefinedTermsSummaryOut:
    doc = _ready_document(doc_id, user, db)
    return extract_defined_terms(db, doc)


@router.get("/playbooks/default", response_model=dict[str, PlaybookRule])
def get_default_playbook(
    user: User = Depends(get_current_user),
) -> dict[str, PlaybookRule]:
    return DEFAULT_PLAYBOOK_RULES
