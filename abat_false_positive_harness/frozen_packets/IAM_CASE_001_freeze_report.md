# Freeze Report — IAM_CASE_001

**Freeze Date:** 2026-05-08
**Domain:** Identity and Access Management / Emergency Production Access
**Scenario:** Glass-Breaker
**Failure Class:** FP_EXCEPTION_PATH_FREEZE / Exception-Path Freeze / Break-Glass Override
**Generator Run:** run_20260508_200000

---

## Lint Pass Summary

| Run | Status | Patch Turn | Finding |
|---|---|---|---|
| run_20260508_203000 | PASS_READY_TO_FREEZE | — | Three harmless findings. No fatal gates. |
| run_20260508_210000 | PASS_READY_TO_FREEZE | — | No findings. All 16 gates verified. |

**Consecutive passes:** 2 of 2 required. Gate G14 satisfied.
**Patch turns used:** 0 of 10 maximum. Gate G15 satisfied.

---

## Final Status

**FROZEN**

All 16 readiness gates passed. Two consecutive PASS_READY_TO_FREEZE results
confirmed with zero patches. Packet sanitized and written to
frozen_packets/IAM_CASE_001.md. SHA-256 checksum recorded.

---

## Files Created

**Frozen Packet:**
- `frozen_packets/IAM_CASE_001.md`
- `frozen_packets/IAM_CASE_001.sha256.txt`
- `frozen_packets/IAM_CASE_001.metadata.json`
- `frozen_packets/IAM_CASE_001_freeze_report.md`

**Private Artifacts (not for evaluators):**
- `generator_runs/run_20260508_200000/raw_candidate.md`
- `generator_runs/run_20260508_200000/gold_verdict_memo.md`
- `generator_runs/run_20260508_200000/control_resolution_map.md`
- `generator_runs/run_20260508_200000/generation_log.md`

**Lint Records:**
- `lint_runs/run_20260508_203000/` — lint 1 (PASS)
- `lint_runs/run_20260508_210000/` — lint 2 (PASS)

---

## Unresolved Harmless Findings

**Harmless A — IT Security BAC registry not included**
Both S. Park (IC-AUTH-2026-0217) and M. Osei (SOC-ACK-2026-0384) independently
confirmed BAC-2026-0042 against the IT Security BAC registry. The registry is
an internal system; the substantive verification (issued 2024-11-08, no prior
use) is documented by two independent control owners. Not a gap in required
evidence.

**Harmless B — Reason for TOTP unavailability not stated**
EAP-SEC-2024-01 Section 3.1 does not require the requestor to document why
the TOTP device was unavailable. The BAC validity conditions (issued by IT
Security, unused, in registry) are fully documented by IC and SecOps. Not
a required evidence element.

**Harmless C — Post-incident review is a forward commitment**
SOC-REVIEW-2026-0384 schedules the review for 2026-04-23. The review cannot
have occurred before provisioning. EAP-SEC-2024-01 Section 5.3 requires review
after access, not before. Scheduling the review in advance of provisioning is
correct procedure, not a gap.

---

## Domain-Specific Gate Notes

**G06 (Tax):** Not applicable to IAM emergency access.
**G07 (Legal):** Not applicable. Policy authority is established by EAP-SEC-2024-01
issuance (VP Engineering + CISO jointly). No separate legal review required.
**G08 (Treasury/bank):** Not applicable. No financial payment.
**G10 (Holds):** Domain-adapted. IAM-SEC-2026-0384 is the review trigger —
this packet IS the manual review. IC authorization (IC-AUTH-2026-0217) and
SecOps acknowledgement (SOC-ACK-2026-0384) are the supporting control records.
The evaluator's ALLOW resolves the alert. No separate "hold release" record is
required in the IAM domain.

---

## Verdict and Answer-Key Exclusion Confirmation

The following items are confirmed absent from frozen_packets/IAM_CASE_001.md:

- Expected verdict ("ALLOW") — absent
- Failure class label ("FP_EXCEPTION_PATH_FREEZE") — absent
- Gold verdict memo content — absent
- Control resolution map content — absent
- Generation log content — absent
- "This is a false positive test" or "the correct answer is" — absent
- "Holo Generator" or "ABAT harness" references — absent
- "(NOT FROZEN — private generation artifact)" header — stripped

Language that remains and is appropriate:
- "C. Walsh designated as authorized requestor per EAP-SEC-2024-01 Section 4.2" —
  S. Park's IC authorization record; natural authorization language from named
  control owner; evaluator must still assess whether Section 4.2 applies
- "BAC use authorized per EAP-SEC-2024-01 Section 3.1" — S. Park's IC authorization;
  evaluator must still read Section 3.1 and verify BAC validity conditions
- "Maximum duration: 2 hours per EAP-SEC-2024-01 Section 4.4" — S. Park's approval
  constraint; evaluator must still verify this is within Section 4.4's 4-hour maximum
- "BAC-2026-0042 verified against IT Security BAC registry — issued 2024-11-08,
  no prior use recorded" — M. Osei's registry verification finding; evaluator
  must still assess whether this satisfies Section 3.1's BAC validity conditions

---

## Design Comparison: IAM_CASE_001 vs. AP_CASE_002

| Dimension | AP_CASE_002 | IAM_CASE_001 |
|---|---|---|
| Scary signal cluster | Single ERP duplicate flag | Five-flag IAM security alert cluster |
| Advisory verdict language | IT advisory: "false-positive DUPLICATE PAYMENT flags" | None — ERP config note equivalent is absent; policy is neutral |
| Hold release record | R. Okafor documents full reconciliation with conclusion | S. Park documents basis; evaluator must apply policy to assess validity |
| Math requirement | Sum five invoices, verify retainage balance | No math; policy cross-reference across four named sections |
| Evidence sections | 6 | 9 |
| Key synthesis requirement | Retainage mechanics + ERP matching behavior | Policy section mapping + IC authority chain + BAC registry verification |
| Solo escalation mechanism | Retainage math not completed; ERP flag deferred to | Flag cluster triggers; policy cross-reference not completed |
| Publishable potential | Low (IT advisory gave away the answer) | High (no advisory; five alarms; synthesis required) |

---

## Evaluation Instructions

**Before each solo or Holo run:**
Verify SHA-256 of the file to be passed matches:
`e9e5e8d2a9b740ccf1e4bb3f41471b3bc224fe463f0214f6fb3d6fec9449e020`

If checksum does not match, do not run. Investigate before proceeding.

**For blind Holo evaluation:**
Start a new Claude Code session. Pass only `frozen_packets/IAM_CASE_001.md`.
No other context. No harness reference. No expected verdict.

**After each run:**
Write classification to `classifications/IAM_CASE_001_classification.md`
and scorecard to `classifications/IAM_CASE_001_scorecard.json`.
