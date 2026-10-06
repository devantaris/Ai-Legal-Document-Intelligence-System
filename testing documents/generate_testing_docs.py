"""Generate realistic test documents for manual upload testing.

Creates ten ORIGINAL agreements written in the exact style and structure of
real-world documents (defined terms, numbered clauses, fee tables, exhibits,
signature blocks), across PDF and DOCX so every extraction path gets tested:

  1. Employment_Offer_Letter.pdf        (2 pages, CTC table)
  2. Residential_Lease_Agreement.pdf    (4 pages)
  3. Consultancy_MSA_with_SOW.docx      (MSA + SOW exhibit)
  4. SaaS_Subscription_Agreement.pdf    (SLA + pricing tables)
  5. Loan_Agreement.docx                (EMI schedule, acceleration clause)
  6. Vendor_Supply_Agreement.pdf        (pricing table, penalties, dense layout)
  7. Franchise_Agreement.pdf            (royalty, territory, renewal)
  8. Memorandum_of_Understanding.docx   (non-binding, startup/investor)
  9. Partnership_Deed.docx              (capital shares, profit split)
 10. Website_Privacy_Policy.pdf         (non-contract prose, tests robustness)

All names, companies, addresses and terms are fictional.
Usage:  python "testing documents/generate_testing_docs.py"
"""

import re
from pathlib import Path

import pymupdf
from docx import Document as DocxDocument
from docx.shared import Pt

OUT_DIR = Path(__file__).parent


# ---------------------------------------------------------------- helpers
def write_pdf(name: str, pages: list[str]) -> None:
    doc = pymupdf.open()
    for text in pages:
        page = doc.new_page()
        rc = page.insert_textbox(
            pymupdf.Rect(50, 50, 560, 770), text, fontsize=10, fontname="helv"
        )
        if rc < 0:
            raise ValueError(f"text did not fit a page box (rc={rc}) in {name}")
    doc.save(OUT_DIR / name)
    doc.close()


def write_docx(name: str, blocks: list) -> None:
    """blocks: list of ("h", text) | ("p", text) | ("b", text) | ("t", rows)."""
    doc = DocxDocument()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(10.5)
    for kind, payload in blocks:
        if kind == "h":
            doc.add_heading(payload, level=2)
        elif kind == "t":
            table = doc.add_table(rows=len(payload), cols=len(payload[0]))
            table.style = "Light Grid Accent 1"
            for r, row in enumerate(payload):
                for c, value in enumerate(row):
                    cell = table.rows[r].cells[c]
                    cell.text = str(value)
                    for p in cell.paragraphs:
                        for run in p.runs:
                            run.font.size = Pt(9.5)
        else:
            p = doc.add_paragraph(payload)
            if kind == "b":
                p.paragraph_format.left_indent = Pt(18)
    doc.save(OUT_DIR / name)


def cols(left: str, right: str, width: int = 78) -> str:
    """A simple two-column fee table rendered as plain text."""
    gap = " " * max(2, width - len(left) - len(right))
    return f"{left}{gap}{right}"


# ---------------------------------------------------------------- 1. offer letter
OFFER_P1 = """TRITON ANALYTICS PRIVATE LIMITED
4th Floor, Prestige Tech Park, Outer Ring Road, Bengaluru 560103
CIN: U62099KA2021PTC154882  |  GSTIN: 29AAJCT1234K1ZV

                                                                        12 September 2026

Ms. Ananya Sharma
B-402, Lake View Apartments, HSR Layout, Bengaluru 560102

Subject: Offer of Employment - Senior Data Engineer (Grade E3)

Dear Ms. Sharma,

Reference your interviews with us, we are pleased to offer you employment with Triton
Analytics Private Limited ("the Company") on the terms set out in this letter ("Offer Letter")
and the enclosed Employment Terms Annexure ("Annexure A"), which together constitute your
employment agreement ("Agreement").

1. POSITION AND JOINING
1.1 You will hold the position of Senior Data Engineer in the Data Platform Group and will
    report to the Director of Engineering.
1.2 Your employment commences on 05 October 2026 ("Date of Joining"). Your place of work
    will be the Bengaluru office, subject to the Company's hybrid work policy.
1.3 You shall be on probation for a period of six (6) months from the Date of Joining. The
    Company may, at its discretion, extend the probation by up to three (3) months or confirm
    your employment on completion.

2. REMUNERATION
2.1 Your total cost to company ("CTC") shall be Rs. 24,00,000/- per annum, structured as
    follows:

""" + "\n".join([
    cols("Component", "Amount (Rs. p.a.)"),
    "-" * 78,
    cols("Basic Salary", "9,60,000"),
    cols("House Rent Allowance", "4,80,000"),
    cols("Special Allowance", "4,44,000"),
    cols("Provident Fund (employer share)", "1,15,200"),
    cols("Performance Bonus (target, variable)", "2,40,000"),
    cols("Health Insurance (family floater)", "18,000"),
    cols("Gratuity provision", "42,800"),
]) + """

2.2 The performance bonus is payable annually, is subject to achievement of objectives and
    Company performance, and shall not be treated as salary for any notice-pay computation.
2.3 Salary reviews occur annually in April; nothing in this letter guarantees an increment.

3. DOCUMENTS AND ANTECEDENTS
3.1 This offer is contingent upon (a) satisfactory verification of your educational and
    employment history, (b) reference checks, and (c) execution of Annexure A, including the
    confidentiality and intellectual-property assignments contained in it.
"""

