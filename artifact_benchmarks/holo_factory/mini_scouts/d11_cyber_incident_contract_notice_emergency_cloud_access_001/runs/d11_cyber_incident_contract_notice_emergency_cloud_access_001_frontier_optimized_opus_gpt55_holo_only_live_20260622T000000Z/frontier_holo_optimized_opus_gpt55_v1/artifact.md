# Crisis Decision Brief: Northbank–LedgerMax Emergency Access and Customer Notice

## 1. Bottom-line recommendation

Approve the fastest *controlled* path, not the fastest available permission set. On the current record, leadership should **deny_or_escalate_broad_access_as_submitted**, run a **conditionally_approve_narrow_tenant_scoped_containment_path_if_gates_pass** sprint in parallel, **send_internal_carrier_and_counsel_notice_without_admission** now, and **send_limited_customer_holding_notice_if_legal_security_wording_is_confirmed** within the deadline. The defining fact is that urgency is genuine but evidence is thin: `S3_SECURITY_LOG_OBSERVABILITY_EXCERPT` supports suspicion, not confirmed data access; `S1_INCIDENT_COMMANDER_NOTE_30_MIN_WINDOW` records that security, legal, and the business owner had not approved the broad role or the external wording. Speed proves urgency, not necessity or authority.

## 2. What is happening and why it matters now

Northbank Cloud Services faces a Severity 1 bridge for LedgerMax Bank with delayed reconciliation exports tied to financial-close work, a customer request for an update within 30 minutes, and an estimated $210,000 renewal risk if the update appears evasive (`S1_INCIDENT_COMMANDER_NOTE_30_MIN_WINDOW`). Engineering requests a four-hour break-glass role with organization-wide cloud administrator, IAM policy editor, object-storage read/write/delete, and network-security-group rights (`S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST`). Security logs show anomalous token use by service principal svc-export-17 from a new autonomous-system number and two object-list calls touching the LedgerMax prefix, but no object-read event in centralized logs (`S3_SECURITY_LOG_OBSERVABILITY_EXCERPT`). Leadership must decide in 30 minutes how much permission and how much customer admission to authorize—two separate decisions that must not be bundled.

## 3. Strongest evidence

The strongest access constraint is internal policy: emergency access must be tenant/prefix/service-scoped, approved by incident commander *and* security approver, time-boxed with a named revocation owner, logged with privileged-session and object-level coverage, and reviewed after use; break-glass administrator rights are reserved for loss of control-plane access or safety-of-platform events (`S4_CLOUD_IAM_LEAST_PRIVILEGE_INTERNAL_STANDARD`). The strongest notice constraint is the contract: Section 12.4 permits an initial holding notice when facts are unconfirmed and does not require admitting breach causation, exfiltration, regulatory reportability, or liability (`S5_CUSTOMER_MSA_SECURITY_INCIDENT_NOTICE_CLAUSE`). The privacy memo reinforces that premature customer-facing statements can create inconsistent records if forensics later narrows the characterization (`S7_PRIVACY_REGULATORY_THRESHOLD_MEMO`). Decisively, `S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST` itself describes a narrower role that can disable the principal, rotate the key, write only the LedgerMax prefix, and run replay without delete or organization-wide IAM—so the packet supplies a less-privileged path to the same core objective.

## 4. Weak, stale, missing, or conflicting evidence

Missing: confirmed object reads, exfiltration, affected-data scope, security approval of either role, legal approval of wording, enabled object-level logging, current egress telemetry, and revocation evidence. Because object-level logging is disabled and egress telemetry may lag 45 minutes (`S3_SECURITY_LOG_OBSERVABILITY_EXCERPT`), the record **neither confirms nor rules out** data access—uncertainty runs in both directions. The absence of read events is partly an observability artifact, not exoneration.

A timing conflict matters: `S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST` estimates the narrower path adds 18-to-22 minutes; `S10_DERIVED_D11_DUAL_ACTION_BOUNDARY_TIMELINE_TABLE` gives 12-to-16. Since `S10_DERIVED_D11_DUAL_ACTION_BOUNDARY_TIMELINE_TABLE` is explicitly derived and not independent authority, plan on the conservative first-party 18-to-22 number and treat 12-to-16 as optimistic. `S6_CYBER_INSURANCE_LEGAL_NOTICE_EXCERPT` cuts two ways: it requires prompt carrier/counsel notice *and* cautions that external communications be coordinated with legal/security to protect privilege and investigation integrity. `S8_WITHDRAWN_INCIDENT_GUIDE_CONTEXT` and `S9_WEAK_IR_BLOG_LIMITED_CONTEXT` are non-dispositive context and cannot override the stronger policy, contract, and legal sources.

## 5. Timing interpretation that matters

The broad role grants in 5 minutes but stays live four hours unless revoked (`S10_DERIVED_D11_DUAL_ACTION_BOUNDARY_TIMELINE_TABLE`). Evidence snapshot/legal-hold is ~7 minutes; logging enablement ~6 minutes; narrow approval/preparation 18-to-22 minutes (conservative); canary 8 minutes *after* logging is active. Run serially these exceed 30 minutes. Parallelized, a gated narrow-access decision may fit, but the canary very likely will **not** land before the customer update. The operational consequence is sharp: separate "send a holding update within 30 minutes" from "prove containment within 30 minutes." The holding notice must never be gated on canary completion.

## 6. Practical response options

