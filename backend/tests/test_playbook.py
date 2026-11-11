import uuid
from app.models import Clause, Document
from app.services.playbook import (
    DEFAULT_PLAYBOOK_RULES,
    _heuristic_evaluate_clause,
    review_document_playbook,
)


def test_heuristic_evaluate_clause_high_risk_limitation():
    clause = Clause(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        seq=1,
        clause_type="limitation_of_liability",
        title="Limitation of Liability",
        page_start=4,
        page_end=4,
        section_path="Section 11",
        text="The Customer shall have unlimited liability for any breach, and Vendor liability shall be zero.",
    )
    rule = DEFAULT_PLAYBOOK_RULES["limitation_of_liability"]
    finding = _heuristic_evaluate_clause(clause, rule)

    assert finding.risk_level == "RED"
    assert finding.score <= 30
    assert "unlimited liability" in finding.deviation_reason.lower()
    assert "Except for liability arising" in finding.fallbacks.conservative
    assert finding.fallbacks.compromise != ""
    assert finding.fallbacks.aggressive != ""


def test_heuristic_evaluate_clause_compliant_governing_law():
    clause = Clause(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        seq=2,
        clause_type="governing_law",
        title="Governing Law",
        page_start=12,
        page_end=12,
        section_path="Section 18.1",
        text="This Agreement shall be governed by the laws of the State of Delaware, without regard to conflicts of law.",
    )
    rule = DEFAULT_PLAYBOOK_RULES["governing_law"]
    finding = _heuristic_evaluate_clause(clause, rule)

    assert finding.risk_level == "GREEN"
    assert finding.score >= 90
    assert "aligns" in finding.deviation_reason.lower()


def test_heuristic_evaluate_clause_amber_termination():
    clause = Clause(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        seq=3,
        clause_type="termination",
        title="Termination",
        page_start=8,
        page_end=8,
        section_path="Section 9",
        text="Either party may terminate for material breach with 30 days notice.",
    )
    rule = DEFAULT_PLAYBOOK_RULES["termination"]
    finding = _heuristic_evaluate_clause(clause, rule)

    # Missing termination for convenience is flagged as Amber
    assert finding.risk_level == "AMBER"
    assert finding.score == 65
    assert "convenience" in finding.deviation_reason.lower()