OFFER_P2 = """4. WORKING HOURS, LEAVE AND BENEFITS
4.1 Working hours are 9:30 a.m. to 6:30 p.m., Monday to Friday. The role is exempt from
    overtime provisions under the applicable shops and establishments law.
4.2 You are entitled to twenty-four (24) days of paid leave per calendar year, accrued
    monthly, in addition to declared public holidays.
4.3 Benefits include group medical insurance, term-life cover of Rs. 25,00,000/- and the
    Company's retirement benefits as per statutory requirements.

5. NOTICE AND TERMINATION
5.1 During probation, either party may end this employment with fifteen (15) days' written
    notice. After confirmation, the notice period is sixty (60) days, or salary in lieu.
5.2 The Company may terminate employment without notice for misconduct, breach of the
    confidentiality obligations, or any act of moral turpitude, following due process.
5.3 Upon separation you shall return all Company property and hand over all work in
    progress; unexercised vested stock options shall be dealt with per the ESOP rules.

6. RESTRICTIVE COVENANTS
6.1 You shall not, during employment and for six (6) months after its end, solicit any
    employee or client of the Company with whom you materially dealt in the final year.
6.2 The Parties agree the covenants in this Clause 6 are reasonable and necessary for the
    protection of the Company's legitimate business interests.

7. GENERAL
7.1 This letter, with Annexure A, supersedes all prior discussions. Any modification must
    be in writing and signed by an authorised signatory.
7.2 This Agreement is governed by the laws of India, and the courts at Bengaluru shall have
    exclusive jurisdiction.

We look forward to welcoming you to Triton Analytics.

Yours sincerely,
For TRITON ANALYTICS PRIVATE LIMITED


                                          Accepted and agreed:


(signed) Rohit Menon                     _______________________
Head of People Operations                Ms. Ananya Sharma
Date: 12 September 2026                  Date: _______________

ANNEXURE A - EMPLOYMENT TERMS (extract)
A-1 Confidential Information means any non-public business, technical, product, customer or
    financial information of the Company disclosed to you, in any form.
A-2 All work product created by you in the course of employment vests in the Company on
    creation, and you assign all right, title and interest in it to the Company.
A-3 The confidentiality obligations survive termination of employment for three (3) years.
"""

# ---------------------------------------------------------------- 2. lease
LEASE = [
    """RESIDENTIAL LEASE AGREEMENT

This Residential Lease Agreement ("Agreement") is made and executed at Pune on this 1st day
of November 2026 by and between:

Mr. Mahesh Kulkarni, aged 54 years, residing at 27 Sneh Society, Karve Nagar, Pune 411052,
hereinafter referred to as the "LANDLORD" (which expression shall include his heirs,
executors and permitted assigns);

AND

Ms. Priya Nair, aged 29 years, residing temporarily at Sunbeam Hostel, Baner Road, Pune,
hereinafter referred to as the "TENANT" (which expression shall include her heirs and
permitted assigns).

WHEREAS the Landlord is the absolute owner of Flat No. A-704, "Silver Heights", Plot 12,
Baner Road, Pune 411045 (the "Premises"); AND WHEREAS the Tenant desires to take the
Premises on lease for residential use only; NOW THIS AGREEMENT WITNESSES:

1. TERM. The lease shall be for a period of eleven (11) months commencing 15 November 2026
   and ending 14 October 2027, unless terminated earlier under Clause 10.

2. RENT. The Tenant shall pay monthly rent of Rs. 32,000/- (Rupees thirty-two thousand only)
   by the 5th day of every English calendar month by bank transfer to the Landlord's account
   stated in Schedule A. Rent for the first month is payable on execution.

3. SECURITY DEPOSIT. The Tenant has paid Rs. 96,000/- (three months' rent) as an interest-
   free refundable security deposit. The Landlord shall refund the deposit within fifteen
   (15) days of vacant possession, after deducting unpaid rent and the cost of damages
   beyond normal wear and tear, supported by invoices.

4. MAINTENANCE CHARGES. Monthly society maintenance of approx. Rs. 3,200/- is included in
   the rent. Electricity, internet, cooking-gas and water-tanker charges are payable by the
   Tenant directly.""",
    """5. USE AND OCCUPANCY. The Premises shall be used solely for residential purposes by the
   Tenant and her immediate family, not exceeding four (4) persons. Running a business,
   storing hazardous goods, or subletting any part of the Premises is strictly prohibited.

6. ALTERATIONS. No structural alterations are permitted. The Tenant may install fixtures
   with prior written consent and shall restore the Premises on exit where required.

7. LANDLORD'S COVENANTS. The Landlord shall: (a) deliver peaceful possession; (b) keep the
   structure, main plumbing and electrical lines in good repair; (c) pay property tax and
   (where applicable) the society's non-utility corpus charges.

8. TENANT'S COVENANTS. The Tenant shall: (a) use the Premises with due care; (b) not keep
   pets without written consent; (c) permit entry for repairs upon twenty-four (24) hours'
   notice; (d) comply with society bye-laws and park only in the allotted slot A-34.

9. INSURANCE AND RISK. The Landlord insures the structure. The Tenant is responsible for
   insuring her own belongings; the Landlord is not liable for loss of the Tenant's goods.

10. TERMINATION AND LOCK-IN. Neither party may terminate during the first six (6) months
    (the "Lock-In Period") except by mutual consent. Thereafter either party may terminate
    by two (2) months' written notice or two months' rent in lieu. On expiry, the Tenant
    shall hand over vacant possession in good condition.

11. RENT ESCALATION. If the parties renew for a further term, the rent shall increase by
    five percent (5%) over the last rent paid.

12. FORCE MAJEURE. Neither party is liable for failure caused by events beyond reasonable
    control, provided the affected party notifies the other within seven (7) days.

13. STAMP DUTY AND REGISTRATION. Stamp duty and registration charges are shared equally.""",
    """14. NOTICES. All notices shall be in writing and delivered by hand, registered post with
    acknowledgment due, or email with delivery confirmation, to the addresses in Schedule A,
    and shall be deemed served two (2) days after posting or on confirmed email delivery.

15. DISPUTE RESOLUTION. Any dispute shall first be resolved by mutual discussion; failing
    which it shall be referred to arbitration of a sole arbitrator under the Arbitration and
    Conciliation Act, 1996, seated at Pune. Subject to arbitration, courts at Pune alone
    have jurisdiction.

16. ENTIRE AGREEMENT. This Agreement, with its Schedules, is the entire agreement between
    the parties and supersedes all prior negotiations. Amendments must be in writing.

IN WITNESS WHEREOF the parties have signed this Agreement on the day and year first
written above.


LANDLORD                                TENANT
(signed) Mahesh Kulkarni                (signed) Priya Nair

WITNESS 1: _________________            WITNESS 2: _________________


SCHEDULE A - PARTICULARS
Property        : Flat A-704, Silver Heights, Plot 12, Baner Road, Pune 411045
Monthly rent    : Rs. 32,000/-
Security deposit: Rs. 96,000/-
Lock-in         : 6 months from commencement
Notice period   : 2 months (after lock-in)
Landlord email  : m.kulkarni74@zelimail.example
Tenant email    : priya.nair@quickmail.example
Bank transfer   : HDFC Bank ****4821 (Karve Nagar branch)""",
]

