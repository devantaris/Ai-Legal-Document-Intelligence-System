"""Portfolio & Repository Intelligence: multi-contract cross-examination and
structured due-diligence data grid extraction across an organization's contract repository."""

import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.models import Document
from app.schemas.portfolio import (
    PortfolioAnswerOut,
    PortfolioItem,
    PortfolioMatrixOut,
)
from app.services import retrieval
from app.services.chat import build_context
from app.services.key_terms import generate_key_terms
from app.services.llm import ChatMessage, get_provider
from app.services.playbook import review_document_playbook


def get_portfolio_matrix(session: Session, user_id: uuid.UUID) -> PortfolioMatrixOut:
    """Aggregates all documents into an executive due-diligence spreadsheet dataset."""
    docs = (
        session.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    items: list[PortfolioItem] = []

    for doc in docs:
        parties_list: list[str] = []
        effective_date = None
        governing_law = None
        payment_terms = None
        liability_cap = None
        agreement_type = None

        if doc.key_terms:
            kt = doc.key_terms
            agreement_type = kt.get("agreement_type")
            effective_date = kt.get("effective_date")
            governing_law = kt.get("governing_law")
            payment_terms = kt.get("payment_terms")
            liability_cap = kt.get("indemnification") or kt.get("special_notes", [""])[0] if kt.get("special_notes") else None
            for p in kt.get("parties", []):
                if isinstance(p, dict) and p.get("name"):
                    parties_list.append(p["name"])
                elif isinstance(p, str):
                    parties_list.append(p)

        items.append(
            PortfolioItem(
                id=doc.id,
                filename=doc.filename,
                status=doc.status,
                created_at=doc.created_at,
                page_count=doc.page_count,
                agreement_type=agreement_type,
                parties=parties_list,
                effective_date=effective_date,
                governing_law=governing_law,
                payment_terms=payment_terms,
                liability_cap=liability_cap,
                compliance_score=None,
                overall_risk=None,
            )
        )

    return PortfolioMatrixOut(
        total_documents=len(items),
        documents=items,
    )


def query_portfolio(
    session: Session,
    user_id: uuid.UUID,
    question: str,
    document_ids: list[uuid.UUID] | None = None,
) -> PortfolioAnswerOut:
    """Multi-document cross-contract RAG query that compares or aggregates across contracts."""
    provider = get_provider()

    retrieved = retrieval.retrieve(
        session,
        user_id,
        question,
        document_ids=document_ids,
        top_k=12,
    )

    if not retrieved:
        return PortfolioAnswerOut(
            answer=(
                "No relevant contract clauses were found across your document repository "
                "matching your query. Try rephrasing or verify that target documents have completed ingestion."
            ),
            citations=[],
            documents_referenced=[],
        )

    context, citations = build_context(retrieved)
    unique_filenames = sorted(list({r.filename for r in retrieved}))

    system_prompt = (
        "You are an Elite Legal Counsel analyzing a corporate repository of multiple contracts. "
        "Answer the user's question across all provided documents accurately and rigorously.\n"
        "Guidelines:\n"
        "1. Cite sources inline using bracketed numbers like [1] or [2][3].\n"
        "2. Explicitly name the contract and party when comparing different agreements.\n"
        "3. Highlight discrepancies or variance between contracts (e.g. 'Vendor A requires Net 30, whereas Vendor B imposes Net 15').\n"
        "4. If certain contracts are silent on the subject, state that clearly.\n"
        "5. Never hallucinate terms not found in the context passages."
    )

    user_msg = (
        f"Context passages from multiple contracts across the repository:\n\n"
        f"{context}\n\n"
        f"---\n\n"
        f"Portfolio Question: {question}"
    )

    answer_text = provider.chat(
        [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_msg),
        ],
        temperature=0.2,
    )

    return PortfolioAnswerOut(
        answer=answer_text,
        citations=citations,
        documents_referenced=unique_filenames,
    )
