import io
import uuid
import docx
from app.models import Clause, Document
from app.services.docx_export import (
    _create_del_element,
    _create_ins_element,
    generate_redline_docx,
)
from app.schemas.playbook import PlaybookReviewOut, PlaybookFinding, FallbackDrafts
from unittest.mock import MagicMock, patch


def test_create_ins_and_del_elements():
    doc = docx.Document()
    p = doc.add_paragraph("Preamble ")
    
    ins = _create_ins_element("Inserted text for agreement", 1)
    assert ins.tag.endswith("ins")
    p._p.append(ins)

    del_el = _create_del_element("Deleted bad clause", 2)
    assert del_el.tag.endswith("del")
    p._p.append(del_el)

    buf = io.BytesIO()
    doc.save(buf)
    assert len(buf.getvalue()) > 5000


@patch("app.services.docx_export.review_document_playbook")
def test_generate_redline_docx(mock_review):
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        user_id=uuid.uuid4(),
        filename="Master_Services_Agreement.pdf",
        file_path="/tmp/test.pdf",
        mime="application/pdf",
        status="ready",
    )
    mock_review.return_value = PlaybookReviewOut(
        document_id=doc_id,
        compliance_score=75,
        overall_risk="Moderate Risk",
        summary="Audit summary text",
        red_count=1,
        amber_count=1,
        green_count=2,
        total_evaluated=4,
        findings=[
            PlaybookFinding(
                clause_id=str(uuid.uuid4()),
                clause_type="limitation_of_liability",
                title="Limitation of Liability",
                risk_level="RED",
                score=25,
                page_start=5,
                section_path="Section 11",
                clause_text="Customer has unlimited liability.",
                standard_rule="Liability capped at 12M fees.",
                deviation_reason="Unlimited customer liability.",
                action_required="Replace with 12M mutual cap.",
                fallbacks=FallbackDrafts(
                    conservative="Standard 12M cap provision.",
                    compromise="2x fees cap provision.",
                    aggressive="3 months fees cap.",
                ),
            )
        ],
    )

    session = MagicMock()
    session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        Clause(
            id=uuid.uuid4(),
            document_id=doc_id,
            seq=0,
            clause_type="limitation_of_liability",
            title="Limitation of Liability",
            page_start=5,
            page_end=5,
            section_path="Section 11",
            text="Customer has unlimited liability.",
        )
    ]

    buffer = generate_redline_docx(session, doc)
    assert buffer is not None
    assert buffer.getbuffer().nbytes > 10000

    # Verify the generated document can be loaded back by python-docx
    loaded = docx.Document(buffer)
    full_text = "\n".join(p.text for p in loaded.paragraphs)
    assert "LEGAL AUDIT & REDLINE AMENDMENT" in full_text
    assert "Master_Services_Agreement.pdf" in full_text
