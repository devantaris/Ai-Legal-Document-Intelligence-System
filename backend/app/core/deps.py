import re
import uuid
from typing import Callable

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import CredentialsError, decode_token
from app.models import (
    Document,
    MemberStatus,
    OrgRole,
    Organization,
    OrganizationMember,
    User,
    Workspace,
)

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = decode_token(creds.credentials, "access")
    except CredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists"
        )
    return user


def get_current_tenant(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    x_organization_id: str | None = Header(None, alias="X-Organization-Id"),
) -> tuple[Organization, OrganizationMember]:
    """Resolve the active organization and user's membership.

    If X-Organization-Id header is supplied, validates access.
    Otherwise, falls back to the user's primary/first active organization.
    If none exists, automatically initializes a default one.
    """
    selected_org_id: uuid.UUID | None = None
    if x_organization_id:
        try:
            selected_org_id = uuid.UUID(x_organization_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-Organization-Id header format",
            )

    if selected_org_id:
        member = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.org_id == selected_org_id,
                OrganizationMember.user_id == user.id,
                OrganizationMember.status == MemberStatus.ACTIVE.value,
            )
            .first()
        )
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this organization",
            )
        org = db.get(Organization, member.org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return org, member

    # Fallback to user's first active organization
    member = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user.id,
            OrganizationMember.status == MemberStatus.ACTIVE.value,
        )
        .order_by(OrganizationMember.joined_at.asc())
        .first()
    )

    if member:
        org = db.get(Organization, member.org_id)
        if org:
            return org, member

    # Emergency auto-provision for orphaned/legacy users
    username = user.email.split("@")[0]
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", username) or "user"
    new_org = Organization(
        name=f"{cleaned.title()}'s Legal Org",
        slug=f"{cleaned.lower()}-{user.id.hex[:6]}",
        plan_tier="sovereign_pro",
        settings={},
    )
    db.add(new_org)
    db.flush()

    new_member = OrganizationMember(
        org_id=new_org.id,
        user_id=user.id,
        role=OrgRole.OWNER.value,
        status=MemberStatus.ACTIVE.value,
    )
    db.add(new_member)

    new_ws = Workspace(
        org_id=new_org.id,
        name="General Matters",
        description="Default workspace for corporate contracts",
    )
    db.add(new_ws)
    db.commit()

    return new_org, new_member


def get_current_org(
    tenant: tuple[Organization, OrganizationMember] = Depends(get_current_tenant),
) -> Organization:
    return tenant[0]


def get_current_member(
    tenant: tuple[Organization, OrganizationMember] = Depends(get_current_tenant),
) -> OrganizationMember:
    return tenant[1]


def get_current_workspace(
    org: Organization = Depends(get_current_org),
    db: Session = Depends(get_db),
    x_workspace_id: str | None = Header(None, alias="X-Workspace-Id"),
) -> Workspace:
    """Resolve the active workspace within the current organization."""
    selected_ws_id: uuid.UUID | None = None
    if x_workspace_id:
        try:
            selected_ws_id = uuid.UUID(x_workspace_id)
        except ValueError:
            pass

    if selected_ws_id:
        ws = (
            db.query(Workspace)
            .filter(Workspace.id == selected_ws_id, Workspace.org_id == org.id)
            .first()
        )
        if ws:
            return ws

    # Fallback to the first workspace in the organization
    first_ws = (
        db.query(Workspace)
        .filter(Workspace.org_id == org.id)
        .order_by(Workspace.created_at.asc())
        .first()
    )
    if not first_ws:
        first_ws = Workspace(
            org_id=org.id,
            name="General Matters",
            description="Default workspace for corporate contracts",
        )
        db.add(first_ws)
        db.commit()
    return first_ws


def require_role(allowed_roles: list[str]) -> Callable:
    def _role_checker(
        member: OrganizationMember = Depends(get_current_member),
    ) -> OrganizationMember:
        if member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of the following roles: {', '.join(allowed_roles)}",
            )
        return member

    return _role_checker


def owned_document(
    doc_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    """Fetch a document belonging to the user or an organization the user is an active member of."""
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # 1. Direct owner match
    if doc.user_id == user.id:
        return doc

    # 2. Organization tenant match
    if doc.org_id:
        member = (
            db.query(OrganizationMember)
            .filter(
                OrganizationMember.org_id == doc.org_id,
                OrganizationMember.user_id == user.id,
                OrganizationMember.status == MemberStatus.ACTIVE.value,
            )
            .first()
        )
        if member:
            return doc

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
    )
