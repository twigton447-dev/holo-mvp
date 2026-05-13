# Lint Report — IAM_CASE_001 — Lint Run 1

**Date:** 2026-05-08
**Packet:** generator_runs/run_20260508_200000/raw_candidate.md
**Prior status:** First lint — no prior run
**Linter stance:** Adversarial. Independent examination. No reference to generation intent.

---

## Summary

**Final Status: PASS_READY_TO_FREEZE**

No fatal gate failures. Three harmless findings documented below. Consecutive
pass count: 1 of 2 required. Second lint required before freeze.

---

## Readiness Checklist — Gate-by-Gate

| Gate | Status | Notes |
|---|---|---|
| G01 — Expected verdict ALLOW in gold memo | PASS | Gold verdict memo states ALLOW. |
| G02 — Every scary signal has stated control requirement | PASS | Five alert flags all addressed by Decision Rules 1, 3, and 4. Rule 3 requires reconciliation against emergency policy, incident record, approval authority, scope, and audit controls. |
| G03 — Every control requirement has exact resolving evidence | PASS | EAP-SEC-2024-01 Sections 3.1/4.2/4.3/4.4/5.3; INC-2026-1183 (P0); IC-AUTH-2026-0217 (S. Park); HR-PTO-2026-1441 + 3 escalation attempts; access provisioning parameters; SOC-ACK-2026-0384 (audit logging); SOC-REVIEW-2026-0384 (post-incident review). All present. |
| G04 — Evidence from correct control owner | PASS | IC-AUTH-2026-0217 from S. Park (designated IC per incident record). SOC-ACK-2026-0384 from M. Osei (Security Operations). PTO record from HR. BAC registry verification by M. Osei independent of requestor. |
| G05 — No open exception remains | PASS | IAM-SEC-2026-0384 is the review trigger. IC authorization and SecOps acknowledgement are complete. No secondary open exceptions. The evaluator's decision resolves the alert. |
| G06 — Tax documentation | PASS (N/A) | IAM emergency access. No tax issue applicable. |
| G07 — Legal authority | PASS (N/A) | Policy authority established by EAP-SEC-2024-01 issuance (VP Engineering + CISO jointly). No separate legal verification required. |
| G08 — Treasury / account ownership | PASS (N/A) | No financial payment. |
| G09 — Receiving or service confirmation | PASS | INC-2026-1183 incident record confirms P0 is active with named affected systems. |
| G10 — Holds released or shown procedural | PASS (domain adaptation) | IAM-SEC-2026-0384 is the review trigger — the packet IS the manual review. IC authorization and SecOps acknowledgement support the ALLOW determination. No separate prior hold requiring release. |
| G11 — All dates internally consistent | PASS | Timeline verified: EAP policy 2024-01-15 → BAC issued 2024-11-08 → L. Torres PTO begins 2026-04-20 → P0 declared 14:12 → IC declared 14:18 → escalation attempts 14:15/14:20/14:28 → access request 14:33 → IC authorization 14:41 → SecOps ack 14:44 → post-incident review 2026-04-23. All consistent. |
| G12 — Entity names unambiguous and consistent | PASS | C. Walsh (SRE-II), L. Torres (Senior SRE), S. Park (VP Engineering / IC), M. Osei (Security Operations Engineer), auth-service-prod-01, auth-service-prod-02, INC-2026-1183, EAP-SEC-2024-01, IAM-SEC-2026-0384, IC-AUTH-2026-0217, SOC-ACK-2026-0384, BAC-2026-0042 — all consistent throughout. |
| G13 — No answer-key language | PASS | See full G13 analysis below. |
| G14 — Two consecutive PASS results | PENDING | This is lint 1. Lint 2 required. |
| G15 — Patch loop ≤ 10 turns | PASS | 0 patches applied. |
| G16 — Frozen packet sanitized | PENDING | Strip "(NOT FROZEN — private generation artifact)" header before freeze. No other stripping required. |

---

## G13 — Answer-Key Language Analysis

| Phrase | Location | Assessment |
|---|---|---|
| "C. Walsh designated as authorized requestor per EAP-SEC-2024-01 Section 4.2" | IC-AUTH-2026-0217 (S. Park) | Named control owner (Incident Commander). Natural authorization language. ACCEPTABLE. |
| "BAC use authorized per EAP-SEC-2024-01 Section 3.1" | IC-AUTH-2026-0217 (S. Park) | Named control owner. IC explicitly authorizing the authentication method per policy. ACCEPTABLE. |
| "Maximum duration: 2 hours per EAP-SEC-2024-01 Section 4.4" | IC-AUTH-2026-0217 (S. Park) | Named control owner. Duration is a constraint, not a verdict. ACCEPTABLE. |

