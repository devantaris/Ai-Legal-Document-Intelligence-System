import uuid
from pydantic import BaseModel, Field


class DefinedTermOut(BaseModel):
    term: str
    definition: str
    page_defined: int | None = None
    section_defined: str = ""
    frequency: int = Field(ge=0, description="Number of times this defined term is used across the contract")
    chunk_ids: list[str] = Field(default_factory=list)


class DefinedTermsSummaryOut(BaseModel):
    document_id: uuid.UUID
    total_terms: int
    terms: list[DefinedTermOut]
