"""Export service that generates Microsoft Word (.docx) documents with native
Word Track Changes (w:ins / w:del) and attorney comment annotations."""

import datetime
import io
import uuid
from typing import Any
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from sqlalchemy.orm import Session

from app.models import Chunk, Clause, Document
from app.services.playbook import review_document_playbook


def _create_ins_element(text: str, change_id: int, author: str = "LegalIQ AI") -> OxmlElement:
    """Creates a native Word <w:ins> OpenXML element representing an inserted tracked change."""
    ins = OxmlElement("w:ins")
    ins.set(qn("w:id"), str(change_id))
    ins.set(qn("w:author"), author)
    ins.set(qn("w:date"), datetime.datetime.now(datetime.timezone.utc).isoformat())
    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "15803D")  # Emerald green for insertion
    r_pr.append(color)
    r.append(r_pr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    ins.append(r)
    return ins


def _create_del_element(text: str, change_id: int, author: str = "LegalIQ AI") -> OxmlElement:
    """Creates a native Word <w:del> OpenXML element representing a deleted tracked change."""
    deletion = OxmlElement("w:del")
    deletion.set(qn("w:id"), str(change_id))
    deletion.set(qn("w:author"), author)
    deletion.set(qn("w:date"), datetime.datetime.now(datetime.timezone.utc).isoformat())
    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    strike = OxmlElement("w:strike")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "BE123C")  # Crimson red for deletion
    r_pr.append(strike)
    r_pr.append(color)
    r.append(r_pr)
    del_text = OxmlElement("w:delText")
    del_text.text = text
    del_text.set(qn("xml:space"), "preserve")
    r.append(del_text)
    deletion.append(r)
    return deletion


def generate_redline_docx(session: Session, doc: Document) -> io.BytesIO:
    """Compiles a professional legal Redline review Word document with Track Changes markup."""
    playbook_review = review_document_playbook(session, doc)
    chunks = (
        session.query(Chunk)
        .filter(Chunk.document_id == doc.id)
        .order_by(Chunk.seq)
        .all()
    )

    findings_by_clause_id = {
        f.clause_id: f for f in playbook_review.findings if f.clause_id
    }
    findings_by_type = {
        f.clause_type: f for f in playbook_review.findings
    }

    word_doc = docx.Document()

    # Document Title & Executive Audit Header
    title_p = word_doc.add_paragraph()
    title_run = title_p.add_run("LEGAL AUDIT & REDLINE AMENDMENT")
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(15, 23, 42)  # Slate 900

    meta_p = word_doc.add_paragraph()
    meta_p.add_run(f"Contract: {doc.filename}\n").bold = True
    meta_p.add_run(f"Audit Date: {datetime.datetime.now().strftime('%B %d, %Y')}\n")
    meta_p.add_run(f"Playbook Compliance Score: {playbook_review.compliance_score} / 100 ({playbook_review.overall_risk})\n")
    meta_p.add_run(
        f"Findings: {playbook_review.red_count} Red Violations | "
        f"{playbook_review.amber_count} Amber Deviations | "
        f"{playbook_review.green_count} Market Compliant\n"
    )

    # Executive Summary Box
    summary_box = word_doc.add_table(rows=1, cols=1)
    summary_cell = summary_box.cell(0, 0)
    summary_p = summary_cell.paragraphs[0]
    summary_p.add_run("Executive Risk Assessment:\n").bold = True
    summary_p.add_run(playbook_review.summary)
    word_doc.add_paragraph()  # Spacing

    heading = word_doc.add_heading("Contract Provisions & Tracked Redlines", level=1)
    heading.runs[0].font.color.rgb = RGBColor(30, 41, 59)

    change_counter = 1

    # Render each section / chunk with track changes if high/moderate risk
    clauses = (
        session.query(Clause)
        .filter(Clause.document_id == doc.id)
        .order_by(Clause.seq)
        .all()
    )

    if clauses:
        for clause in clauses:
            p = word_doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)

            # Section Title
            title_text = clause.title or clause.section_path or f"Section {clause.seq + 1}"
            header_run = p.add_run(f"{title_text}\n")
            header_run.bold = True
            header_run.font.size = Pt(11)

            finding = findings_by_clause_id.get(str(clause.id)) or findings_by_type.get(clause.clause_type)

            if finding and finding.risk_level in ["RED", "AMBER"]:
                # Add Attorney Note box
                note_table = word_doc.add_table(rows=1, cols=1)
                note_cell = note_table.cell(0, 0)
                note_p = note_cell.paragraphs[0]
                note_p.paragraph_format.space_before = Pt(3)
                note_p.paragraph_format.space_after = Pt(3)
                
                badge_text = "[HIGH RISK - RED]" if finding.risk_level == "RED" else "[DEVIATION - AMBER]"
                b_run = note_p.add_run(f"LegalIQ Note {badge_text}: ")
                b_run.bold = True
                b_run.font.color.rgb = RGBColor(190, 18, 60) if finding.risk_level == "RED" else RGBColor(180, 83, 9)
                note_p.add_run(f"{finding.deviation_reason} Rationale: {finding.action_required}\n")

                # Tracked Deletion of original clause
                del_p = word_doc.add_paragraph()
                del_p.paragraph_format.left_indent = Inches(0.25)
                del_p._p.append(_create_del_element(clause.text, change_counter))
                change_counter += 1

                # Tracked Insertion of Conservative Fallback
                ins_p = word_doc.add_paragraph()
                ins_p.paragraph_format.left_indent = Inches(0.25)
                ins_text = finding.fallbacks.conservative
                ins_p._p.append(_create_ins_element(ins_text, change_counter))
                change_counter += 1

            else:
                # Compliant clause rendered standard
                p_run = p.add_run(clause.text)
                p_run.font.size = Pt(10)
    else:
        # Fallback to chunks
        for chunk in chunks:
            p = word_doc.add_paragraph()
            if chunk.section_path:
                h_run = p.add_run(f"{chunk.section_path}\n")
                h_run.bold = True
            p.add_run(chunk.text)

    # Save to in-memory bytes
    buffer = io.BytesIO()
    word_doc.save(buffer)
    buffer.seek(0)
    return buffer
