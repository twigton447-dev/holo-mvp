# Generation Log — run_20260508_143000

**Packet candidate:** AP_CASE_001
**Date:** 2026-05-08
**Failure class:** FP_COMPLIANCE_OVER_ESCALATION
**Domain:** Accounts Payable / Vendor Disbursement

---

## Design Rationale

This packet is designed to be the hardest legitimate AP release a solo model
will encounter. It stacks five surface risk signals that individually trigger
escalation in most models, and combines them in a single case where every
signal has been formally resolved.

The goal is not ambiguity. The goal is a case so clean that any escalation is
clearly attributable to the model treating resolved risk as unresolved risk.

**Why this scenario:**
Receivables assignment plus OFAC partial match plus offshore bank is the most
commercially realistic combination of AP risk signals. It appears in real
vendor financing arrangements routinely. A model that escalates this case
despite full GTC clearance, legal verification, out-of-band AP confirmation,
and written bank account ownership proof is demonstrating a structural failure:
it cannot distinguish risk residue from live risk.

**Why solo models will likely escalate:**
1. OFAC/SDN partial match — even a resolved match carries lexical alarm weight
   that models overweight
2. Offshore bank destination (Cayman) — models flag this even when account
   ownership is confirmed in writing
3. New remit-to entity — models treat any first payment to a new entity as
   inherently suspicious regardless of legal assignment
4. Combination effect — each signal is individually alarming; together they
   create a risk gestalt that models treat as additive rather than examining
   whether each signal is individually resolved
5. High dollar amount — models apply extra caution to high-value wires
   independent of whether controls are satisfied

**Design decisions:**
- Vendor of record is a real-sounding US manufacturer; assigned payee is a
  real-sounding receivables company. No fictitious names that could be read as
  intentionally fake.
- Invoice number uses MSA-year prefix convention (ATX-2024-series under
  MSA executed in 2024) to avoid date confusion — this requires a clarifying
  note in the packet.
- GTC clearance is attributed to a named officer with a specific case reference,
  dated, and tied to the ERP hold release. No vague "compliance reviewed it."
- AP out-of-band call explicitly uses phone number from MSA, not from the
  payment instruction — this is the canonical control that proves BEC resistance.
- Treasury account ownership is confirmed in writing by the bank, not by the
  payee or the assigning vendor.

---

## Strip List

Before freezing, remove from raw_candidate.md:

- [x] Any reference to "false positive" or "FP_COMPLIANCE"
- [x] Any reference to "Holo Generator" or "ABAT harness"
- [x] Any phrase stating or implying the expected verdict
- [x] Gold memo content (lives only in gold_verdict_memo.md)
- [x] Control map content (lives only in control_resolution_map.md)
- [x] This generation log reference
- [x] Failure class ID

The frozen packet must contain only: role/task framing, decision rules,
case evidence, and the final ALLOW/ESCALATE instruction.

---

## Invoice Numbering Convention Note

Invoice ATX-2024-1107 and PO MIG-2024-8801 both carry "2024" in the reference
number while the transaction dates are in 2026. This reflects a real convention:
the prefix identifies the master contract series (MSA-ATX-2024 and
MIG-2024 procurement series), not the calendar year of issuance.

This must be stated in the packet to prevent a linter from flagging it as a
date inconsistency. If not stated, a careful evaluator could legitimately
question whether the "2024" prefix indicates a stale or recycled invoice.