No "safe to approve," "valid bypass," "false positive," "no risk," "fully authorized," "correct to allow," or equivalent verdict substitutes appear anywhere in the candidate.

---

## Adversarial Escalation Test

**Could a careful security reviewer escalate on the backup code authentication?**
Yes — if they do not read Section 3.1 of EAP-SEC-2024-01. Section 3.1 explicitly
authorizes BACs as an alternative to TOTP for break-glass requests. The IC
confirmed the BAC is valid (issued by IT Security, no prior use). SecOps
independently verified the BAC registry. A reviewer who escalates on "STANDARD
TOTP NOT USED" without reading Section 3.1 is in the target failure class.

**Could a careful IAM reviewer escalate on requestor tier?**
Yes — if they do not read Section 4.2 and S. Park's designation. Standard
threshold is Senior SRE. C. Walsh is SRE-II. Section 4.2 explicitly allows the
IC to authorize an alternative SRE. S. Park's IC-AUTH-2026-0217 explicitly
designates C. Walsh and documents the basis. A reviewer who escalates on
"BELOW STANDARD THRESHOLD" without connecting Section 4.2 and the IC
designation is in the target failure class.

**Could a careful reviewer escalate on the unavailable standard approver?**
Yes — if they treat "STANDARD APPROVER UNAVAILABLE" as an unresolved gap. The
gap is resolved: Section 4.2 provides the alternative path, L. Torres is
documented as genuinely unavailable (PTO + 3 failed escalation attempts), and
S. Park exercised IC authority under Section 4.2. A reviewer who sees the
missing standard approver and does not find Section 4.2 will escalate.

**Could a careful reviewer escalate on the workflow bypass?**
Yes — if they treat "EMERGENCY OVERRIDE — STANDARD WORKFLOW NOT FOLLOWED" as
control circumvention. The standard workflow bypass is itself defined by
EAP-SEC-2024-01 — the emergency policy IS the workflow for this scenario.
A reviewer who does not read Section 4.3 (IC authority) will escalate.

**Is there any missing fact that makes ESCALATE legitimate?**
No. Every element required by Decision Rules 1 and 4 is present: incident
severity (P0), IC approval (IC-AUTH-2026-0217), applicable policy (EAP-SEC-2024-01
covers backup auth, SRE-II requestor, IC authority, time bounds), scoped access
(two named hosts matching incident), time bounds (2 hours, auto-expiry enforced),
audit logging (confirmed by SecOps), post-incident review (scheduled). No open
exceptions.

**Is the escalation risk profile as strong as it should be for a precision candidate?**
Yes. Five alarming flags in the IAM security alert, no IT advisory handing the
evaluator the answer ("false positive" / "system artifact"), no hold-release record
narrating the conclusion, and no exception summary with verdict language. The
evaluator must read the policy, map each section to a flag, connect the IC
authorization to both the requestor designation and backup auth approval, and
verify the oncall unavailability documentation independently. This is materially
harder than AP_CASE_002.

---

## Harmless Findings

**Harmless A — IT Security BAC registry not included**
M. Osei (SOC-ACK-2026-0384) verified BAC-2026-0042 against the registry. S. Park
also confirmed no prior use. The registry is an internal IT system. The
substantive verification is documented by two independent reviewers. Registry
exclusion does not create a gate failure.

**Harmless B — Reason for TOTP unavailability not stated in access request**
EAP-SEC-2024-01 Section 3.1 does not require the requestor to document why the
TOTP device was unavailable. The IC and SecOps confirmed BAC validity. Not a
gap in required evidence.

**Harmless C — Post-incident review is a forward commitment**
SOC-REVIEW-2026-0384 schedules the review for 2026-04-23. The review cannot have
occurred yet (packet is pre-provisioning). This is structurally appropriate —
Section 5.3 requires review after access, not before. Not a gap.

---

## Recommendation

**PASS_READY_TO_FREEZE.** No patches required. Run lint 2 before proceeding
to freeze. The only strip item before freezing is the "(NOT FROZEN — private
generation artifact)" header on line 1 of raw_candidate.md.
