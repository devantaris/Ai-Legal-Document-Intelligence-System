import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreateIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=256)
    slug: str | None = Field(None, max_length=128)


class OrganizationUpdateIn(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=256)
    settings: dict[str, Any] | None = None


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    plan_tier: str
    role: str = "counsel"
    member_count: int = 1
    workspace_count: int = 1
    created_at: datetime


class OrganizationMemberOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: str | None = None
    role: str
    status: str
    joined_at: datetime


class MemberInviteIn(BaseModel):
    email: str
    role: str = "counsel"


class MemberRoleUpdateIn(BaseModel):
    role: str


class WorkspaceCreateIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str | None = None


class WorkspaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    description: str | None = None
    document_count: int = 0
    created_at: datetime


class OrgUsageOut(BaseModel):
    plan_tier: str
    plan_display: str
    status_label: str
    members_count: int
    workspaces_count: int
    documents_count: int
    pages_processed: int
    storage_bytes: int
    sovereign_inference: bool
    features: list[str]
