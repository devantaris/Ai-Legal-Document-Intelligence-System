import json
import re
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_org, get_current_user, require_role
from app.models import (
    AuditLog,
    Document,
    MemberStatus,
    OrgRole,
    Organization,
    OrganizationMember,
    User,
    Workspace,
)
from app.schemas.organization import (
    AuditLogOut,
    MemberInviteIn,
    MemberRoleUpdateIn,
    OrgUsageOut,
    OrganizationCreateIn,
    OrganizationMemberOut,
    OrganizationOut,
    OrganizationUpdateIn,
    WorkspaceCreateIn,
    WorkspaceOut,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _check_membership(db: Session, org_id: uuid.UUID, user_id: uuid.UUID) -> OrganizationMember:
    member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
        .first()
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization",
        )
    return member


@router.get("", response_model=list[OrganizationOut])
def list_user_organizations(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrganizationOut]:
    """List all organizations that the current user belongs to."""
    memberships = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user.id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
        .all()
    )

    out: list[OrganizationOut] = []
    for m in memberships:
        org = db.get(Organization, m.org_id)
        if not org:
            continue
        member_count = db.scalar(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.org_id == org.id,
                OrganizationMember.status == MemberStatus.ACTIVE.value,
            )
        ) or 1
        ws_count = db.scalar(
            select(func.count(Workspace.id)).where(Workspace.org_id == org.id)
        ) or 1

        out.append(
            OrganizationOut(
                id=org.id,
                name=org.name,
                slug=org.slug,
                plan_tier=org.plan_tier,
                role=m.role,
                member_count=member_count,
                workspace_count=ws_count,
                created_at=org.created_at,
            )
        )
    return out


@router.post("", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationOut:
    """Create a new organization and make the current user the Owner."""
    clean_name = payload.name.strip()
    slug_base = payload.slug or re.sub(r"[^a-zA-Z0-9]", "-", clean_name.lower())
    slug_base = re.sub(r"-+", "-", slug_base).strip("-") or "org"
    slug = f"{slug_base}-{uuid.uuid4().hex[:6]}"

    org = Organization(
        name=clean_name,
        slug=slug,
        plan_tier="sovereign_pro",
        settings={},
    )
    db.add(org)
    db.flush()

    member = OrganizationMember(
        org_id=org.id,
        user_id=user.id,
        role=OrgRole.OWNER.value,
        status=MemberStatus.ACTIVE.value,
    )
    db.add(member)

    workspace = Workspace(
        org_id=org.id,
        name="General Matters",
        description="Default workspace for corporate contracts",
    )
    db.add(workspace)
    db.commit()

    return OrganizationOut(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan_tier=org.plan_tier,
        role=OrgRole.OWNER.value,
        member_count=1,
        workspace_count=1,
        created_at=org.created_at,
    )


@router.get("/{org_id}", response_model=OrganizationOut)
def get_organization(
    org_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationOut:
    member = _check_membership(db, org_id, user.id)
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")

    member_count = db.scalar(
        select(func.count(OrganizationMember.id)).where(
            OrganizationMember.org_id == org.id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
    ) or 1
    ws_count = db.scalar(
        select(func.count(Workspace.id)).where(Workspace.org_id == org.id)
    ) or 1

    return OrganizationOut(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan_tier=org.plan_tier,
        role=member.role,
        member_count=member_count,
        workspace_count=ws_count,
        created_at=org.created_at,
    )


@router.patch("/{org_id}", response_model=OrganizationOut)
def update_organization(
    org_id: uuid.UUID,
    payload: OrganizationUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationOut:
    member = _check_membership(db, org_id, user.id)
    if member.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owners and Admins can update organization settings",
        )
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")

    if payload.name:
        org.name = payload.name.strip()
    if payload.settings is not None:
        org.settings = payload.settings
    db.commit()

    return get_organization(org_id, user, db)


# ==================== Member Management ====================


@router.get("/{org_id}/members", response_model=list[OrganizationMemberOut])
def list_members(
    org_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[OrganizationMemberOut]:
    _check_membership(db, org_id, user.id)
    members = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.org_id == org_id)
        .order_by(OrganizationMember.joined_at.asc())
        .all()
    )

    out: list[OrganizationMemberOut] = []
    for m in members:
        u = db.get(User, m.user_id)
        if not u:
            continue
        out.append(
            OrganizationMemberOut(
                id=m.id,
                user_id=u.id,
                email=u.email,
                full_name=u.full_name,
                role=m.role,
                status=m.status,
                joined_at=m.joined_at,
            )
        )
    return out


@router.post("/{org_id}/members", response_model=OrganizationMemberOut, status_code=status.HTTP_201_CREATED)
def invite_member(
    org_id: uuid.UUID,
    payload: MemberInviteIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMemberOut:
    current_m = _check_membership(db, org_id, user.id)
    if current_m.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owners and Admins can invite team members",
        )

    invite_email = payload.email.lower().strip()
    target_user = db.query(User).filter(User.email == invite_email).first()

    # If user does not exist, provision placeholder user account
    if not target_user:
        from app.core.security import hash_password
        target_user = User(
            email=invite_email,
            full_name=invite_email.split("@")[0].title(),
            password_hash=hash_password(uuid.uuid4().hex),
        )
        db.add(target_user)
        db.flush()

    existing_member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == target_user.id,
        )
        .first()
    )
    if existing_member:
        if existing_member.status == MemberStatus.SUSPENDED.value:
            existing_member.status = MemberStatus.ACTIVE.value
            existing_member.role = payload.role
            db.commit()
            return OrganizationMemberOut(
                id=existing_member.id,
                user_id=target_user.id,
                email=target_user.email,
                full_name=target_user.full_name,
                role=existing_member.role,
                status=existing_member.status,
                joined_at=existing_member.joined_at,
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already a member of this organization",
        )

    new_member = OrganizationMember(
        org_id=org_id,
        user_id=target_user.id,
        role=payload.role,
        status=MemberStatus.ACTIVE.value,
    )
    db.add(new_member)
    db.commit()

    return OrganizationMemberOut(
        id=new_member.id,
        user_id=target_user.id,
        email=target_user.email,
        full_name=target_user.full_name,
        role=new_member.role,
        status=new_member.status,
        joined_at=new_member.joined_at,
    )


