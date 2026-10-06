"""Generate three LONG test contracts (30-40 pages each) for manual upload testing.

All text is ORIGINAL but follows real-world structure: long definitions articles,
clause-by-clape conditions, and page-filling schedules (SLA grids, rate cards,
bills of quantities, repayment schedules). This mirrors how genuine long
contracts accumulate pages.

  1. Enterprise_IT_Outsourcing_Agreement.pdf  (~35 pages)
  2. Construction_Works_Contract.pdf          (~38 pages)
  3. Term_Loan_Facility_Agreement.pdf         (~32 pages)

Usage:  python "testing documents/generate_large_docs.py"
"""

from pathlib import Path

import pymupdf

OUT_DIR = Path(__file__).parent

CHARS_PER_PAGE = 1750  # conservative capacity of the A4 textbox at 10pt


def render_pdf(name: str, text: str) -> None:
    """Split `text` into pages on \f markers, hard-splitting any oversized page
    at line boundaries so the textbox never overflows."""
    doc = pymupdf.open()
    sections = [s for s in text.split("\f") if s.strip()]
    for section in sections:
        while len(section) > CHARS_PER_PAGE:
            cut = section.rfind("\n", int(CHARS_PER_PAGE * 0.7), CHARS_PER_PAGE)
            if cut == -1:
                cut = CHARS_PER_PAGE
            page_text, section = section[:cut], section[cut:]
            page = doc.new_page()
            rc = page.insert_textbox(
                pymupdf.Rect(50, 50, 560, 770), page_text, fontsize=10, fontname="helv"
            )
            if rc < 0:
                raise ValueError(f"page overflow in {name}")
        page = doc.new_page()
        rc = page.insert_textbox(
            pymupdf.Rect(50, 50, 560, 770), section, fontsize=10, fontname="helv"
        )
        if rc < 0:
            raise ValueError(f"page overflow in {name}")
    doc.save(OUT_DIR / name)
    doc.close()
    print(f"wrote {name}: {len(doc.page_count if False else pymupdf.open(OUT_DIR / name))} pages")


def num(n: int, width: int) -> str:
    return str(n).rjust(width)


