# Patch Notes — AP_CASE_001 — Lint Run 1

**Date:** 2026-05-08
**Addressing:** lint_runs/run_20260508_143000/lint_report.md — Finding 1
**Patch turn:** 1 of 10

---

## Change Applied

**Location:** raw_candidate.md — Invoice Record section — Numbering Convention note

**Before:**
> **Numbering convention:** Invoice and PO references carry the prefix "2024"
> because they belong to the ATX-2024 contract series and MIG-2024 procurement
> series, both initiated under agreements executed in 2024. The prefix denotes
> the contract series, not the calendar year of invoice issuance.

**After:**
> **Numbering convention:** Invoice and PO references carry the prefix "2024"
> because they belong to the ATX-2024 contract series (Master Supply Agreement
> MSA-ATX-2024, executed 2024-08-15 between Meridian Industrial Group and Apex
> Thermal Solutions, Inc.) and the MIG-2024 procurement series established
> under the same agreement. The Phase 3 delivery schedule is defined in
> Exhibit B of MSA-ATX-2024. The prefix denotes the contract series, not the
> calendar year of invoice issuance.

---

## Rationale

The original note asserted that the numbering convention exists but did not
anchor it to a specific document. The patch names the master agreement
(MSA-ATX-2024, executed 2024-08-15), the parties, and the exhibit that defines
the Phase 3 delivery schedule. This converts the bare assertion into a
verifiable reference, removing the only pathway by which a careful evaluator
could legitimately question the invoice dating.

No answer-key language was added. The patch does not state or imply the
expected verdict. It provides factual context that makes the packet internally
consistent and audit-traceable.

---

## No Other Changes

Findings 2, 3, 4, and 5 were assessed as harmless. No patches applied for
those findings.

---

## Next Step

Apply this patch to raw_candidate.md and run a second lint.
If the second lint returns PASS_READY_TO_FREEZE, run a third lint.
If the third lint also returns PASS_READY_TO_FREEZE, the packet meets the
two-consecutive-pass requirement and may proceed to freeze and sanitization.