@router.patch("/{org_id}/members/{target_user_id}", response_model=OrganizationMemberOut)
def update_member_role(
    org_id: uuid.UUID,
    target_user_id: uuid.UUID,
    payload: MemberRoleUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationMemberOut:
    current_m = _check_membership(db, org_id, user.id)
    if current_m.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owners and Admins can update roles",
        )

    target_m = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == target_user_id,
        )
        .first()
    )
    if not target_m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found in organization")

    # Guard: do not demote the last owner
    if target_m.role == OrgRole.OWNER.value and payload.role != OrgRole.OWNER.value:
        owner_count = db.scalar(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.org_id == org_id,
                OrganizationMember.role == OrgRole.OWNER.value,
            )
        )
        if owner_count <= 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot change role: an organization must have at least one Owner",
            )

    target_m.role = payload.role
    db.commit()

    target_u = db.get(User, target_user_id)
    return OrganizationMemberOut(
        id=target_m.id,
        user_id=target_u.id,
        email=target_u.email,
        full_name=target_u.full_name,
        role=target_m.role,
        status=target_m.status,
        joined_at=target_m.joined_at,
    )


@router.delete("/{org_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    org_id: uuid.UUID,
    target_user_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_m = _check_membership(db, org_id, user.id)
    if current_m.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owners and Admins can remove members",
        )

    target_m = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.org_id == org_id,
            OrganizationMember.user_id == target_user_id,
        )
        .first()
    )
    if not target_m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Member not found in organization")

    if target_m.role == OrgRole.OWNER.value:
        owner_count = db.scalar(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.org_id == org_id,
                OrganizationMember.role == OrgRole.OWNER.value,
            )
        )
        if owner_count <= 1:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot remove the only Owner of an organization",
            )

    db.delete(target_m)
    db.commit()


# ==================== Workspaces Management ====================


@router.get("/{org_id}/workspaces", response_model=list[WorkspaceOut])
def list_workspaces(
    org_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkspaceOut]:
    _check_membership(db, org_id, user.id)
    workspaces = (
        db.query(Workspace)
        .filter(Workspace.org_id == org_id)
        .order_by(Workspace.created_at.asc())
        .all()
    )

    out: list[WorkspaceOut] = []
    for ws in workspaces:
        doc_count = db.scalar(
            select(func.count(Document.id)).where(Document.workspace_id == ws.id)
        ) or 0
        out.append(
            WorkspaceOut(
                id=ws.id,
                org_id=ws.org_id,
                name=ws.name,
                description=ws.description,
                document_count=doc_count,
                created_at=ws.created_at,
            )
        )
    return out