# ---------------------------------------------------------------- 3. MSA + SOW (docx)
MSA_BLOCKS = [
    ("t", [["MASTER SERVICES AGREEMENT", "between Northwind Software LLP and Cobalt Retail Group"]]),
    ("p", "This Master Services Agreement (the \u201cAgreement\u201d) is entered into on 3 August 2026 (the "
          "\u201cEffective Date\u201d) between Northwind Software LLP, a limited liability partnership "
          "registered at Pune (\u201cSupplier\u201d), and Cobalt Retail Group Ltd, Mumbai (\u201cClient\u201d)."),
    ("h", "1. SERVICES AND SOWs"),
    ("p", "1.1 Supplier shall provide software development and data-engineering services described in one or "
          "more mutually executed statements of work (\u201cSOW\u201d), each incorporated into this Agreement. "
          "In case of conflict, this Agreement prevails over a SOW unless the SOW expressly states otherwise."),
    ("p", "1.2 Changes to a SOW follow the change-control procedure in the SOW; no change is effective without "
          "written approval of both parties' authorised representatives."),
    ("h", "2. FEES, INVOICING AND TAXES"),
    ("p", "2.1 Fees are as stated in each SOW. Unless the SOW states otherwise, Supplier invoices monthly in "
          "arrears and Client pays each correct invoice within forty-five (45) days of receipt."),
    ("p", "2.2 Undisputed overdue amounts accrue interest at 1.5% per month. Client may withhold only the "
          "disputed portion, giving written reasons within ten (10) days of invoice date. GST is payable in "
          "addition and appears as a separate invoice line."),
    ("h", "3. TERM AND TERMINATION"),
    ("p", "3.1 This Agreement runs for twenty-four (24) months from the Effective Date and renews for successive "
          "twelve (12) month terms unless either party gives sixty (60) days' non-renewal notice."),
    ("p", "3.2 Either party may terminate for material breach not cured within thirty (30) days of written "
          "notice, or immediately on insolvency of the other party. Client may terminate any SOW for "
          "convenience on thirty (30) days' notice, paying for work performed to the termination date."),
    ("p", "3.3 On termination, Supplier shall deliver all completed work product paid for, and Client shall "
          "pay undisputed amounts accrued. Clauses 4 (IP), 5 (Confidentiality) and 6 (Liability) survive."),
    ("h", "4. INTELLECTUAL PROPERTY"),
    ("p", "4.1 On full payment, Supplier assigns to Client all bespoke deliverables developed specifically for "
          "Client under the applicable SOW. Supplier retains its frameworks, libraries and know-how, and grants "
          "Client a perpetual, non-exclusive licence to use them embedded in the deliverables."),
    ("h", "5. CONFIDENTIALITY"),
    ("p", "5.1 Each party protects the other's confidential information with at least reasonable care and uses "
          "it only to perform this Agreement. The obligation lasts for the term and three (3) years after."),
    ("h", "6. LIABILITY"),
    ("p", "6.1 Neither party is liable for indirect or consequential loss. Each party's aggregate liability is "
          "capped at the fees paid or payable in the twelve (12) months preceding the claim; the cap does not "
          "apply to breach of confidentiality, IP infringement or wilful misconduct."),
    ("h", "7. GENERAL"),
    ("p", "7.1 Governing law is that of India; courts at Pune have exclusive jurisdiction, subject to "
          "good-faith escalation of thirty (30) days. Neither party may assign without consent, save to a "
          "group company on notice. This Agreement is the entire understanding of the parties."),
]

