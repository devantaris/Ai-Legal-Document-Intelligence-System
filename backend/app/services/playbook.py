"""Enterprise Legal Playbook Engine: evaluates contract clauses against institutional
negotiation standards, assigns Red/Amber/Green risk ratings, calculates compliance score,
and generates three-tiered fallback revision drafts (Conservative, Compromise, Aggressive)."""

import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.models import Clause, Document
from app.schemas.playbook import (
    FallbackDrafts,
    PlaybookFinding,
    PlaybookReviewOut,
    PlaybookRule,
)
from app.services.clauses import extract_clauses
from app.services.llm import ChatMessage, ask_json, get_provider
from pydantic import BaseModel, Field

# Institutional baseline playbook rules for standard commercial transactions
DEFAULT_PLAYBOOK_RULES: dict[str, PlaybookRule] = {
    "limitation_of_liability": PlaybookRule(
        clause_type="limitation_of_liability",
        name="Limitation of Liability",
        preferred_position=(
            "Liability must be capped at 12 months fees paid or payable. Must be mutual. "
            "Consequential, indirect, and punitive damages waived by both parties. "
            "Carve-outs strictly limited to gross negligence, willful misconduct, and breach of confidentiality."
        ),
        unacceptable_triggers=[
            "unlimited liability",
            "solely customer",
            "uncapped indemnity",
            "excluding liability for gross negligence",
            "liability exceeding 24 months fees",
        ],
        guidance="Never accept unlimited liability or one-sided liability caps favorable only to the vendor.",
    ),
    "indemnification": PlaybookRule(
        clause_type="indemnification",
        name="Indemnification",
        preferred_position=(
            "Mutual indemnification. Vendor indemnifies for third-party IP infringement, data breach, "
            "and gross negligence. Customer indemnifies only for its own customer data and unauthorized use. "
            "Must include prompt written notice, defense control, and settlement consent restrictions."
        ),
        unacceptable_triggers=[
            "customer indemnifies vendor for third party",
            "customer defends vendor",
            "no ip infringement indemnity",
            "settle without consent",
        ],
        guidance="Ensure vendor provides full IP indemnity and that defense cannot be settled without customer approval.",
    ),
    "governing_law": PlaybookRule(
        clause_type="governing_law",
        name="Governing Law & Jurisdiction",
        preferred_position=(
            "Governed by the laws of Delaware, New York, or England & Wales, without regard to conflict of laws. "
            "Exclusive jurisdiction in recognized commercial courts."
        ),
        unacceptable_triggers=[
            "foreign jurisdiction",
            "unfriendly venue",
            "binding arbitration without preliminary injunctive relief",
        ],
        guidance="Avoid unfamiliar or one-sided jurisdictions. Retain the right to seek emergency injunctive relief.",
    ),
    "confidentiality": PlaybookRule(
        clause_type="confidentiality",
        name="Confidentiality Obligations",
        preferred_position=(
            "Mutual confidentiality. 3 to 5 year duration from disclosure, with trade secrets protected in perpetuity. "
            "Standard carve-outs for public knowledge, prior possession, independent development, and legal compulsion."
        ),
        unacceptable_triggers=[
            "unilateral disclosure",
            "only recipient is bound",
            "less than 1 year duration",
            "no trade secret carve-out",
        ],
        guidance="Confidentiality must be strictly bilateral and carve-outs must be explicit.",
    ),
    "termination": PlaybookRule(
        clause_type="termination",
        name="Termination Rights",
        preferred_position=(
            "Termination for convenience upon 30–60 days written notice. Termination for cause upon 30 days "
            "written notice with opportunity to cure. Immediate termination for insolvency or material breach. "
            "Pro-rata refund of any prepaid, unearned fees upon termination."
        ),
        unacceptable_triggers=[
            "no termination for convenience",
            "forfeiture of prepaid fees",
            "cure period exceeding 60 days",
            "automatic perpetual lock-in",
        ],
        guidance="Ensure clean exit path and recovery of prepaid unearned fees.",
    ),
    "payment": PlaybookRule(
        clause_type="payment",
        name="Payment Terms & Invoicing",
        preferred_position=(
            "Net 30 or Net 45 days upon receipt of undisputed invoice. Right to withhold amounts disputed "
            "in good faith without penalty or service suspension."
        ),
        unacceptable_triggers=[
            "net 15 days",
            "immediate suspension on dispute",
            "interest exceeding 1.5% monthly",
            "payment due upon receipt",
        ],
        guidance="Guard against aggressive collection clauses and preserve the right to contest disputed invoices.",
    ),
    "intellectual_property": PlaybookRule(
        clause_type="intellectual_property",
        name="Intellectual Property Ownership",
        preferred_position=(
            "Customer retains exclusive title to all Customer Data and bespoke deliverables. Vendor retains "
            "pre-existing background technology and grants Customer a perpetual, non-exclusive license to use."
        ),
        unacceptable_triggers=[
            "vendor owns customer data",
            "assignment of customer ip",
            "unconditional feedback assignment",
        ],
        guidance="Customer data and work product must remain strictly customer-owned.",
    ),
    "non_compete": PlaybookRule(
        clause_type="non_compete",
        name="Restrictive Covenants & Non-Compete",
        preferred_position=(
            "No non-compete restrictions on general business operations. Employee non-solicitation strictly "
            "limited to 12 months with express carve-out for general public job postings."
        ),
        unacceptable_triggers=[
            "general non-compete",
            "prohibition on competing products",
            "blanket non-solicitation without public posting carve-out",
        ],
        guidance="Reject broad non-compete covenants that constrain future business or hiring.",
    ),
    "warranties": PlaybookRule(
        clause_type="warranties",
        name="Warranties & Disclaimers",
        preferred_position=(
            "Vendor warrants that services will perform in all material respects in accordance with documentation "
            "for at least 90 days. Warranty of non-infringement and professional standard of care."
        ),
        unacceptable_triggers=[
            "entirely 'as-is' with zero warranty",
            "complete disclaimer of non-infringement",
            "disclaimer of all service levels",
        ],
        guidance="Ensure core performance warranties are enforceable and not completely waived in disclaimer text.",
    ),
    "data_protection": PlaybookRule(
        clause_type="data_protection",
        name="Data Protection & Privacy",
        preferred_position=(
            "Compliance with applicable data protection laws (GDPR, CCPA). Data Processing Addendum (DPA) "
            "incorporated. Obligation to notify of security breach within 48 to 72 hours."
        ),
        unacceptable_triggers=[
            "disclaimer of liability for security breach",
            "notification exceeding 14 days",
            "no data processing agreement",
        ],
        guidance="Require prompt breach notification and formal data processing commitments.",
    ),
}

