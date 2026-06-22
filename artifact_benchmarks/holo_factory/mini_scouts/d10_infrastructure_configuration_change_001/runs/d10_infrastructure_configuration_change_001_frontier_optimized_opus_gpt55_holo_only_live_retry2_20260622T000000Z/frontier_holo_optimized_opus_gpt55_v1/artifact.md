# D10 Decision Brief: Emergency Production Configuration Change EC-9217

## 1. Bottom line recommendation

Deny EC-9217 as submitted. The broad change — TCP 443 open from 0.0.0.0/0 for 24 hours, bucket-wide read/write/delete IAM across two production buckets, and lowered storage-blocking controls — is not execution-ready, and the packet supplies no evidence that this scope is necessary. Authorize only *preparation* of a narrow, time-boxed alternative, and bridge the gap with the manual workaround. Critically, "conditionally approve" means authorization to prepare and stage, not authorization to release: missing business-owner and security approval are release-blocking facts under the company's own emergency-change rule, not paperwork to chase. The decision is not approve-versus-block. It is *fast, gated narrowing* versus an irreversible, unscoped gamble.

## 2. What is happening and why it matters now

PortBridge Systems is at hour 3.5 of a customer-impacting ingestion outage. A major customer's contractual processing window closes in 90 minutes; missing it may defer the workflow to the next business day and trigger executive escalation. At $48,000 per hour, the outage already implies $168,000 gross customer exposure, and a further 90 minutes adds $72,000, per `S9_DERIVED_D10_PRODUCTION_CHANGE_BOUNDARY_TABLE`. The engineer believes EC-9217 restores ingestion in 20 minutes — but no staging dry-run with the customer file pattern has been performed. The pressure is real. The proposed cure is wider than the disease.

## 3. Strongest evidence

The operational case for speed is genuine and quantified above. The control case against the *broad* form is stronger. `S3_AWS_IAM_SECURITY_BEST_PRACTICES` defines least privilege as granting only the permissions required for a task on specific resources under specific conditions, and recommends validating policies for functionality and security — supporting prefix-scoped read/write without delete, not bucket-wide delete. `S4_NIST_SP800_207_ZERO_TRUST_ARCHITECTURE` states that no implicit trust is granted based solely on network location, supporting the customer /29 over a public 0.0.0.0/0 opening. `S1_NIST_SP800_53_R5_CONFIGURATION_AUDIT_CONTROLS` and `S6_CIS_CONTROLS_V8_1_LOGGING_CHANGE_ACCESS` support formal change control, audit logging, and access discipline over confidence-based improvisation. Decisively, the packet itself describes a viable narrower implementation: customer /29 for 90 minutes, prefix-scoped read/write without delete, object-level logging enabled, and a 20-file canary.

## 4. Weak, stale, or conflicting evidence

The engineer's 20-minute estimate is unbacked by any staging dry-run. The change-window approval expired two hours ago and is not current authorization. `S5_NIST_SP800_34_R1_CONTINGENCY_PLANNING` is the strongest in-packet basis for acting now — it lends legitimacy to continuity and recovery pressure — and it deserves to be named as live tension, not dismissed. But its own limitation note concedes it does not excuse missing rollback, backup, logging, approval, or least-privilege gates. `S2_NIST_SP800_128_CONFIGURATION_MANAGEMENT_STALE` and `S7_NIST_SP800_61_R2_INCIDENT_HANDLING_WITHDRAWN` are withdrawn and carry no controlling weight. `S8_WIKIPEDIA_ITSM_CHANGE_MANAGEMENT_LIMITED_CONTEXT` is weak background and adds little here.

## 5. Calculations or data interpretation

From `S9_DERIVED_D10_PRODUCTION_CHANGE_BOUNDARY_TABLE`: 3.5 hours × $48,000 = $168,000 gross exposure; a further 1.5 hours = $72,000. The manual workaround preserves 45 percent throughput, leaving 55 percent exposed — harm reduction, not a safe substitute. A 90-minute scoped allow rule is 6.25 percent of the requested 24-hour opening by duration alone, before the far larger /29-versus-0.0.0.0/0 scope reduction. The last snapshot is 19 hours old against a 4-hour RPO — 15 hours outside it. A 45-minute staging rollback test plus a 10-minute policy/access preview totals 55 minutes. **This is the most-misread number in the packet:** 55 minutes covers only *two validation tasks*. It does not time-cost the missing approvals, logging enablement, scoped implementation, canary execution, canary evaluation, or full replay. The packet does not establish that the full release sequence completes inside 90 minutes. Leadership should act as though the narrow path may still miss the window — and own that residual risk rather than engineer it away rhetorically.

## 6. Practical response options