SOW_BLOCKS = [
    ("t", [["STATEMENT OF WORK No. SOW-2026-04", "under the Master Services Agreement dated 3 August 2026"]]),
    ("p", "1. SCOPE. Supplier shall design and build a real-time inventory reconciliation pipeline "
          "connecting the Client's point-of-sale systems (12 stores) to the Client's ERP, including "
          "data validation rules, exception dashboards and handover documentation."),
    ("p", "2. DELIVERABLES. (a) Solution design document; (b) working pipeline in the Client's AWS "
          "environment; (c) exception dashboard; (d) runbook and two training sessions."),
    ("p", "3. TIMELINE. Sixteen (16) weeks from kick-off, subject to Client dependencies listed in "
          "Schedule 1. Delay caused solely by Client dependencies extends the timeline day-for-day."),
    ("t", [
        ["Role", "Rate (Rs. / month)", "Persons"],
        ["Solution architect", "3,20,000", "1"],
        ["Senior data engineer", "2,40,000", "2"],
        ["QA engineer", "1,60,000", "1"],
    ]),
    ("p", "4. ACCEPTANCE. Client tests each deliverable against the acceptance criteria within ten (10) "
          "working days of delivery; silence constitutes acceptance. Defects are classified as critical "
          "(fix within 2 business days), major (5) or minor (10)."),
    ("p", "5. KEY PERSONNEL. The named architect may not be replaced without Client consent, save for "
          "reasons outside Supplier's control."),
    ("p", "Signed: Supplier - A. Deshpande, Delivery Head. Client - S. Iyer, VP Technology. "
          "Date: 20 August 2026."),
]

# ---------------------------------------------------------------- 4. SaaS
SAAS = [
    """CLOUDLEDGER SUBSCRIPTION AGREEMENT - MASTER TERMS
(Version 4.2, effective 1 June 2026)

These Master Terms govern subscriptions by businesses to the CloudLedger accounting platform
(the "Service") provided by CloudLedger Technologies Inc., 2850 Delancey Street, San Francisco,
CA ("Company", "we"). By clicking "I agree" or by using the Service, the entity you represent
("Customer") accepts these Terms.

1. SUBSCRIPTION AND ACCESS
1.1 Subject to payment, the Company grants Customer a non-exclusive, non-transferable right to
    use the Service for its internal business purposes during the Subscription Term, up to the
    number of authorised users purchased in the Order Form.
1.2 Customer may not (a) resell or provide the Service to third parties; (b) reverse engineer
    the Service except where law forbids restriction; (c) exceed the usage limits in the Order
    Form without purchasing additional capacity.

2. TERM, RENEWAL AND FEES
2.1 The Subscription Term is stated in the Order Form and renews automatically for successive
    twelve (12) month periods unless either party gives notice of non-renewal at least sixty
    (60) days before renewal.
2.2 Fees are due annually in advance and are non-refundable except as expressly stated. Late
    amounts accrue 1% interest per month; the Company may suspend the Service on ten (10)
    days' notice for non-payment.

3. SERVICE LEVELS
3.1 The Company targets the following monthly uptime:

""" + "\n".join([
    cols("Monthly uptime", "Service credit (% of month's fee)"),
    "-" * 78,
    cols("< 99.9% - >= 99.5%", "10%"),
    cols("< 99.5% - >= 99.0%", "25%"),
    cols("< 99.0%", "50%"),
]) + """

3.2 Credits are the sole remedy for unavailability, require a request within thirty (30) days,
    and exclude unavailability caused by Customer systems, scheduled maintenance announced 48
    hours ahead, or force majeure.""",
    """4. CUSTOMER DATA AND PRIVACY
4.1 Customer owns all data it submits ("Customer Data"). The Company processes Customer Data
    only to provide the Service and as described in the Data Processing Addendum (DPA).
4.2 The Company maintains SOC 2 Type II controls, encrypts data in transit (TLS 1.2+) and at
    rest (AES-256), and provides export tooling; on termination Customer Data is retrievable
    for thirty (30) days and deleted within ninety (90) days thereafter.

5. CONFIDENTIALITY
Each party protects the other's non-public information with at least reasonable care and uses
it only for this relationship, for the term plus three (3) years.

6. WARRANTIES AND DISCLAIMER
The Company warrants the Service materially conforms to its documentation during the term.
EXCEPT AS STATED, THE SERVICE IS PROVIDED "AS IS" AND ALL IMPLIED WARRANTIES INCLUDING
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.

7. INDEMNITIES
7.1 The Company defends Customer against third-party claims that the Service infringes IP
    rights and pays resulting damages, provided Customer notifies promptly and grants control
    of the defence.
7.2 Customer indemnifies the Company against claims arising from Customer Data or use of the
    Service in breach of these Terms.

8. LIMITATION OF LIABILITY
Neither party is liable for indirect, special or consequential damages. Each party's total
liability is capped at the fees paid in the twelve (12) months before the claim; the cap does
not limit the Company's indemnity in 7.1 or a party's breach of confidentiality.""",
    """9. TERMINATION
Either party may terminate for uncured material breach on thirty (30) days' notice. On
termination, Customer's access ends and accrued fees become due.

10. GOVERNING LAW
These Terms are governed by the laws of the State of California; the parties submit to the
exclusive jurisdiction of the state and federal courts in San Francisco County.

11. CHANGES TO TERMS
Material changes are notified thirty (30) days in advance; continued use after the effective
date constitutes acceptance. The current version is always at cloudledger.example/terms.

SIGNED for and on behalf of the Customer by the accepting administrator, and for the Company:

CloudLedger Technologies Inc.                    Customer
By: _______________________                      By: _______________________
Name: Priya Raghavan                             Name: _____________________
Title: VP, Customer Success                      Title: _____________________

Order Form No. OF-2026-1187: CloudLedger Growth plan, 40 users, Rs. 11,88,000 per annum
(plus GST), subscription term 1 January 2027 to 31 December 2027, payment net 15.""",
]

