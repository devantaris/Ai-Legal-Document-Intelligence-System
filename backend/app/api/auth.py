import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import (
    CredentialsError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import MemberStatus, OrgRole, Organization, OrganizationMember, User, Workspace
from app.schemas import LoginIn, RefreshIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _tokens(user: User) -> TokenOut:
    return TokenOut(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> TokenOut:
    email = payload.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(
        email=email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    # Create default organization & workspace for the new user
    username = email.split("@")[0]
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", username) or "user"
    org_name = f"{cleaned.title()}'s Legal Org"
    org_slug = f"{cleaned.lower()}-{user.id.hex[:6]}"

    org = Organization(
        name=org_name,
        slug=org_slug,
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

    return _tokens(user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if user is None or not verify_password(user.password_hash, payload.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return _tokens(user)


@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshIn, db: Session = Depends(get_db)) -> TokenOut:
    try:
        user_id = decode_token(payload.refresh_token, "refresh")
    except CredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User no longer exists")
    return _tokens(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
