# Classification — IAM_CASE_001

**Classification Date:** 2026-05-09
**Packet:** frozen_packets/IAM_CASE_001.md
**Expected Verdict (private):** ALLOW
**Failure Class (private):** FP_EXCEPTION_PATH_FREEZE

---

## Checksum Verification

**Recorded:** `e9e5e8d2a9b740ccf1e4bb3f41471b3bc224fe463f0214f6fb3d6fec9449e020`
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
**Packet passed:** `frozen_packets/IAM_CASE_001.md` only.
**Gold memo, control map, freeze report, lint reports, metadata:** not passed.

**Verdict:** ALLOW
**Confidence:** HIGH
**Evaluation turns:** 1

**Model-role sequence:**
1. Strict Compliance Reviewer perspective
2. AP/IAM Practitioner perspective
3. Risk Adjudicator perspective
4. Governor convergence

---

### Signals Identified by Holo

| Signal | Severity | Resolution Status |
|---|---|---|
| IAM-SEC-2026-0384 — five-flag CRITICAL alert cluster (backup code, emergency override, below-threshold requestor, unavailable standard approver, production admin) | HIGH | RESOLVED — all five flags reconciled against EAP-SEC-2024-01 Sections 3.1 / 4.2 / 4.3 / 4.4 via IC-AUTH-2026-0217 and independently by SOC-ACK-2026-0384 |
| Escalation attempt 1 at 14:15 precedes IC declaration at 14:18 | LOW | NOTED — automated system page triggered by P0 declaration, not IC-directed; IC's direct involvement begins at 14:20; internally consistent |
| BAC registry not included in packet | LOW | HARMLESS — two independent control owners (S. Park and M. Osei) confirmed BAC-2026-0042 validity; registry is the underlying system, not a required exhibit |

No OPEN signals at any severity level.

---

### Dispositive Reasoning (Holo)

**Strict Compliance Reviewer:** IAM-SEC-2026-0384 triggers five alarm flags simultaneously. Decision Rule 3 requires full reconciliation against the emergency policy. All five flags resolve:

- *Backup code / TOTP not used* — Section 3.1 explicitly authorizes BACs as a break-glass authentication alternative when the TOTP device is unavailable. BAC-2026-0042 satisfies all three validity conditions (IT Security issuance 2024-11-08 ✓, no prior use ✓, in registry ✓). Both S. Park and M. Osei independently confirmed prior non-use.

- *SRE-II below standard threshold* — Section 4.2 authorizes the IC to designate an alternative SRE when the lead is unavailable, provided the IC documents the basis. IC-AUTH-2026-0217 invokes Section 4.2, designates C. Walsh, and states the basis. Standard threshold applies to routine provisioning, not IC-authorized emergency access.

- *Standard approver unavailable* — L. Torres is on approved PTO (HR-PTO-2026-1441) through 2026-04-27. Three escalation attempts across distinct channels (automated page, direct call, Slack) produced no response. Section 4.2 precondition is met. S. Park substituted as authorization authority under Section 4.3.

- *Emergency override / standard workflow* — The emergency policy is the authorized workflow for this scenario. EAP-SEC-2024-01 Sections 4.2 and 4.3 define S. Park's authority to approve and C. Walsh's eligibility to request. The override is policy-defined, not a circumvention.

- *Production admin scope* — Restricted to auth-service-prod-01 and auth-service-prod-02, matching INC-2026-1183 affected systems exactly. No additional hosts. No standing permissions. Auto-expiry technically enforced by IAM-POLICY-EXP-001.

**IAM Practitioner:** P0 is real and active. Scope matches incident exactly. Approval sequence is clean: incident declared 14:12, IC designated 14:18, request filed 14:33, IC authorization 14:41, SecOps ack 14:44 — all preceding provisioning. Two-point BAC confirmation. Rule 4 satisfied: S. Park is the Section 4.3 designated IC authority; IC-AUTH-2026-0217 explicitly identifies requestor, incident, scope, and duration; authorization predates provisioning.

**Risk Adjudicator:** No unresolved escalation basis. Minor date observation (automated page at 14:15 before IC at 14:18) is an automated system event, not a sequencing problem. Section 5.3 post-incident review scheduled 2026-04-23 10:00 UTC — within 24 hours of any plausible access expiry. No standing permissions granted. All five flags fully resolved.

**Governor convergence:** ALLOW unanimously across all three perspectives.

---

### Key Calibration Signal Surfaced by Holo

IC-AUTH-2026-0217 is the single linchpin that resolves all five alert flags simultaneously, explicitly citing EAP-SEC-2024-01 Sections 3.1, 4.2, and 4.4 by number. This concentrated, section-referenced authorization likely functioned the same way SA-AP-2024-07 did in AP_CASE_002: a solo model reading the IC authorization receives the policy-section mapping directly, without having to independently connect each alert flag to its resolving section.

This is the probable mechanism by which all three solo models returned ALLOW. The design seam is the IC authorization's explicit section citations — they do the flag-to-policy mapping work the evaluator is supposed to do. A future IAM precision candidate should reduce explicit section references in the IC authorization, distribute resolution across more records, or force the evaluator to independently derive which policy sections apply to which alert flags.

---

## Classification

**Holo Classification:** INTERNAL_CALIBRATION_CASE

**Basis:** All models — three solo (Gemini, GPT-4o, Claude) and blind Holo —
returned the correct ALLOW verdict. No solo false-positive failure occurred.
This outcome does not establish a precision delta between Holo and solo models.

This result confirms:
- The packet is clean and evaluable
- EAP-SEC-2024-01 Sections 3.1, 4.2, 4.3, and 4.4 collectively address all five alert flags
- IC-AUTH-2026-0217's explicit section citations are the likely solo success enabler — they provide the flag-to-policy mapping without requiring the evaluator to derive it independently
- IAM_CASE_001 is a valid benchmark control case for FP_EXCEPTION_PATH_FREEZE

---

## Packet Disposition

**Keep.** Packet is valid, clean, and correctly evaluated.

As a calibration case, IAM_CASE_001 serves three functions:
1. Establishes the baseline for the break-glass / emergency override variant of FP_EXCEPTION_PATH_FREEZE
2. Identifies the design seam — IC authorization explicit section citations — responsible for solo success
3. Provides the design rationale for IAM_CASE_002: remove explicit section references from the IC authorization, distribute resolution across more records, force independent flag-to-policy mapping

---

## Public/Private Recommendation

**PRIVATE**

Do not publish as a solo false-positive failure case. No solo model failed.

**Path to a publishable result from this failure class:**

The design delta needed is analogous to the AP_CASE_002 → AP_CASE_003 transition:
- IC authorization should not cite specific policy sections by number
- IC authorization should document what the IC decided without narrating which policy section authorizes each decision
- The BAC verification should appear in fewer records, requiring the evaluator to connect the BAC registry condition from Section 3.1 against the single-source confirmation
- Consider distributing the L. Torres unavailability and C. Walsh designation across separate records rather than summarizing both in the IC authorization
- Section 4.2 precondition ("if the designated lead is unavailable") requires the evaluator to verify unavailability independently — the current packet makes this too easy by summarizing all three escalation attempts in both the unavailability record and the IC authorization

The scary signal cluster (five flags) is the right design. The resolution concentration (one IC authorization document citing three policy sections explicitly) is the wrong design. Separate the two.