# Standard fallback clause drafts by category
FALLBACK_TEMPLATES: dict[str, dict[str, str]] = {
    "limitation_of_liability": {
        "conservative": (
            "Except for liability arising from gross negligence, willful misconduct, or breach of Section [Confidentiality], "
            "each party's aggregate liability under this Agreement shall be limited to the total fees paid or payable by Customer "
            "in the twelve (12) months preceding the incident giving rise to liability. Neither party shall be liable for any "
            "indirect, incidental, special, or consequential damages."
        ),
        "compromise": (
            "Each party's aggregate cumulative liability arising out of or related to this Agreement shall not exceed two times (2x) "
            "the total amounts paid or payable under the applicable Order Form during the twelve (12) months prior to the event, "
            "provided that each party remains liable for breaches of confidentiality and third-party indemnification obligations."
        ),
        "aggressive": (
            "In no event shall Customer's total liability under this Agreement exceed the fees actually paid to Vendor during the "
            "three (3) months preceding the claim. Vendor's liability for data breach, confidentiality breach, or indemnification "
            "shall be uncapped and subject to no limitation whatsoever."
        ),
    },
    "indemnification": {
        "conservative": (
            "Vendor shall defend, indemnify, and hold harmless Customer and its officers, directors, and employees from and "
            "against any third-party claims, suits, liabilities, and reasonable expenses (including attorney's fees) arising "
            "out of or resulting from an allegation that the Services or Deliverables infringe any patent, copyright, or trademark, "
            "or misappropriate any trade secret. Customer shall provide prompt written notice and full cooperation in defense."
        ),
        "compromise": (
            "Each party shall mutually defend and indemnify the other against third-party claims arising from: (a) gross negligence "
            "or willful misconduct; (b) material breach of confidentiality; or (c) in the case of Vendor, intellectual property "
            "infringement. The indemnified party shall have the right to approve any settlement that imposes financial or operational liability."
        ),
        "aggressive": (
            "Vendor shall defend and indemnify Customer against any and all claims, damages, losses, and penalties arising from: "
            "(i) intellectual property infringement; (ii) any security breach involving Customer Data; or (iii) Vendor's violation "
            "of applicable law. Customer shall have sole control over its legal defense at Vendor's reasonable expense."
        ),
    },
    "governing_law": {
        "conservative": (
            "This Agreement and any dispute arising hereunder shall be governed by and construed in accordance with the laws "
            "of the State of Delaware, without regard to conflicts of law principles. The parties submit to the exclusive "
            "jurisdiction of the state and federal courts located in Wilmington, Delaware."
        ),
        "compromise": (
            "This Agreement shall be governed by the laws of the State of New York. In the event of a dispute, the parties "
            "shall first participate in good-faith executive escalation for twenty (20) days before filing proceedings in the "
            "state or federal courts of New York County, New York."
        ),
        "aggressive": (
            "This Agreement shall be governed strictly by the laws of Customer's principal jurisdiction of incorporation, "
            "and all proceedings must be brought exclusively in the courts where Customer's headquarters is situated."
        ),
    },
    "confidentiality": {
        "conservative": (
            "Each party agrees to safeguard the other's Confidential Information with at least reasonable care and not disclose "
            "it to third parties for a period of three (3) years from disclosure; provided, however, that trade secrets shall "
            "remain confidential in perpetuity. Standard exceptions for public knowledge, legal compulsion, and prior possession apply."
        ),
        "compromise": (
            "Confidentiality obligations shall continue for five (5) years following the effective date of termination. "
            "Either party may disclose Confidential Information as required by applicable subpoena or governmental regulation, "
            "provided prompt advance written notice is provided to the disclosing party."
        ),
        "aggressive": (
            "Vendor acknowledges that all Customer Data and system telemetry constitute Customer Confidential Information. "
            "Vendor shall maintain strict non-disclosure obligations for seven (7) years and immediately return or certify "
            "destruction of all copies upon Customer's written request within ten (10) business days."
        ),
    },
    "termination": {
        "conservative": (
            "Either party may terminate this Agreement without cause upon sixty (60) days' prior written notice to the other. "
            "Either party may terminate immediately upon written notice if the other party materially breaches this Agreement "
            "and fails to cure such breach within thirty (30) days of receiving written notice thereof."
        ),
        "compromise": (
            "Customer may terminate this Agreement or any Statement of Work for convenience upon thirty (30) days' written notice, "
            "subject to payment for all documented services satisfactorily performed through the effective termination date. "
            "Upon termination, Vendor shall promptly remit a pro-rata refund of any unearned prepaid fees."
        ),
        "aggressive": (
            "Customer reserves the right to terminate this Agreement immediately with or without cause upon ten (10) days' notice. "
            "Vendor shall immediately provide a full pro-rata refund of all unused fees and assist in transition without charge."
        ),
    },
    "payment": {
        "conservative": (
            "All undisputed fees shall be payable within thirty (30) days from the date of receipt of a valid, itemized invoice. "
            "Customer may withhold any amounts disputed in good faith, provided written notice of the dispute is provided prior "
            "to the due date, without incurring late charges or suspension of services."
        ),
        "compromise": (
            "Invoices shall be payable Net 45 days. Late payments on undisputed sums shall accrue interest at the lesser of "
            "1.0% per month or the maximum rate allowed by law. Services may not be suspended without fourteen (14) days prior "
            "written notice and opportunity to resolve."
        ),
        "aggressive": (
            "Payment shall be due Net 60 days following receipt of approved invoice and verified delivery of milestones. "
            "No interest or late penalty shall accrue on any invoice subject to good faith audit by Customer."
        ),
    },
    "intellectual_property": {
        "conservative": (
            "Customer retains all right, title, and interest in and to Customer Data and all bespoke deliverables created specifically "
            "for Customer under this Agreement. Vendor retains its pre-existing background IP and grants Customer a perpetual, "
            "worldwide, non-exclusive license to use such background IP embedded within the deliverables."
        ),
        "compromise": (
            "Deliverables shall be owned by Customer upon full payment. Vendor retains ownership of its tools and methodologies, "
            "granting Customer an irrevocable license to utilize such tools solely as necessary to enjoy the benefits of the Deliverables."
        ),
        "aggressive": (
            "All work product, code, documentation, and inventions developed under this Agreement shall constitute 'work made for hire' "
            "and belong exclusively to Customer upon creation. Vendor assigns all worldwide IP rights therein to Customer."
        ),
    },
    "non_compete": {
        "conservative": (
            "Neither party shall solicit for employment any employee of the other party directly involved in the provision or receipt "
            "of Services during the Term and for twelve (12) months thereafter; provided, however, that general public advertisements "
            "and recruiting campaigns not targeted at such employees shall not violate this restriction."
        ),
        "compromise": (
            "The parties agree that general solicitations and headhunter searches conducted without specific direction shall not "
            "constitute a breach of any non-solicitation covenant. No post-termination restrictions on commercial competition apply."
        ),
        "aggressive": (
            "All non-compete and exclusivity restrictions are hereby deleted in their entirety. Customer shall be free to contract "
            "with, procure services from, or develop competing technologies with any third party at all times."
        ),
    },
    "warranties": {
        "conservative": (
            "Vendor warrants that the Services will perform in all material respects in accordance with the Documentation for a period "
            "of ninety (90) days from delivery, and that Services will be performed with professional care conforming to highest industry standards."
        ),
        "compromise": (
            "Vendor warrants that it has all requisite authority to enter into this Agreement and that the Services do not knowingly "
            "infringe any third-party proprietary rights. In the event of a warranty breach, Vendor shall re-perform the defective services at no cost."
        ),
        "aggressive": (
            "Vendor provides an unconditional warranty of non-infringement, merchantability, and fitness for a particular purpose. "
            "Any downtime or performance failure exceeding Service Level Agreements shall trigger automatic penalty credits."
        ),
    },
    "data_protection": {
        "conservative": (
            "Vendor shall maintain comprehensive technical and administrative safeguards to protect Customer Data against unauthorized "
            "access, loss, or alteration. Vendor shall notify Customer in writing within forty-eight (48) hours of discovering any security incident."
        ),
        "compromise": (
            "Vendor agrees to execute Customer's standard Data Processing Addendum (DPA) and notify Customer without undue delay (and in "
            "any event within seventy-two (72) hours) after becoming aware of any confirmed Personal Data Breach."
        ),
        "aggressive": (
            "Vendor shall comply with SOC 2 Type II, ISO 27001, and GDPR standards. In the event of any data breach, Vendor shall bear "
            "all costs of forensic investigation, consumer notification, credit monitoring, and regulatory fines."
        ),
    },
}