@router.post("/{org_id}/workspaces", response_model=WorkspaceOut, status_code=status.HTTP_201_CREATED)
def create_workspace(
    org_id: uuid.UUID,
    payload: WorkspaceCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkspaceOut:
    member = _check_membership(db, org_id, user.id)
    if member.role == OrgRole.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot create workspaces",
        )

    ws = Workspace(
        org_id=org_id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
    )
    db.add(ws)
    db.commit()

    return WorkspaceOut(
        id=ws.id,
        org_id=ws.org_id,
        name=ws.name,
        description=ws.description,
        document_count=0,
        created_at=ws.created_at,
    )


@router.delete("/{org_id}/workspaces/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(
    org_id: uuid.UUID,
    workspace_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    member = _check_membership(db, org_id, user.id)
    if member.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owners and Admins can delete workspaces",
        )

    ws_count = db.scalar(
        select(func.count(Workspace.id)).where(Workspace.org_id == org_id)
    ) or 1
    if ws_count <= 1:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Cannot delete the only workspace in an organization",
        )

    ws = db.get(Workspace, workspace_id)
    if not ws or ws.org_id != org_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Workspace not found")

    db.delete(ws)
    db.commit()


# ==================== Organization Usage & Tier Overview ====================


@router.get("/{org_id}/usage", response_model=OrgUsageOut)
def get_usage(
    org_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgUsageOut:
    _check_membership(db, org_id, user.id)
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")

    members_count = db.scalar(
        select(func.count(OrganizationMember.id)).where(
            OrganizationMember.org_id == org.id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
    ) or 0
    workspaces_count = db.scalar(
        select(func.count(Workspace.id)).where(Workspace.org_id == org.id)
    ) or 0
    documents_count = db.scalar(
        select(func.count(Document.id)).where(Document.org_id == org.id)
    ) or 0
    pages_processed = db.scalar(
        select(func.coalesce(func.sum(Document.page_count), 0)).where(Document.org_id == org.id)
    ) or 0
    storage_bytes = db.scalar(
        select(func.coalesce(func.sum(Document.size_bytes), 0)).where(Document.org_id == org.id)
    ) or 0

    return OrgUsageOut(
        plan_tier=org.plan_tier,
        plan_display="Sovereign Enterprise Pro",
        status_label="Active (Subscription Plans Coming Soon)",
        members_count=members_count,
        workspaces_count=workspaces_count,
        documents_count=documents_count,
        pages_processed=int(pages_processed),
        storage_bytes=int(storage_bytes),
        sovereign_inference=True,
        features=[
            "100% Sovereign Local Inference (Ollama / vLLM) — zero data leaves premise",
            "Multi-Tenant Isolation & Workspace Segmentation",
            "Institutional 10-Standard Playbook Compliance Review",
            "Native Word Track Changes (.docx) Redline Export",
            "Mathematical Sentence-Level Entailment Verification",
            "Cross-Repository Multi-Contract Portfolio Due Diligence Grid",
        ],
    )


# ==================== Enterprise Audit Trails & Compliance ====================


@router.get("/{org_id}/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    org_id: uuid.UUID,
    limit: int = Query(default=100, ge=1, le=500),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AuditLogOut]:
    _check_membership(db, org_id, user.id)
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.org_id == org_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )

    out: list[AuditLogOut] = []
    for l in logs:
        actor_email = None
        if l.user_id:
            u = db.get(User, l.user_id)
            if u:
                actor_email = u.email
        out.append(
            AuditLogOut(
                id=l.id,
                org_id=l.org_id,
                user_id=l.user_id,
                actor_email=actor_email,
                action=l.action,
                resource_type=l.resource_type,
                resource_id=l.resource_id,
                details=l.details or {},
                ip_address=l.ip_address,
                created_at=l.created_at,
            )
        )
    return out


@router.get("/{org_id}/audit-logs/export-csv")
def export_audit_logs_csv(
    org_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import csv
    import io
    from fastapi.responses import Response

    member = _check_membership(db, org_id, user.id)
    if member.role not in [OrgRole.OWNER.value, OrgRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Owners and Admins can export compliance audit logs",
        )

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.org_id == org_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp (UTC)", "Actor Email", "Action", "Resource Type", "Resource ID", "IP Address", "Metadata"])

    for l in logs:
        actor_email = ""
        if l.user_id:
            u = db.get(User, l.user_id)
            if u:
                actor_email = u.email
        writer.writerow([
            l.created_at.isoformat(),
            actor_email,
            l.action,
            l.resource_type,
            l.resource_id or "",
            l.ip_address or "",
            json.dumps(l.details or {}),
        ])

    csv_data = output.getvalue()
    filename = f"LegalIQ_Audit_Log_{org_id}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

