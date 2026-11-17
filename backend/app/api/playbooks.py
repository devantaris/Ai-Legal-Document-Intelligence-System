import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import (
    get_current_member,
    get_current_org,
    get_current_user,
    owned_document,
    require_role,
)
from app.models import (
    ClauseDecision,
    Document,
    OrgRole,
    Organization,
    OrganizationMember,
    Playbook,
    User,
)
from app.schemas.playbook import (
    ClauseDecisionIn,
    ClauseDecisionOut,
    PlaybookCreateIn,
    PlaybookOut,
    PlaybookRule,
    PlaybookUpdateIn,
)
from app.services.playbook import DEFAULT_PLAYBOOK_RULES

router = APIRouter(prefix="/playbooks", tags=["playbooks"])


def _playbook_out(p: Playbook) -> PlaybookOut:
    rules_dict = {}
    if p.rules:
        for k, v in p.rules.items():
            if isinstance(v, dict):
                rules_dict[k] = PlaybookRule.model_validate(v)
    return PlaybookOut(
        id=p.id,
        org_id=p.org_id,
        name=p.name,
        description=p.description,
        is_default=p.is_default,
        rules=rules_dict,
        rule_count=len(rules_dict),
        created_at=p.created_at,
        updated_at=p.updated_at,
    )


def _seed_default_if_none(db: Session, org_id: uuid.UUID) -> None:
    count = db.scalar(select(func.count(Playbook.id)).where(Playbook.org_id == org_id))
    if not count:
        serialized = {k: v.model_dump() for k, v in DEFAULT_PLAYBOOK_RULES.items()}
        default_pb = Playbook(
            org_id=org_id,
            name="Institutional Commercial Standard",
            description="Baseline 10-clause corporate review playbook",
            is_default=True,
            rules=serialized,
        )
        db.add(default_pb)
        db.commit()


@router.get("", response_model=list[PlaybookOut])
def list_playbooks(
    org: Organization = Depends(get_current_org),
    db: Session = Depends(get_db),
) -> list[PlaybookOut]:
    """List all negotiation playbooks belonging to the active organization."""
    _seed_default_if_none(db, org.id)
    playbooks = (
        db.query(Playbook)
        .filter(Playbook.org_id == org.id)
        .order_by(Playbook.is_default.desc(), Playbook.created_at.asc())
        .all()
    )
    return [_playbook_out(p) for p in playbooks]


@router.post("", response_model=PlaybookOut, status_code=status.HTTP_201_CREATED)
def create_playbook(
    payload: PlaybookCreateIn,
    org: Organization = Depends(get_current_org),
    member: OrganizationMember = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> PlaybookOut:
    if member.role == OrgRole.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot create playbooks",
        )

    # If new playbook is set to default, unmark others
    if payload.is_default:
        db.query(Playbook).filter(Playbook.org_id == org.id).update({"is_default": False})

    rules_data = {k: v.model_dump() for k, v in payload.rules.items()}
    if not rules_data:
        # Clone default baseline rules if empty
        rules_data = {k: v.model_dump() for k, v in DEFAULT_PLAYBOOK_RULES.items()}

    pb = Playbook(
        org_id=org.id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        is_default=payload.is_default,
        rules=rules_data,
    )
    db.add(pb)
    db.commit()
    db.refresh(pb)
    return _playbook_out(pb)


@router.get("/{playbook_id}", response_model=PlaybookOut)
def get_playbook(
    playbook_id: uuid.UUID,
    org: Organization = Depends(get_current_org),
    db: Session = Depends(get_db),
) -> PlaybookOut:
    pb = db.get(Playbook, playbook_id)
    if not pb or pb.org_id != org.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Playbook not found")
    return _playbook_out(pb)


@router.patch("/{playbook_id}", response_model=PlaybookOut)
def update_playbook(
    playbook_id: uuid.UUID,
    payload: PlaybookUpdateIn,
    org: Organization = Depends(get_current_org),
    member: OrganizationMember = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> PlaybookOut:
    if member.role in [OrgRole.VIEWER.value, OrgRole.REVIEWER.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Counsel, Admins, and Owners can edit playbooks",
        )

    pb = db.get(Playbook, playbook_id)
    if not pb or pb.org_id != org.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Playbook not found")

    if payload.name:
        pb.name = payload.name.strip()
    if payload.description is not None:
        pb.description = payload.description.strip() if payload.description else None
    if payload.is_default is not None:
        if payload.is_default:
            db.query(Playbook).filter(Playbook.org_id == org.id).update({"is_default": False})
        pb.is_default = payload.is_default
    if payload.rules is not None:
        pb.rules = {k: v.model_dump() for k, v in payload.rules.items()}

    db.commit()
    db.refresh(pb)
    return _playbook_out(pb)


@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playbook(
    playbook_id: uuid.UUID,
    org: Organization = Depends(get_current_org),
    member: OrganizationMember = Depends(get_current_member),
    db: Session = Depends(get_db),
):
    if member.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admins and Owners can delete playbooks",
        )

    count = db.scalar(select(func.count(Playbook.id)).where(Playbook.org_id == org.id))
    if count <= 1:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cannot delete the only playbook in an organization",
        )

    pb = db.get(Playbook, playbook_id)
    if not pb or pb.org_id != org.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Playbook not found")

    db.delete(pb)
    db.commit()


# ==================== Clause Review Decisions Endpoints ====================


@router.get("/documents/{doc_id}/decisions", response_model=list[ClauseDecisionOut])
def get_clause_decisions(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ClauseDecisionOut]:
    doc = owned_document(doc_id, user, db)
    decisions = (
        db.query(ClauseDecision)
        .filter(ClauseDecision.document_id == doc.id)
        .order_by(ClauseDecision.updated_at.desc())
        .all()
    )
    return [ClauseDecisionOut.model_validate(d) for d in decisions]


@router.post("/documents/{doc_id}/decisions", response_model=ClauseDecisionOut)
def record_clause_decision(
    doc_id: uuid.UUID,
    payload: ClauseDecisionIn,
    user: User = Depends(get_current_user),
    member: OrganizationMember = Depends(get_current_member),
    db: Session = Depends(get_db),
) -> ClauseDecisionOut:
    if member.role == OrgRole.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot record review decisions",
        )

    doc = owned_document(doc_id, user, db)

    existing = (
        db.query(ClauseDecision)
        .filter(
            ClauseDecision.document_id == doc.id,
            ClauseDecision.clause_type == payload.clause_type,
        )
        .first()
    )

    if existing:
        existing.decision = payload.decision
        existing.notes = payload.notes
        existing.decided_by_user_id = user.id
        db.commit()
        db.refresh(existing)
        return ClauseDecisionOut.model_validate(existing)

    decision = ClauseDecision(
        document_id=doc.id,
        clause_type=payload.clause_type,
        decision=payload.decision,
        notes=payload.notes,
        decided_by_user_id=user.id,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return ClauseDecisionOut.model_validate(decision)