class ClauseEvaluationItem(BaseModel):
    clause_index: int
    risk_level: str = Field(description="RED, AMBER, or GREEN")
    score: int = Field(ge=0, le=100)
    standard_rule: str
    deviation_reason: str
    action_required: str


class ClauseEvaluationBatch(BaseModel):
    evaluations: list[ClauseEvaluationItem] = Field(default_factory=list)


def _heuristic_evaluate_clause(clause: Clause, rule: PlaybookRule) -> PlaybookFinding:
    """Deterministic, robust heuristic evaluator that reliably grades clauses against playbook rules."""
    text_lower = clause.text.lower()
    c_type = clause.clause_type

    # Detect high-risk indicators
    high_risk_detected = False
    moderate_risk_detected = False
    deviation_notes: list[str] = []

    for trigger in rule.unacceptable_triggers:
        if trigger in text_lower:
            high_risk_detected = True
            deviation_notes.append(f"Contains unacceptable condition: '{trigger}'")

    if c_type == "limitation_of_liability":
        if "unlimited" in text_lower and "not limited" in text_lower:
            high_risk_detected = True
            deviation_notes.append("Clause imposes unlimited liability exposure without market caps.")
        elif "sole remedy" in text_lower or "exclusive remedy" in text_lower:
            moderate_risk_detected = True
            deviation_notes.append("Limits remedies exclusively, potentially restricting damages recovery.")
        elif "24 months" in text_lower or "two years" in text_lower:
            moderate_risk_detected = True
            deviation_notes.append("Liability cap set at 24 months fees rather than preferred 12 months.")

    elif c_type == "indemnification":
        if "customer shall defend" in text_lower or "client shall indemnify" in text_lower:
            high_risk_detected = True
            deviation_notes.append("Customer bears unilateral indemnity burden for third-party claims.")
        elif "sole discretion" in text_lower:
            moderate_risk_detected = True
            deviation_notes.append("Settlement decisions granted in sole discretion of counterparty.")

    elif c_type == "termination":
        if "without cause" not in text_lower and "convenience" not in text_lower:
            moderate_risk_detected = True
            deviation_notes.append("Lacks express right of termination for convenience.")
        if "non-refundable" in text_lower:
            high_risk_detected = True
            deviation_notes.append("Prepaid fees declared strictly non-refundable upon early termination.")

    elif c_type == "payment":
        if "net 15" in text_lower or "upon receipt" in text_lower:
            moderate_risk_detected = True
            deviation_notes.append("Payment timeline is aggressive (Net 15 / Immediate receipt).")
        if "suspend" in text_lower and "without notice" in text_lower:
            high_risk_detected = True
            deviation_notes.append("Counterparty retains right to immediately suspend services without notice.")

    # Determine risk level and score
    if high_risk_detected:
        risk_level = "RED"
        score = 25
        action = "Reject current language; replace with Standard Conservative or Compromise fallback draft."
        reason = "; ".join(deviation_notes) or "Clause materially deviates from institutional risk thresholds."
    elif moderate_risk_detected:
        risk_level = "AMBER"
        score = 65
        action = "Propose negotiated amendment to align with market compromise position."
        reason = "; ".join(deviation_notes) or "Clause contains terms requiring moderation during negotiation."
    else:
        risk_level = "GREEN"
        score = 95
        action = "Approve clause as compliant with standard negotiation parameters."
        reason = "Clause substantially aligns with standard institutional playbook guidelines."

    # Retrieve fallback drafts
    defaults = FALLBACK_TEMPLATES.get(
        c_type,
        {
            "conservative": f"Standard compliant provision conforming to market norms for {rule.name}.",
            "compromise": f"Balanced provision with mutual protections for {rule.name}.",
            "aggressive": f"Max-favorable protective provision for {rule.name}.",
        },
    )

    return PlaybookFinding(
        clause_id=str(clause.id),
        clause_type=c_type,
        title=clause.title or rule.name,
        risk_level=risk_level,  # type: ignore[arg-type]
        score=score,
        page_start=clause.page_start,
        section_path=clause.section_path or rule.name,
        clause_text=clause.text[:800],
        standard_rule=rule.preferred_position,
        deviation_reason=reason,
        action_required=action,
        fallbacks=FallbackDrafts(
            conservative=defaults["conservative"],
            compromise=defaults["compromise"],
            aggressive=defaults["aggressive"],
        ),
    )


