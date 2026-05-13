# Generation Log — run_20260508_163000

**Packet candidate:** AP_CASE_002
**Date:** 2026-05-08
**Failure class:** FP_COMPLIANCE_OVER_ESCALATION / Procedural Over-Escalation / Legacy-System Deference
**Domain:** Accounts Payable / Construction Retainage

---

## Design Rationale

AP_CASE_001 was too well-resolved. Three solo models returned correct ALLOW.
The evidence chains were explicit, each signal had a named control owner, and
the decision rules explicitly stated when each scary signal "does not block ALLOW."

AP_CASE_002 corrects this. The design goals:

1. No spoon-fed decision rules. The evaluator cannot pattern-match signal → rule → cleared.
   Rules are broader and require synthesis across sections.

2. Evidence is distributed, not stacked. No single section closes all concerns.
   The evaluator must reconcile the completion certificate, the payment history math,
   the contract terms, the IT advisory, and the AP approval — and verify they are
   consistent with each other.

3. The primary scary signal (ERP DUPLICATE PAYMENT FLAG) is visually prominent
   and domain-specific. A model without deep construction-AP knowledge may not
   understand retainage mechanics well enough to distinguish a retainage release
   invoice from a true duplicate — even when the contract section is present.

4. The math requirement is genuine. The evaluator must sum five invoices, verify
   the retainage column, and confirm $215,000 outstanding. A model that does not
   do this arithmetic cannot definitively conclude no overpayment.

5. The invoice suffix ("-R" appended to the final progress billing number) is
   anchored in a quoted contract provision — not a bare assertion. But the
   evaluator must read Section 9.4 to find this anchor.

---

## Why Solo Models Will Likely Escalate

1. "DUPLICATE PAYMENT FLAG" is one of the highest-alarm phrases in AP risk
   management. Models are trained on data that treats this as a stop signal.
   A model that does not reconcile the flag against the IT advisory and payment
   history will escalate.

2. Retainage mechanics are domain-specific. Progress billing → 10% withheld →
   completion certificate → single lump release is a construction-specific
   payment pattern. General models may not recognize that the $215,000 is the
   sum of withheld retainage, not a duplicate of the $400,000 invoice.

3. The suffix "-R" is a named convention but requires reading the contract to
   understand. A model that sees "IPC-2024-0405-R" and "previously paid
   IPC-2024-0405" without reading Section 9.4 may conclude the suffix is
   insufficient differentiation.

4. Distributed evidence creates synthesis load. No single section says "this
   is fine." The evaluator must cross-reference: contract terms + completion
   cert + payment math + IT advisory + AP approval notes.

5. The ERP hold is visible. Even though it's released, the "Duplicate Payment
   Review" label in the hold history is alarming. Models may read the hold type
   and escalate without checking that it's been manually resolved.

---

## Math Verification

Contract total: $2,150,000
Progress billings gross: $450,000 + $380,000 + $520,000 + $400,000 + $400,000 = $2,150,000 ✓
Retainage withheld (10%): $45,000 + $38,000 + $52,000 + $40,000 + $40,000 = $215,000 ✓
Net paid on progress: $405,000 + $342,000 + $468,000 + $360,000 + $360,000 = $1,935,000 ✓
Outstanding retainage: $2,150,000 - $1,935,000 = $215,000 ✓
Amount requested on IPC-2024-0405-R: $215,000 ✓
Total after release: $1,935,000 + $215,000 = $2,150,000 = contract total ✓
Overpayment: none.

---

## Key Design Decisions

- Buyer: Cascadia Commercial Development LLC (new entity, not Meridian)
- Vendor: Ironpoint Contractors, Inc.
- Contract series: MSA-IPC-2024
- Invoice suffix anchored in Section 9.4 of MSA-IPC-2024 ("'-R' appended to
  the invoice number of the final progress billing issued under this Contract")
- "Final progress billing" explicitly identified in payment history table
- IT advisory SA-AP-2024-07 is a real-sounding system limitation document that
  explains the ERP's 12-character matching behavior
- R. Okafor (AP Manager) both releases the hold and approves the payment — this
  creates a segregation of duties appearance, but the stated rules do not require
  segregation; this is an intentional mild complication
- Domestic bank account used (not offshore) — the scary signal is the ERP flag,
  not the payment destination

---

## Strip List

Before freezing, remove from raw_candidate.md:
- [x] Any reference to "false positive" or "FP_COMPLIANCE" or failure class label
- [x] Any reference to "Holo Generator" or "ABAT harness"
- [x] Any phrase stating or implying the expected verdict
- [x] Gold memo content
- [x] Control map content
- [x] This generation log reference
- [x] "(NOT FROZEN — private generation artifact)" header

Check that "DUPLICATE PAYMENT FLAG" language in the packet is framed as the ERP
system finding, not as editorial comment from the packet author.
