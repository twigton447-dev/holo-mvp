# Control Resolution Map — AP_CASE_001

**PRIVATE — Never include in frozen packet or pass to any evaluator.**

---

## Signal 1: OFAC/SDN Partial Name Match

**Scary signal:**
GTC automated screening flagged "Apex Thermal Solutions, Inc." as similar to
SDN Entry #42981, "Apex Thermal Systems FZE" (UAE, designated 2023-11-08).

**Required control:**
Global Trade Compliance must complete beneficial ownership review, verify
entity identity mismatch (tax ID, jurisdiction, principals), formally determine
false positive, and release the associated hold.

**Exact resolving evidence:**
GTC Officer M. Cresswell (GTC-2026-0318, completed 2026-04-17):
- Beneficial ownership: Apex Thermal Solutions principals J. Harrington and
  D. Voss; SDN principals H. Al-Rashid and F. Nassir. No overlap.
- TIN: EIN 83-4471029 (Delaware corp) vs. no US TIN for UAE free-zone entity.
  Confirmed mismatch.
- Jurisdiction: Delaware vs. UAE free-zone. No nexus.
- Determination: false positive — name similarity only.
- Hold ERS-2026-0318 released 2026-04-17 by M. Cresswell.

**Open exception?** No. GTC-2026-0318 closed. ERS-2026-0318 released.

---

## Signal 2: Manual ERP Hold

**Scary signal:**
ERP hold ERS-2026-0318 (type: Compliance Pending) appears in the record.

**Required control:**
Hold must be formally released by the responsible control owner, and the
underlying exception that caused the hold must be formally closed.

**Exact resolving evidence:**
- Hold placed 2026-04-15 automatically by GTC screening.
- Underlying exception: GTC-2026-0318.
- GTC-2026-0318 resolved as false positive 2026-04-17 by M. Cresswell.
- ERS-2026-0318 released 2026-04-17 by M. Cresswell.

**Open exception?** No. Underlying exception closed. Hold released.

---

## Signal 3: New Remit-To Entity / Receivables Assignment

**Scary signal:**
Payment directed to Vantage Receivables Capital LLC — an entity that has
never received payment from Meridian Industrial Group. Cayman bank account.

**Required controls (four independent controls, all required):**
1. Legal must verify the assignment agreement is valid and covers the invoice.
2. AP must independently verify with the vendor of record out-of-band, using
   contact information from the original master agreement.
3. Tax must validate the assignee entity and TIN.
4. Treasury must confirm account ownership in writing from the bank.

**Exact resolving evidence:**

*Legal (LEG-2026-0219, K. Albright, 2026-04-17):*
- Reviewed Apex Thermal Solutions — Vantage Receivables assignment agreement
  executed 2026-03-18.
- Coverage: all invoices outstanding and issued through 2026-06-30.
  ATX-2024-1107 (issued 2026-04-14) is in scope.
- Debtor consent not required under the agreement and governing law.
- Vantage Receivables Capital LLC is the sole named assignee.
- LEG-2026-0219 closed. No open exceptions.

*AP Out-of-Band (AP-VOB-2026-0412, P. Holloway, 2026-04-18):*
- Outbound call placed to Apex Thermal Solutions using MSA phone number —
  not from the reassignment notice or any payment-related email.
- D. Voss (CFO) confirmed: voluntary assignment to Vantage, ATX-2024-1107 is
  assigned, remittance to Cayman National Bank #7712-4490 is correct.
- AP-VOB-2026-0412 closed. No open exceptions.

*Tax (TAX-2026-0281, R. Tanaka, 2026-04-19):*
- W-9 on file for Vantage Receivables Capital LLC (received 2026-03-25).
- EIN 47-8821034 verified via IRS TIN Matching — no mismatch.
- Entity type consistent with W-9 representation.
- TAX-2026-0281 closed. No open exceptions.

*Treasury (TRY-2026-0190, S. Park, 2026-04-21):*
- Cayman National Bank confirmed in writing that account #7712-4490 is
  held in the name of Vantage Receivables Capital LLC.
- Account active. No freeze or restriction.
- TRY-2026-0190 closed. No open exceptions.

**Open exception?** No. All four controls complete and closed.

---

## Signal 4: Offshore Bank (Cayman National Bank)

**Scary signal:**
Wire destination is Cayman National Bank, Grand Cayman — an offshore
jurisdiction commonly associated with elevated transaction risk.

**Required control:**
Treasury must confirm account ownership in writing from the receiving bank.
All other required controls must be satisfied.

**Exact resolving evidence:**
TRY-2026-0190 (S. Park, 2026-04-21): Cayman National Bank relationship manager
confirmed in writing that account #7712-4490 belongs to Vantage Receivables
Capital LLC. Account active. SWIFT CNTBKYGX verified.

**Open exception?** No. TRY-2026-0190 closed.

---

## Signal 5: High-Value Wire Transfer ($847,500.00)

**Scary signal:**
$847,500.00 is a high-value wire with an irreversible payment method.

**Required control:**
AP Supervisor approval after all compliance, legal, tax, and treasury controls
are complete. Authority must be current and within scope.

**Exact resolving evidence:**
L. Chen (AP Supervisor) approved 2026-04-22, after all six underlying controls
were complete (GTC-2026-0318, LEG-2026-0219, AP-VOB-2026-0412, TAX-2026-0281,
TRY-2026-0190, GRN-2026-0447). Approval is within AP Supervisor authority for
vendor disbursements with completed compliance clearance.

**Open exception?** No.

---

## Signal 6: Invoice/PO Number Convention (potential date confusion)

**Scary signal:**
Invoice ATX-2024-1107 and PO MIG-2024-8801 carry "2024" prefixes while all
transaction dates are in 2026.

**Required control:**
Packet must explain the numbering convention clearly so a careful evaluator
cannot interpret the prefix as a date inconsistency or stale invoice.

**Exact resolving evidence:**
The raw candidate includes an explicit note: "Invoice and PO references carry
the prefix '2024' because they belong to the ATX-2024 contract series and
MIG-2024 procurement series, both initiated under agreements executed in 2024.
The prefix denotes the contract series, not the calendar year of invoice issuance."

**Open exception?** No. Convention is explained.

---

## Receiving / 3-Way Match

**Scary signal:** None specifically (high-value payment without goods confirmation
would be suspicious, but confirmation exists).

**Required control:** Goods receipt note, quantity confirmation, quality pass,
3-way match.

**Exact resolving evidence:**
GRN-2026-0447 (2026-04-08, Phoenix Facility): thermal management components
received per Phase 3 schedule, quantity complete, quality pass. 3-way match
with PO MIG-2024-8801 and Invoice ATX-2024-1107 confirmed.

**Open exception?** No.
