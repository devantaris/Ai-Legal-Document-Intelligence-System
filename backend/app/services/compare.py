"""Clause-level comparison of two documents: embed-match clauses across
documents, then have the LLM characterize each material change."""

from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models import Clause, Document
from app.services.clauses import _clause_dict, _cosine, extract_clauses
from app.services.llm import ChatMessage, ask_json, get_provider

_MATCH_THRESHOLD = 0.70
_IDENTICAL_THRESHOLD = 0.995
_TYPE_WEIGHT = 0.3  # weight of "same clause type" in the match score
_PAIR_TEXT_CHARS = 1200


class PairVerdict(BaseModel):
    index: int
    change_level: str = "unchanged"  # unchanged | minor | moderate | major
    change_summary: str = ""


class VerdictBatch(BaseModel):
    pairs: list[PairVerdict] = Field(default_factory=list)


def _match(a_clauses: list[Clause], b_clauses: list[Clause]) -> tuple[list[tuple[Clause, Clause, float]], list[Clause], list[Clause]]:
    scored: list[tuple[float, int, int]] = []
    for i, a in enumerate(a_clauses):
        for j, b in enumerate(b_clauses):
            sim = _cosine(list(a.embedding), list(b.embedding))
            score = sim + _TYPE_WEIGHT * (1.0 if a.clause_type == b.clause_type else 0.0)
            if score >= _MATCH_THRESHOLD:
                scored.append((score, i, j))
    scored.sort(reverse=True)

    used_a: set[int] = set()
    used_b: set[int] = set()
    pairs: list[tuple[Clause, Clause, float]] = []
    for score, i, j in scored:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        pairs.append((a_clauses[i], b_clauses[j], score))
    pairs.sort(key=lambda p: p[0].seq)
    removed = [a for i, a in enumerate(a_clauses) if i not in used_a]
    added = [b for j, b in enumerate(b_clauses) if j not in used_b]
    return pairs, removed, added


def _verdicts(provider, pairs: list[tuple[Clause, Clause, float]]) -> list[PairVerdict]:
    if not pairs:
        return []
    lines = []
    for n, (a, b, _score) in enumerate(pairs, start=1):
        lines.append(
            f"### PAIR {n} (type: {a.clause_type})\n"
            f"--- Version A:\n{a.text[:_PAIR_TEXT_CHARS]}\n"
            f"--- Version B:\n{b.text[:_PAIR_TEXT_CHARS]}\n"
        )
    result = ask_json(
        provider,
        [
            ChatMessage(
                role="system",
                content=(
                    "You compare clauses between two versions of a legal document. "
                    "Reply with ONLY the requested JSON."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    "For each pair of clauses below, judge how materially Version B "
                    "differs from Version A. change_level must be one of: unchanged, "
                    "minor, moderate, major. In change_summary (one sentence) state "
                    "what changed and who benefits, or 'no substantive change' if "
                    "identical in meaning.\n\n"
                    'Reply as JSON: {"pairs": [{"index": <pair number>, '
                    '"change_level": "...", "change_summary": "..."}]} - one entry '
                    "per pair.\n\n" + "\n".join(lines)
                ),
            ),
        ],
        VerdictBatch,
    )
    return result.pairs


def _overall_summary(provider, items: list[dict[str, Any]]) -> str:
    changed = [
        f"- [{i['change_level']}] {i['a']['title']}: {i['change_summary']}"
        for i in items
        if i["status"] == "modified"
    ]
    if not changed:
        return "No substantive clause-level changes were detected between the two versions."
    return ask_json(
        provider,
        [
            ChatMessage(
                role="system",
                content=(
                    "You summarize legal document comparisons. Reply with ONLY a "
                    "JSON object."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    "Write a 2-4 sentence executive overview of what changed between "
                    "the two contract versions and who the changes favor. Mention only "
                    "the most significant changes.\n\n"
                    "Per-clause changes:\n" + "\n".join(changed) + "\n\n"
                    'Reply as JSON: {"summary": "..."}'
                ),
            ),
        ],
        OverallSummary,
    ).summary


class OverallSummary(BaseModel):
    summary: str


def compare_documents(session: Session, user_id, doc_a: Document, doc_b: Document) -> dict[str, Any]:
    a_clauses = extract_clauses(session, doc_a)
    b_clauses = extract_clauses(session, doc_b)
    provider = get_provider()

    pairs, removed, added = _match(a_clauses, b_clauses)
    items: list[dict[str, Any]] = []

    material = [p for p in pairs if p[2] < _IDENTICAL_THRESHOLD]
    verdict_by_index: dict[int, PairVerdict] = {}
    for verdict in _verdicts(provider, material):
        verdict_by_index[verdict.index - 1] = verdict  # prompt numbering is 1-based

    for n, (a, b, score) in enumerate(pairs):
        if score >= _IDENTICAL_THRESHOLD:
            level, summary = "unchanged", "No substantive change."
        else:
            verdict = verdict_by_index.get(n)
            level = verdict.change_level if verdict else "minor"
            summary = verdict.change_summary if verdict else ""
        items.append(
            {
                "status": "modified",
                "change_level": level,
                "change_summary": summary,
                "similarity": round(min(score, 1.0), 3),
                "a": _clause_dict(a),
                "b": _clause_dict(b),
            }
        )
    for c in removed:
        items.append(
            {"status": "removed", "change_level": "removed", "change_summary": "",
             "a": _clause_dict(c), "b": None}
        )
    for c in added:
        items.append(
            {"status": "added", "change_level": "added", "change_summary": "",
             "a": None, "b": _clause_dict(c)}
        )

    counts = {
        "modified": sum(1 for i in items if i["status"] == "modified"),
        "added": len(added),
        "removed": len(removed),
        "unchanged": sum(1 for i in items if i["change_level"] == "unchanged"),
    }
    return {
        "document_a": {"id": str(doc_a.id), "filename": doc_a.filename},
        "document_b": {"id": str(doc_b.id), "filename": doc_b.filename},
        "counts": counts,
        "summary": _overall_summary(provider, items),
        "items": items,
    }