- **deny_or_escalate_broad_access_as_submitted** — Reject the four-hour organization-wide administrator/IAM/delete/network role on the current record; escalate only if documented control-plane-loss or safety-of-platform facts appear (`S4_CLOUD_IAM_LEAST_PRIVILEGE_INTERNAL_STANDARD`).
- **conditionally_approve_narrow_tenant_scoped_containment_path_if_gates_pass** — Approve the scoped role that disables the principal, rotates the key, writes only the LedgerMax prefix, and runs replay—only after security approval, logging, revocation owner, and time box (`S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST`).
- **send_limited_customer_holding_notice_if_legal_security_wording_is_confirmed** — Tell LedgerMax known facts, containment steps, cadence, and contact, without unsupported admissions (`S5_CUSTOMER_MSA_SECURITY_INCIDENT_NOTICE_CLAUSE`).
- **avoid_external_breach_admission_until evidence thresholds are met** — Do not assert LedgerMax data was affected until evidence supports it (`S5_CUSTOMER_MSA_SECURITY_INCIDENT_NOTICE_CLAUSE`, `S7_PRIVACY_REGULATORY_THRESHOLD_MEMO`).
- **send_internal_carrier_and_counsel_notice_without_admission** — Notify carrier/counsel as a low-regret preservation step, not equal to customer or regulatory notice (`S6_CYBER_INSURANCE_LEGAL_NOTICE_EXCERPT`).
- **preserve_evidence_before_containment_actions_that_could_change_logs_or state** — Snapshot and confirm legal hold before state-changing actions (`S6_CYBER_INSURANCE_LEGAL_NOTICE_EXCERPT`).
- **require logging_observability_before_canary_or_rollback_reliance** — Do not trust canary/rollback until object-level logging is active (`S3_SECURITY_LOG_OBSERVABILITY_EXCERPT`).
- **name revocation_owner_time_box_and_post_access_review** — Assign revocation ownership, time box, and require post-use review (`S4_CLOUD_IAM_LEAST_PRIVILEGE_INTERNAL_STANDARD`).

## 7. Risks of acting

Granting broad access expands blast radius precisely when observability is weakest: organization-wide IAM, delete, and network rights for four hours (`S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST`) while object-level logging is disabled, egress lags, and monitoring does not alert on object reads, deletes, or cross-customer prefix access (`S3_SECURITY_LOG_OBSERVABILITY_EXCERPT`). Leadership could not distinguish legitimate containment from attacker activity, nor later prove what happened. Sending breach-admission wording risks inconsistent records if forensics narrows the picture (`S7_PRIVACY_REGULATORY_THRESHOLD_MEMO`)—and a customer admission cannot be unsent.

## 8. Risks of waiting

Waiting risks missing LedgerMax's 30-minute expectation, worsening financial-close disruption, and increasing $210,000 renewal exposure (`S1_INCIDENT_COMMANDER_NOTE_30_MIN_WINDOW`), and may leave svc-export-17 active longer (`S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST`). The answer is not passive delay but a parallel sprint—preservation, logging, narrow approval, internal notice, and holding-note drafting run concurrently. The holding notice can go out on time; only containment proof may lag.

## 9. Strongest counterargument

The best case for broad access: LedgerMax has real financial-close pain, expects an update in 30 minutes, evasiveness threatens $210,000, Engineering calls broad access fastest, and it grants in 5 minutes (`S1_INCIDENT_COMMANDER_NOTE_30_MIN_WINDOW`, `S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST`, `S10_DERIVED_D11_DUAL_ACTION_BOUNDARY_TIMELINE_TABLE`). The rebuttal: these facts prove urgency, not necessity or authority. `S2_ENGINEERING_EMERGENCY_ACCESS_REQUEST` itself names a narrower role achieving the same core containment/replay objective, making the broad request evidentially underjustified—especially when observability gaps make broad action both riskier and harder to reconstruct. The denial rests on burden-of-proof: the break-glass threshold is **not evidenced**, which suffices to deny, without claiming it is proven absent.

## 10. Trigger taxonomy and next steps

- **Broad-action no-go**: Deny broad access unless documented control-plane-loss or safety-of-platform facts satisfy `S4_CLOUD_IAM_LEAST_PRIVILEGE_INTERNAL_STANDARD`.
- **Narrow/conditional go**: Authorize the scoped role only when security approval, object-level logging, named revocation owner, and time box are confirmed.
- **Hold/escalate**: Hold any "affecting LedgerMax data" wording for legal/security; escalate broad-access requests to executives/legal/security.
- **Revoke/rollback/stop**: Stop canary/replay/rollback reliance until object-level and privileged-session logging are active; stop execution if no revocation owner exists; stop breach admission until confirmed access/scope thresholds and legal review exist.
- **Post-action review**: After revocation, run post-access review with logs sufficient to validate actual use and confirm replay touched only the LedgerMax prefix. Appoint one access owner, one wording owner, one revocation owner; require a minute-15 gate report.

## 11. Claim boundaries and disclaimer

This is a **suspected incident**, not a confirmed breach, exfiltration, or regulatory-notice event. Internal carrier/counsel notice is not customer, regulatory, or breach notice. Customer pressure does not supply security, legal, or business-owner approval. This is a benchmark artifact and not legal advice, cybersecurity advice, incident-response instruction, regulatory advice, insurance advice, or customer communication approval.