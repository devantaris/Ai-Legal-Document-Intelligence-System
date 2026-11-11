"""Defined-Terms Graph Engine: parses, indexes, and resolves contractual defined terms,
their canonical definitions, cross-section usage frequencies, and reference links."""

import re
import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.models import Chunk, Document
from app.schemas.defined_terms import DefinedTermOut, DefinedTermsSummaryOut

# Patterns for extracting defined terms and their definitions
_DEFINITION_PATTERNS = [
    # "Term" means / shall mean / refers to ...
    re.compile(
        r'["“](?P<term>[A-Z][a-zA-Z0-9\s\-\'\/]{2,60})["”]\s+(?:means|shall\s+mean|has\s+the\s+meaning|refers\s+to)\s+(?P<def>[^.;\n]{15,600}[.;])',
        re.MULTILINE,
    ),
    # Term: means ... (definition lists)
    re.compile(
        r'(?:^|\n)\s*(?:\([a-z0-9]+\)|\d+\.\d+|\*|\-)?\s*["“]?(?P<term>[A-Z][a-zA-Z0-9\s\-\'\/]{2,60})["”]?\s*:\s*(?P<def>[A-Z][^.;\n]{15,600}[.;])',
        re.MULTILINE,
    ),
    # ... (hereinafter referred to as the "Term") or (the "Term")
    re.compile(
        r'(?P<def>[A-Z][a-zA-Z0-9\s,]{10,120})\s*\((?:hereinafter\s+(?:referred\s+to\s+as\s+)?(?:the\s+)?)?["“](?P<term>[A-Z][a-zA-Z0-9\s\-\'\/]{2,50})["”]\)',
    ),
]

_COMMON_STOPWORDS = {
    "The",
    "This",
    "That",
    "These",
    "Those",
    "Section",
    "Article",
    "Exhibit",
    "Schedule",
    "Agreement",
    "Parties",
    "Party",
    "Whereas",
    "Now",
    "Therefore",
    "In",
    "On",
    "At",
    "By",
}


def extract_defined_terms(session: Session, doc: Document) -> DefinedTermsSummaryOut:
    """Extracts all capitalized defined terms, their official definitions, and usage locations."""
    chunks = (
        session.query(Chunk)
        .filter(Chunk.document_id == doc.id)
        .order_by(Chunk.seq)
        .all()
    )

    terms_dict: dict[str, dict[str, Any]] = {}

    for chunk in chunks:
        text = chunk.text
        for pattern in _DEFINITION_PATTERNS:
            for match in pattern.finditer(text):
                raw_term = match.group("term").strip()
                raw_def = match.group("def").strip()

                if raw_term in _COMMON_STOPWORDS or len(raw_term) < 3:
                    continue

                if raw_term not in terms_dict:
                    terms_dict[raw_term] = {
                        "term": raw_term,
                        "definition": raw_def,
                        "page_defined": chunk.page_start,
                        "section_defined": chunk.section_path or "Definitions",
                        "defining_chunk_id": str(chunk.id),
                    }

    # If few definitions found via strict regex, check for capitalized quoted terms in chunks
    if len(terms_dict) < 2:
        for chunk in chunks:
            for m in re.finditer(r'["“]([A-Z][a-zA-Z\s]{3,40})["”]', chunk.text):
                cand = m.group(1).strip()
                if cand not in _COMMON_STOPWORDS and cand not in terms_dict:
                    # Look ahead 200 chars for definition context
                    snippet_start = m.end()
                    snippet = chunk.text[snippet_start : snippet_start + 250].strip()
                    terms_dict[cand] = {
                        "term": cand,
                        "definition": snippet or f"Defined term in {chunk.section_path or 'document'}.",
                        "page_defined": chunk.page_start,
                        "section_defined": chunk.section_path or "Definitions",
                        "defining_chunk_id": str(chunk.id),
                    }

    # Now calculate global occurrence frequencies and referenced chunk IDs
    results: list[DefinedTermOut] = []
    for term, data in terms_dict.items():
        # Match as whole word with word boundaries
        term_pattern = re.compile(rf"\b{re.escape(term)}\b")
        total_freq = 0
        ref_chunks: list[str] = []

        for chunk in chunks:
            count = len(term_pattern.findall(chunk.text))
            if count > 0:
                total_freq += count
                ref_chunks.append(str(chunk.id))

        results.append(
            DefinedTermOut(
                term=term,
                definition=data["definition"],
                page_defined=data["page_defined"],
                section_defined=data["section_defined"],
                frequency=total_freq,
                chunk_ids=ref_chunks,
            )
        )

    # Sort by frequency descending (most pivotal terms first)
    results.sort(key=lambda t: t.frequency, reverse=True)

    return DefinedTermsSummaryOut(
        document_id=doc.id,
        total_terms=len(results),
        terms=results,
    )
