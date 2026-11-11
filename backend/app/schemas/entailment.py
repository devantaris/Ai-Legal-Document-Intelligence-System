from typing import Literal
from pydantic import BaseModel, Field


class SentenceAudit(BaseModel):
    sentence_index: int
    sentence_text: str
    status: Literal["VERIFIED", "EXTRAPOLATED", "UNSUPPORTED"]
    entailment_score: float = Field(ge=0.0, le=1.0)
    best_matching_citation: int | None = None
    supporting_quote: str = ""


class EntailmentAuditOut(BaseModel):
    fidelity_score: float = Field(ge=0.0, le=1.0)
    audit_passed: bool
    status_label: Literal["100% Citation Grounded", "High Fidelity", "Contains Ungrounded Claims"]
    verified_count: int
    total_count: int
    sentence_audits: list[SentenceAudit]
