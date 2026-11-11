import uuid
from typing import Literal
from pydantic import BaseModel, Field


class FallbackDrafts(BaseModel):
    conservative: str = Field(description="Market standard, favorable revision to propose first")
    compromise: str = Field(description="Balanced fallback position if counterparty pushes back")
    aggressive: str = Field(description="Maximum protection posture when holding strong leverage")


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


class PlaybookReviewOut(BaseModel):
    document_id: uuid.UUID
    compliance_score: int = Field(ge=0, le=100)
    overall_risk: Literal["Low Risk", "Moderate Risk", "High Risk", "Severe Exposure"]
    summary: str
    red_count: int
    amber_count: int
    green_count: int
    total_evaluated: int
    findings: list[PlaybookFinding]


class PlaybookRule(BaseModel):
    clause_type: str
    name: str
    preferred_position: str
    unacceptable_triggers: list[str] = Field(default_factory=list)
    guidance: str