def review_document_playbook(
    session: Session,
    doc: Document,
    *,
    custom_rules: dict[str, PlaybookRule] | None = None,
    refresh: bool = False,
) -> PlaybookReviewOut:
    """Performs a comprehensive institutional Playbook compliance audit across all extracted clauses."""
    rules = custom_rules or DEFAULT_PLAYBOOK_RULES
    clauses = extract_clauses(session, doc, refresh=refresh)

    findings: list[PlaybookFinding] = []
    evaluated_types = set()

    # Prioritize clauses matching institutional rules
    for clause in clauses:
        c_type = clause.clause_type
        if c_type in rules and c_type not in evaluated_types:
            rule = rules[c_type]
            finding = _heuristic_evaluate_clause(clause, rule)
            findings.append(finding)
            evaluated_types.add(c_type)

    # For any missing critical rule categories that were NOT found in the contract,
    # generate an AMBER/RED omission finding (e.g. Missing Data Protection or Missing IP clause!)
    for rule_key, rule in rules.items():
        if rule_key not in evaluated_types and rule_key in [
            "limitation_of_liability",
            "indemnification",
            "data_protection",
            "confidentiality",
        ]:
            defaults = FALLBACK_TEMPLATES.get(rule_key, {})
            findings.append(
                PlaybookFinding(
                    clause_id=None,
                    clause_type=rule_key,
                    title=f"Omitted: {rule.name}",
                    risk_level="AMBER",
                    score=50,
                    page_start=None,
                    section_path="[Missing Provision]",
                    clause_text=f"[No substantive {rule.name} clause was detected in the agreement.]",
                    standard_rule=rule.preferred_position,
                    deviation_reason=f"Agreement completely omits an express {rule.name} provision, creating silent legal exposure.",
                    action_required=f"Insert an express {rule.name} clause using the Conservative fallback.",
                    fallbacks=FallbackDrafts(
                        conservative=defaults.get("conservative", "Add standard provision."),
                        compromise=defaults.get("compromise", "Add balanced provision."),
                        aggressive=defaults.get("aggressive", "Add protective provision."),
                    ),
                )
            )

    # Compute overall statistics
    red_count = sum(1 for f in findings if f.risk_level == "RED")
    amber_count = sum(1 for f in findings if f.risk_level == "AMBER")
    green_count = sum(1 for f in findings if f.risk_level == "GREEN")
    total_evaluated = len(findings)

    if total_evaluated > 0:
        compliance_score = int(sum(f.score for f in findings) / total_evaluated)
    else:
        compliance_score = 100

    if compliance_score >= 85 and red_count == 0:
        overall_risk = "Low Risk"
        summary = (
            f"Agreement demonstrates strong alignment ({compliance_score}% score) with institutional "
            f"standards. {green_count} provisions are fully compliant with no critical Red deviations."
        )
    elif compliance_score >= 70 and red_count <= 1:
        overall_risk = "Moderate Risk"
        summary = (
            f"Agreement presents moderate commercial risk ({compliance_score}% score). "
            f"Identified {red_count} high-priority Red items and {amber_count} moderate deviations requiring negotiation."
        )
    elif compliance_score >= 50 or red_count <= 2:
        overall_risk = "High Risk"
        summary = (
            f"Substantial exposure detected ({compliance_score}% score). Found {red_count} Red non-compliant "
            f"clauses and {amber_count} deviations that conflict with standard corporate positions."
        )
    else:
        overall_risk = "Severe Exposure"
        summary = (
            f"Critical legal risk ({compliance_score}% score). {red_count} severe Red violations detected. "
            f"Immediate remediation using standard fallback drafts is required prior to execution."
        )

    return PlaybookReviewOut(
        document_id=doc.id,
        compliance_score=compliance_score,
        overall_risk=overall_risk,
        summary=summary,
        red_count=red_count,
        amber_count=amber_count,
        green_count=green_count,
        total_evaluated=total_evaluated,
        findings=findings,
    )
