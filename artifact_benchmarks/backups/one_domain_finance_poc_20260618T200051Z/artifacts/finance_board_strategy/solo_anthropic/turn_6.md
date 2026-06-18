# Board Strategy Memo: AI Infrastructure Capacity Decision

**To:** Board of Directors and Chief Financial Officer
**From:** Strategy & Finance
**Date:** [Current Quarter]
**Re:** AI Infrastructure Capacity Commitment — Final Recommendation
**Classification:** Confidential — Board Use Only

---

## Executive Summary

**This memo authorizes a 30-day precondition phase. It does not authorize contract execution.**

Management recommends pursuing a partial reserved capacity commitment of approximately 50% (~$4.8M/year on a one-year initial term) as the preferred outcome. However, the Board should not vote on contract terms until four preconditions are confirmed. Those preconditions — commercial availability of partial contracts, pipeline validation, workload coverage analysis, and a CFO cash flow model — must be completed within 30 days. If all four are met, management is authorized to execute Stage 1 without a further Board meeting. If any precondition fails, management returns to the Board with a revised recommendation within 30 days.

**Why not full two-year commitment now?** At $9.6M/year, a full commitment reduces runway from approximately 24 months to approximately 15 months under Finance's base-case estimate — below the proposed 18-month runway floor. The two-year lock-in also carries unmitigated stranded-cost risk if AI inference architecture shifts and portability provisions are commercially unavailable.

**Why not pure six-month optionality?** On-demand capacity costs approximately 1.35× the reserved price at expected utilization. Optionality is not free. Sales attributes $6M of expansion pipeline to AI feature reliability concerns. Delay has a compounding revenue cost if enterprise customers reach decision points before the window closes.

**The staged path is superior to both — but only if its preconditions are met.** If partial contracts are unavailable and the choice is binary, the decision criteria and risk register below apply directly to that choice.

---

## Explicit Assumptions

The Board should revisit this recommendation if any of the following proves materially incorrect.

1. **Inference cost causality.** Gross margin compression from 73% to 66% over three quarters is assumed to reflect inference usage growing faster than pricing adjustments. Reserved capacity stabilizes cost-per-unit at a fixed volume; it does not reduce total inference spend if usage continues to grow beyond reserved capacity. The margin recovery plan must address both cost-per-unit and volume growth simultaneously.

2. **On-demand cost baseline.** On-demand capacity costs approximately 1.35× the reserved price at expected utilization. The precise annual on-demand cost equivalent requires confirmation of the company's actual current inference run-rate, which is not available in the data provided to this memo. *[CFO to confirm before Board vote.]*

3. **Pipeline attribution reliability.** The $6M at-risk expansion pipeline reflects Sales attribution and should be treated as directional until the CRO completes deal-by-deal documentation confirming that infrastructure reliability — not pricing, competitive alternatives, or feature gaps — is the primary blocker. This validation is a precondition for Stage 1 commitment, not a post-commitment activity.

4. **Runway calculation.** Finance's estimate that a full $9.6M/year commitment produces approximately 15 months of runway is accepted as the planning baseline. A partial commitment falls directionally between 15 and 24 months; the precise figure depends on operating burn rate, collections timing, and ARR growth trajectory. The CFO cash flow model must be completed before contract execution.

5. **Runway floor and financing milestone.** This memo proposes 18 months as the minimum runway floor on the basis that 18 months provides sufficient time to reach the next ARR milestone at which external financing becomes accessible. At 18% YoY growth on $42M ARR, the company reaches approximately $50M ARR within roughly 12 months. **The Board must confirm whether $50M ARR — or a different milestone — represents the actual financing threshold, and whether current market conditions support that assumption. The 18-month floor is a proposed policy threshold requiring Board ratification, not a figure derived from available data.**

6. **Partial contract availability.** The staged recommendation depends on the infrastructure provider offering partial or phased reserved capacity. This has not been tested. Management must confirm availability before this recommendation becomes actionable. If partial terms are unavailable, the binary decision criteria in the Decision Criteria section apply.

7. **No near-term financing event.** This analysis assumes no capital raise within the decision window. If a financing event is probable within 12 months, the runway constraint relaxes and the calculus shifts toward full commitment. The Board should disclose any such expectation before approving this memo.

