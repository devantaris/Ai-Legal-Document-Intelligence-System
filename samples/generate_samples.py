"""Generate sample contracts for manual testing.

Creates fictional, self-written agreements (no real-world text):
  - Mutual_NDA.txt
  - Services_Agreement_v1.pdf / .txt
  - Services_Agreement_v2.pdf / .txt  (modified payment, termination, warranty
    clauses plus a new insurance clause — useful for the Compare feature)

Usage:  python samples/generate_samples.py
"""

import re
from pathlib import Path

import pymupdf

SAMPLES_DIR = Path(__file__).parent


def flex_replace(text: str, old: str, new: str) -> str:
    """Replace `old` with `new` ignoring line-wrap differences. Raises when the
    snippet is not found so sample edits can never silently no-op."""
    pattern = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
    out, count = pattern.subn(lambda _m: new, text)
    if count == 0:
        raise ValueError(f"sample edit snippet not found: {old[:60]!r}")
    return out

NDA = """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement (the "Agreement") is entered into as of
January 1, 2024 (the "Effective Date"), by and between Acme Corp, a Delaware
corporation with offices at 100 Main Street, Wilmington, DE ("Company"), and
Beta LLC, a New York limited liability company with offices at 5 Park Avenue,
New York, NY ("Recipient"), each a "Party" and together the "Parties".

1. PURPOSE. The Parties wish to explore a potential business relationship
(including the evaluation of a possible software licensing arrangement) and
may disclose certain confidential information to one another in connection
with that purpose.

2. CONFIDENTIAL INFORMATION. "Confidential Information" means any non-public
information disclosed by one Party to the other, whether oral, written or
electronic, that is designated as confidential or that reasonably should be
understood to be confidential given the nature of the information and the
circumstances of disclosure. Confidential Information includes business
plans, customer lists, financial data, software source code and product
roadmaps.

3. EXCLUSIONS. Confidential Information does not include information that:
3.1 is or becomes publicly available through no fault of the receiving
Party; or
3.2 was rightfully known to the receiving Party before disclosure; or
3.3 is independently developed without use of the disclosing Party's
Confidential Information; or
3.4 is rightfully obtained from a third party without restriction.

4. OBLIGATIONS OF THE RECEIVING PARTY. The receiving Party shall:
4.1 protect the disclosing Party's Confidential Information with at least
the same degree of care it uses to protect its own confidential information,
and in no event with less than reasonable care;
4.2 not disclose the Confidential Information to any third party without the
prior written consent of the disclosing Party, except to employees and
advisors who have a need to know and who are bound by confidentiality
obligations at least as protective as this Agreement; and
4.3 use the Confidential Information solely for the Purpose stated in
Section 1.

5. TERM. This Agreement commences on the Effective Date and continues for a
period of two (2) years, unless terminated earlier in accordance with
Section 6.

6. TERMINATION. Either Party may terminate this Agreement at any time upon
thirty (30) days' prior written notice to the other Party. The obligations in
Sections 2, 4 and 7 survive termination for a period of three (3) years.

7. GOVERNING LAW. This Agreement is governed by the laws of the State of
Delaware, without regard to its conflict of laws principles.

8. DISPUTE RESOLUTION. Any dispute arising out of or relating to this
Agreement shall be finally resolved by binding arbitration administered by
the American Arbitration Association in New York, New York, before a single
arbitrator. Each Party shall bear its own legal costs.

9. MISCELLANEOUS. This Agreement constitutes the entire agreement between the
Parties with respect to its subject matter and may be amended only in writing
signed by both Parties. Neither Party may assign this Agreement without the
prior written consent of the other Party. If any provision of this Agreement
is held unenforceable, the remaining provisions continue in full force.

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the
Effective Date.

ACME CORP                               BETA LLC

By: ______________________              By: ______________________
Name: Jane Doe                          Name: John Smith
Title: Vice President                   Title: Managing Member
"""

