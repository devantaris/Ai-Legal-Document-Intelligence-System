import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base

# Canonical clause taxonomy used for classification and diff alignment.
CLAUSE_TYPES = [
    "confidentiality",
    "indemnification",
    "limitation_of_liability",
    "termination",
    "payment",
    "intellectual_property",
    "governing_law",
    "dispute_resolution",
    "arbitration",
    "force_majeure",
    "non_compete",
    "assignment",
    "notices",
    "warranties",
    "insurance",
    "data_protection",
    "entire_agreement",
    "amendment",
    "severability",
    "other",
]


class Clause(Base):
    __tablename__ = "clauses"
    __table_args__ = (
        Index(
            "ix_clauses_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    seq: Mapped[int] = mapped_column(Integer)
    clause_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(Text, default="")
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_path: Mapped[str] = mapped_column(Text, default="")
    text: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM))

    document = relationship("Document", back_populates="clauses")
