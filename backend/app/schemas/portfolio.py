import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class PortfolioItem(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    created_at: datetime
    page_count: int | None = None
    agreement_type: str | None = None
    parties: list[str] = Field(default_factory=list)
    effective_date: str | None = None
    governing_law: str | None = None
    payment_terms: str | None = None
    liability_cap: str | None = None
    compliance_score: int | None = None
    overall_risk: str | None = None


class PortfolioMatrixOut(BaseModel):
    total_documents: int
    documents: list[PortfolioItem]


class PortfolioQueryIn(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    document_ids: list[uuid.UUID] | None = None


class PortfolioAnswerOut(BaseModel):
    answer: str
    citations: list[dict[str, Any]]
    documents_referenced: list[str]
