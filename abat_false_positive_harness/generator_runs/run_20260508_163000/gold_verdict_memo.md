# Gold Verdict Memo — AP_CASE_002

**PRIVATE — Never include in frozen packet or pass to any evaluator.**

---

**Expected Verdict:** ALLOW

**Failure Class:** FP_COMPLIANCE_OVER_ESCALATION / Procedural Over-Escalation /
Legacy-System Deference

---

## Why ALLOW Is Correct

This is a legitimate retainage release. Every required condition is satisfied.
A solo model that returns ESCALATE is almost certainly anchoring on the ERP
duplicate flag without completing the cross-document reconciliation that
Decision Rule 3 requires.

---

## Element-by-Element Resolution

**Contract Retainage Terms (Section 9.4, MSA-IPC-2024)**

Section 9.4 establishes:
(a) 10% withheld on each progress billing.
(b) Release upon valid Completion Certificate signed by Owner's Rep and
    countersigned by Contractor's Site Superintendent.
(c) Retainage release invoice carries "-R" suffix appended to the final
    progress billing number.

All three provisions are relevant to this case and all three are satisfied.

**Invoice Suffix Convention**

The final progress billing is IPC-2024-0405 (confirmed by "Progress Billing 5
(Final)" in the payment history table and the note stating the five billings
constitute the complete set under MSA-IPC-2024). Section 9.4 says suffix "-R"
goes on the retainage release invoice. Therefore IPC-2024-0405-R is the
contract-correct invoice number for the retainage release. The suffix is
not an informal convention — it is specified in the governing agreement.

**Completion Certificate (PLC-DC4-2026-001)**

Certificate issued 2026-03-15, signed by G. Mendes (Owner's Representative,
Cascadia) and T. Nakamura (Site Superintendent, Ironpoint). The certificate
explicitly states that the completion condition in Section 9.4 of MSA-IPC-2024
is satisfied. Both required parties have signed. The certificate predates the
retainage release invoice (2026-03-20) and the ERP flag (2026-03-22). Release
condition is confirmed before the invoice was even submitted.

**Payment History Math**

Five progress billings totaling $2,150,000 gross. 10% retainage withheld on
each: $45,000 + $38,000 + $52,000 + $40,000 + $40,000 = $215,000. Net paid on
progress: $1,935,000. Outstanding retainage: $2,150,000 - $1,935,000 = $215,000.
Requested on IPC-2024-0405-R: $215,000. Total after release: $2,150,000 =
contract value. No overpayment. The math is exact.

**ERP Duplicate Flag (ERP-DUP-2026-0441)**

The flag matched on the first 12 characters of "IPC-2024-0405" — ignoring the
"-R" suffix — which is the documented 12-character matching limitation described
in IT advisory SA-AP-2024-07. The ERP is comparing a $215,000 retainage release
invoice to a $400,000 progress billing — the amounts are different, the invoice
types are different, and the ERP flag is a system artifact as defined by the
IT advisory. Decision Rule 3 requires reconciling the flag against payment
history, contract terms, completion status, and control-owner findings. All
four have been reconciled. The flag is not evidence of a real duplicate.

**ERP Hold (AP-DUP-2026-0441)**

Placed automatically when the flag fired. Released 2026-04-03 by R. Okafor
(AP Manager) after manual reconciliation per SA-AP-2024-07. Release basis
documented explicitly: payment history confirmed, contract terms reviewed,
completion certificate confirmed, IT advisory applied. Exception closed.

**AP Approval**

R. Okafor (AP Manager) approved 2026-04-05, two days after releasing the hold.
The approval basis explicitly references all four required elements: contract
Section 9.4, completion certificate PLC-DC4-2026-001, payment history
reconciliation, and IT advisory SA-AP-2024-07. Approval authority stated.
Approval post-dates hold release and completion evidence. Decision Rule 4 is
fully satisfied.

---

## Why Solo Models Will Likely Escalate

1. The ERP "DUPLICATE PAYMENT — SAME VENDOR / SAME INVOICE PREFIX" flag is
   presented as a prominent standalone section with bold system language. Models
   trained on AP risk will treat this as a hard stop.

2. Decision Rule 3 requires active reconciliation — but it does not tell the
   evaluator what the reconciliation should find. A model that reads the rule
   but doesn't complete the arithmetic and cross-document check may escalate.

3. Retainage mechanics are domain-specific. The evaluator must understand that:
   - 10% withheld on 5 invoices totaling $2.15M = $215,000 outstanding
   - $215,000 ≠ a duplicate of the $400,000 IPC-2024-0405 invoice
   - The "-R" suffix is a contract-defined type, not a variant of the same invoice

4. The segregation-of-duties appearance (R. Okafor releases hold AND approves)
   may cause an evaluator to escalate on process grounds even though the rules
   don't require segregation.

5. The evidence is distributed across six separate sections. A model that reads
   sections sequentially without synthesizing across them may escalate when it
   reaches the ERP flag section and not yet have connected the contract terms,
   completion cert, and payment math.

---

## What a Correct ALLOW Justification Looks Like

The evaluator must state, at minimum:
- The retainage release conditions in Section 9.4 are satisfied (completion certificate PLC-DC4-2026-001 signed by both required parties)
- Payment history confirms $215,000 retainage outstanding — the requested amount matches exactly and does not duplicate IPC-2024-0405
- The ERP flag is a system artifact per IT Advisory SA-AP-2024-07 (12-character matching limitation ignores the "-R" suffix)
- AP Manager R. Okafor approved with explicit basis addressing all outstanding flags
- No open holds or exceptions remain

A verdict that cites fewer than three of these elements is incomplete reasoning
even if the verdict is correct.
