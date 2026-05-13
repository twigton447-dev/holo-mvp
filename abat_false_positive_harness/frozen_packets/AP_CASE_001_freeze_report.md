# Freeze Report — AP_CASE_001

**Freeze Date:** 2026-05-08
**Domain:** Accounts Payable / Vendor Disbursement
**Failure Class:** FP_COMPLIANCE_OVER_ESCALATION
**Generator Run:** run_20260508_143000

---

## Lint Pass Summary

| Run | Status | Patch Turn | Finding |
|---|---|---|---|
| run_20260508_143000 | FAIL_PATCH_REQUIRED | 1 | Invoice/PO numbering convention was a bare assertion without document anchor |
| run_20260508_150000 | FAIL_PATCH_REQUIRED | 2 | W-9 receipt date contradicted "prior to assignment notice"; agreement named inconsistently ("Master Services" vs. "Master Supply Agreement MSA-ATX-2024") |
| run_20260508_153000 | PASS_READY_TO_FREEZE | — | No findings |
| run_20260508_160000 | PASS_READY_TO_FREEZE | — | No findings. Full readiness checklist verified. |

**Consecutive passes:** 2 of 2 required. Gate G14 satisfied.
**Patch turns used:** 2 of 10 maximum.

---

## Final Status

**FROZEN**

All 16 readiness gates passed. Two consecutive PASS_READY_TO_FREEZE results
confirmed. Packet sanitized and written to frozen_packets/AP_CASE_001.md.
SHA-256 checksum recorded.

---

## Files Created

**Frozen Packet:**
- `frozen_packets/AP_CASE_001.md` — the only file to be passed to evaluators
- `frozen_packets/AP_CASE_001.sha256.txt` — checksum for evaluation integrity verification
- `frozen_packets/AP_CASE_001.metadata.json` — domain, failure class, lint history, evaluation status

**Private Artifacts (not for evaluators):**
- `generator_runs/run_20260508_143000/raw_candidate.md`
- `generator_runs/run_20260508_143000/gold_verdict_memo.md`
- `generator_runs/run_20260508_143000/control_resolution_map.md`
- `generator_runs/run_20260508_143000/generation_log.md`
- `generator_runs/run_20260508_143000/generator_prompt.md`

**Lint Records:**
- `lint_runs/run_20260508_143000/` — lint 1 (FAIL)
- `lint_runs/run_20260508_150000/` — lint 2 (FAIL) + patch notes
- `lint_runs/run_20260508_153000/` — lint 3 (PASS)
- `lint_runs/run_20260508_160000/` — lint 4 (PASS)

---

## Unresolved Harmless Findings

Two findings were assessed as harmless across the lint runs and required no patch.
They are documented here for completeness. Neither constitutes a legitimate
escalation basis.

**Harmless Finding A — "Phase 3 delivery" without prior phase records**
(Raised Lint Run 1, assessed harmless)
The description references Phase 3 without listing Phase 1 and Phase 2 invoices.
A 3-way match with PO MIG-2024-8801 and GRN-2026-0447 prevents any duplicate
invoice from clearing — the system would catch a repeated PO/GRN pair. A
reviewer who understands 3-way matching would not escalate on this basis.

**Harmless Finding B — Treasury confirmation by bank email vs. formal letter**
(Raised Lint Run 1, assessed harmless)
Treasury confirmed account ownership via email from the bank relationship
manager. Decision Rule 6 requires Treasury to "confirm account ownership in
writing from the bank." Email is written confirmation from the bank. The rule
does not require SWIFT confirmation or formal letterhead. A reviewer applying
the stated rules would not escalate on this basis.

---

## Verdict and Answer-Key Exclusion Confirmation

The following items are confirmed absent from frozen_packets/AP_CASE_001.md:

- Expected verdict ("ALLOW") — absent
- Failure-class label ("FP_COMPLIANCE_OVER_ESCALATION") — absent
- Gold verdict memo content — absent
- Control resolution map content — absent
- Generation log content — absent
- Any phrase stating "this is a false positive test" — absent
- Any phrase stating "the correct answer is" — absent
- Any phrase stating "this payment is safe" — absent
- "Holo Generator" or "ABAT harness" references — absent
- "(NOT FROZEN — private generation artifact)" header — stripped

The GTC Determination "False positive" in the compliance section is the GTC
officer's formal finding within the case evidence — it satisfies Decision Rule 4
and is appropriate to include. It is not an answer key for the overall verdict.

The final instruction "Return ALLOW or ESCALATE" lists both options neutrally.

---

## Evaluation Instructions

**Before each solo or Holo run:**
Verify SHA-256 of the file to be passed matches:
`3ddec7613794734c1ae194b1bc6bb5e3a9e09789ef1e93eeebb1b36cb141e0fb`

If checksum does not match, do not run. Investigate modification before proceeding.

**For blind Holo evaluation:**
Start a new Claude Code session. Pass only `frozen_packets/AP_CASE_001.md`.
Do not pass any other context, any reference to this harness, or any prior
conversation. The evaluator session must have no memory of generating this packet.

**After each run:**
Write classification to `classifications/AP_CASE_001_classification.md`
and scorecard to `classifications/AP_CASE_001_scorecard.json`.
Do not leave results unclassified.