V1 = """MASTER SERVICES AGREEMENT (VERSION 1)

This Master Services Agreement (the "Agreement") is entered into as of
March 1, 2024 (the "Effective Date"), by and between Alpha Inc, a California
corporation ("Provider"), and Gamma Partners LLC, a Texas limited liability
company ("Client").

ARTICLE 1 - SERVICES

1.1 Provision of Services. Provider shall provide the professional services
described in each mutually executed Statement of Work ("SOW") incorporated
herein by reference. Each SOW shall specify the deliverables, timeline and
applicable fees.

1.2 Standard of Performance. Provider shall perform the Services in a
professional and workmanlike manner consistent with generally accepted
industry standards.

ARTICLE 2 - FEES AND PAYMENT

2.1 Fees. Client shall pay Provider the fees set out in the applicable SOW.
Unless otherwise stated in the SOW, Provider shall invoice monthly in
arrears.

2.2 Payment Terms. Client shall pay each correct invoice within thirty (30)
days of receipt. Late payments accrue interest at the rate of 1% per month
or the maximum rate permitted by law, whichever is lower.

2.3 Expenses. Client shall reimburse Provider for reasonable, pre-approved
out-of-pocket expenses incurred in performing the Services.

ARTICLE 3 - TERM AND TERMINATION

3.1 Term. This Agreement begins on the Effective Date and continues for an
initial term of twelve (12) months, renewing automatically for successive
one (1) year periods unless either Party gives written notice of
non-renewal at least sixty (60) days before the end of the then-current
term.

3.2 Termination for Convenience. Either Party may terminate this Agreement
for convenience upon ninety (90) days prior written notice to the other
Party.

3.3 Termination for Cause. Either Party may terminate this Agreement
immediately upon written notice if the other Party materially breaches this
Agreement and fails to cure the breach within thirty (30) days after
receiving written notice describing the breach.

3.4 Effect of Termination. Upon termination, Client shall pay Provider for
all Services performed and expenses incurred through the effective date of
termination. Sections 2.2, 5, 6 and 7 survive termination.

ARTICLE 4 - INTELLECTUAL PROPERTY

4.1 Ownership of Deliverables. Upon full payment, Provider assigns to
Client all right, title and interest in the deliverables developed
specifically for Client under each SOW (excluding Provider's pre-existing
tools, libraries and know-how).

4.2 Provider Tools. Provider retains all rights in its methodologies,
software tools and generic know-how developed or used independently of the
Services.

ARTICLE 5 - CONFIDENTIALITY

5.1 Mutual Obligation. Each Party shall protect the other Party's
confidential information with reasonable care and use it only to fulfill
its obligations under this Agreement.

5.2 Duration. The obligations in this Article 5 continue during the term of
this Agreement and for three (3) years thereafter.

ARTICLE 6 - WARRANTIES AND LIMITATION OF LIABILITY

6.1 Mutual Warranties. Each Party represents and warrants that it has full
power and authority to enter into this Agreement.

6.2 Disclaimer. EXCEPT AS EXPRESSLY STATED IN THIS AGREEMENT, THE SERVICES
ARE PROVIDED "AS IS" AND PROVIDER DISCLAIMS ALL OTHER WARRANTIES, WHETHER
EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE.

6.3 Limitation of Liability. NEITHER PARTY SHALL BE LIABLE FOR ANY
INDIRECT, INCIDENTAL, SPECIAL OR CONSEQUENTIAL DAMAGES. EACH PARTY'S TOTAL
AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL NOT EXCEED THE FEES PAID BY
CLIENT IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.

ARTICLE 7 - GOVERNING LAW AND DISPUTES

7.1 Governing Law. This Agreement is governed by the laws of the State of
California.

7.2 Escalation and Litigation. The Parties shall first attempt to resolve
any dispute through good-faith negotiation between senior executives for a
period of thirty (30) days. Failing resolution, either Party may bring
proceedings in the state or federal courts located in San Francisco County,
California, and each Party submits to their exclusive jurisdiction.

ARTICLE 8 - GENERAL

8.1 Force Majeure. Neither Party is liable for delays caused by events
beyond its reasonable control, including natural disasters, war, labor
disputes and failures of public infrastructure.

8.2 Assignment. Neither Party may assign this Agreement without the prior
written consent of the other Party, except to a successor in a merger or
sale of substantially all assets.

8.3 Notices. All notices must be in writing and delivered by email with
confirmation, or by certified mail, to the addresses on the first page.

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the
Effective Date.
"""