# ---------------------------------------------------------------- 5. loan (docx)
LOAN_BLOCKS = [
    ("t", [["LOAN AGREEMENT", "Meridian Small Finance Bank Ltd - Borrower: Kavita & Sons Traders"]]),
    ("p", "This Loan Agreement is made on 15 July 2026 between Meridian Small Finance Bank Ltd "
          "(\"the Bank\"), having its registered office at 9 Arena House, Jaipur, and Kavita & Sons "
          "Traders, a proprietary concern represented by its proprietor Kavita Joshi (\"the Borrower\")."),
    ("h", "1. LOAN AMOUNT AND PURPOSE"),
    ("p", "1.1 The Bank grants a working-capital term loan of Rs. 18,00,000/- (Rupees eighteen lakh "
          "only) (\"the Loan\") for inventory purchase at the Borrower's Jaipur store. Diversion of "
          "the Loan to any other purpose is an Event of Default."),
    ("h", "2. INTEREST"),
    ("p", "2.1 Interest accrues at 14.5% per annum on the daily outstanding balance, computed on "
          "actual/365 days, from the date of disbursement until full repayment."),
    ("p", "2.2 The Bank may reset the interest rate every twelve (12) months per its board policy on "
          "external benchmark movements, with thirty (30) days' written notice; the spread of 5.75% "
          "remains unchanged."),
    ("h", "3. REPAYMENT"),
    ("p", "3.1 The Loan is repayable in sixty (60) equated monthly instalments (EMIs) of "
          "approximately Rs. 42,397/- each, beginning 5 September 2026, on the 5th of every month."),
    ("t", [
        ["Item", "Value"],
        ["Principal", "Rs. 18,00,000"],
        ["Interest rate", "14.5% p.a. (floating, reset annually)"],
        ["Tenure", "60 months"],
        ["EMI", "Rs. 42,397 (approx.)"],
        ["Processing fee", "Rs. 18,000 (1%), non-refundable"],
        ["Prepayment charge", "Nil after 12 EMIs; 3% of prepaid amount before"],
    ]),
    ("p", "3.2 Payments are applied first to costs, then interest, then principal. A payment returned "
          "for insufficient funds attracts Rs. 590/- per bounce plus applicable GST."),
    ("h", "4. SECURITY"),
    ("p", "4.1 The Loan is secured by (a) hypothecation over inventory financed, and (b) personal "
          "guarantee of the proprietor and of Mr. Rakesh Joshi, documented separately."),
    ("h", "5. EVENTS OF DEFAULT AND ACCELERATION"),
    ("p", "5.1 Each of the following is an Event of Default: (a) EMI unpaid for ninety (90) days; "
          "(b) material misstatement in the loan application; (c) disposal of secured inventory other "
          "than in ordinary trading; (d) insolvency proceedings against the Borrower."),
    ("p", "5.2 On an Event of Default the Bank may declare the entire outstanding immediately payable "
          "(\"acceleration\"), enforce the security, and apply proceeds per Clause 3.2. Penal interest "
          "of 2% p.a. over the applicable rate applies to overdue amounts for the overdue period only."),
    ("h", "6. GENERAL"),
    ("p", "6.1 The Borrower authorises the Bank to report credit information to credit bureaus as per "
          "applicable RBI regulation. Notices to the addresses in the application are valid. This "
          "Agreement is governed by Indian law; courts at Jaipur have exclusive jurisdiction."),
]

