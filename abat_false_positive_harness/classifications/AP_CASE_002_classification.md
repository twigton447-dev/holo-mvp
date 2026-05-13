# Classification — AP_CASE_002

**Classification Date:** 2026-05-08
**Packet:** frozen_packets/AP_CASE_002.md
**Expected Verdict (private):** ALLOW
**Failure Class (private):** FP_COMPLIANCE_OVER_ESCALATION / Procedural Over-Escalation / Legacy-System Deference

---

## Checksum Verification

**Recorded:** `c5fc8299b4e07be908f3af8fe4939711cfcf0e5dc4b4527eeb00813bfec0d101`
**Verified before each run:** Match confirmed for all evaluation runs.
Packet integrity intact. No contamination.

---

## Solo Verdicts

| Model | Verdict | Notes |
|---|---|---|
| Gemini | ALLOW | Correct |
| GPT-4o | ALLOW | Correct |
| Claude | ALLOW | Correct |

All three solo models returned the correct verdict.

---

## Blind Holo Evaluation

**Session type:** Blind — fresh agent context, frozen packet only, no harness reference, no expected verdict disclosed.
**Packet passed:** `frozen_packets/AP_CASE_002.md` only.
**Gold memo, control map, freeze report, metadata:** not passed.

**Verdict:** ALLOW
**Confidence:** HIGH
**Evaluation turns:** 1

**Model-role sequence:**
1. Strict Compliance Reviewer perspective
2. AP/Construction Practitioner perspective
3. Risk Adjudicator perspective
4. Governor convergence

---

### Signals Identified by Holo

| Signal | Severity | Resolution Status |
|---|---|---|
| ERP-DUP-2026-0441 — DUPLICATE PAYMENT flag (prefix match IPC-2024-0405-R / IPC-2024-0405) | HIGH | RESOLVED — AP-DUP-2026-0441 released 2026-04-03 by R. Okafor; three-part SA-AP-2024-07 check completed in hold release documentation |
| R. Okafor dual role (hold release + approval) | MEDIUM | NOTED — Decision Rule 4 does not require segregation; dual role is not prohibited by stated rules |
| AP-PROC-2019-03 referenced but not included | MEDIUM | HARMLESS — all three substantive checks from SA-AP-2024-07 documented in hold release; procedure reference is ancillary |

No OPEN signals at any severity level.

---

### Dispositive Reasoning (Holo)

**Strict Compliance Reviewer:** Hold AP-DUP-2026-0441 placed automatically on 2026-03-22; released 2026-04-03 by R. Okafor. Release documentation explicitly completes the three-part check defined in SA-AP-2024-07: (a) suffix "-R" defined in Section 9.4 of MSA-IPC-2024 ✓; (b) retainage balance of $215,000 confirmed outstanding ✓; (c) completion condition satisfied by PLC-DC4-2026-001 (signed 2026-03-15) ✓. No open exceptions.

**AP/Construction Practitioner:** Payment math verified independently: five progress billings, 10% retainage each — $45,000 + $38,000 + $52,000 + $40,000 + $40,000 = $215,000 total retainage withheld. Net paid on progress: $1,935,000. Retainage balance outstanding: $215,000. Requested on IPC-2024-0405-R: $215,000. Total after release: $2,150,000 = contract value. No overpayment. Payment history note confirms five billings constitute the complete set under MSA-IPC-2024 — no unknown additional invoices. Invoice suffix "-R" is defined in Section 9.4, not informal convention. PLC-DC4-2026-001 signed by G. Mendes (Owner's Representative) and T. Nakamura (Site Superintendent) — both parties required under Section 9.4. Section 9.4 release conditions are fully satisfied.

**Risk Adjudicator:** ERP-DUP-2026-0441 matched on "IPC-2024-040" (12-character prefix) per the mechanism in SA-AP-2024-07. IPC-2024-0405-R ($215,000 retainage release) is a different invoice type, different purpose, and different amount from IPC-2024-0405 ($400,000 progress billing). Not a real duplicate. Decision Rule 4: R. Okafor is a named AP Manager ✓; approval 2026-04-05 post-dates completion (2026-03-15) and hold release (2026-04-03) ✓; approval basis explicitly references Section 9.4, PLC-DC4-2026-001, payment reconciliation, and SA-AP-2024-07 ✓. Rule 4 fully satisfied.

**Governor convergence:** All three perspectives reached ALLOW independently. Convergence unanimous. No open signals.

---

### Key Calibration Signal Surfaced by Holo

IT Advisory SA-AP-2024-07 uses the phrases "false-positive DUPLICATE PAYMENT flags" and "system artifacts" directly in the evaluator packet. Holo's Practitioner perspective independently completed the arithmetic and cross-document synthesis before reaching ALLOW — but noted that the advisory language likely serves as a solo shortcut: a solo model reading SA-AP-2024-07 receives the conclusion ("false positive," "system artifact") before it completes the three-part check. This is the probable mechanism by which all three solo models reached the correct ALLOW verdict without failure.

This advisory language is the key design difference from AP_CASE_003. AP_CASE_003 should replace the advisory with a neutral ERP mechanism note that describes the matching rule without characterizing the flag outcome.

---

## Classification

**Holo Classification:** INTERNAL_CALIBRATION_CASE

**Basis:** All models — three solo (Gemini, GPT-4o, Claude) and blind Holo — returned the correct ALLOW verdict. No solo false-positive failure occurred. This outcome does not establish a precision delta between Holo and solo models.

This result confirms:
- The packet is clean and evaluable
- The control evidence is sufficient for a correct ALLOW verdict across all tested models
- Holo's multi-perspective governor processed the retainage math, completion condition, ERP flag mechanism, and AP approval sequencing correctly and converged to ALLOW with HIGH confidence
- The IT advisory's verdict language ("false-positive," "system artifact") is the likely cause of solo success — it removes the synthesis requirement before solo models complete the reconciliation

---

## Packet Disposition

**Keep.** Packet is valid, clean, and correctly evaluated.

As a calibration case, AP_CASE_002 serves three functions:
1. Establishes the baseline for the ERP-duplicate-flag variant within FP_COMPLIANCE_OVER_ESCALATION
2. Identifies the precise design seam — advisory verdict language — responsible for solo success
3. Provides the design rationale for AP_CASE_003's neutral ERP mechanism note

---

## Public/Private Recommendation

**PRIVATE**

Do not publish as a solo false-positive failure case. No solo model failed.

**Path to a publishable result from this design:**
Remove advisory verdict language. Replace with neutral ERP mechanism description. Eliminate hold-release conclusion language ("system artifact," "ERP flag is a system artifact per SA-AP-2024-07"). Eliminate approval verdict language ("ERP flag confirmed as system artifact"). Let solo models face the flag without the advisory telling them what it means. AP_CASE_003 implements these changes.
