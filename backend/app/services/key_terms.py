"""Structured key-term extraction: base pass over the document head, then a
retrieval-backed gap-fill pass for any fields the first pass could not find."""

from typing import Any

from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.services.llm import ChatMessage, ask_json, get_provider
from app.services import retrieval

_HEAD_CHARS = 12000

_GAPS_TO_RETRY = [
    "governing_law",
    "termination",
    "payment_terms",
    "confidentiality",
    "indemnification",
    "dispute_resolution",
    "term",
    "renewal",
]

_FIELDS_DESCRIPTION = """\
- agreement_type: what kind of agreement this is (e.g. "Mutual NDA", "SaaS Master Services Agreement")
- parties: every party with their role in the agreement (e.g. "Disclosing Party")
- effective_date: when the agreement takes effect (verbatim, e.g. "March 1, 2024" or "the Effective Date")
- term: duration / length of the agreement
- governing_law: jurisdiction whose law governs
- payment_terms: fees, amounts, invoicing, penalties
- termination: how either side can terminate, notice periods
- renewal: auto-renewal / extension mechanics
- confidentiality: confidentiality obligations and their duration
- indemnification: who indemnifies whom for what
- dispute_resolution: litigation/arbitration/mediation arrangements
- obligations: the most important obligations of each party (short bullets)
- special_notes: anything unusual, one-sided or worth a lawyer's attention (short bullets)"""


_STRING_FIELDS = (
    "agreement_type",
    "effective_date",
    "term",
    "governing_law",
    "payment_terms",
    "termination",
    "renewal",
    "confidentiality",
    "indemnification",
    "dispute_resolution",
)


def _to_text(value: Any) -> str | None:
    """Flatten whatever shape the model returned into displayable text."""
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, dict):
        parts: list[str] = []
        for v in value.values():
            if isinstance(v, list):
                parts.extend(str(x) for x in v)
            else:
                parts.append(str(v))
        return "; ".join(p for p in parts if p)
    if isinstance(value, list):
        return "; ".join(str(x) for x in value)
    return str(value)


class Party(BaseModel):
    name: str
    role: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data = dict(data)
            if "name" in data:
                data["name"] = _to_text(data["name"]) or "Unknown party"
            if "role" in data:
                data["role"] = _to_text(data["role"])
        return data


class KeyTerms(BaseModel):
    agreement_type: str | None = None
    parties: list[Party] = Field(default_factory=list)
    effective_date: str | None = None
    term: str | None = None
    governing_law: str | None = None
    payment_terms: str | None = None
    termination: str | None = None
    renewal: str | None = None
    confidentiality: str | None = None
    indemnification: str | None = None
    dispute_resolution: str | None = None
    obligations: list[str] = Field(default_factory=list)
    special_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, data: Any) -> Any:
        """Small local models return nested objects/lists for string fields;
        coerce everything to the declared shape instead of failing."""
        if not isinstance(data, dict):
            return data
        data = dict(data)
        for field in _STRING_FIELDS:
            if field in data:
                data[field] = _to_text(data[field])
        for field in ("obligations", "special_notes"):
            value = data.get(field)
            if isinstance(value, str):
                data[field] = [value]
            elif isinstance(value, list):
                data[field] = [_to_text(v) for v in value if _to_text(v)]
        return data


def _base_pass(session: Session, doc: Document) -> KeyTerms:
    rows = (
        session.query(Chunk)
        .filter(Chunk.document_id == doc.id)
        .order_by(Chunk.seq)
        .all()
    )
    head: list[str] = []
    size = 0
    for c in rows:
        head.append(c.text)
        size += len(c.text)
        if size >= _HEAD_CHARS:
            break
    provider = get_provider()
    return ask_json(
        provider,
        [
            ChatMessage(
                role="system",
                content=(
                    "You extract structured metadata from legal documents. Reply "
                    "with ONLY a JSON object; use null for fields not present in "
                    "the text and empty lists where nothing applies."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    "Extract the following from this legal document:\n"
                    f"{_FIELDS_DESCRIPTION}\n\n"
                    "Return JSON with exactly these keys: agreement_type (string or null), "
                    "parties (list of {name, role}), effective_date, term, governing_law, "
                    "payment_terms, termination, renewal, confidentiality, indemnification, "
                    "dispute_resolution (each string or null), obligations (list of strings), "
                    "special_notes (list of strings).\n\n"
                    "Document text (may be truncated):\n\n" + "\n\n".join(head)
                ),
            ),
        ],
        KeyTerms,
    )


def _gap_fill(session: Session, doc: Document, terms: KeyTerms) -> KeyTerms:
    missing = [f for f in _GAPS_TO_RETRY if getattr(terms, f) is None]
    if not missing:
        return terms
    provider = get_provider()
    passages: list[str] = []
    for field in missing:
        query = field.replace("_", " ")
        for r in retrieval.retrieve(session, doc.user_id, query, document_ids=[doc.id], top_k=2):
            loc = f" (p. {r.page_start})" if r.page_start else ""
            passages.append(f"re: {query}{loc}\n{r.text[:1200]}")
    if not passages:
        return terms
    filled = ask_json(
        provider,
        [
            ChatMessage(
                role="system",
                content=(
                    "You extract structured metadata from legal documents. Reply "
                    "with ONLY a JSON object; use null for fields not present."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    "These excerpts were retrieved from the document. Fill in ONLY "
                    "these fields, leaving others null:\n"
                    f"{', '.join(missing)}\n\n"
                    "Return JSON with exactly the keys: agreement_type, parties, "
                    "effective_date, term, governing_law, payment_terms, termination, "
                    "renewal, confidentiality, indemnification, dispute_resolution, "
                    "obligations, special_notes.\n\nExcerpts:\n\n" + "\n\n".join(passages)
                ),
            ),
        ],
        KeyTerms,
    )
    for field in missing:
        value = getattr(filled, field)
        if value:
            setattr(terms, field, value)
    return terms


def generate_key_terms(session: Session, doc: Document, *, refresh: bool = False) -> dict[str, Any]:
    if doc.key_terms and not refresh:
        return doc.key_terms
    terms = _base_pass(session, doc)
    terms = _gap_fill(session, doc, terms)
    doc.key_terms = terms.model_dump()
    session.commit()
    return doc.key_terms