# =====================================================================
# DOCUMENT 1 - Enterprise IT Outsourcing Agreement (~35 pages)
# =====================================================================
def build_ita() -> str:
    defs = [
        ("Agreement", "this master services agreement, including all Schedules and Exhibits"),
        ("Affiliate", "of a party, any entity controlling, controlled by, or under common control with that party"),
        ("Applicable Law", "all statutes, regulations, notifications and binding directions of any competent authority applicable to a party"),
        ("Business Day", "any day other than a Saturday, Sunday or public holiday at the location where the affected Services are performed"),
        ("Business Continuity Plan", "the documented arrangements described in Schedule 3 for continuing critical Services during a disruption"),
        ("Charges", "the fees and charges set out in Schedule 2 (Rate Card), as adjusted under Clause 7"),
        ("Confidential Information", "any non-public information disclosed by or on behalf of a party, in any form, designated confidential or that a reasonable recipient would treat as confidential"),
        ("Data Protection Law", "the Digital Personal Data Protection Act, 2023 and any successor or supplementary data protection legislation applicable to the Services"),
        ("Deliverable", "each item of work product to be provided by the Supplier as specified in an SOW or this Agreement"),
        ("Dispute Notice", "a written notice issued under Clause 19.1 identifying a dispute and the outcome sought"),
        ("Effective Date", "1 April 2026"),
        ("Escalation Matrix", "the escalation contacts and timeframes set out in Schedule 4"),
        ("Exit Date", "the date on which this Agreement terminates or expires for any reason"),
        ("Exit Plan", "the transition-out plan required by Clause 15"),
        ("Force Majeure Event", "an event beyond a party's reasonable control including war, terrorism, civil unrest, epidemic, earthquake, flood, and wide-area utility or internet failures"),
        ("Good Industry Practice", "practices, standards and procedures that a reasonably skilled and prudent service provider in the information technology outsourcing industry would follow"),
        ("Governmental Authority", "any national, state or local government, regulatory or administrative agency, or any court or tribunal"),
        ("Intellectual Property Rights", "patents, utility models, rights in inventions, copyright and neighbouring rights, trademarks, business names, domain names, goodwill, database rights, and all other similar rights, in each case whether registered or unregistered"),
        ("Key Personnel", "the individuals named in Clause 8.1 whose replacement requires the Customer's consent"),
        ("Losses", "losses, liabilities, damages, costs and expenses, including reasonable professional fees"),
        ("Major Outage", "unavailability of a Critical Service for more than four continuous hours in any calendar day, excluding Excluded Downtime"),
        ("Material Breach", "a breach which, having regard to its nature and consequences, substantially deprives a party of what it entered into this Agreement to obtain"),
        ("Party", "Northgate or Meridian, and Parties means both of them"),
        ("Personal Data", "any data relating to an identified or identifiable natural person processed in connection with the Services"),
        ("Rates", "the time-and-materials rates in Schedule 2"),
        ("Security Incident", "any unauthorised access to, or disclosure, loss or destruction of, Customer Systems or Personal Data"),
        ("Service Credit", "a credit against Charges calculated under Schedule 1 for a failure to meet a Service Level"),
        ("Service Levels", "the measurable performance standards for the Services set out in Schedule 1"),
        ("Services", "the application management, infrastructure operations, service-desk and related services to be performed by Meridian under this Agreement and each SOW"),
        ("SLA Measurement Period", "each calendar month during the Term, unless an SOW specifies a different period"),
        ("Statement of Work / SOW", "a statement of work executed by the Parties substantially in the form of Exhibit A"),
        ("Subcontractor", "any third party engaged by Meridian to perform any part of the Services"),
        ("Supplier Personnel", "Meridian's employees and individual contractors engaged in performing the Services"),
        ("Systems", "all hardware, software, networks and middleware used to provide or receive the Services"),
        ("Term", "the term of this Agreement as defined in Clause 14.1"),
        ("Transition Plan", "the plan for transitioning the Services from incumbent providers, attached as Schedule 3"),
        ("Volume Threshold", "the transaction volumes stated in Schedule 2 above which additional Charges apply"),
        ("Work Product", "all documents, code, configurations and other materials created by Meridian specifically for Northgate in performing the Services"),
        ("Critical Service", "each Service identified as critical in Schedule 1"),
        ("Excluded Downtime", "downtime caused by Customer Systems, Customer-caused faults, scheduled maintenance notified at least 5 Business Days ahead, or a Force Majeure Event"),
        ("Change Request", "a written proposal under Clause 6 to change the Services, Charges or Service Levels"),
        ("Benchmark", "the market benchmarking exercise described in Clause 7.4"),
        ("Grievance Officer", "the individual appointed under Data Protection Law whose details appear in Schedule 5"),
        ("Audit Report", "the annual controls report (SOC 2 Type II or ISO 27001 certificate with statement of applicability) delivered under Clause 9.6"),
        ("Acceptance Criteria", "the criteria for accepting a Deliverable stated in the applicable SOW"),
    ]
    parts = []
    parts.append(
        "ENTERPRISE INFORMATION TECHNOLOGY OUTSOURCING AGREEMENT\n\n"
        "between\n"
        "NORTHGATE GENERAL INSURANCE COMPANY LIMITED (\u201cCustomer\u201d)\n"
        "and\n"
        "MERIDIAN IT SERVICES PRIVATE LIMITED (\u201cSupplier\u201d)\n\n"
        "This Enterprise Information Technology Outsourcing Agreement (the \u201cAgreement\u201d) is made on "
        "1 April 2026 between Northgate General Insurance Company Limited, a public company registered "
        "under the companies law with its registered office at 42 Ridgeway House, Fort District, Mumbai "
        "400001 (the \u201cCustomer\u201d), and Meridian IT Services Private Limited, a private company with "
        "its registered office at Tower B, Salcon Aurelia, Outer Ring Road, Bengaluru 560103 (the "
        "\u201cSupplier\u201d).\n\n"
        "WHEREAS:\n"
        "(A) The Customer operates general insurance businesses across India and relies on a portfolio "
        "of information technology systems supporting policy administration, claims, distribution and "
        "finance (the \u201cCustomer Environment\u201d).\n"
        "(B) The Customer wishes to outsource to the Supplier the operation, support and enhancement "
        "of identified parts of the Customer Environment, and the Supplier represents that it has the "
        "capability, personnel and infrastructure to provide those services.\n"
        "(C) The Parties wish to record the terms on which the Supplier will provide the Services.\n\n"
        "NOW IT IS AGREED as follows:"
    )

    # Article 1 - Definitions
    parts.append("\f1. DEFINITIONS AND INTERPRETATION\n\n1.1 In this Agreement the following meanings apply:\n")
    for i, (term, meaning) in enumerate(defs, start=1):
        parts.append(f'"{term}" means {meaning.rstrip(".")}.\n')
    parts.append(
        "\n1.2 In this Agreement: (a) headings are for convenience only; (b) the singular includes "
        "the plural and vice versa; (c) references to Clauses and Schedules are to clauses of, and "
        "schedules to, this Agreement; (d) \u201cincluding\u201d means \u201cincluding without limitation\u201d; "
        "(e) references to any law include any amendment or re-enactment of it; and (f) where a "
        "conflict arises, the order of precedence is: this Agreement, then the Schedules, then each "
        "SOW, save that a Data Protection Annex prevails over all for data protection matters.\n"
        "1.3 Each Schedule and each executed SOW forms part of this Agreement."
    )

    # Article 2 - Services
    parts.append(
        "\f2. COMMENCEMENT AND SCOPE OF SERVICES\n\n"
        "2.1 With effect from the Effective Date and subject to the terms of this Agreement, the "
        "Supplier shall provide the Services described in Schedule 6 (Service Catalogue) and in each "
        "SOW, in accordance with this Agreement, Good Industry Practice, the Transition Plan and all "
        "Applicable Law.\n"
        "2.2 The Supplier shall perform the Services so that the Service Levels are met in each SLA "
        "Measurement Period. Meeting Service Levels is not of itself performance of the Services; it "
        "is a minimum standard.\n"
        "2.3 The Services are delivered from the delivery centres named in Schedule 6. The Supplier "
        "shall not move a delivery centre outside India without the Customer's prior written consent, "
        "except that disaster-recovery failover may occur to the secondary centre named in Schedule 3 "
        "for the minimum period necessary.\n"
        "2.4 The Supplier is responsible for the acts and omissions of the Supplier Personnel and "
        "Subcontractors as if they were its own. Nothing in this Agreement creates any right in any "
        "third party.\n"
        "2.5 The Supplier shall manage the Services so that the Customer's business continuity "
        "objectives, stated in Schedule 3, continue to be met throughout the Term, and shall test the "
        "Business Continuity Plan at least annually and provide the test report within 10 Business "
        "Days of each test.\n"
        "2.6 Where the Customer requests additional services reasonably within the scope of the "
        "Service Catalogue, the Parties shall negotiate in good faith an SOW or Change Request on the "
        "charging basis stated in Schedule 2. The Supplier shall not be obliged to accept, and shall "
        "not unreasonably refuse, any such request.\n"
        "2.7 The Customer shall provide, at its cost, the items listed as Customer Responsibilities "
        "in Schedule 6, including timely decisions, access to the Customer Environment and nominated "
        "business contacts. The Supplier is not in breach to the extent a delay is caused by a "
        "Customer Responsibility default."
    )

    # Article 3 - Governance
    parts.append(
        "\f3. GOVERNANCE AND MANAGEMENT\n\n"
        "3.1 The Parties shall operate the governance structure described in this Clause 3 "
        "throughout the Term.\n"
        "3.2 An Operational Review shall be held fortnightly between the Supplier's service delivery "
        "manager and the Customer's IT operations lead, reviewing tickets, Service Level performance, "
        "risks and upcoming changes. Minutes shall be issued within 2 Business Days and are deemed "
        "accepted unless objected to within 5 Business Days.\n"
        "3.3 A monthly Service Review shall be held between the Supplier's account director and the "
        "Customer's head of IT, reviewing SLA reports, Service Credits due, root-cause analyses for "
        "Major Outages, continuous-improvement actions and forward workload.\n"
        "3.4 A quarterly Executive Review shall be held between the Supplier's delivery vice-"
        "president and the Customer's chief information officer, reviewing strategic plans, "
        "benchmarking outcomes, contract performance and the relationship health score.\n"
        "3.5 Either party may convene an extraordinary governance meeting on 2 Business Days' notice "
        "to address a Major Outage, a dispute risk, or a Security Incident.\n"
        "3.6 Each party shall nominate a contract manager as the single point of accountability for "
        "the administration of this Agreement; the initial nominees are stated in Schedule 5.\n"
        "3.7 Where this Agreement requires approval, consent or agreement of a party, such approval "
        "shall not be unreasonably withheld or delayed, and a request shall be answered within 10 "
        "Business Days, failing which the requesting party may escalate under the Escalation Matrix."
    )

    # Article 4 - Service management
    parts.append(
        "\f4. SERVICE MANAGEMENT AND HELP DESK\n\n"
        "4.1 The Supplier shall operate a service desk for the Services on a follow-the-sun basis "
        "from its Pune and Bengaluru centres, providing a single point of contact for incidents and "
        "service requests 24 hours a day, 7 days a week.\n"
        "4.2 Every ticket shall be classified by priority (P1 critical, P2 high, P3 medium, P4 low) "
        "using the matrix in Schedule 1, acknowledged within the response times for its priority, and "
        "progressed to resolution or a documented workaround within the corresponding resolution "
        "targets.\n"
        "4.3 The Supplier shall maintain a ticketing system providing the Customer read access to "
        "live and historical tickets, and shall produce monthly reports including volumes by "
        "priority, first-contact resolution rate, reopen rate and SLA attainment.\n"
        "4.4 For each P1 incident, the Supplier shall: (a) notify the Customer within 30 minutes of "
        "classification; (b) establish a bridge and provide status updates every hour until "
        "resolution; and (c) deliver a root-cause analysis with corrective and preventive actions "
        "within 5 Business Days.\n"
        "4.5 Problem management: recurring incidents of the same underlying cause on 3 or more "
        "occasions in any rolling 30-day period shall be raised as a problem record with an owner "
        "and a fix plan.\n"
        "4.6 Changes to the Customer Environment within the Supplier's responsibility follow the "
        "change-management procedure in Schedule 3, with a weekly Change Advisory Board; emergency "
        "changes require retrospective approval within 2 Business Days.\n"
        "4.7 The Supplier shall maintain configuration management data covering the in-scope "
        "configuration items, reconciled quarterly to a stated accuracy of at least 95 percent."
    )

    # Article 5 - Personnel
    parts.append(
        "\f5. SUPPLIER PERSONNEL AND KEY PERSONNEL\n\n"
        "5.1 The initial Key Personnel are: (a) the account director; (b) the service delivery "
        "manager for application operations; (c) the infrastructure operations manager; and (d) the "
        "information security officer for the account.\n"
        "5.2 The Supplier shall not replace Key Personnel except for death, illness, resignation, "
        "dismissal for cause, promotion within the Supplier's organisation, or end of engagement, "
        "and in each case only with a successor of equal or better seniority and qualifications "
        "approved by the Customer, such approval not to be unreasonably withheld. The Supplier "
        "shall give at least 30 days' notice of any planned replacement and overlap the successor "
        "for at least 10 Business Days.\n"
        "5.3 The Supplier shall maintain a skills matrix for the account and ensure each Supplier "
        "Personnel is appropriately trained, certified for the technologies stated in Schedule 6, "
        "and holds any clearance required under Applicable Law.\n"
        "5.4 The Supplier shall not assign to the Services any individual who has been offered to "
        "the Customer for employment within the previous 6 months, or who is employed by the "
        "Customer, without the Customer's written consent.\n"
        "5.5 The Customer may require the removal of any Supplier Personnel for misconduct, material "
        "security concerns or breach of confidentiality, stating reasons; the Supplier shall remove "
        "the individual within 5 Business Days and provide a suitable replacement.\n"
        "5.6 The Supplier shall comply with all employment, social security, withholding and "
        "immigration laws in respect of Supplier Personnel, and shall indemnify the Customer "
        "against any claim by any individual that the Customer is their employer."
    )

    # Article 6 - Changes
    parts.append(
        "\f6. CHANGE MANAGEMENT OF THE AGREEMENT\n\n"
        "6.1 Either party may propose a Change Request. Each Change Request shall state the change, "
        "the reason, the impact on Charges, Service Levels and the Term, and the proposed effective "
        "date.\n"
        "6.2 The Supplier shall provide an impact assessment within 10 Business Days of receiving a "
        "Change Request, including a firm price for changes to SOW Deliverables and an estimate for "
        "other changes.\n"
        "6.3 No Change Request takes effect until executed in writing by authorised signatories of "
        "both Parties. Performed-but-unsigned changes are performed at the Supplier's risk.\n"
        "6.4 If the Parties cannot agree the price of a Change Request within 20 Business Days, the "
        "parties shall escalate to the Executive Review; the dispute provisions in Clause 19 apply "
        "to any remaining disagreement.\n"
        "6.5 Emergency changes required to restore a Critical Service may be implemented orally "
        "with written confirmation within 2 Business Days; the Parties shall then settle the charge "
        "basis promptly in accordance with Schedule 2."
    )

    # Article 7 - Charges
    parts.append(
        "\f7. CHARGES, INVOICING AND TAXES\n\n"
        "7.1 The Customer shall pay the Charges. Fixed monthly charges are payable monthly in "
        "arrears; time-and-materials work is invoiced against approved timesheets in the Rates in "
        "Schedule 2; and consumption above any Volume Threshold is charged at the unit rates in "
        "Schedule 2.\n"
        "7.2 The Supplier shall invoice on the first Business Day of each month for the preceding "
        "month, with supporting detail sufficient for the Customer to verify the invoice. Undisputed "
        "amounts are payable within 30 days of receipt of a correct invoice.\n"
        "7.3 The Customer may withhold from payment any amount it disputes in good faith, giving "
        "written reasons within 15 days of invoice receipt; the Parties shall resolve the dispute "
        "promptly and the Customer shall pay any undisputed balance when due.\n"
        "7.4 Late payment of undisputed amounts accrues interest at 1.25 percent per month or the "
        "maximum permitted by Applicable Law, whichever is lower.\n"
        "7.5 Base fixed charges may be adjusted once per Contract Year on each anniversary of the "
        "Effective Date by the lower of (a) the percentage movement in the consumer price index for "
        "industrial workers over the prior year, and (b) 5 percent. All other charges change only "
        "by Change Request.\n"
        "7.6 Benchmark: at the Customer's request not more than once in any 24-month period, an "
        "independent benchmark of the fixed charges against comparable Indian outsourcing "
        "arrangements shall be conducted by a firm agreed by the Parties. Where the benchmark shows "
        "the fixed charges exceed the market median by more than 5 percent, the Parties shall agree "
        "an adjustment to bring charges to the median; costs of the benchmark are shared equally "
        "unless the reduction exceeds 8 percent, in which case the Supplier bears them.\n"
        "7.7 All Charges are exclusive of GST, which shall be added at the applicable rate. The "
        "Supplier is responsible for its employees' taxes and social contributions.\n"
        "7.8 Service Credits due under Schedule 1 shall be applied against the next invoice after "
        "they are ascertained, and are the Customer's exclusive monetary remedy for Service Level "
        "failures, save where Clause 10.4 applies."
    )

    # Article 8 - Data protection
    parts.append(
        "\f8. DATA PROTECTION AND SECURITY\n\n"
        "8.1 Each Party shall comply with Data Protection Law in connection with this Agreement. "
        "The Parties record that the Customer is the data principal's business contact controller "
        "for Personal Data and the Supplier processes it only on the Customer's documented "
        "instructions.\n"
        "8.2 The Supplier shall: (a) process Personal Data only to provide the Services; (b) "
        "implement technical and organisational measures no less protective than those in Schedule "
        "5, including encryption in transit (TLS 1.2 or higher) and at rest (AES-256), "
        "role-based access with quarterly recertification, and centralised logging retained 12 "
        "months; (c) ensure Supplier Personnel are bound by confidentiality obligations; (d) not "
        "transfer Personal Data outside India without prior written consent or valid legal basis; "
        "(e) notify the Customer without undue delay and in any event within 24 hours of becoming "
        "aware of a Security Incident, providing cooperation, containment and remediation at its "
        "cost where the incident arises from its breach; and (f) on the Exit Date, return or "
        "securely destroy Personal Data and certify destruction within 30 days.\n"
        "8.3 The Supplier shall appoint the Grievance Officer for account matters and display "
        "contact details in the services portal.\n"
        "8.4 The Supplier shall undergo an annual third-party penetration test of the in-scope "
        "platforms and remediate critical findings within 15 days and high findings within 30 days, "
        "sharing the summary report with the Customer.\n"
        "8.5 The Customer retains the right to audit the Supplier's compliance with this Clause 8 "
        "once per Contract Year on 20 Business Days' notice, in person or through an independent "
        "firm under confidentiality, and additionally after any Security Incident."
    )

    # Article 9 - IP
    parts.append(
        "\f9. INTELLECTUAL PROPERTY AND LICENSES\n\n"
        "9.1 All Intellectual Property Rights in the Work Product vest in the Customer on creation, "
        "and to the extent vesting requires an assignment the Supplier hereby assigns them. On the "
        "Customer's request the Supplier shall execute such further documents as are reasonably "
        "necessary to perfect the Customer's title.\n"
        "9.2 The Supplier retains all Intellectual Property Rights in its pre-existing tools, "
        "frameworks, methodologies and generic know-how (the \u201cSupplier Materials\u201d). The Supplier "
        "grants the Customer a perpetual, irrevocable, worldwide, royalty-free, non-exclusive "
        "licence to use the Supplier Materials solely as embedded in or necessary to operate and "
        "maintain the Work Product.\n"
        "9.3 The Supplier shall not incorporate third-party or open-source components into any "
        "Deliverable without disclosing them and their licences in writing; the Supplier warrants "
        "that no Deliverable is delivered under a licence that would oblige the Customer to "
        "disclose or license its own source code.\n"
        "9.4 The Supplier indemnifies the Customer against any third-party claim that the receipt "
        "or use of the Services or Deliverables in accordance with this Agreement infringes any "
        "Indian or foreign patent, copyright, trademark or trade secret, and shall pay resulting "
        "Losses, provided the Customer notifies the Supplier promptly, grants the Supplier sole "
        "control of the defence and does not settle it without consent. If an injunction or claim "
        "prevents continued use, the Supplier shall at its cost procure the right to continue use, "
        "modify the item to be non-infringing, or replace it, and failing these, refund the fees "
        "paid for the affected item."
    )

    # Article 10 - Warranties & liability
    parts.append(
        "\f10. WARRANTIES AND LIMITATION OF LIABILITY\n\n"
        "10.1 Each Party warrants that it has full power and authority to enter into and perform "
        "this Agreement.\n"
        "10.2 The Supplier warrants that: (a) the Services will be performed with reasonable skill "
        "and care and in accordance with Good Industry Practice; (b) Deliverables will materially "
        "conform to their specifications and the Acceptance Criteria; (c) the Services and the "
        "Supplier's systems will comply with Applicable Law; and (d) it holds all registrations and "
        "licences required for its business.\n"
        "10.3 Except as expressly stated, all conditions, warranties and terms implied by statute "
        "or common law are excluded to the fullest extent permitted by law.\n"
        "10.4 Nothing in this Agreement excludes or limits liability for: death or personal injury "
        "caused by negligence; fraud or fraudulent misrepresentation; wilful misconduct; a Party's "
        "indemnity obligations; or breach of Clause 8 (Data Protection) or Clause 9 (Intellectual "
        "Property) or any liability that cannot lawfully be limited.\n"
        "10.5 Subject to Clause 10.4, neither Party is liable for indirect, special, incidental or "
        "consequential loss, or for loss of profit, revenue, anticipated savings or goodwill, "
        "however arising.\n"
        "10.6 Subject to Clause 10.4, each Party's total aggregate liability arising out of or in "
        "connection with this Agreement in any 12-month period is capped at an amount equal to the "
        "total Charges paid and payable in that 12-month period. The Supplier shall maintain "
        "professional indemnity and cyber insurance of at least Rs. 25 crore per claim with a "
        "reputable insurer and provide evidence on request.\n"
        "10.7 The Customer's exclusive remedies for Service Level failures are Service Credits "
        "and the step-in right in Clause 10.8.\n"
        "10.8 If a Major Outage affects a Critical Service on 3 or more occasions in any rolling "
        "3-month period, the Customer may (in addition to Service Credits) require a remediation "
        "plan agreed within 10 Business Days; persistent failure (6 or more occasions in any "
        "rolling 6-month period) constitutes a Material Breach."
    )

    # Article 11-13 Confidentiality, term, exit
    parts.append(
        "\f11. CONFIDENTIALITY\n\n"
        "11.1 Each Party shall keep the other's Confidential Information secret, use it only to "
        "perform this Agreement, and protect it with at least the same care as its own "
        "confidential information and in no event less than reasonable care.\n"
        "11.2 Permitted disclosures are those to: employees, officers, auditors and professional "
        "advisers of a Party who need to know and are bound by confidentiality; Subcontractors "
        "bound by terms no less protective; and a Governmental Authority where required by law, "
        "with (where lawful) prior notice to the other Party.\n"
        "11.3 The obligation lasts during the Term and for 5 years after the Exit Date; for trade "
        "secrets and Personal Data it lasts for as long as the information retains protection "
        "under Applicable Law.\n"
        "11.4 On request, each Party shall return or destroy the other's Confidential Information, "
        "save for one archival copy retained for legal compliance and copies in backup systems "
        "that are destroyed in the ordinary cycle.\n"
        "11.5 Neither Party shall make any press release or public statement referring to the "
        "other Party or this Agreement without prior written consent, save as required by law or "
        "stock-exchange regulation.\n\n"
        "12. TERM\n\n"
        "12.1 This Agreement commences on the Effective Date and continues for 60 months (the "
        "\u201cInitial Term\u201d), renewing automatically for successive periods of 24 months (each a "
        "\u201cRenewal Term\u201d) unless either Party gives written notice of non-renewal at least 90 days "
        "before the end of the Initial Term or the then-current Renewal Term.\n\n"
        "13. SUSPENSION\n\n"
        "13.1 The Supplier may suspend the Services (other than where suspension would itself "
        "endanger life, safety or regulatory obligations) if undisputed Charges remain unpaid 30 "
        "days after written notice, giving the Customer at least 10 Business Days' further written "
        "notice. Suspension is limited to the minimum scope and duration necessary and the Supplier "
        "shall restore Services promptly on payment.\n"
        "13.2 The Customer may direct immediate suspension of any Service where reasonably "
        "necessary to contain a Security Incident or comply with Applicable Law; the Parties shall "
        "agree in good faith an equitable charge basis for the suspension period."
    )

    # Article 14 - termination
    parts.append(
        "\f14. TERMINATION\n\n"
        "14.1 Either Party may terminate this Agreement, or any SOW, by written notice if the "
        "other Party commits a Material Breach and fails to remedy it within 30 days of a written "
        "notice describing the breach.\n"
        "14.2 The Customer may terminate this Agreement, in whole or in part, for convenience on "
        "90 days' written notice, paying: all Charges accrued to the Exit Date; and, where the "
        "termination falls before the second anniversary of the Effective Date, an early-"
        "termination charge equal to 25 percent of the average monthly fixed Charges for the "
        "remaining months of the Initial Term (net of costs saved).\n"
        "14.3 Either Party may terminate with immediate effect if the other becomes insolvent, "
        "enters liquidation or administration, has an encumbrancer take possession, or ceases (or "
        "threatens to cease) business.\n"
        "14.4 The Customer may terminate for change of control of the Supplier on 60 days' "
        "notice, where the resulting controller is a competitor of the Customer.\n"
        "14.5 Termination of this Agreement terminates all SOWs unless the Parties agree "
        "otherwise; termination of a SOW does not by itself terminate this Agreement.\n"
        "14.6 Termination is without prejudice to accrued rights. Clauses which by their nature "
        "are intended to survive (including 8, 9, 10, 11, 15 and 19 to 22) survive the Exit Date."
    )

    # Article 15 - exit
    parts.append(
        "\f15. EXIT AND TRANSITION ASSISTANCE\n\n"
        "15.1 Not later than 90 days after the Effective Date, the Supplier shall deliver an Exit "
        "Plan covering: the register of Services, systems and credentials in its control; the "
        "knowledge-transfer materials to be maintained; data extraction in documented formats; "
        "assistance to a successor provider; and a de-provisioning timeline. The Supplier shall "
        "keep the Exit Plan current throughout the Term at no additional charge.\n"
        "15.2 On notice of termination or non-renewal, the Supplier shall perform the Exit Plan, "
        "provide transition assistance for up to 6 months at the Rates, and prioritise continuity "
        "of Critical Services above all commercial considerations.\n"
        "15.3 The Supplier shall not, during exit assistance, take any step to lock in the "
        "Customer, including refusing reasonable access to documentation, credentials, source "
        "configurations or data in undocumented formats.\n"
        "15.4 All Customer Data shall be returned in the documented formats stated in the Exit "
        "Plan, with verified integrity checks; destruction certifications follow within 30 days.\n"
        "15.5 The obligations in this Clause 15 survive termination howsoever caused, and the "
        "Parties agree they are reasonable and necessary protections for the Customer's business."
    )

    # Article 16 - business continuity / subcontracting
    parts.append(
        "\f16. BUSINESS CONTINUITY AND SUBCONTRACTING\n\n"
        "16.1 The Supplier shall maintain and test the Business Continuity Plan per Clause 2.5, "
        "covering delivery-centre loss, staffing disruption, network failure and pandemic "
        "scenarios, with recovery time objectives of 4 hours for Critical Services.\n"
        "16.2 The Supplier may engage Subcontractors listed in Schedule 5 without consent. New "
        "Subcontractors require the Customer's prior written consent, save for staff augmentation "
        "through the Supplier's own bench. For each Subcontractor the Supplier remains fully "
        "liable, shall flow down obligations equivalent to Clauses 8 and 11, and shall provide the "
        "Customer access to audit reports relevant to the Services.\n"
        "16.3 Where Applicable Law requires regulatory approval of a Subcontractor (including any "
        "outsourcing notification to the insurance regulator), the Supplier shall provide "
        "information promptly and the arrangement shall not commence until any required approval "
        "is obtained.\n\n"
        "17. INSURANCE\n\n"
        "17.1 The Supplier shall maintain, at its own cost, with insurers of good repute: "
        "(a) commercial general liability of not less than Rs. 5 crore per occurrence; (b) "
        "professional indemnity (technology errors and omissions) of not less than Rs. 25 crore in "
        "the aggregate; (c) cyber liability of not less than Rs. 25 crore including notification "
        "costs and regulatory defence; and (d) statutory employee compensation coverage.\n"
        "17.2 The Supplier shall provide certificates of insurance on execution and on each "
        "renewal, and shall give the Customer 30 days' notice of cancellation or material "
        "reduction. The insurance requirements do not limit or reduce the Supplier's liabilities "
        "under this Agreement."
    )

    # Article 18-19 dispute + law
    parts.append(
        "\f18. FORCE MAJEURE\n\n"
        "18.1 Neither Party is liable for failure or delay caused by a Force Majeure Event, "
        "provided the affected Party: notifies the other within 5 Business Days with reasonable "
        "detail; uses reasonable endeavours to mitigate; and resumes performance promptly when "
        "the event ceases.\n"
        "18.2 Payment obligations are not excused by a Force Majeure Event except to the extent "
        "Services could not be performed; Charges for services not performed are equitably "
        "reduced, and the Parties shall cooperate on invoking the Business Continuity Plan.\n"
        "18.3 If a Force Majeure Event prevents substantial performance for more than 60 "
        "consecutive days, either Party may terminate this Agreement on 30 days' written notice, "
        "and the Parties shall agree transition assistance per Clause 15.\n\n"
        "19. DISPUTE RESOLUTION, GOVERNING LAW\n\n"
        "19.1 The Parties shall first attempt to resolve any dispute by escalation per the "
        "Escalation Matrix over a period not exceeding 20 Business Days from a Dispute Notice.\n"
        "19.2 Failing resolution, the dispute shall be referred to arbitration of a sole "
        "arbitrator jointly appointed under the Arbitration and Conciliation Act, 1996; the seat "
        "and venue is Mumbai; proceedings and the award are in English; the award is final and "
        "binding.\n"
        "19.3 Nothing prevents either Party from seeking urgent interim relief from a court, and "
        "each Party irrevocably submits to the courts at Mumbai for that purpose only.\n"
        "19.4 During any dispute the Supplier shall continue performing the Services undisputed, "
        "and the Customer shall continue paying undisputed Charges.\n"
        "19.5 This Agreement is governed by the laws of India."
    )

    # Article 20 - general boilerplate
    parts.append(
        "\f20. GENERAL PROVISIONS\n\n"
        "20.1 Entire agreement: this Agreement (with its Schedules, Exhibits and executed SOWs) "
        "is the entire agreement between the Parties regarding its subject matter and supersedes "
        "all prior proposals, discussions and understandings. Each Party acknowledges it has not "
        "relied on any representation not expressly set out herein.\n"
        "20.2 Variations: no variation is effective unless in writing signed by authorised "
        "signatories of both Parties (a Change Request under Clause 6 being sufficient).\n"
        "20.3 Waiver: no failure or delay in exercising a right operates as a waiver; a waiver is "
        "effective only if written and only to the extent stated.\n"
        "20.4 Assignment: neither Party may assign or transfer this Agreement without the other's "
        "prior written consent, not to be unreasonably withheld, save that the Supplier may "
        "assign to an Affiliate performing substantially the same business, on written notice "
        "and an assumption of obligations.\n"
        "20.5 Severability: if any provision is held invalid or unenforceable, it shall be "
        "modified to the minimum extent necessary or, if not possible, severed; the remainder "
        "continues in force, and the Parties shall negotiate in good faith a valid replacement "
        "with equivalent effect.\n"
        "20.6 Relationship: the Parties are independent contractors; nothing creates a "
        "partnership, joint venture, agency or employment relationship.\n"
        "20.7 Notices: notices shall be in writing and delivered by hand, registered post, or "
        "email with delivery confirmation to the addresses in Schedule 5, and are deemed received "
        "on delivery or 2 Business Days after posting.\n"
        "20.8 Third parties: no person other than the Parties has any right to enforce this "
        "Agreement.\n"
        "20.9 Language and counterparts: this Agreement is in English and may be executed in "
        "counterparts, including by PDF signature, each of which is an original.\n"
        "20.10 Survival and cumulative remedies: rights and remedies under this Agreement are "
        "cumulative and in addition to those at law.\n\n"
        "IN WITNESS WHEREOF the Parties, by their duly authorised representatives, have executed "
        "this Agreement on the date first written above.\n\n"
        "For NORTHGATE GENERAL INSURANCE COMPANY LIMITED        For MERIDIAN IT SERVICES "
        "PRIVATE LIMITED\n\n"
        "Signed: _____________________________                 Signed: "
        "_____________________________\n"
        "Name: Vandana Krishnan                               Name: Prakash Iyengar\n"
        "Title: Chief Operating Officer                       Title: Chief Executive Officer\n"
        "Date: 1 April 2026                                   Date: 1 April 2026\n\n"
        "Witness 1: ________________________                  Witness 2: "
        "________________________"
    )

    # SCHEDULE 1 - SLA grid
    lines = []
    lines.append("SCHEDULE 1 - SERVICE LEVELS AND SERVICE CREDITS")
    lines.append("\nA. Availability and incident response for Critical Services\n")
    w1 = 34
    for row in [
        ("Metric", "Target"),
        ("Monthly availability (per Critical Service)", "99.7% measured over the SLA Measurement Period"),
        ("P1 response / restore / workaround", "15 min / 4 hours / 8 hours"),
        ("P2 response / resolution", "1 hour / 2 Business Days"),
        ("P3 response / resolution", "4 hours / 5 Business Days"),
        ("P4 response / resolution", "1 Business Day / 10 Business Days"),
        ("Major Outage notification", "Within 30 minutes of classification"),
        ("Service desk first-contact resolution", ">= 60% monthly"),
        ("Ticket reopen rate", "<= 4% monthly"),
        ("Change success rate", ">= 97% monthly (no failed change requiring rollback)"),
        ("Backup success rate", ">= 99% of scheduled jobs; restore test monthly"),
        ("Security patching: critical / high", "15 days / 30 days from vendor release"),
        ("Access review completion", "Quarterly, within 10 Business Days of quarter end"),
        ("Report delivery (monthly pack)", "3 Business Days after month end"),
        ("Root cause analysis delivery (P1)", "5 Business Days"),
    ]:
        if row[0] == "Metric":
            lines.append(row[0].ljust(w1) + "  " + row[1])
            lines.append("-" * 96)
        else:
            import textwrap
            wrapped = textwrap.wrap(f"{row[0]}".ljust(w1) + "  " + row[1], width=96) or [""]
            lines.append(wrapped[0])
            for extra in wrapped[1:]:
                lines.append(" " * (w1 + 2) + extra.strip())
    lines.append("\nB. Service Credits (per SLA Measurement Period, per affected Service)\n")
    for row in [
        ("Attainment band", "Credit (% of that Service's monthly fixed charge)"),
        ("99.5% to < 99.7% availability or <=2 SLA misses", "5%"),
        ("99.0% to < 99.5% availability or 3-5 SLA misses", "10%"),
        ("95.0% to < 99.0% availability", "20%"),
        ("< 95.0% availability or any Major Outage > 8 hours", "30%"),
    ]:
        lines.append(row[0].ljust(w1) + "  " + row[1])
    lines.append(
        "\nC. Measurement and reporting: SLA attainment is measured automatically from system "
        "and ticketing data; Excluded Downtime is deducted. The monthly report shows attainment, "
        "misses, Excluded Downtime and Credits due. Persistent failure is treated under Clause "
        "10.8."
    )
    parts.append("\f" + "\n".join(lines))

    # SCHEDULE 2 - rate card + volumes
    lines2 = []
    lines2.append("SCHEDULE 2 - RATE CARD AND VOLUME THRESHOLDS\n")
    lines2.append("A. Fixed monthly charges (summary)\n")
    for row in [
        ("Workstream", "Monthly charge (Rs.)"),
        ("Application operations - policy suite", "18,50,000"),
        ("Application operations - claims suite", "16,20,000"),
        ("Infrastructure operations (120 VMs, 2 DCs)", "12,80,000"),
        ("Service desk (24x7, tiered)", "7,40,000"),
        ("Security operations (managed)", "6,60,000"),
    ]:
        lines2.append(row[0].ljust(46) + row[1].rjust(24))
    lines2.append("\nB. Time-and-materials Rates (Rs. per person-day)\n")
    for role, onshore, off_ncr, off_blr in [
        ("Programme director", "95,000", "52,000", "48,000"),
        ("Solution architect", "82,000", "46,000", "42,000"),
        ("Senior engineer (8+ yrs)", "68,000", "38,000", "34,000"),
        ("Engineer (4-8 yrs)", "52,000", "29,000", "26,000"),
        ("Analyst (2-4 yrs)", "40,000", "22,000", "20,000"),
        ("Service desk agent", "28,000", "16,000", "14,000"),
        ("Project manager", "62,000", "35,000", "32,000"),
        ("QA automation engineer", "50,000", "28,000", "25,000"),
        ("Security analyst (L2)", "58,000", "33,000", "30,000"),
        ("Database administrator", "56,000", "32,000", "29,000"),
        ("Cloud platform engineer", "60,000", "34,000", "31,000"),
        ("Technical writer", "32,000", "18,000", "16,000"),
    ]:
        lines2.append(role.ljust(26) + onshore.rjust(14) + off_ncr.rjust(14) + off_blr.rjust(14))
    lines2.append("\nC. Volume thresholds (beyond which unit rates apply)\n")
    for row in [
        ("Tickets beyond 6,000 per month", "Rs. 145 per ticket (P3/P4 weighted average)"),
        ("Backup storage beyond 80 TB", "Rs. 210 per TB per month"),
        ("Additional monitored instances beyond 120", "Rs. 2,400 per instance per month"),
        ("Test environment refreshes beyond 24 per year", "Rs. 85,000 per refresh"),
    ]:
        lines2.append(row[0].ljust(46) + row[1])
    parts.append("\f" + "\n".join(lines2))

    # SCHEDULE 3 - transition + BCP
    t_lines = [
        "SCHEDULE 3 - TRANSITION PLAN, CHANGE PROCEDURE AND BUSINESS CONTINUITY\n",
        "A. Transition (from incumbent providers) - 16-week plan\n",
        "Weeks 1-2   Mobilise: joint team stand-up, access provisioning, comms plan.",
        "Weeks 2-4   Discovery: document systems, credentials vault transfer, CMDB baseline.",
        "Weeks 3-6   Knowledge transfer: shadowing, runbook review, incumbents' exit sessions.",
        "Weeks 5-8   Parallel run: Supplier executes with incumbent oversight per workstream.",
        "Weeks 8-12  Cut-over wave 1 (service desk), wave 2 (application ops), wave 3 (infra).",
        "Weeks 12-16 Stabilisation: daily SLA monitoring, hyper-care staffing, exit gate review.",
        "Transition acceptance criteria: 4 consecutive weeks at or above SLA floors; zero P1 "
        "unresolved older than 2 Business Days; credential vault reconciled; runbooks signed off "
        "by the Customer for every Critical Service.",
        "",
        "B. Change management procedure",
        "1. Requester raises a change record with classification and risk assessment.",
        "2. CAB meets weekly (Wednesday) and approves standard/normal changes; emergency CAB "
        "convenes within 2 hours for P1-related changes.",
        "3. Approved changes are scheduled in the forward schedule of change; conflicting "
        "changes are sequenced by the CAB chair.",
        "4. Post-implementation review within 3 Business Days; failed changes trigger root-cause "
        "and are reported in the monthly pack.",
        "",
        "C. Business continuity - recovery objectives",
        "Critical Services RTO 4 hours / RPO 15 minutes; DR site: Hyderabad; failover tested "
        "annually and after any material architecture change; the BCP owner is the Supplier's "
        "information security officer for the account.",
    ]
    parts.append("\f" + "\n".join(t_lines))

    # SCHEDULE 4/5 - escalation + contacts + subcontractors + security measures
    m_lines = [
        "SCHEDULE 4 - ESCALATION MATRIX\n",
        "Level 1: Service delivery manager <-> IT operations lead - within 1 Business Day.",
        "Level 2: Account director <-> Head of IT - within 2 Business Days.",
        "Level 3: Delivery VP <-> Chief Information Officer - within 5 Business Days.",
        "Level 4: Chief executives - within 10 Business Days, then Dispute Notice if unresolved.",
        "",
        "SCHEDULE 5 - CONTACTS, SUBCONTRACTORS AND SECURITY MEASURES",
        "",
        "Customer contract manager: R. Senthil, GM IT Operations, r.senthil@northgate.example",
        "Supplier contract manager: K. Anand, Account Director, k.anand@meridianits.example",
        "Grievance Officer (Supplier): Ms. Jyoti Menon, grievance.officer@meridianits.example",
        "",
        "Approved subcontractors: Meridian Staffing Solutions Pvt Ltd (bench augmentation); "
        "SecureWatch Systems LLP (SOC tooling). Any addition requires Clause 16.2 consent.",
        "",
        "Minimum security measures: ISO 27001-aligned ISMS; encryption in transit TLS 1.2+ and "
        "at rest AES-256; MFA for all privileged access; privileged access management vault; "
        "centralised logging 12 months; quarterly vulnerability scans and annual penetration "
        "test; secure SDLC with code review; segregation of duties; background verification of "
        "Supplier Personnel; data classification handling rules; clean-desk and screen-lock "
        "policy; incident response plan aligned to Schedule 1 timelines.",
    ]
    parts.append("\f" + "\n".join(m_lines))

    # SCHEDULE 6 - catalogue
    c_lines = [
        "SCHEDULE 6 - SERVICE CATALOGUE, DELIVERY CENTRES AND CUSTOMER RESPONSIBILITIES",
        "",
        "In-scope services:",
        "  1. Policy administration suite - application support and minor enhancements",
        "  2. Claims suite - application support and minor enhancements",
        "  3. Distribution portal and partner APIs - support",
        "  4. Data centre operations - compute, storage, backup (Mumbai primary, Hyderabad DR)",
        "  5. Network operations support (L1/L2), working with the Customer's carrier",
        "  6. 24x7 service desk for named applications and infrastructure",
        "  7. Security operations - monitoring, vulnerability management, access administration",
        "  8. Database administration - performance, patching, high-availability upkeep",
        "  9. Reporting and MIS pack production for business stakeholders",
        " 10. Test environment management and scheduled refreshes",
        "",
        "Delivery centres: Pune (primary), Bengaluru (secondary), Hyderabad (DR only).",
        "",
        "Customer responsibilities: timely decisions and approvals; accurate documentation of the "
        "Customer Environment at handover; third-party vendor coordination where the Supplier is "
        "not the contracted party; named business SMEs per application (at least one per suite); "
        "network and identity infrastructure owned by the Customer (links, AD/SSO platform); "
        "license procurement for third-party products; and reasonable physical access "
        "arrangements for audits and major incident bridging.",
        "",
        "Technology stack (for certification requirements): Java 17 microservices on Kubernetes; "
        "PostgreSQL 15 and Oracle 19c databases; VMware virtualisation on NetApp storage; "
        "Kafka-based integration bus; Azure AD SSO with F5 load balancing; Terraform-managed "
        "infrastructure; Dynatrace monitoring; ServiceNow ticketing.",
    ]
    parts.append("\f" + "\n".join(c_lines))

    # EXHIBIT A - SOW form
    ex_lines = [
        "EXHIBIT A - FORM OF STATEMENT OF WORK",
        "",
        "SOW No.: ______        Title: ______________________        Effective: ______",
        "Under the Enterprise IT Outsourcing Agreement dated 1 April 2026.",
        "",
        "1. Background and objective: ____________________________________________",
        "2. Scope of work (in scope / out of scope): ______________________________",
        "3. Deliverables and Acceptance Criteria: ________________________________",
        "4. Timeline and milestones: _____________________________________________",
        "5. Charges: fixed ______ / T&M ______ / consumption _____________________",
        "6. Service Levels specific to this SOW: _________________________________",
        "7. Dependencies (Customer/Supplier): ____________________________________",
        "8. Governance: reporting cadence and contacts: __________________________",
        "9. Acceptance procedure and remedies for rejection: _____________________",
        "10. Special terms (if any): _____________________________________________",
        "",
        "For the Customer: name, title, signature, date.   For the Supplier: name, title, "
        "signature, date. SOWs are executed by the contract managers unless the Parties agree "
        "otherwise. An SOW cannot amend this Agreement; conflicts resolve per Clause 1.2.",
    ]
    parts.append("\f" + "\n".join(ex_lines))

    return "".join(parts)


