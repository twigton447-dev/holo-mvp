# Board Strategy Memo: AI Infrastructure Capacity Decision

**To:** Board of Directors and Chief Financial Officer
**From:** Strategy Office
**Date:** [Current Quarter]
**Re:** Recommendation on Two-Year AI Infrastructure Capacity Commitment
**Classification:** Confidential — Board Use Only

---

## Executive Summary

This memo recommends a **staged commitment**: execute a one-year reserved capacity contract for approximately half the available reserved capacity now, with a structured six-month review gate before committing to the full two-year term. This approach captures meaningful cost savings and signals infrastructure reliability to enterprise customers, while preserving sufficient runway and optionality against demand uncertainty.

---

## Explicit Assumptions

The following assumptions underpin this analysis. The Board should revisit the recommendation if any assumption proves materially incorrect.

1. **Utilization growth continues at or near current trajectory.** Inference usage has outpaced pricing adjustments for three consecutive quarters, compressing gross margin from 73% to 66%. We assume this trend continues absent deliberate pricing action.
2. **On-demand pricing remains at 1.35x reserved pricing at expected utilization.** This differential is the primary economic argument for reservation. If on-demand pricing falls or utilization drops, the savings case weakens.
3. **The $6M at-risk expansion pipeline is genuinely at risk.** Sales attribution is directionally credible but not independently verified in this context. We treat it as a real but uncertain figure.
4. **Cash burn rate is consistent with a 24-month runway on current trajectory.** Finance's warning that a full commitment reduces runway to 15 months implies approximately $640K per month in incremental cash consumption from the reserved contract above current spend levels. *(Note: exact monthly burn is not provided; this figure is derived from the stated runway impact and should be confirmed by Finance.)*
5. **No debt financing or equity raise is imminent.** The company holds $31M cash with no debt. We assume no near-term capital event that would change the liquidity calculus.
6. **Data residency, audit log, and latency commitments are contractually achievable under the reserved capacity structure.** This is not confirmed in the source context and should be validated with the infrastructure vendor before signing.

---

## The Core Tension

Two legitimate strategic imperatives conflict here:

- **Reliability defends revenue.** Enterprise customers are conditioning $6M in expansion pipeline on AI feature reliability. Reserved capacity enables latency commitments and uptime guarantees that on-demand capacity cannot reliably provide. Waiting six months risks losing deals that close in the interim.
- **Fixed cost creates fragility.** A full two-year commitment of $19.2M total ($9.6M/year) against $31M cash and an 18% ARR growth rate that could decelerate reduces runway from 24 to 15 months. Nine months of runway is a meaningful margin of safety to surrender.

A binary choice — full commitment now versus full deferral — is a false frame. The staged approach resolves the tension without fully accepting either risk.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Growth decelerates; fixed capacity becomes cash drain | Medium | High | Staged commitment limits initial exposure; six-month gate allows reassessment |
| $6M pipeline converts to churn or lost expansion without reliability commitment | Medium | High | Partial reservation now signals commitment; vendor SLA terms should be negotiated immediately |
| On-demand pricing falls, eliminating cost advantage of reservation | Low | Medium | Monitor quarterly; include contract exit or renegotiation clause if available |
| Two-year lock-in coincides with infrastructure technology shift (e.g., more efficient accelerators) | Medium | Medium | Negotiate annual capacity flex provisions; avoid locking 100% of anticipated need |
| Vendor fails to support data residency requirements under reserved terms | Low–Unknown | High | Validate before signing; treat as a contract condition precedent |
| Runway falls below 12 months before growth re-accelerates | Low | Critical | Trigger threshold (see below) activates board review and potential financing action |

---

## Decision Criteria

The Board should evaluate this decision against the following criteria, in priority order:

1. **Runway floor.** No capacity commitment should reduce cash runway below 18 months under base-case growth assumptions. The full two-year commitment at $9.6M/year breaches this threshold if growth slows modestly.
2. **Pipeline defense.** If the $6M at-risk expansion pipeline can be partially defended through a credible infrastructure commitment — even a partial one — the revenue protection justifies near-term cost.
3. **Cost efficiency.** The 1.35x on-demand premium is material at scale. At current and projected utilization, reservation saves real dollars. Cost efficiency is a supporting criterion, not the primary one.
4. **Contractual flexibility.** Any commitment must include provisions for capacity adjustment, data residency compliance, and ideally an early exit or renegotiation window at month 12.

---

## Staged Option Structure and Trigger Thresholds

### Phase 1 — Immediate Action (Now through Month 6)

- Execute a reserved capacity agreement for **50% of the full reserved volume**, structured as a one-year term with an option to expand.
- Negotiate data residency, audit log, and latency SLA terms as conditions of the contract.
- Estimated annual cost of Phase 1: **~$4.8M**, preserving runway above 20 months under base-case assumptions.
- Begin communicating infrastructure reliability commitments to the enterprise pipeline accounts identified by Sales.

### Phase 2 — Six-Month Review Gate

At month six, the Board reviews the following trigger thresholds before deciding whether to expand to full reserved capacity:

| Trigger | Expand to Full Reservation | Hold or Reduce |
|---|---|---|
| ARR growth rate | ≥15% trailing two quarters | <12% trailing two quarters |
| Gross margin | Stabilized at ≥67% | Continued decline below 65% |
| Cash runway (projected) | ≥20 months post-expansion | <18 months post-expansion |
| Pipeline conversion | ≥$3M of at-risk pipeline converted | <$1.5M converted |
| On-demand price movement | Stable or rising | Fallen >15% |

If thresholds are met, execute the remaining reserved capacity for the balance of the two-year term. If thresholds are not met, continue on partial reservation and reassess at month nine.

---

## Near-Term Action Plan