8. **Enterprise requirements addressable via reserved capacity.** Data residency, audit logs, and latency commitments from enterprise customers are assumed to be materially addressable through reserved infrastructure, not solely through architectural changes. The CTO must confirm this before Stage 1 commitment.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Partial contracts unavailable; binary choice forced | Low–Medium | High | Complete provider negotiation within 30 days; binary decision criteria defined below |
| Growth slows below 18% YoY; commitment creates cash pressure | Medium | High | Stage commitment; maintain Board-ratified runway floor; CFO models monthly burn |
| Pipeline attribution overstated; reliability not primary blocker | Medium | High | CRO deal-by-deal validation required **before** Stage 1 commitment |
| 50% reserved capacity insufficient to cover enterprise latency requirements | Medium | High | CTO workload coverage analysis required before Stage 1; adjust commitment percentage if needed |
| Inference volume growth exhausts reserved capacity before term ends | Medium | High | Monitor utilization monthly; include volume growth rate in Stage 2 trigger review |
| Stage 2 triggers unmet at six months; one-year term approaches expiration | Medium | High | Explicit Stage 3 renewal decision required regardless of Stage 2 outcome; see below |
| Two-year lock-in becomes stranded cost if AI architecture shifts | Low–Medium | Medium | Require portability or credit provisions; if unavailable, treat as unmitigated risk in binary scenario |
| On-demand costs spike above 1.35× during demand volatility | Medium | Medium | Partial reserved capacity hedges worst-case on-demand exposure |
| Enterprise customer defection before 30-day precondition window closes | Low–Medium | High | Sales to flag imminent deal decisions; CEO authorized to accelerate timeline if confirmed deal loss is imminent |
| Provider negotiation extends beyond 21 days without resolution | Medium | Medium | CEO escalation protocol triggered at day 21; maximum window 30 days; default to on-demand if unresolved |

---

## Decision Criteria

**1. Board-Ratified Runway Floor.**
The company should not allow committed fixed costs to reduce runway below a Board-ratified minimum. Management proposes 18 months, contingent on Board confirmation that the underlying financing milestone assumption is valid. Under Finance's base-case, a full $9.6M/year commitment produces approximately 15 months of runway — below the proposed floor. A partial commitment is required to stay above it, subject to CFO cash flow modeling.

**2. Pipeline Validation Before Commitment.**
The CRO must confirm that infrastructure reliability is the primary blocker for at least $3M of the $6M attributed pipeline before Stage 1 is executed. If confirmed pipeline at risk falls below $3M, the urgency case for even a partial commitment weakens materially and the Board must be notified before proceeding.

**3. Workload Coverage Confirmation.**
The CTO must confirm what percentage of current inference workload 50% of reserved capacity covers. If 50% of reserved capacity is insufficient to meet enterprise latency commitments for the at-risk pipeline deals, the commitment percentage must be adjusted upward — or the reliability defense rationale does not hold. The 50% figure is a financial placeholder pending this analysis.

**4. Margin Recovery as a Paired Obligation.**
Any capacity commitment must be paired with a credible plan to recover gross margin toward 70%+ within four quarters, addressing both cost-per-unit and inference volume growth. A capacity contract without a volume management plan hedges part of the margin problem while leaving the rest unaddressed.

**5. Contract Flexibility.**
Preference should be given to structures with expansion options, step-up clauses tied to ARR milestones, or portability provisions. A rigid all-or-nothing two-year contract is a last resort. If portability provisions are commercially unavailable, the Board should treat full two-year commitment as carrying unmitigated stranded-cost risk.

---

## Staged Option Structure

### Precondition Phase — 30 Days (Authorizes Execution; Does Not Execute)

| Precondition | Owner | Deadline | Go / No-Go Threshold |
|---|---|---|---|
| Confirm partial/phased contract availability with provider | CTO / Procurement | Day 21 | Partial terms available; if not, invoke binary path |
| CRO deal-by-deal pipeline validation | CRO | Day 21 | Reliability confirmed as primary blocker for ≥$3M of pipeline |
| CTO workload coverage analysis | CTO | Day 21 | 50% reserved capacity sufficient to address latency commitments for at-risk deals |
| CFO three-scenario cash flow model with runway floor confirmation | CFO | Day 21 | Staged commitment keeps runway ≥18 months under Board-ratified floor |

If all four preconditions are met by day 21, management is authorized to execute Stage 1 without a further Board meeting. If any precondition fails, management returns to the Board by day 30 with a revised recommendation. **Escalation protocol:** If provider negotiation is unresolved at day 21, the CEO notifies the Board immediately. The maximum negotiation window is 30 days. If partial terms are not confirmed by day 30, the company defaults to on-demand capacity while the binary recommendation is prepared. Indefinite indecision is not an option.

### Stage 1 — Immediate Execution (Post-Preconditions)
Commit to approximately 50% of available reserved capacity (~$4.8M/year) on a one-year initial term with a renewal option. Simultaneously launch the inference pricing and volume review with a 60-day deadline.

### Stage 2 — Six-Month Gate Review
Evaluate against all five trigger thresholds before expanding commitment. All five should be met; if four of five are met, the CFO may recommend expansion with Board notification.

| Trigger | Threshold | Action if Met | Action if Not Met |
|---|---|---|---|
| ARR growth rate | ≥18% sustained | Expand to full reserved capacity | Maintain partial; reassess at Stage 3 |
| Gross margin | Recovery to ≥69% | Proceed with full commitment | Delay expansion; escalate pricing and volume action |
| Pipeline conversion | ≥$3M of validated pipeline converted | Expand | Investigate whether reliability remains the true blocker |
| Runway post-full-commitment | ≥18 months (Board-ratified floor) | Full commitment permissible | Full commitment deferred |
| Reserved capacity utilization | ≥60% and <85% of reserved capacity utilized | Sufficient demand signal;