# =====================================================================
# DOCUMENT 2 - Construction works contract (~38 pages)
# =====================================================================
def build_ccc() -> str:
    parts = []
    parts.append(
        "CONSTRUCTION CONTRACT FOR WORKS\n\n"
        "Employer: SUNCREST DEVELOPERS PRIVATE LIMITED\n"
        "Contractor: BALAJI INFRA PROJECTS PRIVATE LIMITED\n"
        "Project: Construction of \u201cSuncrest Greens\u201d Residential Tower B (G+16), Plot 74, "
        "Sector 88, Noida, Uttar Pradesh\n"
        "Contract No: SDL/NP/TB/2026-11\n\n"
        "This Construction Contract (the \u201cContract\u201d) is made on 15 June 2026 between Suncrest "
        "Developers Private Limited, a company incorporated under the companies law having its "
        "registered office at 3rd Floor, Orbis Tower, Sector 62, Noida 201301 (the \u201cEmployer\u201d), "
        "and Balaji Infra Projects Private Limited, having its registered office at 902, Wave "
        "One, Sector 18, Noida 201301 (the \u201cContractor\u201d).\n\n"
        "WHEREAS the Employer intends to construct a residential tower known as Tower B "
        "(ground plus sixteen upper floors) with two basement levels, associated external "
        "development, and all works described in the Contract Documents (the \u201cWorks\u201d), and has "
        "accepted the Contractor's tender dated 2 May 2026; and whereas the Parties wish to "
        "record the terms on which the Contractor shall execute and complete the Works.\n\n"
        "NOW THIS CONTRACT WITNESSES as follows:"
    )

    parts.append(
        "\f1. DEFINITIONS AND INTERPRETATION\n\n"
        "1.1 In this Contract:\n"
        "(a) \u201cAct of Insubordination\u201d is not used; \u201cAdjudicating Officer\u201d means the person "
        "named in Clause 22 to decide disputes in the first instance.\n"
        "(b) \u201cBill of Quantities\u201d means the priced schedule of items, quantities and rates in "
        "Schedule B, including preliminary and general items.\n"
        "(c) \u201cCommencement Date\u201d means 1 July 2026 or the date the Contractor is given "
        "unencumbered possession of the Site, whichever is later.\n"
        "(d) \u201cCompletion\u201d means the stage at which the Works are complete, tested and fit "
        "for the intended occupation described in the Employer's Requirements, save for minor "
        "items that do not prejudice occupation.\n"
        "(e) \u201cContract Price\u201d means Rs. 96,50,00,000/- (Rupees ninety-six crore fifty lakh "
        "only), as adjusted under this Contract.\n"
        "(f) \u201cContractor's Documents\u201d means all drawings, calculations, method statements, "
        "shop drawings, as-built records and other documents prepared by or for the Contractor.\n"
        "(g) \u201cDefects Liability Period\u201d means 365 days from the date of Completion, "
        "extendable under Clause 17 for portions repaired or replaced.\n"
        "(h) \u201cDelay Damages\u201d has the meaning in Clause 15.\n"
        "(i) \u201cEmployer's Requirements\u201d means the functional, dimensional and aesthetic "
        "requirements in Schedule C.\n"
        "(j) \u201cEngineer\u201d means the architect/engineer-in-charge appointed by the Employer, "
        "initially M/s Framework Design Studio LLP, acting through its partner in charge.\n"
        "(k) \u201cGross Completion Certificate\u201d or \u201cGCC\u201d means the certificate issued by the "
        "Engineer under Clause 16 confirming Completion.\n"
        "(l) \u201cGood Industry Practice\u201d means practices conforming to the National Building "
        "Code 2016, IS codes, and the standards of a reasonably competent contractor executing "
        "similar works.\n"
        "(m) \u201cNotice of Intention to Claim EOT\u201d has the meaning in Clause 14.3.\n"
        "(n) \u201cPerformance Security\u201d means the bank guarantee required by Clause 12.\n"
        "(o) \u201cProgramme\u201d means the programme in Schedule D as updated under Clause 9.\n"
        "(p) \u201cRA Bill\u201d means a running-account bill for work executed to date.\n"
        "(q) \u201cRetention Money\u201d means the amount retained under Clause 13.4.\n"
        "(r) \u201cSite\u201d means Plot 74, Sector 88, Noida, as delineated in the Site Plan.\n"
        "(s) \u201cVariation\u201d has the meaning in Clause 10.\n"
        "1.2 Interpretation: headings are for convenience; the singular includes the plural; "
        "statutory references include re-enactments; \u201cmonth\u201d means calendar month; time is of "
        "the essence for the Time for Completion; where documents conflict, the order of "
        "precedence is: (1) this Contract, (2) Schedules, (3) Employer's Requirements, (4) "
        "Contractor's tender, (5) Contractor's Documents."
    )

    parts.append(
        "\f2. SCOPE AND STANDARD OF WORKS\n\n"
        "2.1 The Contractor shall execute, complete and remedy defects in the Works in "
        "accordance with this Contract, the Bill of Quantities, the Employer's Requirements, "
        "the Programme and Good Industry Practice.\n"
        "2.2 The Works comprise, without limitation: excavation and shoring; raft and "
        "pile-supported foundations; reinforced-concrete frame to G+16 with two basements; "
        "blockwork and plastering; waterproofing to basements, terraces and toilets; internal "
        "and external finishes as specified; plumbing and sanitary installations; electrical "
        "installations including DG backup; fire detection, firefighting and sprinklers; "
        "elevator installation coordination (lifts supplied nominally by the Employer); "
        "external development including roads, storm-water, landscaping boundaries and the "
        "clubhouse shell; testing, commissioning and handover documentation.\n"
        "2.3 All materials and workmanship shall conform to the specifications in Schedule C "
        "and, where silent, to IS codes and the National Building Code 2016. The Engineer may "
        "reject non-conforming work, which the Contractor shall remove and re-execute at its "
        "cost within the time directed.\n"
        "2.4 The Contractor shall provide all plant, tools, scaffolding, labour, supervision, "
        "consumables, temporary utilities and site facilities necessary for execution, save "
        "only items expressly stated as Employer-supplied in Schedule C.\n"
        "2.5 Setting out: the Contractor shall set out the Works from benchmarks established "
        "by the Engineer and verify all dimensions on Site before execution; errors in setting "
        "out are rectified at the Contractor's cost.\n"
        "2.6 The Contractor shall protect third parties, adjoining structures and existing "
        "services, and shall be liable for damage caused by its operations, save to the extent "
        "caused by the Employer or the Engineer's instructions.\n"
        "2.7 Statutory compliance: labour licences, EPF/ESI registrations, building-permit "
        "conditions applicable to the executing contractor, pollution-control consents for "
        "batching and crushing, and safety rules under the BOCW Act, 1996 are the "
        "Contractor's responsibility; core permits for the project are the Employer's."
    )

    parts.append(
        "\f3. EMPLOYER AND ENGINEER OBLIGATIONS\n\n"
        "3.1 The Employer shall: (a) give possession of the Site on the Commencement Date; "
        "(b) provide the drawings listed in Schedule C at the times stated; (c) make payments "
        "as provided in Clause 13; (d) procure and fund statutory approvals that only the owner "
        "can obtain (commencement certificate, occupancy certificate support); and (e) supply "
        "free of cost the lifts, DG sets and transformer named in Schedule C per the delivery "
        "schedule.\n"
        "3.2 The Engineer shall administer the Contract neutrally: issue drawings and "
        "instructions with reasonable promptness, inspect and certify work, decide on quality "
        "conformity, and assess Variation values and EOT claims with reasons. The Engineer's "
        "site instructions bind the Contractor unless they require a Variation, in which case "
        "Clause 10 applies.\n"
        "3.3 Neither the Employer nor the Engineer may relieve the Contractor of any "
        "obligation under this Contract; no instruction or omission operates as a waiver.\n"
        "3.4 The Employer may replace the Engineer by 15 days' notice; the successor shall be "
        "of equivalent professional standing.\n\n"
        "4. PROGRAMME AND TIME\n\n"
        "4.1 The Contractor shall complete the Works within 30 months of the Commencement Date "
        "(the \u201cTime for Completion\u201d), in accordance with the Programme (Schedule D), which "
        "includes milestones: plinth completion by month 4; each successive slab cycle at 21 "
        "days average; structure top-out by month 13; masonry and plastering complete by month "
        "19; MEP first-fix by month 20; lifts operational by month 23; finishes by month 27; "
        "testing and commissioning by month 29; GCC by month 30.\n"
        "4.2 The Contractor shall submit a detailed Programme within 21 days of the "
        "Commencement Date for the Engineer's review, and update it monthly, showing progress "
        "against milestones and a recovery proposal wherever actual progress falls more than "
        "15 days behind.\n"
        "4.3 The Contractor shall commence within 7 days of receiving possession and shall "
        "proceed with due expedition and without delay, save as permitted."
    )

    parts.append(
        "\f5. POSSESSION, SITE DATA AND OBLIGATIONS ON SITE\n\n"
        "5.1 The Employer grants possession of the Site progressively: full basement area by "
        "the Commencement Date; the balance plot by 30 days later. The Contractor shall not "
        "use any part of the Site for purposes other than the Works.\n"
        "5.2 Subsoil data: the Employer provides the geotechnical investigation report in "
        "Schedule C. The Contractor is deemed to have satisfied itself as to subsoil "
        "conditions save for contamination or archaeological finds which it could not "
        "reasonably have foreseen from the report, which are dealt with as Variations or EOT "
        "events.\n"
        "5.3 Site management: the Contractor shall keep the Site tidy, control dust and "
        "noise within CPCB norms, provide barricading, signage and night lighting, manage "
        "worker welfare facilities (creche, first aid, drinking water, toilets per BOCW "
        "rules), and remove debris weekly.\n"
        "5.4 No site huts or storage beyond the zones allotted by the Engineer; the "
        "Contractor is liable for theft of its materials and plant, save where caused by "
        "the Employer's breach.\n\n"
        "6. LABOUR AND MANAGEMENT\n\n"
        "6.1 The Contractor shall employ a full-time project manager with 10+ years' "
        "experience on similar G+12+ projects, a qualified structural engineer, a safety "
        "officer per 500 workers, and quantity surveyor support, whose names and CVs are "
        "stated in Schedule E; replacements require the Engineer's prior approval.\n"
        "6.2 The Contractor shall pay wages not below statutory rates, maintain muster "
        "rolls, and display wage information; the Employer may (after 7 days' notice) pay "
        "workers directly and deduct equivalents where wages are unpaid.\n"
        "6.3 No child labour; no subcontracting to blacklisted entities; the Contractor "
        "shall obtain the Engineer's consent before subcontracting any material portion, "
        "and remains fully responsible for subcontractors."
    )

    parts.append(
        "\f7. MATERIALS, PLANT AND TESTING\n\n"
        "7.1 Approval: samples and manufacturer data for all listed materials are submitted "
        "for the Engineer's approval before procurement; approved samples govern quality.\n"
        "7.2 Cement and steel: procurement is from manufacturers on the approved list; each "
        "consignment carries test certificates; site cube tests and steel tensile tests are "
        "conducted per IS at NABL-accredited laboratories at the Contractor's cost, at the "
        "frequencies in Schedule C.\n"
        "7.3 Concrete: design mixes are approved before use; site-batched concrete is "
        "replaced by ready-mix where specified; cube strengths below specification require "
        "the Engineer's structural assessment, and non-compliant work is demolished and "
        "rebuilt at the Contractor's cost.\n"
        "7.4 Employer-supplied items are inspected on delivery jointly; risk passes to the "
        "Contractor on receipt; the Contractor is responsible for storage and protection.\n"
        "7.5 Plant brought to Site is deemed intended for the Works and removal requires the "
        "Engineer's consent until Completion.\n\n"
        "8. QUALITY, INSPECTION AND SAFETY\n\n"
        "8.1 The Engineer may inspect any part of the Works at any time; the Contractor "
        "shall give notice before covering work (foundations, reinforcement, waterproofing "
        "layers, concealed services) and shall not cover without certification; uncovers and "
        "re-executes work covered without notice at its own cost.\n"
        "8.2 Third-party quality audits: the Employer may appoint an independent quality "
        "auditor; the Contractor shall cooperate and remedy findings within directed times.\n"
        "8.3 Safety: the Contractor shall implement a written safety plan, provide PPE, "
        "conduct weekly toolbox talks, maintain accident registers, report notifiable "
        "accidents within 24 hours, and comply with BOCW Act, 1996 and its rules. The "
        "Contractor is solely liable for its personnel's safety; stop-work on safety "
        "grounds by the Engineer is not a delay event save where the direction was "
        "unreasonable.\n"
        "8.4 Environmental: C&D waste is handled under the C&D Waste Rules, 2016; no "
        "burning of waste on Site; water for curing is sourced per CGWA permissions."
    )

    parts.append(
        "\f9. PROGRESS, SUSPENSION AND EXTENSION OF TIME\n\n"
        "9.1 The Contractor shall achieve progress so that no milestone in Schedule D slips; "
        "where progress falls behind, the Contractor shall at its cost increase resources or "
        "work extra shifts to recover.\n"
        "9.2 The Engineer may instruct suspension for safety, quality or coordination; the "
        "Contractor shall comply, protect the suspended work and resume on instruction. "
        "Suspension not caused by the Contractor entitles the Contractor to EOT and costs of "
        "the unavoidable standstill actually incurred, subject to Clause 14.\n"
        "9.3 Extension of Time (EOT): the Time for Completion and affected milestones are "
        "extended to the extent the Contractor is delayed by: a Variation (net of its own "
        "delays); the Employer's failure to give possession, drawings or Employer-supplied "
        "items on time; a Force Majeure Event; a statutory prohibition; or any other event "
        "for which the Contract states the Contractor is entitled to EOT.\n"
        "9.4 Claims procedure: the Contractor shall issue a Notice of Intention to Claim EOT "
        "within 10 days of becoming aware of the event, with a detailed claim (events, "
        "analysis, entitlement) within 30 days, or entitlement is reduced to the extent the "
        "Engineer is prejudiced and extinguished if no notice is given at all.\n"
        "9.5 The Engineer assesses EOT within 21 days of a complete claim with reasons; "
        "EOT is the only remedy for delay save as expressly provided.\n\n"
        "10. VARIATIONS\n\n"
        "10.1 The Engineer may instruct a Variation (addition, omission, substitution, or "
        "change of quality/form) at any time before GCC; the Contractor shall not vary the "
        "Works without instruction or written agreement.\n"
        "10.2 Valuation: Variations are valued at Bill rates for like items; pro-rata for "
        "items with a cost basis; where no rate exists, at daywork rates in Schedule B or a "
        "new rate agreed on a cost-plus 10 percent basis with the Engineer's determination "
        "in default.\n"
        "10.3 If the aggregate net value of Variations exceeds +/- 10 percent of the "
        "Contract Price, the Parties shall negotiate adjustment of preliminary and general "
        "costs; failure to agree follows Clause 22.\n"
        "10.4 No Variation shall vitiate the Contract; the Contractor shall continue "
        "executing instructed Variations pending valuation."
    )

    parts.append(
        "\f11. CONTRACT PRICE AND BASIS\n\n"
        "11.1 The Contract Price is a lump-sum with measured variations, based on the Bill "
        "of Quantities (Schedule B). Quantities in the Bill are estimates for tendering; "
        "payment is made on actual measured quantities at Bill rates, subject to Clause "
        "11.2.\n"
        "11.2 Measurement: measurements follow IS 1200; joint monthly measurement is "
        "recorded and signed; the Engineer's measurements are conclusive absent manifest "
        "error.\n"
        "11.3 Items with quantities noted \u201clump sum\u201d are not remeasured save for Variations.\n"
        "11.4 The Price is deemed to include all costs of execution, supervision, insurances "
        "required of the Contractor, taxes other than GST on the value of work, and "
        "compliance with statutory obligations; GST on the value of taxable supplies is "
        "payable additionally against valid tax invoices.\n\n"
        "12. PERFORMANCE SECURITY AND ADVANCE PAYMENTS\n\n"
        "12.1 The Contractor shall furnish a Performance Security of 5 percent of the "
        "Contract Price by unconditional and irrevocable bank guarantee from a scheduled "
        "bank, valid until 60 days after the Defects Liability Period, within 14 days of "
        "signing, failing which the Employer may terminate and recover tender costs.\n"
        "12.2 Mobilisation advance: the Employer shall pay an advance of 10 percent of the "
        "Contract Price against an equivalent bank guarantee, recovered pro-rata from RA "
        "bills from the 4th bill onward.\n"
        "12.3 Secured advance may be paid on materials brought to Site for incorporation, "
        "at 75 percent of their Bill value, against hypothecation and insurance, recovered "
        "as the materials are incorporated.\n"
        "12.4 The Performance Security is returned within 28 days of the end of the "
        "Defects Liability Period less amounts applied to unremedied defects."
    )

    parts.append(
        "\f13. PAYMENT TERMS\n\n"
        "13.1 RA Bills: the Contractor submits monthly RA Bills within 7 days of each "
        "measurement date, with the Engineer certifying within 14 days and the Employer "
        "paying the certified amount within 14 days of certification.\n"
        "13.2 Deductions from each RA Bill: (a) Retention of 5 percent, capped at 5 percent "
        "of the Contract Price; (b) advance recovery per Clause 12.2; (c) secured advance "
        "recovery; (d) income-tax deduction at source at statutory rates; (e) GST as "
        "applicable under the reverse-charge mechanism for any specified services; and (f) "
        "any amounts the Employer is entitled to recover under this Contract.\n"
        "13.3 Final Bill: submitted within 90 days of GCC with all documentation; the "
        "Engineer certifies within 60 days; payment within 28 days of certification less "
        "retention.\n"
        "13.4 Retention release: 50 percent of Retention on GCC; the balance 50 percent on "
        "the end of the Defects Liability Period, against a defects-liability guarantee, "
        "less the cost of defects not remedied.\n"
        "13.5 Late payment by the Employer accrues interest at 10 percent per annum on the "
        "certified-but-unpaid amount for the period of default; interest is the sole remedy "
        "for late payment.\n"
        "13.6 Price escalation: for works delayed beyond the Time for Completion for "
        "reasons not the Contractor's fault, escalation on cement, steel and labour is "
        "computed per the formulae in Schedule F using published indices; no escalation "
        "applies within the original Time for Completion (the Price includes escalation "
        "provision for that period)."
    )

    parts.append(
        "\f14. DELAY EVENTS, EOT RECORDS\n\n"
        "14.1 The Contractor shall maintain contemporaneous records (daily progress reports, "
        "photographs, resource logs) sufficient to substantiate any EOT or cost claim, and "
        "allow the Engineer access.\n"
        "14.2 Where an event entitles the Contractor to EOT and cost, entitlement to cost "
        "is limited to unavoidable standstill costs of labour and plant specifically "
        "mobilised for the affected activity, supported by records; overhead and profit "
        "additions apply only to Variation-related cost claims at 10 percent.\n"
        "14.3 Concurrent delay: where delay events overlap, EOT is granted for the period "
        "of Employer-risk delay only to the extent it is not concurrent with "
        "Contractor-risk delay; no cost follows for concurrent periods.\n"
        "14.4 Disruption vs. delay: disruption claims (loss of productivity) require "
        "expert analysis demonstrating causation to the Engineer's satisfaction.\n\n"
        "15. DELAY DAMAGES AND INCENTIVE\n\n"
        "15.1 If the Contractor fails to complete by the Time for Completion (as extended), "
        "the Contractor shall pay Delay Damages of Rs. 3,50,000/- per calendar day of delay, "
        "capped at 10 percent of the Contract Price.\n"
        "15.2 Delay Damages are the Employer's exclusive remedy for delay save for "
        "termination under Clause 19; the Employer may deduct Delay Damages from any "
        "amounts due, from Retention, or call the Performance Security.\n"
        "15.3 Early-completion incentive: if Completion is achieved at least 60 days "
        "before the Time for Completion, the Employer shall pay an incentive of "
        "Rs. 2,00,00,000/-, which shall not be payable if quality audit scores average "
        "below 85 percent."
    )

    parts.append(
        "\f16. COMPLETION, TESTS AND HANDOVER\n\n"
        "16.1 When the Contractor considers the Works complete, it shall notify the "
        "Engineer; the Engineer inspects within 14 days with the Employer's representatives, "
        "and issues the GCC where Completion has been achieved, listing minor outstanding "
        "items with completion dates.\n"
        "16.2 Pre-completion tests per Schedule C are witnessed by the Engineer and "
        "statutory authorities; successful results are a condition of the GCC.\n"
        "16.3 On the GCC, the Contractor shall deliver as-built drawings (2 sets + soft "
        "copy), operation and maintenance manuals, warranties for installed equipment, "
        "statutory test certificates, and a completion report; the Employer shall not "
        "withhold the GCC merely for the delivery of documents, but payment of the final "
        "50 percent retention release is linked to their delivery.\n"
        "16.4 Taking over of parts: the Employer may take over identifiable parts early; "
        "the Defects Liability Period for those parts runs from taking over, and the "
        "Contractor's site presence continues for the balance Works.\n\n"
        "17. DEFECTS LIABILITY\n\n"
        "17.1 The Contractor shall, during the Defects Liability Period, remedy with due "
        "expedition and at its own cost any defect or damage arising from defective "
        "materials or workmanship, and any damage caused by remedial works.\n"
        "17.2 The Engineer notifies defects with reasonable detail; urgent defects are "
        "remedied within 7 days, others within 30 days or as directed. Failure to remedy "
        "entitles the Employer to employ others at the Contractor's risk and cost, and to "
        "recover the cost from Retention or the Performance Security.\n"
        "17.3 Where a defect is remedied, the Defects Liability Period for that part is "
        "extended by 180 days from remedy; the total period shall not exceed 730 days from "
        "GCC.\n"
        "17.4 Normal wear and tear, and defects arising from the Employer's or occupants' "
        "misuse, are not the Contractor's liability."
    )

    parts.append(
        "\f18. RISK, INSURANCE AND INDEMNITY\n\n"
        "18.1 Risk in the Works passes to the Employer on the GCC, save that the "
        "Contractor bears the risk of loss or damage to the Works, materials and plant "
        "until then, to the extent caused by its negligence or that of its "
        "subcontractors.\n"
        "18.2 Contractor's all-risk (CAR) insurance for full reinstatement value plus 10 "
        "percent, third-party liability of not less than Rs. 10 crore per occurrence, and "
        "workmen's compensation and ESIF as applicable, all with insurers of repute, from "
        "the Commencement Date until the end of the Defects Liability Period (CAR: until "
        "GCC plus 7 days). The Employer is a co-insured under CAR to the extent of its "
        "interest.\n"
        "18.3 The Contractor indemnifies the Employer against claims by third parties for "
        "bodily injury or property damage arising from execution of the Works, and "
        "against all penalties for statutory non-compliance attributable to the "
        "Contractor; the Employer indemnifies the Contractor against claims arising from "
        "the Employer's design documents, where the failure is not attributable to the "
        "Contractor's failure to review obvious errors.\n"
        "18.4 Neither Party is liable to the other for indirect or consequential loss, "
        "save for fraud and wilful default. The aggregate cap on the Contractor's "
        "liability (other than for fraud, wilful default, and its indemnities) is 100 "
        "percent of the Contract Price.\n\n"
        "19. FORCE MAJEURE\n\n"
        "19.1 Force Majeure includes acts of God, war, hostilities, terrorism, riots, "
        "epidemics and government-imposed prohibitions, floods and earthquakes of "
        "unusual severity, but does not include weather that is normal for the season, "
        "labour shortages generally, or the Contractor's financial condition.\n"
        "19.2 The affected Party shall notify the other within 7 days with particulars, "
        "mitigate, and keep records; EOT follows under Clause 9; attributable standstill "
        "costs of both Parties are borne by each Party respectively (no global cost "
        "claim), save that the Contractor is paid for materials and permanent plant "
        "damaged to the extent not covered by insurance.\n"
        "19.3 If Force Majeure continues for 120 days, either Party may terminate on 30 "
        "days' notice; the Employer pays the value of work done and materials on Site, "
        "and neither Party is liable to the other in respect of the termination."
    )

    parts.append(
        "\f20. EMPLOYER'S DEFAULT AND CONTRACTOR'S SUSPENSION\n\n"
        "20.1 If the Employer: fails to pay a certified amount within 28 days of the due "
        "date after notice; obstructs the Contractor's performance; or becomes insolvent, "
        "the Contractor may (after 14 days' notice and failure to remedy) suspend "
        "progress or reduce the rate of work, with entitlement to EOT and reasonable "
        "consequential standstill costs, and may terminate under Clause 19 procedure.\n\n"
        "21. TERMINATION\n\n"
        "21.1 Termination by the Employer for contractor default, on 14 days' notice and "
        "failure to remedy: abandonment of the Works; suspension of progress for 28 days "
        "without cause; substandard materials or workmanship persisting after notice; "
        "insolvency events; persistent breach entitling termination.\n"
        "21.2 On such termination: the Employer may complete the Works itself or through "
        "others, using the Contractor's plant and materials on Site to the extent "
        "necessary (with payment at fair value); the Contractor shall vacate and hand "
        "over documents; the value of work executed is ascertained and, after deducting "
        "extra completion costs, Delay Damages and other recoveries, any surplus is paid "
        "to the Contractor and any deficit is recoverable.\n"
        "21.3 Termination by the Contractor for Employer default follows Clause 20; on "
        "such termination the Contractor is entitled to payment for work executed, "
        "materials on Site, and unavoidable demobilisation costs, but not lost profits "
        "on unexecuted work.\n"
        "21.4 Neither Party may terminate for convenience; changes in project economics "
        "are not grounds for termination or price adjustment beyond the express "
        "provisions."
    )

    parts.append(
        "\f22. DISPUTE RESOLUTION AND LAW\n\n"
        "22.1 Disputes are first referred to the Engineer's adjudication: either Party "
        "may refer a dispute in writing; the Engineer decides within 30 days with "
        "reasons; the decision binds until revised.\n"
        "22.2 A Party dissatisfied with adjudication may, within 30 days, require "
        "arbitration of a sole arbitrator under the Arbitration and Conciliation Act, "
        "1996; seat: Noida; language: English. Where the aggregate amount in dispute "
        "exceeds Rs. 10 crore, a three-member tribunal applies.\n"
        "22.3 Work continues during disputes, and payments of undisputed amounts "
        "continue.\n"
        "22.4 This Contract is governed by Indian law; courts at Gautam Buddha Nagar "
        "alone have jurisdiction for interim relief under the arbitration agreement.\n\n"
        "23. GENERAL\n\n"
        "23.1 Notices in writing to the addresses on the first page, by hand, registered "
        "post or verified email, are deemed served on delivery or 3 days of posting.\n"
        "23.2 No waiver is effective unless in writing; no course of dealing varies this "
        "Contract.\n"
        "23.3 The Contractor shall not assign this Contract; the Employer may assign to "
        "a financier on notice for security purposes.\n"
        "23.4 The Contract Documents are complementary; the Contractor shall promptly "
        "notify the Engineer of any apparent error or discrepancy, which the Engineer "
        "shall resolve with reasons; the Contractor executes at its risk until so "
        "resolved where safety is affected.\n"
        "23.5 Anti-bribery: neither Party shall offer or accept any inducement to "
        "secure improper advantage; breach entitles the innocent Party to terminate.\n"
        "23.6 This Contract supersedes all prior negotiations; executed in two "
        "counterparts; each page is initialled by both Parties.\n\n"
        "SIGNED for the Employer: __________________ (D. Chauhan, Director) \n"
        "SIGNED for the Contractor: ________________ (S. Balaji, Managing Director)\n"
        "Witnesses: 1. ________________ 2. ________________   Date: 15 June 2026"
    )

    # SCHEDULE A - payment milestones
    lines = ["SCHEDULE A - MILESTONE PAYMENT STRUCTURE (information; RA billing governs)", ""]
    for row in [
        ("Milestone", "Weight (%)", "Target month"),
        ("Site possession and mobilisation", "3", "0"),
        ("Excavation, shoring and piling", "5", "3"),
        ("Raft foundation and basements cast", "8", "5"),
        ("Plinth beam completion", "4", "6"),
        ("Structure - 25% of slabs cast", "8", "10"),
        ("Structure - 50% of slabs cast", "8", "14"),
        ("Structure - 75% of slabs cast", "8", "18"),
        ("Structure top-out", "6", "22"),
        ("Masonry and internal plaster complete", "10", "26"),
        ("Waterproofing and external finishes complete", "8", "28"),
        ("MEP first and second fix complete", "10", "30"),
        ("Lifts, DG, fire systems commissioned", "6", "31"),
        ("Finishes, flooring and fixtures complete", "8", "33"),
        ("Testing, commissioning and snag closure", "5", "34"),
        ("GCC and handover with documents", "3", "35"),
    ]:
        if row[0] == "Milestone":
            lines.append(f"{row[0]:<48}{row[1]:>10}{row[2]:>14}")
            lines.append("-" * 72)
        else:
            lines.append(f"{row[0]:<48}{row[1]:>10}{row[2]:>14}")
    parts.append("\f" + "\n".join(lines))

    # SCHEDULE B - bill of quantities (multi-page)
    boq_lines = [
        "SCHEDULE B - BILL OF QUANTITIES (extract; full BOQ forms part of tender)",
        "",
        f"{'Item':<6}{'Description':<52}{'Unit':>7}{'Qty':>10}{'Rate Rs.':>12}{'Amount Rs.':>14}",
        "-" * 101,
    ]
    import random

    random.seed(42)
    # Section 1: earthwork and foundations
    boq_lines.append("SECTION 1 - EARTHWORK, SHORING AND FOUNDATIONS")
    items1 = [
        ("1.1 Excavation in ordinary soil incl. dewatering", "cum", 12400, 385),
        ("1.2 Excavation in hard soil / murrum", "cum", 4300, 610),
        ("1.3 Rock excavation (ripping)", "cum", 850, 1450),
        ("1.4 Shoring and sheet piling to basements", "sqm", 5600, 980),
        ("1.5 Disposal of surplus earth beyond 5 km", "cum", 9800, 265),
        ("1.6 Pile caps - PCC 1:2:4 levelling course", "cum", 210, 5200),
        ("1.7 Raft foundation M30 with admixture", "cum", 2350, 7850),
        ("1.8 Bored cast-in-situ piles M25, D=600mm", "rm", 1860, 4650),
        ("1.9 Pile reinforcement TMT Fe500D", "MT", 148, 68500),
        ("1.10 Anti-termite treatment pre and post", "sqm", 8900, 58),
        ("1.11 Backfilling with approved excavated soil", "cum", 7600, 295),
        ("1.12 Waterproof raft membrane 3mm APP", "sqm", 4200, 640),
        ("1.13 Basement box waterproofing - integral", "sqm", 12400, 410),
    ]
    for row in items1:
        desc, unit, qty, rate = row
        code, desc = desc.split(" ", 1)
        amt = qty * rate
        boq_lines.append(
            f"{code:<6}{desc:<52}{unit:>7}{num(qty,10):>10}{num(rate,12):>12}{num(amt,14):>14}"
        )
    boq_lines.append("")
    boq_lines.append("SECTION 2 - REINFORCED CONCRETE FRAME")
    items2 = [
        ("2.1 RC columns M40 up to 7th floor", "cum", 1180, 8450),
        ("2.2 RC columns M35 from 8th to 16th floor", "cum", 940, 8100),
        ("2.3 RC shear walls M40 incl. formwork", "cum", 2650, 8750),
        ("2.4 RC beams and slabs M30", "cum", 6350, 7600),
        ("2.5 Staircase and lift core walls M40", "cum", 720, 8900),
        ("2.6 High-frequency vibrators and screeds (incl.)", "ls", 1, 485000),
        ("2.7 Reinforcement TMT Fe500D", "MT", 2650, 66800),
        ("2.8 Formwork - aluminium shuttering system", "sqm", 48200, 780),
        ("2.9 Concrete pump hire incl. boom placer", "month", 30, 185000),
        ("2.10 Curing compound and wet curing", "sqm", 38400, 38),
        ("2.11 Terrazzo-finish stair treads nosings", "rm", 640, 950),
    ]
    for row in items2:
        desc, unit, qty, rate = row
        code, desc = desc.split(" ", 1)
        amt = qty * rate
        boq_lines.append(
            f"{code:<6}{desc:<52}{unit:>7}{num(qty,10):>10}{num(rate,12):>12}{num(amt,14):>14}"
        )
    parts.append("\f" + "\n".join(boq_lines))

    boq2_lines = [
        "SCHEDULE B - BILL OF QUANTITIES (continued)",
        "",
        f"{'Item':<6}{'Description':<52}{'Unit':>7}{'Qty':>10}{'Rate Rs.':>12}{'Amount Rs.':>14}",
        "-" * 101,
        "SECTION 3 - MASONRY, PLASTER AND FINISHES",
    ]
    items3 = [
        ("3.1 AAC block masonry 200mm in CM 1:4", "cum", 4850, 3950),
        ("3.2 AAC block masonry 100mm partitions", "cum", 1620, 4100),
        ("3.3 Internal plaster 12mm sand-faced", "sqm", 48200, 385),
        ("3.4 External plaster with waterproof compound", "sqm", 14600, 445),
        ("3.5 Internal acrylic emulsion (2 coats + primer)", "sqm", 46800, 210),
        ("3.6 External weatherproof elastomeric paint", "sqm", 14600, 320),
        ("3.7 Vitrified tile flooring 800x800 incl. laying", "sqm", 9800, 1250),
        ("3.8 Anti-skid ceramic tiles in toilets/balconies", "sqm", 3400, 1050),
        ("3.9 Granite kitchen platform with nosing", "rm", 1850, 3200),
        ("3.10 POP false ceiling in lobby and flats", "sqm", 6200, 760),
        ("3.11 Toilet CG + mirror + accessories set", "no", 192, 14500),
    ]
    for row in items3:
        desc, unit, qty, rate = row
        code, desc = desc.split(" ", 1)
        amt = qty * rate
        boq2_lines.append(
            f"{code:<6}{desc:<52}{unit:>7}{num(qty,10):>10}{num(rate,12):>12}{num(amt,14):>14}"
        )
    boq2_lines.append("")
    boq2_lines.append("SECTION 4 - WATERPROOFING, PLUMBING AND FIRE")
    items4 = [
        ("4.1 Terrace waterproofing PU 2mm with protection", "sqm", 2850, 720),
        ("4.2 Toilet waterproofing sunken slab", "sqm", 3800, 560),
        ("4.3 UPVC SWR piping 110mm incl. fittings", "rm", 4650, 640),
        ("4.4 CPVC hot and cold water lines 25-50mm", "rm", 8600, 420),
        ("4.5 CP fittings - concealed diverters (CP brand)", "no", 96, 8600),
        ("4.6 Sprinkler system as per NBC with hydraulics", "no", 192, 46500),
        ("4.7 Fire pumps, jockey pump, controls and panel", "ls", 1, 6850000),
        ("4.8 Fire detection and alarm - addressable", "ls", 1, 5420000),
        ("4.9 Underground and terrace water tanks", "cum", 380, 8900),
        ("4.10 STP 120 KLD with DG-set backup", "ls", 1, 8450000),
    ]
    for row in items4:
        desc, unit, qty, rate = row
        code, desc = desc.split(" ", 1)
        amt = qty * rate
        boq2_lines.append(
            f"{code:<6}{desc:<52}{unit:>7}{num(qty,10):>10}{num(rate,12):>12}{num(amt,14):>14}"
        )
    boq2_lines.append("")
    boq2_lines.append("SECTION 5 - ELECTRICAL AND EXTERNAL DEVELOPMENT")
    items5 = [
        ("5.1 Point wiring 1.5/2.5 sq.mm FRLS in conduit", "point", 9600, 1650),
        ("5.2 Distribution boards with MCB/RCCB", "no", 96, 8500),
        ("5.3 LT cabling, risers and panel termination", "ls", 1, 14250000),
        ("5.4 DG 500 kVA with AMF panel (install only)", "ls", 1, 2850000),
        ("5.5 Transformer installation (Employer supplied)", "ls", 1, 950000),
        ("5.6 CCTV, intercom and gate automation", "ls", 1, 4850000),
        ("5.7 External roads in PCC with paver blocks", "sqm", 3400, 1450),
        ("5.8 Storm-water drains and manholes", "rm", 1850, 2100),
        ("5.9 Compound wall, gates and guard room", "ls", 1, 2450000),
        ("5.10 Landscaping, horticulture and drip system", "sqm", 2800, 680),
        ("5.11 Clubhouse shell (structure + finishes)", "ls", 1, 12500000),
        ("5.12 Preliminary and general items (10%)", "ls", 1, 64500000),
    ]
    for row in items5:
        desc, unit, qty, rate = row
        code, desc = desc.split(" ", 1)
        amt = qty * rate
        boq2_lines.append(
            f"{code:<6}{desc:<52}{unit:>7}{num(qty,10):>10}{num(rate,12):>12}{num(amt,14):>14}"
        )
    boq2_lines.append("")
    boq2_lines.append(
        f"{'':<6}{'SUB-TOTAL (Sections 1-5, before GST)':<52}{'':>7}{'':>10}{'':>12}"
        f"{num(741235800,14):>14}"
    )
    boq2_lines.append(
        f"{'':<6}{'Contract Price (as per Clause 11.1, lump-sum basis)':<52}{'':>7}{'':>10}{'':>12}"
        f"{num(965000000,14):>14}"
    )
    boq2_lines.append(
        "\nNotes: (1) Rates are firm and inclusive of all taxes except GST on works "
        "contracts. (2) Quantities are estimated; payment on actual measurement per IS 1200. "
        "(3) Daywork schedule: skilled worker Rs. 1,450/day; mason Rs. 1,250/day; labour "
        "Rs. 850/day; structural engineer Rs. 4,500/day; tower crane (month) Rs. 6,85,000. "
        "(4) Leads and lifts for materials are deemed included. (5) The Employer reserves "
        "the right to omit items at Bill rates without prejudice."
    )
    parts.append("\f" + "\n".join(boq2_lines))

    # SCHEDULE C-F
    sched_lines = [
        "SCHEDULE C - EMPLOYER'S REQUIREMENTS AND SPECIFICATIONS (EXTRACT)",
        "",
        "C-1 Design documents to be issued by the Employer/Engineer: architectural GFC "
        "drawings (issued month 0); structural drawings (rolling, month 0-8); MEP "
        "consultant drawings (month 3-12); landscape (month 10). The Contractor shall "
        "notify clashes and constructability issues within 10 days of each issue.",
        "C-2 Concrete: M30/M35/M40 grades with admixtures; cover blocks of matching "
        "concrete; cube tests 1 set per 20 cum; core-cutting where cubes fail.",
        "C-3 Steel: Fe500D TMT from primary producers; lap lengths per IS 456; couplers "
        "for bars >= 32mm; weld tests for pre-fabricated cages.",
        "C-4 Formwork: aluminium form system for typical floors; deshuttering per IS 456 "
        "age/strain criteria; props left in place per Engineer's direction.",
        "C-5 Waterproofing: 3mm APP membrane for basements (external); PU 2mm terraces; "
        "crystalline coating for toilets; flood test 72 hours for terraces and toilets.",
        "C-6 Employer-supplied items: 6 passenger lifts + 1 service lift (brand per "
        "Schedule E); 2 DG sets 500 kVA; transformer 1.6 MVA; delivered to Site month "
        "20-22 with 30 days' notice.",
        "C-7 Testing frequency: cube test 1 per 20 cum or per slab pour; steel test 1 "
        "per 50 MT; brick/block 1 per 50,000 units; concrete NDT (rebound hammer/UPV) "
        "where cubes fail.",
        "C-8 Statutory quality audits: third-party structural auditor appointed by the "
        "Employer reviews all structural drawings and every 4th slab; contractor "
        "cooperation mandatory; audit findings closed within 15 days.",
        "",
        "SCHEDULE D - PROGRAMME AND MILESTONES",
        "The tender Programme is attached to the Contract at execution and governs "
        "Clause 4. The Contractor's detailed Programme (CPM, Primavera P6 or equivalent) "
        "shows: activities, logic, resource loading, milestones from Schedule A, and a "
        "4-week look-ahead updated monthly. Slippage beyond 15 days triggers a recovery "
        "plan with additional shifts/resources at the Contractor's cost.",
        "",
        "SCHEDULE E - KEY PERSONNEL AND EMPLOYER-SUPPLIED SCHEDULE",
        "Contractor project manager: Mr. Anil Rathore (18 yrs, executed 3 G+15 towers).",
        "Contractor structural engineer: Ms. Deepa Menon (M.Tech Structures, 12 yrs).",
        "Safety officer: Mr. Farhan Ali (ADIS certified). QS: Mr. Praveen Kumar (MRICS).",
        "Employer-supplied: lifts (month 20), DG sets (month 21), transformer (month 22).",
        "",
        "SCHEDULE F - ESCALATION FORMULAE (post-completion-date delays)",
        "Cement component 12 percent: index = All-India Wholesale Price Index for cement.",
        "Steel component 18 percent: index = WPI for bars and rods; base month = month "
        "preceding the due completion month; escalation = value of component x (current "
        "index - base index) / base index; labour component 25 percent uses the CPI for "
        "industrial workers (Uttar Pradesh); no escalation applies to the balance 45 "
        "percent. Claims quarterly with index certificates; audited by the Engineer.",
    ]
    parts.append("\f" + "\n".join(sched_lines))
    return "".join(parts)


