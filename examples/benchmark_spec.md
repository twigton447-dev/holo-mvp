# Holo Benchmark Scenario Library — Part 2
## Scenarios 7–12 + Audit + Design Notes

---

## Overview

This document contains the specification, design notes, and audit commentary for scenarios 7–12 of the Holo Benchmark Scenario Library. These scenarios cover two buckets:

- **subtle_fraud** — Fraudulent payments where all surface signals are plausible and the fraud is detectable only through cross-field reasoning, metadata analysis, or organizational graph validation.
- **false_positive_trap** — Legitimate payments that contain multiple surface-level fraud indicators, designed to test whether the system can distinguish genuine context from manufactured urgency/anomaly.

Each scenario JSON lives in `examples/scenarios/` named by its `scenario_id`.

---

## Scenario Index (Part 2: Scenarios 7–12)

| ID | Title | Category | Difficulty | Expected Verdict |
|----|-------|----------|------------|-----------------|
| BEC-SUBTLE-001 | Thread Hijack with Plausible Continuity | subtle_fraud | high | ESCALATE |
| BEC-SUBTLE-002 | Routing Change Buried in Routine Status Update | subtle_fraud | high | ESCALATE |
| BEC-SUBTLE-003 | Approval-Chain Compromise with Clean Surface | subtle_fraud | high | ESCALATE |
| BEC-FP-001 | Suspicious-Looking but Legitimate Rush Invoice | false_positive_trap | high | ALLOW |
| BEC-FP-002 | Vendor Domain Migration with Valid Notification Trail | false_positive_trap | high | ALLOW |
| BEC-FP-003 | Header Anomaly from Legitimate Email Infrastructure Change | false_positive_trap | high | ALLOW |

---

## Design Notes

### The Core Thesis Being Tested

These scenarios are designed to test whether Holo's architecture — **shared-context, compounding postmortems by structurally independent models governed by a Context Governor** — produces a measurable advantage over:

1. Solo one-pass systems
2. Solo multi-pass self-critique systems
3. Parallel multi-LLM sign-off (no shared context)
4. Sequential multi-LLM chains (no governor)

The wedge is **Business Email Compromise (BEC) / invoice-payment intercept** because:
- It is the highest-dollar-value fraud category in enterprise AP operations
- The most sophisticated attacks are undetectable by any single signal
- Detection requires **conjunctive reasoning** across multiple independent signal classes
- False positives destroy operational trust — so precision matters as much as recall

### Why Subtle Fraud Scenarios Are Hard

Each `subtle_fraud` scenario is designed so that:
- Every **surface signal** (email body, tone, domain, auth) is clean or explainable
- Every **individual anomaly** is deniable in isolation
- The fraud is only detectable through the **conjunction** of multiple weak signals across different signal classes

This is specifically designed to differentiate architectures. A system that processes signals independently (even multiple models in parallel without shared context) may miss the conjunction. A system where structurally independent models compound their postmortems into shared context — and a governor reasons about correlations between signals — should surface the pattern.

**BEC-SUBTLE-001** is the canonical test case. It is the scenario the entire benchmark is built around.

### Why False Positive Traps Are Hard

Each `false_positive_trap` scenario is designed so that:
- Multiple **escalation criteria fire simultaneously** (urgency language, off-cadence amount, domain change, auth anomaly)
- Each suspicious signal has a **legitimate contextual explanation** documented elsewhere in the payload
- A system that sums independent risk factors without reading causation will over-trigger

The FP scenarios test the other side of the same capability: **contextual reasoning**, not just signal aggregation.

### Architecture Differentiation

The scenarios are annotated with `architecture_differentiation_notes` in `scoring_targets` that predict how each architecture will perform. The key predictions:

| Scenario | Solo One-Pass | Solo Multi-Pass | Parallel Multi-LLM | Sequential Chain | Holo Full |
|----------|--------------|-----------------|-------------------|-----------------|-----------|
| BEC-SUBTLE-001 | ALLOW (FN) | ALLOW/ESCALATE | ESCALATE (partial) | ESCALATE (partial) | ESCALATE |
| BEC-SUBTLE-002 | ALLOW (FN) | ALLOW/ESCALATE | ESCALATE (partial) | ESCALATE | ESCALATE |
| BEC-SUBTLE-003 | ALLOW (FN) | ALLOW (FN) | ESCALATE | ESCALATE | ESCALATE |
| BEC-FP-001 | ESCALATE (FP) | ESCALATE (FP) | ESCALATE (FP) | ALLOW/ESCALATE | ALLOW |
| BEC-FP-002 | ESCALATE (FP) | ALLOW | ALLOW | ALLOW | ALLOW |
| BEC-FP-003 | ESCALATE (FP) | ALLOW/ESCALATE | ALLOW | ALLOW | ALLOW |

### Scoring Methodology

Each scenario specifies `required_evidence_cited` in `scoring_targets`. A verdict is only scored as correct if:
1. The verdict matches `expected_verdict`
2. The system cites at least the required evidence signals

This prevents correct-verdict-wrong-reasoning from scoring as a pass.

---

## Audit Notes

### Signal Strength Taxonomy

Evidence signals are rated by strength:
- **strong** — definitive if present; absence/mismatch is conclusive
- **moderate** — significant flag; requires corroboration
- **weak** — worth noting; insufficient alone; raises suspicion when combined

A correct ESCALATE verdict requires citing at least one **strong** signal or two **moderate** signals from `required_evidence_cited`.

### False Negative Risk vs. False Positive Risk

Each scenario rates the primary failure mode:
- **FN Risk: High** — the system will likely ALLOW a fraudulent payment
- **FP Risk: High** — the system will likely ESCALATE a legitimate payment

The benchmark is designed to expose both failure modes. A system optimized only for recall (ESCALATE everything suspicious) will fail the FP scenarios. A system optimized only for precision (ALLOW unless certain) will fail the subtle fraud scenarios.

### Truncation Note

BEC-FP-003 was truncated in the source document at the 50,000 character limit. The `vendor_record`, `sender_history`, `approval_chain`, `org_policies`, `hidden_ground_truth`, `scoring_targets`, and `notes_for_humans` fields require reconstruction. The scenario premise: SPF soft-fail on a legitimate invoice from Clearwater Janitorial Services, caused by a documented IT infrastructure migration (Barracuda → Microsoft Defender) during March 1–15, 2026. Expected verdict: ALLOW. The SPF soft-fail is explicitly anticipated and explained by the IT advisory in the email thread.