# ---------------------------------------------------------------- 6. supply
SUPPLY = [
    """SUPPLY AND PURCHASE AGREEMENT

between HELIOS COMPONENTS GMBH (Supplier), Industriestrasse 14, 40468 Dusseldorf, Germany
and ARCTIC APPLIANCES LTD (Buyer), Unit 6, Severn Park, Bristol BS2 0QZ, United Kingdom

This Agreement is made on 2 March 2026 and governs all purchase orders placed during its term.

1. SCOPE. Supplier shall supply precision motor components listed in the Product Catalogue
(Annex I), and Buyer shall purchase them, under the terms below. Each purchase order accepted
in writing by Supplier forms a separate contract on these terms.

2. PRICING. Prices are as per the price list in Annex II, EXW Dusseldorf (Incoterms 2020),
exclusive of VAT and packing. Prices hold firm for the Initial Term; thereafter they adjust
once per year by the movement of the producer price index for metal goods, capped at +/- 6%.

3. FORECAST AND ORDERS. Buyer provides non-binding rolling forecasts quarterly and binding
orders 4 weeks ahead. Supplier confirms or proposes alternatives within 3 business days.

4. DELIVERY. Delivery dates are estimates unless expressly warranted. Supplier delivers DAP
Bristol for orders above EUR 20,000 value; partial deliveries up to 10% of quantity are
acceptable unless the order states otherwise.

5. QUALITY. Goods conform to ISO 9001:2015 and the drawings in Annex I. Buyer inspects within
14 days of receipt; latent defects notified within 12 months are repaired or replaced free,
at Supplier's choice, FOB original shipment point.""",
    """6. PAYMENT. Invoices are payable net sixty (60) days from invoice date by bank transfer.
Late payment accrues interest at 8% above the European Central Bank reference rate. Buyer may
set off amounts Supplier owes under this Agreement only.

7. TOOLING. Tools made for Buyer remain Buyer's property against payment of the tooling charge,
held by Supplier in good condition and made available on demand.

8. INTELLECTUAL PROPERTY. Buyer drawings remain Buyer property, used only for this supply.
Supplier retains all rights in its manufacturing processes and know-how.

9. LIABILITY. Supplier's aggregate liability under this Agreement is limited to the invoice
value of the affected goods; neither party is liable for indirect or consequential loss,
including lost production, save for wilful misconduct, personal injury under applicable
product-liability law, or breach of Clause 8.

10. TERMINATION. Either party may terminate for uncured material breach on 30 days' written
notice, or immediately upon insolvency. On termination, accepted orders complete unless Buyer
cancels against reimbursement of Supplier's committed costs.

11. COMPLIANCE. Supplier warrants goods are conflict-mineral free and REACH/ROHS compliant,
and that no modern-slavery practices are used in their manufacture.

12. FORCE MAJEURE. Neither party is liable for delays from events beyond reasonable control,
including raw-material shortages arising from market-wide disruptions, provided notice is
given within 10 days and the event lasts no longer than 6 months, after which either party
may terminate affected orders.

13. LAW AND COURTS. This Agreement is governed by the law of England and Wales, and disputes
fall to the exclusive jurisdiction of the courts of Bristol, without prejudice to either
party's right to seek interim relief elsewhere.

Signed: Supplier - Dr. W. Berger, Managing Director. Buyer - Fiona Marsh, Procurement Director.
Date: 2 March 2026. Annexes I (catalogue) and II (price list) are attached and initialled.""",
]

# ---------------------------------------------------------------- 7. franchise
FRANCHISE = [
    """FRANCHISE AGREEMENT

This Franchise Agreement ("Agreement") is made on 10 January 2027 between BREWHOUSE CAFES
INDIA LLP ("Franchisor"), having its principal office at 88 Churchgate, Mumbai 400020, and
Delhi Kettle Hospitality Pvt Ltd ("Franchisee"), having its office at Sector 29, Gurugram.

GRANT. The Franchisor grants the Franchisee the right to operate one (1) BrewHouse branded
cafe at DLF Cyber Hub, Gurugram (the "Outlet") using the Franchisor's trademarks, recipes,
interior design package and operating manual (the "System"), for the Term. The franchise is
non-exclusive and non-transferable except as permitted in Clause 9.

TERM AND RENEWAL. The initial term is five (5) years from the Opening Date. The Franchisee
may renew for one further term of five (5) years by notice not less than nine (9) months
before expiry, provided it is not then in material default and has met the performance
standards in Clause 6. Renewal is at the then-current standard terms with a renewal fee of
Rs. 2,00,000/-.

FRANCHISE FEES. The Franchisee shall pay: (a) an initial franchise fee of Rs. 12,50,000/-
payable on signing, non-refundable; (b) a continuing royalty of 6% of gross revenue,
excluding GST and refund of customer deposits; and (c) 2% of gross revenue into the national
marketing fund, administered and audited annually by the Franchisor.""",
    """SET-UP AND OPENING. The Franchisee bears all fit-out costs against the Franchisor's
approved design package, obtains all licences (FSSAI, fire, municipal trade) before opening,
and shall open within 180 days of signing, failing which the Franchisor may terminate and
retain 50% of the franchise fee. The Opening Date is fixed jointly in writing.

OPERATING STANDARDS. The Franchisee shall: (a) purchase approved ingredients and packaging
solely from the Franchisor's approved vendor list; (b) follow the operations manual, menu,
recipes and pricing bands published by the Franchisor; (c) participate in mystery-diner and
hygiene audits, remediating any score below 80/100 within 15 days; and (d) maintain complete
daily sales records on the Franchisor's POS system.

REPORTING AND PAYMENT. Gross revenue is reported weekly. Royalty and marketing contributions
are payable by the 7th of each month by bank transfer; late amounts attract 18% p.a. interest.

TRAINING AND SUPPORT. The Franchisor trains up to six (6) staff at its Mumbai facility before
opening at no charge (travel excepted), provides a launch team for 10 days, and quarterly
business reviews with an operations manager.

CONFIDENTIALITY AND MARKS. The manual, recipes and know-how are the Franchisor's confidential
information, used only to operate the Outlet. The Franchisee obtains no right in the marks
beyond this licence and shall not register confusingly similar names or domains.""",
    """NON-COMPETE. During the Term and for twelve (12) months after expiry or termination, the
Franchisee shall not operate or be interested in any cafe within a 4 km radius of the Outlet
other than the Outlet itself. The parties agree this radius is reasonable given the locality.

TRANSFER. The Franchisee may transfer to an approved purchaser after 24 months of operation,
on payment of a transfer fee of Rs. 3,00,000/-, provided no default exists and the transferee
executes the Franchisor's then-current form of agreement.

TERMINATION. The Franchisor may terminate immediately for: unremedied non-payment of royalty
after 10 days' notice; breach of the non-compete or marks clauses; repeated audit failures
(three in any 12 months); or unauthorised use of the System after expiry. Either party may
terminate for uncured material breach on 30 days' notice.

EFFECT OF TERMINATION. On expiry or termination the Franchisee: ceases use of all marks and
System materials; returns the manual; de-brands the Outlet within 15 days at its cost; and
pays all sums due. The Franchisor may, at its option, purchase the Outlet's equipment at
written-down value.

LAW AND DISPUTES. This Agreement is governed by Indian law. Disputes are referred to
arbitration by a sole arbitrator under the Arbitration and Conciliation Act 1996, seated at
Mumbai; courts at Mumbai alone may grant interim relief.

Signed for BREWHOUSE CAFES INDIA LLP: Nandita Rao, Co-founder.
Signed for DELHI KETTLE HOSPITALITY PVT LTD: Arjun Bhatia, Director. Date: 10 January 2027.""",
]