# =====================================================================
# DOCUMENT 3 - Term loan facility agreement (~32 pages)
# =====================================================================
def build_facility() -> str:
    parts = []
    parts.append(
        "TERM LOAN FACILITY AGREEMENT\n\n"
        "Lender: GRANDWAY FINANCE AND LEASING LIMITED\n"
        "Borrower: ROSHAN FOODS PROCESSING PRIVATE LIMITED\n"
        "Facility No: GFL/TL/2027/0417\n\n"
        "This Term Loan Facility Agreement (the \u201cAgreement\u201d) is made on 12 January 2027 "
        "between Grandway Finance and Leasing Limited, a non-banking finance company with "
        "its registered office at 18B Trade Crest, Bandra Kurla Complex, Mumbai 400051 (the "
        "\u201cLender\u201d), and Roshan Foods Processing Private Limited, a company with its "
        "registered office at Plot 32, Food Park, Kazipet, Telangana 506003 (the "
        "\u201cBorrower\u201d).\n\n"
        "WHEREAS the Borrower operates a fruit-pulp and ready-to-cook food processing "
        "facility and requires long-tenor finance to expand capacity by a second processing "
        "line, a cold store of 4,000 MT and associated utilities (the \u201cProject\u201d); AND "
        "WHEREAS the Lender has agreed, on the terms of this Agreement, to make available a "
        "term loan facility to finance part of the Project cost.\n\n"
        "NOW THIS AGREEMENT WITNESSES as follows:"
    )

    defs = [
        ("Agreement", "this term loan facility agreement, including the Schedules and Annexes"),
        ("Authorised Signatories", "the individuals notified by the Borrower in Schedule E as authorised to operate the Facility Account and sign Utilisation Requests"),
        ("Base Rate", "the Lender's internal reference rate notified from time to time"),
        ("Borrower Default Rate", "the Facility Interest Rate plus 2.5 percent per annum"),
        ("Business Day", "a day on which scheduled banks are open for general business in Mumbai and Hyderabad"),
        ("Conditions Precedent", "the conditions in Clause 5 and Annex B"),
        ("Covenant Period", "the period from the Utilisation Date until the date all Outstanding is repaid"),
        ("Default Interest", "interest at the Borrower Default Rate on overdue amounts"),
        ("Event of Default", "each event listed in Clause 15"),
        ("Facility", "the term loan facility described in Clause 3, up to the Facility Amount"),
        ("Facility Amount", "Rs. 42,50,00,000/- (Rupees forty-two crore fifty lakh only)"),
        ("Facility Account", "the loan account opened by the Lender for the Facility"),
        ("Facility Interest Rate", "7.85 percent per annum over the Base Rate, subject to reset under Clause 8.3"),
        ("Final Repayment Date", "the date falling 84 months after the first Utilisation Date"),
        ("Financial Statements", "the audited consolidated financial statements of the Borrower for each Financial Year"),
        ("First Utilisation Date", "the date of the first valid Utilisation Request"),
        ("Interest Payment Date", "each date on which interest is payable under Clause 8.2"),
        ("Lender's Costs", "all costs, charges and expenses payable under Clause 9"),
        ("Material Adverse Effect", "a material adverse effect on the Borrower's ability to perform its payment obligations under this Agreement"),
        ("Outstanding", "the aggregate principal, interest and all other amounts outstanding and unpaid under this Agreement"),
        ("Prepayment", "any repayment under Clause 10"),
        ("Project", "has the meaning in the recitals"),
        ("Project Cost", "Rs. 58,00,00,000/- as appraised by the Lender's technical consultant"),
        ("Repayment Schedule", "the amortisation table in Schedule A"),
        ("Security", "the security created under Clause 12 and described in Annex C"),
        ("TDS", "tax deductible at source under the Income-tax Act, 1961"),
        ("Term", "the period from the date of this Agreement until the Final Repayment Date"),
        ("Utilisation Date", "each date on which the Lender makes an advance under the Facility"),
        ("Utilisation Request", "a request in the form of Schedule D"),
        ("DSCR", "the ratio of cash accruals plus interest and scheduled principal for the period, as defined in Annex C"),
        ("Total Outside Liabilities", "as defined in Annex C"),
        ("Tangible Net Worth", "as defined in Annex C"),
        ("Grace Period", "the principal moratorium of 18 months from the First Utilisation Date"),
        ("Moratorium", "the Grace Period during which only interest is payable"),
    ]
    parts.append(
        "\f1. DEFINITIONS AND INTERPRETATION\n\n1.1 In this Agreement:\n"
        + "".join(
            f'\u201c{t}\u201d means {m.rstrip(".")}.\n'
            for t, m in defs
        )
        + "\n1.2 Interpretation: (a) clause and Schedule headings are for convenience; (b) "
        "\u201cincluding\u201d is without limitation; (c) references to law include amendments and "
        "re-enactments; (d) where amounts are in rupees they are Indian rupees; (e) the "
        "Schedules and Annexes form part of this Agreement; (f) in case of conflict, this "
        "body prevails over Schedules, which prevail over Annexes, save that the Security "
        "documents prevail for enforcement matters."
    )

    parts.append(
        "\f2. AMOUNT AND PURPOSE OF THE FACILITY\n\n"
        "2.1 Subject to the Conditions Precedent, the Lender makes available to the "
        "Borrower a term loan facility of the Facility Amount to finance up to 73 percent "
        "of the Project Cost; the balance is funded by the Borrower from internal accruals "
        "and promoter equity of not less than Rs. 15,50,00,000/-, evidenced before the "
        "first Utilisation Date.\n"
        "2.2 The Borrower shall apply all amounts drawn solely towards the Project, "
        "against invoices and architect/civil-engineer certificates, in not more than "
        "eight (8) tranches during the availability period ending 12 months after the "
        "First Utilisation Date.\n"
        "2.3 The Borrower shall not use the Facility for: working-capital purposes; "
        "investment in any other company; repayment of any other borrowing; or any "
        "purpose prohibited by law. Diversion or siphoning of funds is an Event of "
        "Default.\n"
        "2.4 The Lender may, at its option and at the Borrower's cost, appoint a "
        "technical consultant and a chartered accountant to certify progress and "
        "end-use before each disbursement.\n\n"
        "3. UTILISATION\n\n"
        "3.1 Each Utilisation Request shall be delivered at least 5 Business Days before "
        "the proposed Utilisation Date, stating the amount, the Project invoices or "
        "certificates against which it is drawn, and confirming that the statements in "
        "Clause 3.2 are true.\n"
        "3.2 Each Utilisation Request is a representation that: the Conditions Precedent "
        "remain satisfied; no Event of Default is continuing; the Project remains "
        "materially on schedule; and the information supplied is true and complete.\n"
        "3.3 Undrawn amounts cease to be available after the availability period, and "
        "the Facility Amount reduces by each amount drawn.\n"
        "3.4 Amounts repaid or prepaid may not be re-borrowed."
    )

    parts.append(
        "\f4. CONDITIONS PRECEDENT\n\n"
        "4.1 The Lender's obligation to make the first advance is subject to delivery, in "
        "form and substance satisfactory to it, of the documents in Annex B, including: "
        "board and shareholder approvals; corporate authorisations; executed Security "
        "documents; searches confirming the Security is unencumbered; Project approvals "
        "(environmental consent to establish, fire NOC plan approval, FSSAI licence); "
        "chartered accountant's certificate of promoter contribution brought in; insurance "
        "policies per Clause 13; legal opinion; and the Lender's Costs paid.\n"
        "4.2 Each subsequent advance is subject to: continued satisfaction of the "
        "Conditions Precedent; the consultant's progress certificate; and confirmation "
        "that no Default continues.\n\n"
        "5. REPRESENTATIONS\n\n"
        "5.1 The Borrower represents on each Utilisation Date that: it is validly "
        "existing and in good standing; it has power and has obtained all authorisations "
        "to execute, deliver and perform this Agreement and the Security; this Agreement "
        "and the Security are its legal, valid and binding obligations; the Financial "
        "Statements delivered are true and fairly stated; there is no litigation or "
        "arbitration that could have a Material Adverse Effect; and all information "
        "supplied to the Lender is true and complete in all material respects."
    )

    parts.append(
        "\f6. GRACE PERIOD AND REPAYMENT\n\n"
        "6.1 Principal is repayable in 66 successive monthly instalments after the "
        "Grace Period of 18 months from the First Utilisation Date, in the amounts set "
        "out in the Repayment Schedule (Schedule A), commencing on the 19th month, and "
        "the entire Outstanding on the Final Repayment Date.\n"
        "6.2 If any instalment is not paid when due, the Lender may, without prejudice "
        "to its other rights, levy Default Interest under Clause 8.5 and treat the "
        "default under Clause 15.\n"
        "6.3 Payments are applied in the order: (i) costs and expenses of enforcement; "
        "(ii) Default Interest; (iii) ordinary interest; (iv) principal; unless the "
        "Lender directs otherwise at the time of receipt where law permits.\n"
        "6.4 All payments shall be made to the Facility Account in cleared funds by "
        "11 a.m. on the due date, without set-off or counterclaim; where a due date "
        "falls on a non-Business Day, payment is due the next Business Day with "
        "interest for the intervening days.\n\n"
        "7. TAXES AND WITHHOLDING\n\n"
        "7.1 All payments are free of deductions, save TDS which the Borrower shall "
        "deduct, pay to the authority within statutory time and provide certificates "
        "within 15 days of deduction. GST (if applicable to any fee) is payable in "
        "addition.\n"
        "7.2 If the law requires a gross-up, the sums payable are increased so the "
        "Lender receives the amounts it would have received absent the deduction, to "
        "the extent permitted by law."
    )

    parts.append(
        "\f8. INTEREST, RESET AND DEFAULT INTEREST\n\n"
        "8.1 Interest accrues on the Outstanding from the date of each advance at the "
        "Facility Interest Rate, computed on actual days and a 365-day year (366 in a "
        "leap year), from and including the Utilisation Date to but excluding the date "
        "of payment.\n"
        "8.2 Interest is payable monthly on the 7th day of each month for the "
        "preceding month (each an \u201cInterest Payment Date\u201d), and on any payment of "
        "principal on the amount so paid.\n"
        "8.3 The Facility Interest Rate resets quarterly to the Base Rate prevailing "
        "plus the spread of 7.85 percent; the Lender notifies each reset within 3 "
        "Business Days with the computation sheet.\n"
        "8.4 The spread of 7.85 percent is fixed for the Term; the Borrower may request "
        "a step-down of 25 basis points on prepayment that reduces the Outstanding "
        "below Rs. 21 crore, effective the following month.\n"
        "8.5 Default Interest at the Borrower Default Rate accrues on any amount not "
        "paid when due, from the due date until actual payment (both before and after "
        "any award), and compounds monthly; Default Interest does not extend to "
        "amounts disputed in good faith under Clause 20 while the dispute is pending.\n"
        "8.6 Interest for the Moratorium is paid monthly out of the Borrower's own "
        "funds; capitalisation of interest (funding of interest) is not permitted "
        "under this Facility."
    )

    parts.append(
        "\f9. FEES AND EXPENSES\n\n"
        "9.1 Processing fee: 0.85 percent of the Facility Amount, non-refundable, paid "
        "on signing.\n"
        "9.2 Commitment charge: 0.40 percent per annum on the undrawn Facility Amount, "
        "payable monthly during the availability period.\n"
        "9.3 Documentation and security-creation charges (stamp duty, registration, "
        "CERSAI filing, valuations, searches, technical and legal consultant fees) are "
        "to the Borrower's account, with an initial deposit of Rs. 25,00,000/- and "
        "reconciliation monthly.\n"
        "9.4 Late payment charges for cheque/ECS returns: Rs. 750 per instance plus "
        "applicable taxes.\n\n"
        "10. PREPAYMENT AND REDUCTION\n\n"
        "10.1 Voluntary prepayment of any amount may be made on 15 days' notice, in "
        "multiples of Rs. 5,00,000/-, together with: nil prepayment premium after 24 "
        "EMIs are paid; and 2 percent of the prepaid amount before that.\n"
        "10.2 Mandatory prepayment: the Borrower shall prepay, within 30 days of "
        "receipt: (a) 50 percent of net proceeds of any disposal of fixed assets "
        "relating to the Project other than replacement in the ordinary course; (b) "
        "the net proceeds of any insurance claim relating to the Project assets (applied "
        "to reinstatement first, with the Lender's consent); and (c) any amount "
        "required to cure a financial-covenant breach that remains uncured at the end "
        "of the applicable cure period.\n"
        "10.3 Prepaid amounts reduce the Repayment Schedule in direct order unless "
        "the Borrower elects, with the Lender's consent, to reduce the tenor instead."
    )

    parts.append(
        "\f11. AFFIRMATIVE AND NEGATIVE COVENANTS\n\n"
        "11.1 The Borrower shall, during the Covenant Period:\n"
        "(a) maintain the Project in good working order and keep assets insured per "
        "Clause 13;\n"
        "(b) furnish to the Lender: monthly operating and financial information within "
        "30 days of month end; quarterly provisional results within 45 days; audited "
        "Financial Statements within 180 days of Financial Year end; stock and "
        "book-debt statements quarterly; and project-progress reports monthly during "
        "implementation;\n"
        "(c) notify the Lender within 7 days of: any litigation, arbitration or "
        "regulatory action with a claim value above Rs. 2 crore; any Event of Default; "
        "any change in promoters, key managerial personnel or shareholding above 10 "
        "percent; and any new borrowing above Rs. 1 crore;\n"
        "(d) pay all taxes and statutory dues before they become overdue;\n"
        "(e) permit the Lender and its nominees to inspect the Project, assets, books "
        "and records at any reasonable time on 3 Business Days' notice;\n"
        "(f) maintain its existence, and comply with all Applicable Law material to "
        "its business.\n"
        "11.2 The Borrower shall not, without the Lender's prior written consent:\n"
        "(a) create or permit any encumbrance over its assets, save the Security and "
        "statutory liens arising in ordinary course not exceeding Rs. 50 lakh in "
        "aggregate;\n"
        "(b) undertake any merger, demerger, reconstruction or change of business;\n"
        "(c) lend, invest or guarantee any amount above Rs. 25 lakh outside the "
        "Project;\n"
        "(d) declare dividends while any Event of Default continues or where the "
        "financial covenants are breached (cured within the period permitted);\n"
        "(e) alter its accounting year or accounting policies materially;\n"
        "(f) sell, transfer or otherwise dispose of Project assets, save worn-out "
        "assets replaced in ordinary course."
    )

    parts.append(
        "\f12. FINANCIAL COVENANTS\n\n"
        "12.1 The Borrower shall maintain, tested annually on audited Financial "
        "Statements:\n"
        "  (a) Total Outside Liabilities to Tangible Net Worth <= 3.00:1.00 at all "
        "times during the Covenant Period;\n"
        "  (b) Debt-Service Coverage Ratio (DSCR) >= 1.35:1.00 on an annual basis "
        "from Financial Year ending March 2028;\n"
        "  (c) Minimum Tangible Net Worth of Rs. 22,00,00,000/- at all times, "
        "increasing by not less than 25 percent of each year's profits after tax;\n"
        "  (d) Current Ratio >= 1.10:1.00 from FY 2027-28.\n"
        "12.2 A breach of Clause 12.1(b) or 12.1(c) is not an Event of Default for "
        "one testing date per financial year, provided: the breach does not exceed "
        "10 percent of the required ratio; and the Borrower cures within two "
        "consecutive quarters or prepays under Clause 10.2(c). No such cure applies "
        "to Clause 12.1(a) or 12.1(d) more than once in the Term.\n"
        "12.3 Compliance certificates signed by the chief financial officer and a "
        "chartered accountant accompany each set of Financial Statements.\n\n"
        "13. INSURANCE\n\n"
        "13.1 The Borrower shall insure all Project and charged assets for their full "
        "reinstatement value against fire, earthquake, flood and allied perils, "
        "machinery breakdown and business interruption (12 months' gross profit), "
        "with insurers of repute, naming the Lender as mortgagee/loss payee, from "
        "before the first Utilisation Date throughout the Covenant Period.\n"
        "13.2 Premiums are paid before due dates, with renewals evidenced 15 days "
        "before expiry; the Lender may insure and recover premium where cover lapses. "
        "Insurance proceeds are applied per Clause 10.2(b)."
    )

    parts.append(
        "\f14. SECURITY\n\n"
        "14.1 As continuing security for the Outstanding, the Borrower creates in "
        "favour of the Lender:\n"
        "  (a) a first charge by way of hypothecation over all moveable fixed assets "
        "of the Project (plant, machinery, equipment, spares);\n"
        "  (b) an equitable mortgage of the Project land and buildings at Kazipet "
        "measuring 4.8 acres (Survey Nos. 112/2, 113), valued at Rs. 61,00,00,000/- "
        "by the Lender's empanelled valuer;\n"
        "  (c) a charge over receivables of Rs. 8 crore book value and over the "
        "Facility Account;\n"
        "  (d) personal guarantees of Mr. Roshanlal Agarwal and Mrs. Sudha Agarwal, "
        "and a corporate guarantee of Agarwal Retail Ventures Private Limited, each "
        "in the Lender's form.\n"
        "14.2 The Security is created, perfected and registered (including CERSAI "
        "filing) as described in Annex C; further or substitute security of equal "
        "rank is provided for any asset released, and the Lender's consent is "
        "required for any release.\n"
        "14.3 The guarantees are continuing and independent obligations; the "
        "Lender may enforce without first proceeding against the Borrower, to the "
        "extent permitted by law.\n\n"
        "15. EVENTS OF DEFAULT\n\n"
        "15.1 Each of the following is an Event of Default:\n"
        "  (a) non-payment: any amount due is unpaid by the 7th day after written "
        "notice; interest is unpaid for 30 days; the Repayment Schedule default "
        "thresholds in 15.1(b) apply where three or more instalments are in "
        "arrear;\n"
        "  (b) misrepresentation: any representation or information is or becomes "
        "materially incorrect;\n"
        "  (c) covenant breach: any covenant in Clauses 11 or 12 is breached (as "
        "subject to the cure provisions);\n"
        "  (d) cross-default: any other borrowing of the Borrower above Rs. 2 "
        "crore is accelerated, or any payment default on it continues beyond any "
        "applicable grace;\n"
        "  (e) insolvency: the Borrower or a guarantor becomes insolvent, or "
        "proceedings are commenced (including under the Insolvency and Bankruptcy "
        "Code, 2016) and are not dismissed within 60 days;\n"
        "  (f) enforcement: any Security becomes enforceable, or any attachment "
        "or distress is made on charged assets and is not discharged within 30 "
        "days;\n"
        "  (g) cessation of business: the Borrower suspends or threatens to "
        "suspend its business, or disposal of a substantial part of its assets "
        "other than in ordinary course;\n"
        "  (h) unlawfulness: it is unlawful for the Lender to perform any of its "
        "obligations, or any authorisation required is revoked;\n"
        "  (i) Material Adverse Effect: any event occurs that has, or could "
        "reasonably be expected to have, a Material Adverse Effect;\n"
        "  (j) diversion: misuse of the Facility contrary to Clause 2.3.\n"
        "15.2 On an Event of Default the Lender may, by notice: cancel the "
        "undrawn Facility; declare the Outstanding immediately due and payable "
        "(whereupon it becomes immediately due); enforce the Security; appoint "
        "a receiver or administrator over charged assets; and exercise any other "
        "right at law or under this Agreement."
    )

    parts.append(
        "\f16. CONDUCT OF THE ACCOUNT\n\n"
        "16.1 The Borrower shall route a minimum of 60 percent of its gross "
        "receipts through the collection account maintained with the Lender "
        "(escrow of receivables per Annex C), and shall not create any charge "
        "over that account.\n"
        "16.2 Cash flows retained in excess of debt service shall first be "
        "applied to Project completion shortfalls, if any.\n\n"
        "17. COMPUTATIONS AND CERTIFICATES\n\n"
        "17.1 Accounting terms follow Indian Accounting Standards as applicable; "
        "financial covenants are computed on a consolidated basis where the "
        "Borrower has subsidiaries, in each case adjusted for one-off items "
        "disclosed to and agreed by the Lender.\n"
        "17.2 Where the Lender and the Borrower disagree on a computation, the "
        "certificate of a jointly appointed chartered accountant (cost shared "
        "equally) governs, absent manifest error.\n\n"
        "18. ASSIGNMENTS AND PART-INVESTMENTS\n\n"
        "18.1 The Lender may assign or transfer all or part of the Facility and "
        "the Security to any bank, financial institution or fund on written "
        "notice to the Borrower; the Borrower's consents under this Clause are "
        "deemed given where the transferee assumes the Lender's obligations.\n"
        "18.2 The Borrower shall not assign any of its rights or obligations.\n"
        "18.3 The Lender may, with the Borrower's consent (not to be "
        "unreasonably withheld), invite banks to part-finance the Facility on "
        "identical terms, and may appoint an agent bank for documentation."
    )

    parts.append(
        "\f19. NOTICES\n\n"
        "19.1 Notices are in writing in English, delivered by hand against "
        "acknowledgment, by registered post, or by email with delivery "
        "confirmation, to the addresses in Schedule E, and are effective on "
        "delivery (or 3 Business Days after posting; on the Business Day the "
        "email is confirmed where within business hours).\n"
        "19.2 A Party may change its notice address by 10 Business Days' "
        "notice.\n\n"
        "20. SET-OFF, DISPUTES AND WAIVER\n\n"
        "20.1 The Lender may, to the extent permitted by law and after giving "
        "notice, set off amounts standing to the Borrower's credit in any "
        "account with the Lender against the Outstanding, save amounts "
        "disputed in good faith with reasonable grounds.\n"
        "20.2 Disputes are first referred to senior representatives of both "
        "Parties for amicable resolution within 21 days; failing resolution, "
        "disputes are referred to a sole arbitrator under the Arbitration and "
        "Conciliation Act, 1996; seat: Mumbai; language: English; subject to "
        "which, courts at Mumbai alone have exclusive jurisdiction, and this "
        "Agreement is governed by Indian law.\n"
        "20.3 No failure or delay in exercising any right is a waiver; "
        "waivers must be written. The Lender's acquiescence in any breach is "
        "not a course-of-dealing varying this Agreement.\n\n"
        "21. GENERAL\n\n"
        "21.1 Amendments require written signature by both Parties save for "
        "ministerial corrections and the interest reset under Clause 8.3.\n"
        "21.2 If any provision is held invalid, the remainder continues; the "
        "Parties shall substitute a valid provision closest to the intent.\n"
        "21.3 This Agreement (with Schedules and Annexes) is the entire "
        "agreement on its subject matter and supersedes prior term sheets and "
        "indicative letters, save that the sanctions and anti-bribery "
        "undertakings in the executed term sheet survive.\n"
        "21.4 The Borrower undertakes compliance with anti-bribery and "
        "applicable sanctions law and shall not use the Facility for any "
        "prohibited purpose.\n"
        "21.5 Costs: each Party bears its own costs except the Lender's Costs "
        "which are for the Borrower per Clause 9.3.\n"
        "21.6 This Agreement is executed in two counterparts, both together "
        "constituting one instrument.\n\n"
        "IN WITNESS WHEREOF the Parties have executed this Agreement on the "
        "date first written above.\n\n"
        "For GRANDWAY FINANCE AND LEASING LIMITED    For ROSHAN FOODS PROCESSING "
        "PRIVATE LIMITED\n"
        "Signed: ____________________                Signed: ____________________\n"
        "Name: Vikram Sethi                          Name: Roshanlal Agarwal\n"
        "Title: President - Corporate Credit         Title: Managing Director\n\n"
        "Witnesses: 1. ______________  2. ______________"
    )

    # Additional articles
    parts.append(
        "\f5A. ADDITIONAL REPRESENTATIONS\n\n"
        "5A.1 Solvency and pari passu: the Borrower is solvent and is paying (or has "
        "compiled with arrangements for paying) its debts as they fall due; its assets "
        "are not subject to any order of attachment or execution save as disclosed; and "
        "its obligations under this Agreement rank at least pari passu with all its "
        "present and future unsecured and secured obligations, save those mandatorily "
        "preferred by law.\n"
        "5A.2 No proceedings: no litigation, arbitration, administrative proceeding or "
        "investigation is pending or, to the Borrower's knowledge, threatened against it "
        "or any of its charged assets which could have a Material Adverse Effect.\n"
        "5A.3 No default: no Event of Default, and no event which with notice or lapse "
        "of time would constitute an Event of Default, has occurred and is continuing.\n"
        "5A.4 Ownership of assets: the Borrower is the unencumbered legal and beneficial "
        "owner of all charged assets, has good title to the Project land, and the "
        "execution of the Security does not breach any other agreement binding on it.\n"
        "5A.5 Approvals: all consents, licences, approvals and registrations required "
        "for the Project and its business have been obtained and remain in full force, "
        "and no condition of any of them has been breached.\n"
        "5A.6 Sanctions and anti-bribery: neither the Borrower, nor any promoter, "
        "director, or to its knowledge any agent acting for it, is a sanctioned person, "
        "and no Facility amount will be used in contravention of applicable sanctions "
        "or anti-bribery law.\n\n"
        "5B. GUARANTEES\n\n"
        "5B.1 The personal guarantees and the corporate guarantee described in Clause "
        "14.1(d) are continuing, independent and irrevocable obligations covering the "
        "entire Outstanding, present and future, and remain in force until all "
        "Obligations are discharged in full and the Lender releases them in writing.\n"
        "5B.2 Each guarantor waives (to the extent permitted by law): any right to "
        "require the Lender to proceed first against the Borrower or the Security; any "
        "defence of set-off available to the Borrower; notice of default and of "
        "enforcement; and any benefit of marshalling of assets.\n"
        "5B.3 If any guarantee obligation would be reduced, limited or rendered "
        "unenforceable as a preference or fraudulent conveyance under applicable law, "
        "it shall be reduced only to the minimum extent necessary, and the guarantor "
        "shall contribute the maximum recoverable share for the balance.\n"
        "5B.4 The Lender may vary the terms of this Agreement, or grant time or other "
        "indulgence to the Borrower, or take or omit to take enforcement steps, "
        "without notice to or consent from any guarantor, and the guarantees remain "
        "in full force.\n\n"
        "5C. ILLUSTRATIVE FIRST-YEAR PAYMENT PROFILE (single drawdown on 1 April 2027)\n\n"
        "The table below illustrates the cash-flow mechanics of Clause 8 for the first "
        "twelve months of the Moratorium, at the all-in rate of 14.35 percent on the "
        "full Facility Amount. During the Moratorium only interest is payable; the "
        "operative schedule recomputes for staggered drawdowns.\n"
    )

    il = [
        f"{'Month':<8}{'Opening Rs.':>17}{'Interest Rs.':>16}{'Principal Rs.':>16}"
        f"{'Closing Rs.':>17}",
        "-" * 74,
    ]
    bal = 425000000
    for m in range(1, 13):
        interest = round(bal * 0.1435 / 12)
        il.append(f"{num(m,8):<8}{num(bal,17):>17}{num(interest,16):>16}{num(0,16):>16}"
                  f"{num(bal,17):>17}")
    il.append(
        "\nWhere drawdowns occur in tranches, interest for each month is computed on "
        "the daily product of amounts actually outstanding; the Lender's system "
        "statement is the prima facie record, subject to Clause 17.2 reconciliation."
    )
    parts.append("\n".join(il))

    parts.append(
        "\f5D. LENDER'S ENFORCEMENT PROCEDURE (STAIR-STEP)\n\n"
        "5D.1 This Clause 5D governs the sequence of the Lender's actions on a "
        "continuing Event of Default, without prejudice to any right to act "
        "immediately where the security or recoveries are in jeopardy:\n"
        "  Step 1 (Day 0-7): written default notice per Clause 15.1(a); demand on the "
        "Borrower with a cure window; intimation to the guarantors.\n"
        "  Step 2 (Day 7-30): escalation meeting; penal interest accrues; the "
        "collection-account waterfall locks to debt service only; the Lender may "
        "appoint a monitoring agency at the Borrower's cost.\n"
        "  Step 3 (Day 30-60): cancellation of undrawn commitments; declaration of "
        "acceleration; invocation of personal and corporate guarantees by demand; "
        "SARFAESI Section 13(2) demand notice on secured assets where applicable.\n"
        "  Step 4 (Day 60 onward): possession of secured assets by physical or "
        "symbolic possession; appointment of an approved receiver; publication of "
        "the sale notice under SARFAESI rules; application of sale proceeds per "
        "Clause 6.3.\n"
        "5D.2 Nothing in this Clause 5D obliges the Lender to follow any particular "
        "sequence where statute prescribes a different process (including proceedings "
        "before the NCLT under the Insolvency and Bankruptcy Code, 2016), and the "
        "Lender may pursue parallel remedies to the extent permitted by law.\n"
        "5D.3 The Lender shall credit sale or enforcement proceeds to the Facility "
        "Account within 2 Business Days of receipt and furnish a consolidated "
        "statement of account within 15 days of full recovery or settlement.\n\n"
        "5E. EXCLUSION OF LENDER'S LIABILITY; INDEPENDENT APPRAISAL\n\n"
        "5E.1 The Lender has relied solely on the Borrower's representations and the "
        "technical and legal reports commissioned by it in deciding to make the "
        "Facility available. The Lender is not the Project's designer, supervisor or "
        "guarantor of outcome; its appraisal does not constitute a warranty of the "
        "Project's viability.\n"
        "5E.2 The Lender's technical consultant acts for the Lender alone; his "
        "certificates are conditions of disbursement, not professional advice to the "
        "Borrower, and the Borrower remains solely responsible for design adequacy, "
        "construction quality and statutory compliance of the Project.\n"
        "5E.3 Where the Lender appoints any nominee, receiver or agent, it shall act "
        "reasonably and in accordance with its statutory duties; the Lender is "
        "liable to the Borrower only for its own fraud or wilful misconduct.\n\n"
        "5F. FURTHER DEFINITIONS\n\n"
        "\u201cCollection Account\u201d means account no. 50100XXXX882 with the Lender over "
        "which the escrow charge per Annex C is created.\n"
        "\u201cCure Period\u201d means, for financial covenant breaches, the period under "
        "Clause 12.2, and for all other covenants 30 days from written notice.\n"
        "\u201cEscrow Charge\u201d means the charge over the Collection Account and all "
        "monetary rights thereunder in favour of the Lender.\n"
        "\u201cGuarantors\u201d means the personal guarantors and the corporate guarantor "
        "named in Clause 14.1(d).\n"
        "\u201cMonitoring Agency\u201d means an independent engineer or firm appointed "
        "under Clause 5D.2 to report on Project progress and end-use of funds.\n"
        "\u201cObligations\u201d means all obligations of the Borrower to the Lender under "
        "this Agreement and the Security documents, present or future, primary or "
        "collateral, joint or several.\n"
        "\u201cPermitted Encumbrance\u201d means any encumbrance arising by operation of "
        "law in the ordinary course and not exceeding Rs. 50 lakh in aggregate, and "
        "the Security.\n"
        "\u201cSARFAESI\u201d means the Securitisation and Reconstruction of Financial "
        "Assets and Enforcement of Security Interest Act, 2002, together with its "
        "rules.\n\n"
        "5G. INTEGRITY UNDERTAKINGS AND RECORD KEEPING\n\n"
        "5G.1 The Borrower shall maintain for 8 years complete records of the "
        "Project, including all invoices, contractors' bills, measurement books, "
        "bank statements of the Collection Account and end-use certificates, and "
        "make them available to the Lender and to any statutory auditor.\n"
        "5G.2 The Borrower confirms that neither it, nor its promoters, have been "
        "blacklisted by any bank, financial institution or government body, and "
        "shall notify the Lender within 5 Business Days if that changes.\n"
        "5G.3 The Borrower shall prominently display at the Project site the "
        "sanctioned plans, environmental consent and labour-law registrations, and "
        "comply with the applicable factories and labour welfare statutes."
    )

    # Schedule A - repayment schedule (66 EMIs)
    sa = [
        "SCHEDULE A - REPAYMENT SCHEDULE (illustrative amortisation; assumes single "
        "first utilisation on 1 April 2027 at an all-in rate of 14.35 percent p.a.)",
        "",
        f"{'Instalment':<11}{'Month':>7}{'Principal Rs.':>16}{'Interest Rs.':>15}"
        f"{'Total Rs.':>14}{'Balance Rs.':>17}",
        "-" * 80,
    ]
    principal = 425000000
    rate = 0.1435
    emi = 8712500  # approx equal instalment
    for i in range(1, 67):
        month = 18 + i
        interest = round(principal * rate / 12)
        pr = min(emi - interest, principal)
        principal -= pr
        sa.append(
            f"{num(i,11):<11}{num(month,7):>7}{num(pr,16):>16}{num(interest,15):>15}"
            f"{num(pr+interest,14):>14}{num(principal,17):>17}"
        )
    sa.append(
        "\nNotes: figures are rounded to the nearest rupee; the operative schedule is "
        "recalculated on each actual Utilisation Date and rate reset; bullet repayment "
        "of residual balance on the Final Repayment Date; DSCR tested on the aggregate "
        "of principal and interest above."
    )
    parts.append("\f" + "\n".join(sa))

    # Annexes
    an = [
        "ANNEX A - FACILITIES AND FEES SUMMARY",
        "",
        f"{'Facility':<30}{'Amount Rs.':>18}{'Purpose':>30}",
        "-" * 78,
        f"{'Term loan - Project':<30}{'42,50,00,000':>18}{'Plant, cold store, civil':>30}",
        f"{'Commitment charge':<30}{'0.40% p.a.':>18}{'On undrawn amounts':>30}",
        f"{'Processing fee':<30}{'0.85% one-time':>18}{'On signing':>30}",
        f"{'Default interest':<30}{'+2.50% p.a.':>18}{'On overdue amounts':>30}",
        f"{'Prepayment premium':<30}{'2% then nil':>18}{'Before/after 24 EMIs':>30}",
        "",
        "ANNEX B - CONDITIONS PRECEDENT (FIRST DRAWdown)",
        "B-1 Executed Agreement, Security documents and guarantees (notarised where "
        "required); B-2 Board resolution and powers of attorney; B-3 Shareholder "
        "resolution approving the Security; B-4 Search reports (ROC, CERSAI, SARFAESI) "
        "dated within 15 days; B-5 Project approvals: environmental consent to "
        "establish, fire NOC, FSSAI, building plan sanction; B-6 CA certificate of "
        "equity infusion of Rs. 15.50 crore; B-7 Insurance policies per Clause 13 with "
        "loss-payee endorsement; B-8 Legal opinion of the Borrower's counsel; B-9 "
        "Technical consultant's appraisal confirmation; B-10 Payment of Lender's Costs.",
        "",
        "ANNEX C - SECURITY DETAILS AND DEFINED FINANCIAL TERMS",
        "C-1 Equitable mortgage: land 4.8 acres (Sy. Nos. 112/2, 113, Kazipet) and "
        "buildings thereon; memorandum of deposit of title deeds dated with the "
        "Agreement; registration as applicable.",
        "C-2 Hypothecation: all moveable fixed assets of the Project, both present "
        "and future; inventory of the assets annexed to the hypothecation deed.",
        "C-3 Receivables escrow: collection account no. 50100XXXX882 with the Lender; "
        "minimum 60 percent routing per Clause 16; fall-to-the-charge on default.",
        "C-4 Total Outside Liabilities means all liabilities not represented by "
        "tangible net worth, including deferred tax liabilities but excluding "
        "shareholders' funds.",
        "C-5 Tangible Net Worth means paid-up capital plus reserves less intangibles, "
        "accumulated losses and preliminary expenses.",
        "C-6 DSCR for a period means (cash accruals, being profit before interest, "
        "depreciation and tax, plus interest) divided by (interest plus scheduled "
        "principal for the same period).",
        "",
        "SCHEDULE D - FORM OF UTILISATION REQUEST",
        "To: Grandway Finance and Leasing Limited. Facility No. GFL/TL/2027/0417.",
        "Requested drawdown date: ____. Amount: Rs. ______. Against invoice/certificate "
        "Nos.: ______ aggregating Rs. ______. The Borrower confirms: (1) the Conditions "
        "Precedent are satisfied; (2) no Event of Default is continuing and is not "
        "likely to result; (3) the amount will be applied to the Project costs described "
        "above; (4) the representations in Clause 5 are true. Authorised signatory(ies): "
        "signature, name, designation, date; bank stamp where collected by cheque.",
        "",
        "ANNEX D - PROJECT COST BREAKDOWN AND TRANCHE SCHEDULE",
        "",
        f"{'Component':<44}{'Rs. (lakh)':>14}{'Share':>8}",
        "-" * 66,
        f"{'Land and site development (already owned)':<44}{num(820,14):>14}{num(14.1,8):>8}",
        f"{'Civil works - processing block and cold store':<44}{num(1680,14):>14}{num(29.0,8):>8}",
        f"{'Plant and machinery - pulp line 2':<44}{num(1450,14):>14}{num(25.0,8):>8}",
        f"{'Plant and machinery - RTC line':<44}{num(760,14):>14}{num(13.1,8):>8}",
        f"{'Cold store 4,000 MT (turnkey)':<44}{num(620,14):>14}{num(10.7,8):>8}",
        f"{'Utilities - boiler, chillers, ETP, DG':<44}{num(420,14):>14}{num(7.2,8):>8}",
        f"{'Electricals, automation and IT':<44}{num(240,14):>14}{num(4.1,8):>8}",
        f"{'Pre-operative and contingencies':<44}{num(230,14):>14}{num(4.0,8):>8}",
        f"{'Margin for working capital (deposit)':<44}{num(580,14):>14}{num(0.0,8):>8}",
        "",
        "Total project cost: Rs. 58,00,00,000/-. Funding: term loan Rs. 42.50 crore "
        "(73.3 percent); promoter equity Rs. 15.50 crore (26.7 percent), of which "
        "Rs. 6.00 crore is already deployed (CA certificate) and the balance is to "
        "be brought in pro-rata to disbursements, prior to each tranche.",
        "",
        "Tranche schedule (indicative; actual against progress certificates):",
        f"{'Tranche':<10}{'Milestone':<44}{'Amount Rs. lakh':>16}",
        "-" * 70,
        f"{'T1':<10}{'Mobilisation, civil advance, insurance premium':<44}{num(425,16):>16}",
        f"{'T2':<10}{'Foundations and civil up to plinth':<44}{num(510,16):>16}",
        f"{'T3':<10}{'Civil up to lintel level, order placement of line 2':<44}{num(680,16):>16}",
        f"{'T4':<10}{'Structure complete, pulp line 2 delivered':<44}{num(765,16):>16}",
        f"{'T5':<10}{'Cold store civil complete, equipment dispatch':<44}{num(680,16):>16}",
        f"{'T6':<10}{'Equipment erection 50 percent, RTC line delivered':<44}{num(595,16):>16}",
        f"{'T7':<10}{'Erection complete, utilities commissioned':<44}{num(425,16):>16}",
        f"{'T8':<10}{'Trial run and commissioning certificate':<44}{num(170,16):>16}",
        "",
        "ANNEX E - HYPOTHECATION INVENTORY (PRINCIPAL ITEMS)",
        "Fruit-wash and grading line (2); pulper finishing mill 5 TPH (2); screw "
        "press (2); tubular pasteuriser 6 TPH; aseptic filling machine 220 packs/min; "
        "can retort line; rotogravure-less pouch filling (zip) 90 packs/min; chilling "
        "plant 120 TR (screw chiller); cold store panels and racking 4,000 MT with "
        "two reach-truck fleets; blast freezer 2 x 8 MT/day; boilers 6 TPH biomass-"
        "fired with dust collection; DG sets 2 x 750 kVA; transformers 2 x 1,600 kVA "
        "and HT panel; RO water plant 20 KL/day; ETP 150 KLD; effluent drum filter; "
        "compressors 2 x 55 kW with dryers; quality-lab instruments (FTIR, texture "
        "analyser, incubators); weighing bridges 40T; material handling - conveyor "
        "systems and pallet stackers; fire-fighting pumps and hydrant network; "
        "utilities piping and insulation; spares as per annexure list held by the "
        "Lender's technical consultant, updated quarterly.",
        "",
        "ANNEX F - COLLECTION ACCOUNT WATERFALL",
        "Receipts routed per Clause 16 are applied monthly in the following order:",
        "  1. Statutory dues: GST, TDS, minimum wages related to the Project;",
        "  2. Interest due on the Facility and Default Interest;",
        "  3. Scheduled principal instalment;",
        "  4. Insurance premiums for charged assets;",
        "  5. Operating expenses up to the budget approved with the Lender;",
        "  6. Balance: 50 percent retained for Project completion shortfall, the "
        "     remainder freely available to the Borrower.",
        "Statements of the waterfall computation accompany each monthly information "
        "pack; discrepancies above Rs. 5 lakh are explained in writing.",
        "",
        "ANNEX G - COMPLIANCE CALENDAR",
        f"{'Frequency':<12}{'Deliverable':<50}{'Due':>12}",
        "-" * 74,
        f"{'Monthly':<12}{'Operating data + stock statement + waterfall':<50}{'+30 days':>12}",
        f"{'Monthly':<12}{'Interest payment (auto-debit mandate)':<50}{'7th':>12}",
        f"{'Quarterly':<12}{'Provisional results + covenant computation':<50}{'+45 days':>12}",
        f"{'Quarterly':<12}{'Utilisation certificates from engineer':<50}{'+20 days':>12}",
        f"{'Half-yearly':<12}{'Stock and book-debt verification report':<50}{'+30 days':>12}",
        f"{'Annually':<12}{'Audited Financial Statements + CA compliance cert':<50}{'+180 days':>12}",
        f"{'Annually':<12}{'Insurance renewal evidence (all policies)':<50}{'+15 days':>12}",
        f"{'Annually':<12}{'Asset valuation refresh (empanelled valuer)':<50}{'+180 days':>12}",
        f"{'Event-based':<12}{'Litigation notice above Rs. 2 crore':<50}{'+7 days':>12}",
        f"{'Event-based':<12}{'Change in promoter shareholding above 10 percent':<50}{'+7 days':>12}",
        "",
        "SCHEDULE E - NOTICES AND AUTHORISED SIGNATORIES",
        "Lender: Grandway Finance and Leasing Ltd, 18B Trade Crest, BKC, Mumbai 400051, "
        "Attn: Corporate Credit Administration, credit.ops@grandway.example.",
        "Borrower: Roshan Foods Processing Pvt Ltd, Plot 32, Food Park, Kazipet, "
        "Telangana 506003, Attn: Chief Financial Officer, cfo@roshanfoods.example.",
        "Authorised signatories: Roshanlal Agarwal (MD) and Sanjay Gupta (CFO), "
        "jointly; single signatory up to Rs. 5 crore for interest payments only.",
    ]
    parts.append("\f" + "\n".join(an))
    return "".join(parts)


def main() -> None:
    render_pdf("Enterprise_IT_Outsourcing_Agreement.pdf", build_ita())
    render_pdf("Construction_Works_Contract.pdf", build_ccc())
    render_pdf("Term_Loan_Facility_Agreement.pdf", build_facility())
    print("Long-form test documents written to", OUT_DIR)


if __name__ == "__main__":
    main()