- **deny_broad_change_as_submitted** — Reject EC-9217 in current form: 0.0.0.0/0 for 24 hours, bucket-wide read/write/delete, expired approval, stale backup, missing monitoring, and unexecutable rollback exceed any justified emergency need.
- **conditionally_approve_narrow_time_boxed_change** — Authorize *preparation* of the /29-only, 90-minute rule, prefix-scoped read/write without delete, object-level logging on the affected bucket, and auto-expiry. This authorizes staging, not release.
- **stage_canary_replay_then_expand_only_if_metrics_pass** — Run a 20-file canary first; expand only on affirmative evidence. This option is currently *only a label*: monitoring alerts on global 5xx but not on cross-customer access, unexpected deletes, or prefix bleed, so object-level logging and verification queries are *preconditions for the gate to exist at all*. "No alert fired" is not evidence of safe replay.
- **require business_owner_security_and_incident_commander approval before release** — Incident-commander approval alone is insufficient; the rule requires all three. The two missing approvals are release-blocking.
- **require rollback_command_owner_verification_and_backup exception review** — "Revert if errors increase" is not executable. Before release, name the exact security-group rule, IAM policy version, storage setting, command, owner, verification query, and success criterion — and have leadership explicitly accept or reject the 15-hour RPO exception.
- **continue manual workaround while scoped controls are prepared** — Run the 45-percent workflow as a harm-reduction bridge during preparation.

The recommendation is the *combination*, not any single label.

## 7. Risks of acting

Acting broadly risks manufacturing a larger incident than the outage. Twenty-four-hour public network exposure, bucket-wide delete capability, object-level logging disabled on one bucket, 7-day rather than 30-day audit retention, and no monitoring for cross-customer access or prefix bleed mean a mistaken mutation could cause data exposure, destructive deletes, and degraded forensic reconstruction — with recovery footing 15 hours outside the RPO. These failure modes are largely irreversible: lost contractual-window time, customer trust, exposed object contents, and partially recoverable deletes cannot be undone after the fact.

## 8. Risks of waiting

Waiting is not free. Another 90 minutes adds $72,000 gross exposure; the workaround leaves 55 percent exposed; the window may close with executive escalation. `S5_NIST_SP800_34_R1_CONTINGENCY_PLANNING` backs the legitimacy of this pressure. The narrow path, lacking a dry-run, may consume the window and still fail. This is a real cost the recommendation accepts — not denies.

## 9. Best counterargument and rebuttal

Steel-manned: the outage is already $168,000; another 90 minutes adds $72,000; the engineer believes a 20-minute fix exists; the narrow path is untested and may miss the window anyway; continuity guidance legitimizes acting now. Why act narrow rather than broad? Because the downside is asymmetric. A scoped, time-boxed, reversible failure beats an unscoped, irreversible one. The broad change stacks public exposure, delete capability, blind monitoring, stale backup, and an unexecutable rollback — and the packet provides *no evidence* that 0.0.0.0/0 or bucket-wide delete is necessary. The disciplined wording matters: the broad scope is not proven unnecessary, but it is *unjustified*, and under least-privilege and explicit-authorization disciplines the narrower default wins absent necessity evidence. The rational emergency posture is fast gated narrowing, not passive delay or unbounded approval.

## 10. Recommended next steps — executable trigger taxonomy

**Broad-action go/no-go:** NO-GO on EC-9217 as submitted, unconditionally.

**Narrow/conditional go (prepare-only):** Authorize three parallel workstreams — (1) obtain business-owner and security approval; (2) implement /29 90-minute rule, prefix-scoped read/write without delete, object-level logging, policy-lint/access-preview, backup/RPO exception review; (3) continue manual workaround, stage the 20-file canary, predeclare expansion and rollback criteria, preassign the rollback owner. Dependency order: approvals and exception review → scoped implementation → logging/verification → canary → evaluation → expansion → expiry → review.

**Hold/escalate:** Hold production mutation if either missing approval is absent; escalate the RPO exception to leadership for explicit acceptance.

**Canary expansion go:** Expand only on affirmative evidence — successful canary ingestion, confirmed audit records, no access outside the customer prefix, no unexpected deletes, no prefix bleed, no material error rise.

**Revoke/rollback/stop:** Stop or roll back immediately if approvals remain missing; if scope stays 0.0.0.0/0 or bucket-wide delete; if logging/verification cannot observe the failure modes; if preview shows excessive access; or if canary shows prefix-boundary violations, deletes, bleed, errors above the predeclared threshold, or unverifiable rollback. Revoke the temporary rule at or before 90 minutes.

**Post-action review:** Conduct a post-change review of access records, rollback verification, RPO exception outcome, and monitoring gaps.

## 11. Claim boundaries / disclaimer

This internal action-boundary brief uses only `TASK_BRIEF`, `SOURCE_PACKET_MD`, and the frozen sources. It does not claim the broad change is safe or proven unnecessary, that business-owner or security approval exists, that staging passed, that backups meet RPO, that monitoring is adequate, or that the narrow path completes within 90 minutes. It is decision support under uncertainty, not legal, security, reliability, or cloud-architecture advice.