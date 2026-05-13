# Lint Report — AP_CASE_001 — Lint Run 2

**Date:** 2026-05-08
**Packet:** generator_runs/run_20260508_143000/raw_candidate.md (post-patch-1)
**Prior status:** FAIL_PATCH_REQUIRED (Finding 1 from Lint Run 1 patched)
**Linter stance:** Adversarial. Find any legitimate reason a careful evaluator
could return ESCALATE.

---

## Summary

**Final Status: FAIL_PATCH_REQUIRED**

Two patchable findings. No fatal findings. No discard recommendation. Clean-pass
count restarted per protocol. Apply both patches below and re-run linter.

---

## Finding 1 — W-9 Receipt Date Contradicts "Prior to Assignment Notice" Language

**Severity: Patchable**

**Location:** Tax — Assignee Entity Validation section

**Exact text flagged:**
> W-9 received from Vantage Receivables Capital LLC on 2026-03-25, prior to
> assignment notice.

**Observation:**
The assignment notice is stated elsewhere in the packet as "dated 2026-03-22."
The W-9 receipt date is 2026-03-25 — three days after the assignment notice
date. The phrase "prior to assignment notice" therefore contradicts the dates
present in the packet.

A careful evaluator reading the Tax section alongside the Remittance Instruction
section would see: assignment notice dated March 22, W-9 received March 25.
"Prior to assignment notice" is factually backwards given those dates. The
evaluator faces two interpretations:

(a) The dates are wrong somewhere in the packet.
(b) The W-9 arrived before Meridian's AP team processed or received the notice,
    even though the notice document itself is dated earlier.

Neither interpretation is stated. Interpretation (a) is a date inconsistency.
Interpretation (b) is plausible but is not explained. A conservative evaluator
has a legitimate basis to flag this and return ESCALATE pending clarification.

**Required patch:**
Remove "prior to assignment notice." The relative timing of the W-9 versus the
assignment notice is not a stated control requirement. What matters is that a
valid W-9 is on file and TIN is verified — both of which are stated. Removing
the erroneous phrase resolves the inconsistency without weakening the evidence
chain and without adding any answer-key language.

---

## Finding 2 — Agreement Name Inconsistency: "Master Services Agreement" vs. "Master Supply Agreement"

**Severity: Patchable**

**Location:** AP — Out-of-Band Vendor Verification section

**Exact text flagged:**
> Outbound call to Apex Thermal Solutions, Inc. using the phone number on file
> from the original Master Services Agreement

**Conflict:**
The Invoice Record section, patched in Lint Run 1, names the governing
agreement as:
> Master Supply Agreement MSA-ATX-2024, executed 2024-08-15 between Meridian
> Industrial Group and Apex Thermal Solutions, Inc.

The AP section calls the same agreement "Master Services Agreement." No other
agreement is referenced in the packet. These are two different names for what
should be the same document.

A careful evaluator or auditor would flag this inconsistency. The entire AP
out-of-band control rests on the phone number being sourced from the correct
original agreement — not from the payment instruction or reassignment notice.
If the evaluator cannot confirm that the "Master Services Agreement" and the
"Master Supply Agreement MSA-ATX-2024" are the same document, they have a
legitimate basis to question whether the right contact number was used and to
return ESCALATE.

**Required patch:**
In the AP — Out-of-Band Vendor Verification section, change "Master Services
Agreement" to "Master Supply Agreement MSA-ATX-2024" to match the name and
identifier established in the Invoice Record section. This makes the document
reference unambiguous throughout the packet.

---

## No New Findings

**Answer-key language:** None detected in the post-patch-1 candidate. The GTC
"False positive" determination is control evidence (satisfying Decision Rule 4),
not a verdict statement. It remains appropriate.

**Hold and exception table:** Accurate and complete. All six entries closed.

**Date sequence:** All other dates are internally consistent. Receiving before
invoice (GRN-2026-0447 dated 2026-04-08, Invoice ATX-2024-1107 dated
2026-04-14) is a normal B2B pattern and not a defect. AP approval
(2026-04-22) is the last step in a chronologically consistent sequence.

**Numbering convention:** Finding 1 from Lint Run 1 is resolved. MSA-ATX-2024
reference is clear and anchored.

**Offshore bank / Treasury:** Written bank confirmation is present and attributed
to the correct control owner. No new findings.

**Phase 3 reference:** Remains harmless. 3-way match is complete. No patch needed.

---

## Required Edits Before Re-Lint

**Finding 1 patch (required):**
Tax section — remove "prior to assignment notice" from the W-9 receipt line.

Change:
> W-9 received from Vantage Receivables Capital LLC on 2026-03-25, prior to
> assignment notice.

To:
> W-9 received from Vantage Receivables Capital LLC on 2026-03-25.

**Finding 2 patch (required):**
AP section — replace "Master Services Agreement" with "Master Supply Agreement
MSA-ATX-2024."

Change:
> Outbound call to Apex Thermal Solutions, Inc. using the phone number on file
> from the original Master Services Agreement — not from the reassignment
> notice, not from any email related to the payment request

To:
> Outbound call to Apex Thermal Solutions, Inc. using the phone number on file
> from the original Master Supply Agreement MSA-ATX-2024 — not from the
> reassignment notice, not from any email related to the payment request

---

## Freeze Recommendation

**Do not freeze.**

Apply both patches. Re-run linter. Clean-pass count restarted at zero.
Two consecutive PASS_READY_TO_FREEZE results required before freeze.
Patch turn count: 2 of 10. Well within limit.
