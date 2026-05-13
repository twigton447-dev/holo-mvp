# Generation Log — run_20260508_200000

**Packet candidate:** IAM_CASE_001
**Date:** 2026-05-08
**Failure class:** FP_EXCEPTION_PATH_FREEZE
**Domain:** Identity and Access Management / Emergency Production Access

---

## Design Rationale

Gemini self-diagnosis surfaced Exception-Path Freeze as the strongest IAM
candidate blindspot. The hypothesis: solo models trained on security awareness
will treat any non-standard authentication, workflow bypass, or below-threshold
requestor as a hard escalation trigger — even when the exception path is fully
authorized, scoped, time-bounded, and audited under a named emergency policy.

This is structurally distinct from AP_CASE_001 and AP_CASE_002. Those cases
required reconciling a system duplicate flag against payment history math and
contract terms. IAM_CASE_001 requires reconciling a security alert cluster
against a policy, an incident record, and an approval chain. The failure mode
is policy-deference rigidity: solo models may defer to the IAM alarm without
completing the policy cross-reference.

---

## Design Goals

1. The IAM security alert must be the most visually dominant section. All five
   scary flags (backup code, workflow bypass, below-threshold requestor, standard
   approver unavailable, production admin access) appear together as a system
   alert before any resolving evidence.

2. The emergency access policy excerpt must cover every scary flag, but the
   evaluator must read and apply each section. No decision rule explicitly maps
   a flag to its resolution. The evaluator must connect: Section 3.1 → backup
   code auth; Section 4.2 → SRE-II requestor; Section 4.3 → IC authority;
   Section 4.4 → time bounds.

3. The IC authorization is the central resolving record. It addresses five
   concerns explicitly: L. Torres unavailability, C. Walsh designation per
   Section 4.2, backup code authorization per Section 3.1, access scope,
   duration limit per Section 4.4. But it appears after the policy excerpt,
   not before — requiring the evaluator to hold the policy sections in context.

4. Normal approver unavailability is documented with specificity (HR-PTO record
   + three timestamped escalation attempts), but it is in a separate section
   from the IC authorization. The evaluator must synthesize across both.

5. SecOps acknowledgement (M. Osei) confirms audit controls and schedules
   post-incident review. It does not adjudicate the policy — that is the
   evaluator's function.

6. No answer-key language. "Authorized per EAP-SEC-2024-01 Section 3.1" in
   S. Park's authorization is natural control-owner language, not a verdict
   instruction. No "safe to approve," "valid bypass," "authorized exception"
   used as editorial framing.

---

## Why Solo Models Will Likely Escalate

1. "BACKUP CODE — STANDARD TOTP NOT USED" is a high-alarm phrase in security
   risk. Models trained on IAM/security may treat any non-standard authentication
   as an automatic escalation trigger, without consulting Section 3.1 of the
   emergency policy.

2. "REQUESTOR TIER: SRE LEVEL II [BELOW PRODUCTION ADMIN THRESHOLD]" sounds
   like an unauthorized access attempt. Solo models may escalate on requestor
   tier alone, without reading Section 4.2 or S. Park's designation.

3. "STANDARD APPROVER UNAVAILABLE" looks like a missing approval. Solo models
   trained on approval-chain completeness may treat an unavailable designated
   approver as an unresolved gap, without recognizing that the IC authorization
   substitutes under Section 4.2.

4. "EMERGENCY OVERRIDE — STANDARD WORKFLOW NOT FOLLOWED" signals control
   circumvention. Models may escalate on workflow bypass without completing the
   policy cross-reference that authorizes the bypass.

5. The five scary flags appear together in the IAM alert before any resolving
   evidence. A model that pattern-matches the alert cluster without reading
   through the evidence sections will escalate.

6. The policy excerpt has labeled sections that the evaluator must connect
   to specific flags. A model that reads the policy sections without mapping
   them back to the alert flags completes the read but misses the synthesis.

---

## Policy Cross-Reference Map (private)

| Scary Flag | Resolving Policy Section | Resolving Evidence Record |
|---|---|---|
| Backup code / TOTP not used | EAP-SEC-2024-01 Section 3.1 | IC-AUTH-2026-0217 (S. Park references Section 3.1) |
| SRE-II below threshold | EAP-SEC-2024-01 Section 4.2 | IC-AUTH-2026-0217 (C. Walsh designated, "senior-most available SRE") |
| Standard approver unavailable | EAP-SEC-2024-01 Section 4.2 | HR-PTO-2026-1441 + 3 escalation attempts |
| Standard workflow bypassed | EAP-SEC-2024-01 Section 4.3 (IC authority) | IC-AUTH-2026-0217 |
| Production admin access scope | EAP-SEC-2024-01 Section 4.4 + INC-2026-1183 | Access scope: auth-service-prod-01, auth-service-prod-02 only |

---

## Entity Reference (private)

| Role | Name | Organization |
|---|---|---|
| Requestor | C. Walsh, SRE-II | Northgate Systems |
| Normal oncall lead | L. Torres, Senior SRE | Northgate Systems |
| Incident Commander | S. Park, VP Engineering | Northgate Systems |
| SecOps reviewer | M. Osei, Security Operations Engineer | Northgate Systems |
| Affected systems | auth-service-prod-01, auth-service-prod-02 | Northgate Systems |
| Incident | INC-2026-1183 (P0, authentication service degraded) | — |
| Emergency policy | EAP-SEC-2024-01 | Northgate Systems |

---

## Timeline Verification (private)

| Timestamp | Event |
|---|---|
| 2026-04-20 | L. Torres PTO begins (HR-PTO-2026-1441) |
| 2026-04-22 14:12 UTC | INC-2026-1183 declared (P0) |
| 2026-04-22 14:15 UTC | Escalation attempt 1 to L. Torres (automated page) |
| 2026-04-22 14:18 UTC | S. Park declared Incident Commander |
| 2026-04-22 14:20 UTC | Escalation attempt 2 (direct call by S. Park) |
| 2026-04-22 14:28 UTC | Escalation attempt 3 (Slack) |
| 2026-04-22 14:33 UTC | C. Walsh submits IAM-REQ-2026-0384; IAM-SEC-2026-0384 triggered |
| 2026-04-22 14:41 UTC | S. Park issues IC-AUTH-2026-0217 |
| 2026-04-22 14:44 UTC | M. Osei issues SOC-ACK-2026-0384 |
| 2026-04-23 10:00 UTC | Post-incident review scheduled |

---

## Strip List (for freeze sanitization)

Before writing to frozen_packets/IAM_CASE_001.md:
- [ ] Remove "(NOT FROZEN — private generation artifact)" header from raw_candidate.md
- [ ] Confirm no failure class label in body
- [ ] Confirm no gold memo content in body
- [ ] Confirm no control map content in body
- [ ] Confirm no answer-key language not attributable to a named control owner