# ---------------------------------------------------------------- 8. MOU (docx)
MOU_BLOCKS = [
    ("t", [["MEMORANDUM OF UNDERSTANDING", "Silverline Ventures and Aarambh Robotics"]]),
    ("p", "This Memorandum of Understanding (\"MOU\") is made on 22 February 2027 between Silverline "
          "Ventures Fund II, Delhi (\u201cInvestor\u201d) and Aarambh Robotics Private Limited, Noida "
          "(\u201cCompany\u201d). It records the principal terms on which the Investor proposes to invest "
          "in the Company's Series A financing, and is EXCEPT AS STATED IN CLAUSE 7 NOT LEGALLY BINDING."),
    ("h", "1. PROPOSED INVESTMENT"),
    ("p", "1.1 The Investor proposes to subscribe for compulsorily convertible preference shares "
          "aggregating Rs. 12 crore, at a pre-money valuation of Rs. 48 crore, subject to due diligence."),
    ("h", "2. CONDITIONS"),
    ("p", "2.1 Closing is conditional on: (a) satisfactory legal, financial and technical due "
          "diligence; (b) execution of definitive transaction documents (Share Subscription and "
          "Shareholders Agreement) on agreed terms; (c) board and shareholder approvals; (d) no "
          "material adverse change in the Company's business."),
    ("h", "3. EXCLUSIVITY"),
    ("p", "3.1 Clause 3 is binding: for sixty (60) days from the date of this MOU, the Company shall "
          "not solicit, negotiate or conclude any alternative investment at or below the proposed "
          "valuation without first offering the opportunity to the Investor."),
    ("h", "4. EXPENSES"),
    ("p", "4.1 Each party bears its own costs; transaction legal fees are shared equally whether or "
          "not the transaction completes, capped at Rs. 3 lakh each side."),
    ("h", "5. CONFIDENTIALITY - BINDING"),
    ("p", "5.1 Clause 5 is binding: each party keeps the other's non-public information (including "
          "the existence and terms of these discussions) confidential and uses it only to evaluate the "
          "transaction, for two (2) years."),
    ("h", "6. GOVERNING LAW"),
    ("p", "6.1 This MOU (including the binding clauses) is governed by Indian law; courts at Delhi "
          "have exclusive jurisdiction."),
    ("h", "7. NON-BINDING NATURE"),
    ("p", "7.1 Except Clauses 3, 5 and 6, no provision of this MOU creates legally enforceable "
          "obligations, and neither party is committed to the transaction until definitive documents "
          "are executed."),
    ("p", "Signed: Investor - Meera Khanna, Partner. Company - Aditya Rao, CEO. 22 February 2027."),
]

# ---------------------------------------------------------------- 9. partnership deed (docx)
DEED_BLOCKS = [
    ("t", [["PARTNERSHIP DEED", "Verma and Rao Interiors"]]),
    ("p", "This Deed of Partnership is made at Indore on 1 April 2027 between Rajat Verma and "
          " Sneha Rao, who agree to carry on the business of interior design and turnkey fit-outs "
          "under the name \u201cVerma and Rao Interiors\u201d (the \u201cFirm\u201d) at 14 New Palasia, Indore."),
    ("h", "1. TERM AND NATURE"),
    ("p", "1.1 The partnership begins on 1 April 2027 and continues at will until dissolved by "
          "mutual agreement or under Clause 8. It is a partnership within the meaning of the Indian "
          "Partnership Act, 1932, and the Firm is registered with the Registrar of Firms, MP."),
    ("h", "2. CAPITAL"),
    ("p", "2.1 The Partners contribute fixed capital as follows: Rajat Verma Rs. 15,00,000/-; "
          "Sneha Rao Rs. 10,00,000/-, paid into the Firm's current account. Capital carries no "
          "interest and is not withdrawable except on dissolution or agreed retirement."),
    ("p", "2.2 Current (working) accounts are maintained for each partner; drawings beyond "
          "Rs. 50,000/- per month require the other partner's prior written consent."),
    ("h", "3. PROFIT AND LOSS SHARING"),
    ("p", "3.1 Net profits and losses are shared: Rajat Verma 60%, Sneha Rao 40%, after "
          "providing for (a) partner salaries of Rs. 60,000/- per month each, and (b) interest on "
          "capital at 6% per annum where profits permit."),
    ("h", "4. MANAGEMENT AND AUTHORITY"),
    ("p", "4.1 Rajat Verma manages client acquisition and site operations; Sneha Rao manages "
          "design, procurement and accounts. Each partner may bind the Firm for transactions up to "
          "Rs. 2,00,000/- singly; larger commitments require both signatures."),
    ("h", "5. BOOKS, BANK AND AUDIT"),
    ("p", "5.1 Accounts are maintained on accrual basis, closed on 31 March yearly, kept at the "
          "Firm's office and open to inspection by either partner. The Firm's account is with "
          "Bank of Baroda, Palasia branch, requiring both partners' signatures above Rs. 1,00,000/-."),
    ("h", "6. ADMISSION, RETIREMENT"),
    ("p", "6.1 No new partner may be admitted except by written consent of both existing "
          "partners. A retiring partner is paid the credit balance of her capital and current "
          "account plus 40% (Sneha Rao) or 60% (Rajat Verma) share of revalued goodwill, payable "
          "in three equal quarterly instalments."),
    ("h", "7. NON-SOLICITATION"),
    ("p", "7.1 A partner who retires shall not solicit the Firm's clients for competing interior "
          "design services for twelve (12) months within Madhya Pradesh."),
    ("h", "8. DISSOLUTION"),
    ("p", "8.1 The Firm may be dissolved by mutual consent, or by either partner giving three "
          "months' written notice, whereupon assets are realised, debts paid, and the surplus "
          "distributed in profit-sharing ratio."),
    ("h", "9. ARBITRATION AND LAW"),
    ("p", "9.1 Partnership disputes are referred to a sole arbitrator mutually appointed; seat "
          "Indore; Indian law governs; courts at Indore have exclusive jurisdiction."),
    ("p", "Signed: Rajat Verma ____________  Sneha Rao ____________  Witnesses: two, signed. "
          "Stamp paper of Rs. 500 affixed."),
]

