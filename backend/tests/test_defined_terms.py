import uuid
from unittest.mock import MagicMock
from app.models import Chunk, Document
from app.services.defined_terms import extract_defined_terms


def test_extract_defined_terms_basic():
    doc_id = uuid.uuid4()
    doc = Document(id=doc_id, user_id=uuid.uuid4(), filename="Test.pdf", file_path="/tmp/test.pdf", mime="application/pdf", status="ready")

    chunks = [
        Chunk(
            id=uuid.uuid4(),
            document_id=doc_id,
            seq=0,
            page_start=1,
            section_path="Section 1. Definitions",
            text=(
                'In this Agreement:\n'
                '"Confidential Information" means all non-public proprietary technical or business data disclosed hereunder.\n'
                '"Applicable Law" shall mean any statute, law, treaty, rule, or regulation of any governmental authority.'
            ),
        ),
        Chunk(
            id=uuid.uuid4(),
            document_id=doc_id,
            seq=1,
            page_start=2,
            section_path="Section 4. Confidentiality",
            text="Each party agrees to safeguard the Confidential Information of the other. Applicable Law shall govern.",
        ),
    ]

    session = MagicMock()
    session.query.return_value.filter.return_value.order_by.return_value.all.return_value = chunks

    result = extract_defined_terms(session, doc)

    assert result.total_terms >= 2
    terms_by_name = {t.term: t for t in result.terms}

    assert "Confidential Information" in terms_by_name
    ci = terms_by_name["Confidential Information"]
    assert "proprietary" in ci.definition.lower()
    assert ci.frequency == 2

    assert "Applicable Law" in terms_by_name
    al = terms_by_name["Applicable Law"]
    assert "statute" in al.definition.lower()
    assert al.frequency == 2
