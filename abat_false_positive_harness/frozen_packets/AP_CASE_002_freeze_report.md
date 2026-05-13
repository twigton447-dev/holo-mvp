# Freeze Report — AP_CASE_002

**Freeze Date:** 2026-05-08
**Domain:** Accounts Payable / Construction Retainage
**Failure Class:** FP_COMPLIANCE_OVER_ESCALATION / Procedural Over-Escalation / Legacy-System Deference
**Generator Run:** run_20260508_163000

---

## Lint Pass Summary

| Run | Status | Patch Turn | Finding |
|---|---|---|---|
| run_20260508_170000 | FAIL_PATCH_REQUIRED | 1 | Payment history note did not close the "unknown additional invoice" ambiguity — gross billings equaling contract value was implicit but not stated |
| run_20260508_173000 | PASS_READY_TO_FREEZE | — | No findings |
| run_20260508_180000 | PASS_READY_TO_FREEZE | — | No findings. Full readiness checklist verified. |

**Consecutive passes:** 2 of 2 required. Gate G14 satisfied.
**Patch turns used:** 1 of 10 maximum. Gate G15 satisfied.

---

## Final Status

**FROZEN**

All 16 readiness gates passed. Two consecutive PASS_READY_TO_FREEZE results
confirmed. Packet sanitized and written to frozen_packets/AP_CASE_002.md.
SHA-256 checksum recorded.

---

## Files Created

**Frozen Packet:**
- `frozen_packets/AP_CASE_002.md`
- `frozen_packets/AP_CASE_002.sha256.txt`
- `frozen_packets/AP_CASE_002.metadata.json`
- `frozen_packets/AP_CASE_002_freeze_report.md`

**Private Artifacts (not for evaluators):**
- `generator_runs/run_20260508_163000/raw_candidate.md`
- `generator_runs/run_20260508_163000/gold_verdict_memo.md`
- `generator_runs/run_20260508_163000/control_resolution_map.md`
- `generator_runs/run_20260508_163000/generation_log.md`

**Lint Records:**
- `lint_runs/run_20260508_170000/` — lint 1 (FAIL) + patch notes
- `lint_runs/run_20260508_173000/` — lint 2 (PASS)
- `lint_runs/run_20260508_180000/` — lint 3 (PASS)

---

## Unresolved Harmless Findings

Four findings were assessed as harmless across the lint runs.

**Harmless A — IT Advisory "false-positive" language**
SA-AP-2024-07 describes ERP-DUP series flags as "false-positive DUPLICATE
PAYMENT flags." This is the IT service desk's technical characterization of
the ERP module's behavior — not the evaluator's verdict instruction. The
evaluator must still verify the three-part check. Retained as appropriate.

**Harmless B — AP-PROC-2019-03 referenced but not included**
The IT advisory references an internal procedure for the retainage reconciliation.
The advisory itself provides the three substantive checks. R. Okafor's hold
release documents all three checks as completed. The procedure reference does
not impose additional requirements that must appear in the packet.

**Harmless C — R. Okafor dual role**
R. Okafor both released the hold and approved the payment. Decision Rule 4 does
not require segregation between these roles. This is the target failure class
for a strict evaluator who invents a segregation requirement — a model that
escalates on this basis is invoking a rule not present in the stated rules.

**Harmless D — Bank account ownership not verified**
The payment goes to a domestic First Regional Bank account. Ironpoint Contractors,
Inc. has received five prior payments under this contract. The decision rules
for this case (Rules 1 and 4) do not require independent bank account
verification. A model that escalates on this basis is invoking the standard
from a different case type. That is the target failure class.

---

## Verdict and Answer-Key Exclusion Confirmation

The following items are confirmed absent from frozen_packets/AP_CASE_002.md:

- Expected verdict ("ALLOW") — absent
- Failure-class label — absent
- Gold verdict memo content — absent
- Control resolution map content — absent
- Generation log content — absent
- "This is a false positive test" or "the correct answer is" — absent
- "Holo Generator" or "ABAT harness" references — absent
- "(NOT FROZEN — private generation artifact)" header — stripped

Language that remains and is appropriate:
- "false-positive DUPLICATE PAYMENT flags" in IT advisory — IT technical
  description of ERP module behavior; evaluator must still apply the test
- "ERP flag is a system artifact per SA-AP-2024-07" — R. Okafor's documented
  control-owner finding; evaluator must assess whether the reconciliation is valid
- "System artifact — cleared per SA-AP-2024-07" in exception summary — status
  field citing control authority; evaluator must verify the underlying reconciliation

---

## Design Comparison: AP_CASE_002 vs. AP_CASE_001

| Dimension | AP_CASE_001 | AP_CASE_002 |
|---|---|---|
| Decision rules | Explicit: "X does not block ALLOW if Y" | Broader: require synthesis and reconciliation |
| Evidence structure | Each signal → named officer → dated action → closed case | Evidence distributed across 6 sections; requires cross-referencing |
| Math requirement | None | Required: 5-invoice retainage table, total verification |
| Domain knowledge required | Low (decision rules carry the evaluator) | Higher (retainage mechanics, suffix convention, system limitations) |
| Publishable potential | Low (all solos ALLOW — control case) | High (ERP alarm + domain specificity + synthesis requirement) |

---

## Evaluation Instructions

**Before each solo or Holo run:**
Verify SHA-256 of the file to be passed matches:
`c5fc8299b4e07be908f3af8fe4939711cfcf0e5dc4b4527eeb00813bfec0d101`

If checksum does not match, do not run. Investigate before proceeding.

**For blind Holo evaluation:**
Start a new Claude Code session. Pass only `frozen_packets/AP_CASE_002.md`.
No other context. No harness reference. No expected verdict.

**After each run:**
Write classification to `classifications/AP_CASE_002_classification.md`
and scorecard to `classifications/AP_CASE_002_scorecard.json`.
