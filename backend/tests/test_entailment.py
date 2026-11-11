from app.services.entailment import audit_claim_entailment


def test_audit_claim_entailment_grounded():
    answer = (
        "The Agreement terminates upon thirty (30) days written notice [1]. "
        "Each party's liability is capped at twelve (12) months fees [2]."
    )
    citations = [
        {
            "n": 1,
            "quote": "Either party may terminate this agreement upon thirty (30) days prior written notice to the other party.",
        },
        {
            "n": 2,
            "quote": "In no event shall aggregate cumulative liability exceed the total fees paid or payable in the twelve (12) months preceding the incident.",
        },
    ]

    result = audit_claim_entailment(answer, citations)

    assert result.audit_passed is True
    assert result.fidelity_score >= 0.70
    assert result.status_label == "100% Citation Grounded"
    assert result.verified_count == 2
    assert result.total_count == 2


def test_audit_claim_entailment_unsupported():
    answer = (
        "The customer must pay a penalty of $5,000,000 upon termination [1]."
    )
    citations = [
        {
            "n": 1,
            "quote": "Either party may terminate for convenience upon thirty (30) days written notice without penalty.",
        }
    ]

    result = audit_claim_entailment(answer, citations)

    # Missing $5,000,000 figure causes low score
    assert result.audit_passed is False
    assert result.sentence_audits[0].status == "UNSUPPORTED"
