from app.services.chunking import build_chunks, parse_sections

TWO_PAGE = [
    # page 1
    """MASTER SERVICES AGREEMENT

This Agreement is made on March 1, 2024 between Alpha Inc and Beta Co.

ARTICLE 1 - DEFINITIONS
1.1 "Services" means the professional services described in a Statement of
Work. The Services exclude any work not expressly listed there.
1.2 "Deliverables" means all work product provided under this Agreement.

ARTICLE 2 - FEES AND PAYMENT
2.1 Fees. Client shall pay Provider the fees set out in each Statement of
Work within thirty (30) days of receipt of a correct invoice.
2.2 Late payment. Overdue amounts accrue interest at 1% per month.""",
    # page 2
    """ARTICLE 3 - TERM AND TERMINATION
3.1 Term. This Agreement begins on the Effective Date and continues for an
initial term of twelve (12) months, renewing for successive one year periods
unless either party gives notice of non-renewal at least sixty (60) days
before the end of the then-current term.
3.2 Termination for convenience. Either party may terminate for convenience
upon ninety (90) days prior written notice to the other party.
3.3 Termination for cause. Either party may terminate immediately if the
other party materially breaches this Agreement and fails to cure within
thirty (30) days of written notice.""",
]


def test_parse_sections_builds_hierarchy_and_pages():
    sections = parse_sections(TWO_PAGE)
    paths = [s.section_path for s in sections]
    assert any(p.startswith("ARTICLE 1") for p in paths)
    assert any(p.startswith("ARTICLE 2") and "2.1" in p for p in paths)
    assert any("ARTICLE 3" in p and "3.2" in p for p in paths)

    art1 = next(s for s in sections if s.section_path.startswith("ARTICLE 1"))
    assert art1.page_start == 1 and art1.page_end == 1
    art3 = next(s for s in sections if "3.2" in s.section_path)
    assert art3.page_start == 2 and art3.page_end == 2


def test_numbered_subsections_nest():
    sections = parse_sections(TWO_PAGE)
    sub = [s for s in sections if s.section_path.count(" > ") >= 1]
    assert sub, "expected nested section paths"


def test_build_chunks_respects_pages_and_section_paths():
    chunks = build_chunks(TWO_PAGE, max_tokens=120, overlap_tokens=20)
    assert chunks, "expected chunks"
    assert all(c.page_start >= 1 for c in chunks)
    assert all(c.page_end >= c.page_start for c in chunks)
    # page 2 content must appear only in chunks flagged on page 2
    for c in chunks:
        if "termination for convenience" in c.text.lower():
            assert c.page_start == 2
        if "late payment" in c.text.lower():
            assert c.page_start == 1


def test_long_section_is_split_with_overlap():
    one_page = [
        "8. LOREM IPSUM " + ("lorem ipsum dolor sit amet consectetur " * 400)
    ]
    chunks = build_chunks(one_page, max_tokens=200, overlap_tokens=50)
    assert len(chunks) >= 2
    # consecutive windows overlap
    assert chunks[0].text[-80:] in chunks[1].text


def test_tiny_sections_merge_forward():
    pages = [
        """PREAMBLE

X.

1. SHORT. Just a small clause.
2. BIG ONE. """
        + ("content " * 600)
    ]
    chunks = build_chunks(pages, max_tokens=300, overlap_tokens=30)
    assert len(chunks) >= 2
    assert "SHORT" in chunks[0].text
    assert chunks[0].page_start == 1