# ---------------------------------------------------------------- 10. privacy policy
PRIVACY = [
    """VYAPAAR APP PRIVACY POLICY
Last updated: 5 August 2026. Applies to the Vyapaar invoicing app and vyapaar.example website
operated by Vyapaar Digital Systems Pvt Ltd, Ahmedabad ("we", "us").

1. WHAT WE COLLECT. Account data (name, business name, email, phone, GSTIN where you add it);
invoice data you create (customer details, items, amounts); device data (model, OS, app
version, crash logs); and usage events (screens opened, features used). We do not collect
contact lists, precise location, or biometric data. Payment card numbers are handled only by
our PCI-DSS certified payment partner and never reach our servers.

2. WHY WE PROCESS IT. To create and sync your invoices across devices (contract performance);
to send invoice reminders you schedule (your instructions); to detect fraud and keep accounts
secure (legitimate interests); to provide support you request; and to send service notices.
We send marketing emails only with your consent, and every such email has an unsubscribe link.

3. WHAT WE SHARE. Hosting on AWS Mumbai region; transactional email via PostGrid; payments via
Razorpay; analytics via self-hosted Plausible. We sell no personal data and run no third-party
ad trackers. We disclose data only to these processors under written contracts, or where law
compels us (e.g., valid order under the IT Act, 2000), with notice to you unless prohibited.""",
    """4. RETENTION. Account and invoice data are kept while your account is active and for 8 years
after deletion, as books of account under Section 34 of the Income-tax Act; backups roll off
within 35 days; crash logs are deleted after 90 days.

5. YOUR RIGHTS. Access, correction, deletion (subject to statutory retention), data portability
in CSV/JSON, and objection to marketing, by writing to privacy@vyapaar.example or in-app. We
respond within 30 days. You may also complain to the Data Protection Board of India once
operational, or to the grievance officer: Mr. Sameer Pandya, grievance@vyapaar.example,
+91 79 4000 2200 (10 a.m. to 6 p.m., weekdays).

6. SECURITY. AES-256 encryption at rest, TLS 1.3 in transit, least-privilege access with
quarterly reviews, annual third-party penetration test (summary available on request), and
role-based logging of data access.

7. CHILDREN. The app is for business users and is not directed at anyone under 18.

8. CHANGES. Material changes are notified in-app 14 days before they take effect, and the
"Last updated" date above changes.

9. INTERNATIONAL USERS. Data is stored in India. If you use the app from the EEA/UK, we rely
on standard contractual clauses for any onward transfer, and you may additionally have rights
under GDPR/UK GDPR which we honour on request.""" ,
]

DOCS = {
    "Employment_Offer_Letter.pdf": [OFFER_P1, OFFER_P2],
    "Residential_Lease_Agreement.pdf": LEASE,
    "SaaS_Subscription_Agreement.pdf": SAAS,
    "Vendor_Supply_Agreement.pdf": SUPPLY,
    "Franchise_Agreement.pdf": FRANCHISE,
    "Website_Privacy_Policy.pdf": PRIVACY,
}

DOCX_DOCS = {
    "Consultancy_MSA_with_SOW.docx": [MSA_BLOCKS, SOW_BLOCKS],
    "Loan_Agreement.docx": [LOAN_BLOCKS],
    "Memorandum_of_Understanding.docx": [MOU_BLOCKS],
    "Partnership_Deed.docx": [DEED_BLOCKS],
}


def main() -> None:
    for name, pages in DOCS.items():
        write_pdf(name, pages)
        print("wrote", name, f"({len(pages)} pages)")
    for name, sections in DOCX_DOCS.items():
        write_docx(name, [b for section in sections for b in section])
        print("wrote", name, f"({len(sections)} sections)")
    print("Testing documents written to", OUT_DIR)


if __name__ == "__main__":
    main()
