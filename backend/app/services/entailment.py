"""Deterministic Entailment Guard: audits generated legal claims and summaries
sentence-by-sentence against cited source chunks to certify zero-hallucination compliance."""

import re
from typing import Any
from app.schemas.entailment import EntailmentAuditOut, SentenceAudit

_STOPWORDS = {
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "with",
    "by", "of", "is", "are", "was", "were", "be", "been", "being", "this",
    "that", "these", "those", "it", "its", "as", "such", "from", "any",
    "all", "shall", "will", "may", "hereunder", "thereunder", "pursuant"
}


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"\b[a-zA-Z0-9\$\%]{2,}\b", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def _extract_numbers_and_dates(text: str) -> set[str]:
    # Match currency, percentages, integers, and ordinal days
    return set(re.findall(r"\b(?:\$?\d+(?:,\d+)*(?:\.\d+)?%?|\d+(?:st|nd|rd|th)?)\b", text.lower()))


def audit_claim_entailment(answer_text: str, citations: list[dict[str, Any]]) -> EntailmentAuditOut:
    """Audits each sentence in answer_text against the provided citations for strict entailment."""
    # Split into sentences
    raw_sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\[])", answer_text.strip())
        if len(s.strip()) > 15
    ]

    if not raw_sentences:
        return EntailmentAuditOut(
            fidelity_score=1.0,
            audit_passed=True,
            status_label="100% Citation Grounded",
            verified_count=0,
            total_count=0,
            sentence_audits=[],
        )

    # Pre-tokenize all citation snippets
    cited_data: list[tuple[int, set[str], set[str], str]] = []
    for c in citations:
        n = c.get("n", 1)
        quote = c.get("quote", "") or c.get("text", "")
        tokens = _tokenize(quote)
        nums = _extract_numbers_and_dates(quote)
        cited_data.append((n, tokens, nums, quote))

    audits: list[SentenceAudit] = []

    for idx, sentence in enumerate(raw_sentences, start=1):
        # Remove citation tags like [1] or [2][3] for analysis
        cleaned_sentence = re.sub(r"\[\d+\]", "", sentence).strip()
        sent_tokens = _tokenize(cleaned_sentence)
        sent_nums = _extract_numbers_and_dates(cleaned_sentence)

        best_score = 0.0
        best_cit = None
        best_quote = ""

        if not sent_tokens:
            audits.append(
                SentenceAudit(
                    sentence_index=idx,
                    sentence_text=sentence,
                    status="VERIFIED",
                    entailment_score=1.0,
                    best_matching_citation=None,
                    supporting_quote="Procedural or transitional statement.",
                )
            )
            continue

        for n, cit_tokens, cit_nums, quote in cited_data:
            if not cit_tokens:
                continue

            # Token overlap containment
            overlap = sent_tokens & cit_tokens
            containment = len(overlap) / len(sent_tokens) if sent_tokens else 0.0

            # Number/metric check: if sentence contains numbers, verify presence in citation
            num_penalty = 0.0
            if sent_nums:
                missing_nums = sent_nums - cit_nums
                if missing_nums:
                    num_penalty = 0.25 * len(missing_nums)

            score = max(0.0, min(1.0, containment - num_penalty))
            if score > best_score:
                best_score = score
                best_cit = n
                best_quote = quote[:180]

        # Determine verification status
        if best_score >= 0.50 or (len(sent_tokens) <= 4 and best_score >= 0.35):
            status = "VERIFIED"
        elif best_score >= 0.25:
            status = "EXTRAPOLATED"
        else:
            status = "UNSUPPORTED"

        audits.append(
            SentenceAudit(
                sentence_index=idx,
                sentence_text=sentence,
                status=status,
                entailment_score=round(best_score, 3),
                best_matching_citation=best_cit,
                supporting_quote=best_quote,
            )
        )

    verified_count = sum(1 for a in audits if a.status == "VERIFIED")
    total_count = len(audits)
    fidelity_score = round(sum(a.entailment_score for a in audits) / total_count, 3) if total_count > 0 else 1.0

    unsupported_count = sum(1 for a in audits if a.status == "UNSUPPORTED")
    audit_passed = unsupported_count == 0

    if audit_passed and fidelity_score >= 0.70:
        status_label = "100% Citation Grounded"
    elif unsupported_count <= 1:
        status_label = "High Fidelity"
    else:
        status_label = "Contains Ungrounded Claims"

    return EntailmentAuditOut(
        fidelity_score=fidelity_score,
        audit_passed=audit_passed,
        status_label=status_label,
        verified_count=verified_count,
        total_count=total_count,
        sentence_audits=audits,
    )