V2 = V1.replace("MASTER SERVICES AGREEMENT (VERSION 1)", "MASTER SERVICES AGREEMENT (VERSION 2)")
# renegotiated: net-15 payment, 2% interest + suspension right, termination for
# convenience now 30 days with break fee, liability cap doubled, warranty window
# added, insurance clause new
V2 = flex_replace(
    V2,
    "Client shall pay each correct invoice within thirty (30) days of receipt. "
    "Late payments accrue interest at the rate of 1% per month or the maximum "
    "rate permitted by law, whichever is lower.",
    "Client shall pay each correct invoice within fifteen (15) days of receipt. "
    "Late payments accrue interest at the rate of 2% per month or the maximum "
    "rate permitted by law, whichever is lower. Provider may suspend the "
    "Services if an invoice remains unpaid for more than thirty (30) days.",
)
V2 = flex_replace(
    V2,
    "Either Party may terminate this Agreement for convenience upon ninety "
    "(90) days prior written notice to the other Party.",
    "Either Party may terminate this Agreement for convenience upon thirty "
    "(30) days prior written notice to the other Party, provided that "
    "termination during the initial term requires payment of fifty percent "
    "(50%) of the fees remaining for the then-current SOW.",
)
V2 = flex_replace(
    V2,
    "TOTAL AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL NOT EXCEED THE FEES "
    "PAID BY CLIENT IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.",
    "TOTAL AGGREGATE LIABILITY UNDER THIS AGREEMENT SHALL NOT EXCEED TWO (2) "
    "TIMES THE FEES PAID BY CLIENT IN THE TWELVE (12) MONTHS PRECEDING THE "
    "CLAIM.",
)
V2 = V2.replace(
    "ARTICLE 8 - GENERAL",
    """6.4 Warranty Period. Provider warrants that material defects in the
deliverables reported by Client within sixty (60) days after delivery will
be corrected at no additional charge.

ARTICLE 7A - INSURANCE

7A.1 Insurance. Provider shall maintain commercial general liability
insurance with limits of not less than two million dollars ($2,000,000) per
occurrence and shall provide certificates of insurance upon Client's
written request.

ARTICLE 8 - GENERAL""",
)


def write_txt(name: str, text: str) -> None:
    (SAMPLES_DIR / name).write_text(text, encoding="utf-8")


def write_pdf(name: str, text: str, page_chars: int = 1800) -> None:
    doc = pymupdf.open()
    chunks = []
    while text:
        chunks.append(text[:page_chars])
        text = text[page_chars:]
    for chunk in chunks:
        page = doc.new_page()
        rect = pymupdf.Rect(50, 50, 560, 770)
        rc = page.insert_textbox(rect, chunk, fontsize=10, fontname="helv")
        if rc < 0:
            raise ValueError(f"text did not fit the page box (rc={rc}) in {name}")
    doc.save(SAMPLES_DIR / name)
    doc.close()


def main() -> None:
    write_txt("Mutual_NDA.txt", NDA)
    write_txt("Services_Agreement_v1.txt", V1)
    write_txt("Services_Agreement_v2.txt", V2)
    write_pdf("Services_Agreement_v1.pdf", V1)
    write_pdf("Services_Agreement_v2.pdf", V2)
    print("Sample contracts written to", SAMPLES_DIR)


if __name__ == "__main__":
    main()
