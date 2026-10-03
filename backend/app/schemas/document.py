import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    mime: str
    status: str
    page_count: int | None
    size_bytes: int
    error: str | None
    has_summary: bool
    has_key_terms: bool
    clause_count: int
    chunk_count: int
    created_at: datetime


class SummaryOut(BaseModel):
    summary_md: str


class KeyTermsOut(BaseModel):
    data: dict


class ClauseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    seq: int
    clause_type: str
    title: str
    page_start: int | None
    page_end: int | None
    section_path: str
    text: str
