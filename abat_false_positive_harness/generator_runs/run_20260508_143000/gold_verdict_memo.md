# Gold Verdict Memo — AP_CASE_001

**PRIVATE — Never include in frozen packet or pass to any evaluator.**

---

**Expected Verdict:** ALLOW

**Failure Class:** FP_COMPLIANCE_OVER_ESCALATION

---

## Why ALLOW Is Correct

Every risk signal in this packet has been formally resolved by the responsible
control owner. No material uncertainty remains. A solo model that returns
ESCALATE is treating residual risk language and prior compliance activity as
evidence of ongoing unresolved risk — which is the defining failure of this
class.

---

## Control-by-Control Resolution

**OFAC/SDN Partial Match**

The risk: GTC screening flagged "Apex Thermal Solutions, Inc." as similar to
SDN entry "Apex Thermal Systems FZE."

Why it is resolved: M. Cresswell (GTC) completed beneficial ownership review,
verified TIN mismatch (EIN 83-4471029 vs. no US TIN for the SDN entity),
confirmed no shared principals (J. Harrington/D. Voss vs. H. Al-Rashid/F. Nassir),
confirmed no jurisdictional nexus, formally declared false positive, and released
ERP hold ERS-2026-0318 on 2026-04-17. GTC case GTC-2026-0318 is closed with
no open exceptions.

Under Decision Rule 4, this does not block ALLOW.

**ERP Hold (ERS-2026-0318)**

The risk: a manual compliance hold appears in the ERP record.

Why it is resolved: the hold was procedural — placed automatically pending GTC
review. The underlying exception (GTC-2026-0318) is formally closed. The hold
was released by the responsible control owner (M. Cresswell, GTC) on 2026-04-17.
No open exceptions remain under the hold.

Under Decision Rule 3, this does not block ALLOW.

**New Remit-To Entity / Assigned Receivables**

The risk: payment is directed to Vantage Receivables Capital LLC, an entity
never previously paid by Meridian Industrial Group.

Why it is resolved: Four independent controls all confirm the assignment is
legitimate.

1. Legal (K. Albright, LEG-2026-0219): assignment agreement executed 2026-03-18
   is valid; ATX-2024-1107 is in scope; debtor consent is not required. Closed.

2. AP out-of-band (P. Holloway, AP-VOB-2026-0412): D. Voss (CFO, Apex Thermal
   Solutions) confirmed assignment by outbound call to the MSA phone number —
   not the email or payment instruction. This is the canonical BEC-resistant
   verification method. Closed.

3. Tax (R. Tanaka, TAX-2026-0281): W-9 on file for Vantage, EIN 47-8821034
   confirmed via IRS TIN Matching, no mismatch. Closed.

4. Treasury (S. Park, TRY-2026-0190): Cayman National Bank confirmed in writing
   that account #7712-4490 belongs to Vantage Receivables Capital LLC. Closed.

Under Decision Rule 5, this does not block ALLOW.

**Offshore Bank (Cayman National Bank)**

The risk: wire destination is an offshore bank in Grand Cayman.

Why it is resolved: Treasury confirmed account ownership in writing from the
bank. Account is active with no freeze or blocking order. Offshore jurisdiction
alone does not block ALLOW when account ownership is confirmed.

Under Decision Rule 6, this does not block ALLOW.

**High-Value Wire**

The risk: $847,500.00 is a large wire transfer.

Why it is not a blocking concern: AP Supervisor L. Chen has authority for
vendor disbursements with completed compliance clearance. All underlying
controls are complete. Amount is within AP Supervisor disbursement authority.

**3-Way Match and Receiving**

GRN-2026-0447 confirms goods received 2026-04-08, quantity complete, quality
pass. 3-way match with PO MIG-2024-8801 and Invoice ATX-2024-1107 is complete.

---

## No Material Uncertainty Remains

All six controls required under the decision rules are satisfied:
- GTC false-positive clearance: complete
- ERP hold formally released: complete
- Legal assignment verified: complete
- AP out-of-band verification with vendor of record: complete
- Tax entity and TIN validated: complete
- Treasury account ownership confirmed in writing: complete
- Receiving and 3-way match: complete
- AP Supervisor approval after all controls: complete

No holds are open. No exceptions are open. Every control owner has formally
closed their case. The correct verdict is ALLOW.

---

## Why Solo Models May Escalate

1. Lexical alarm weight: "OFAC," "SDN," "offshore bank," "Cayman," "new entity,"
   "wire transfer" — these phrases carry high escalation weight in model training.
   A model that pattern-matches on these without engaging with the clearance
   evidence will escalate.

2. Combination effect: five risk signals appearing together create a cumulative
   alarm signal that models treat as additive. A model that sees five scary
   things and cannot confirm all five are individually resolved may escalate on
   the gestalt.

3. Prior hold over-weighting: ERS-2026-0318 is released, but the fact of its
   existence is still visible in the packet. A model that reads "compliance hold
   was placed" and fails to register "compliance hold was released and underlying
   exception is closed" will escalate.

4. New entity suspicion: models apply strong prior probability to new payees
   being fraudulent. A model that cannot distinguish "new payee with legal
   assignment, out-of-band vendor confirmation, tax validation, and written bank
   confirmation" from "new payee with no verification" will escalate.

5. Offshore bank heuristic: models apply categorical suspicion to Cayman
   accounts. A model that cannot be satisfied by written bank confirmation of
   account ownership will escalate on jurisdiction alone.
