import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class FallbackDrafts(BaseModel):
    conservative: str = Field(description="Market standard, favorable revision to propose first")
    compromise: str = Field(description="Balanced fallback position if counterparty pushes back")
    aggressive: str = Field(description="Maximum protection posture when holding strong leverage")


class PlaybookRule(BaseModel):
    clause_type: str
    name: str
    preferred_position: str
    unacceptable_triggers: list[str] = Field(default_factory=list)
    guidance: str


class PlaybookFinding(BaseModel):
    clause_id: str | None = None
    clause_type: str
    title: str
    risk_level: Literal["RED", "AMBER", "GREEN"]
    score: int = Field(ge=0, le=100)
    page_start: int | None = None
    section_path: str = ""
    clause_text: str
    standard_rule: str
    deviation_reason: str
    action_required: str
    fallbacks: FallbackDrafts
    decision: str = "pending"
    decision_notes: str | None = None


class PlaybookReviewOut(BaseModel):
    document_id: uuid.UUID
    playbook_id: uuid.UUID | None = None
    playbook_name: str = "Institutional Commercial Standard"
    compliance_score: int = Field(ge=0, le=100)
    overall_risk: Literal["Low Risk", "Moderate Risk", "High Risk", "Severe Exposure"]
    summary: str
    red_count: int
    amber_count: int
    green_count: int
    total_evaluated: int
    findings: list[PlaybookFinding]


class PlaybookCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=256)
    description: str | None = None
    is_default: bool = False
    rules: dict[str, PlaybookRule] = Field(default_factory=dict)


class PlaybookUpdateIn(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=256)
    description: str | None = None
    is_default: bool | None = None
    rules: dict[str, PlaybookRule] | None = None


class PlaybookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    description: str | None = None
    is_default: bool
    rules: dict[str, PlaybookRule]
    rule_count: int = 0
    created_at: datetime
    updated_at: datetime


class ClauseDecisionIn(BaseModel):
    clause_type: str
    decision: Literal["pending", "accepted", "flagged", "rejected"]
    notes: str | None = None


class ClauseDecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    clause_type: str
    decision: str
    notes: str | None = None
    decided_by_user_id: uuid.UUID | None = None
    updated_at: datetime
