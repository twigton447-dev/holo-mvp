# Board Strategy Memo: AI Infrastructure Capacity Decision

**To:** Board of Directors and Chief Financial Officer
**From:** Strategy & Finance
**Date:** [Current Quarter]
**Re:** AI Infrastructure Capacity Commitment — Final Recommendation
**Classification:** Confidential — Board Use Only

---

## Executive Summary

**Primary recommendation:** Pursue a partial reserved capacity commitment of approximately 50% (~$4.8M/year), contingent on three preconditions that management must resolve before the Board votes on final contract terms. This memo authorizes management to complete those preconditions within 30 days and return with a binding recommendation. It does not authorize contract execution.

**Why this sequencing matters:** Prior drafts presented the staged path as the recommendation and treated commercial availability of partial contracts as a post-approval task. That sequencing was inverted. The Board should not vote on a commitment structure whose primary feature — partial reserved capacity — has not been confirmed as commercially available. The 30-day precondition window corrects this.

**If partial contracts are unavailable**, the Board will receive a binary recommendation within 30 days. The decision criteria and risk register in this memo apply directly to that binary choice. Full two-year commitment under binary conditions carries material stranded-cost risk that is unmitigated unless contract portability provisions are secured — and their availability is uncertain.

**The core tension this memo resolves:** A full $9.6M/year commitment reduces runway from approximately 24 months to approximately 15 months under Finance's base-case estimate, breaching the proposed 18-month runway floor. Pure on-demand preserves cash but costs approximately 1.35× the reserved price at expected utilization and leaves $6M of at-risk expansion pipeline exposed to reliability concerns. The staged path is superior to both — but only if its preconditions are met.

---

## Explicit Assumptions

The Board should revisit this recommendation if any of the following proves materially incorrect.

1. **Inference cost causality:** Gross margin compression from 73% to 66% over three quarters is assumed to reflect inference usage growing faster than pricing adjustments. Reserved capacity stabilizes cost-per-unit at a fixed volume; it does not reduce total inference spend if usage continues to grow beyond reserved capacity. The margin recovery plan must address both cost-per-unit and volume growth simultaneously.

2. **On-demand cost baseline:** On-demand capacity costs approximately 1.35× the reserved price at expected utilization. The annual on-demand cost equivalent requires confirmation of the company's actual current inference run-rate, which is not available in the data provided to this memo. *[CFO to confirm before Board vote.]*

3. **Pipeline attribution reliability:** The $6M at-risk expansion pipeline reflects Sales attribution. This figure should be treated as directional until the CRO completes deal-by-deal documentation confirming that infrastructure reliability — rather than pricing, competitive alternatives, or feature gaps — is the primary blocker. This validation must occur before Stage 1 commitment, not after.

4. **Runway calculation:** Finance's estimate that a full $9.6M/year commitment produces approximately 15 months of runway is accepted as the planning baseline. A partial commitment is directionally between 15 and 24 months, but the precise figure depends on operating burn rate, collections timing, and ARR growth trajectory. The CFO cash flow model must be completed before the Board votes on contract terms.

5. **Runway floor financing basis:** This memo proposes 18 months as the minimum runway floor. The rationale is that 18 months provides sufficient time to reach the next ARR milestone at which external financing becomes accessible. At 18% YoY growth on $42M ARR, the company reaches approximately $50M ARR within roughly 12 months. *The Board must confirm whether $50M ARR — or a different milestone — represents the actual financing threshold, and whether current market conditions support that assumption. The 18-month floor is a proposed policy threshold requiring Board ratification, not a figure derived from available data.*

6. **Partial contract availability:** The staged recommendation depends on the infrastructure provider offering partial or phased reserved capacity. This has not been tested. Management must confirm availability before this recommendation becomes actionable.

7. **No near-term financing event:** This analysis assumes no capital raise within the decision window. If a financing event is probable within 12 months, the runway constraint relaxes and the calculus shifts toward full commitment. The Board should disclose any such expectation before approving this memo.

8. **Enterprise requirements addressable via reserved capacity:** Data residency, audit logs, and latency commitments from enterprise customers are assumed to be materially addressable through reserved infrastructure, not solely through architectural changes. The CTO must confirm this before Stage 1 commitment.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Partial contracts unavailable; binary choice forced | Low–Medium | High | Complete provider negotiation within 30 days; binary decision criteria defined below |
| Growth slows below 18% YoY; commitment creates cash pressure | Medium | High | Stage commitment; maintain Board-ratified runway floor; CFO models monthly burn |
| $6M pipeline attribution overstated; reliability not primary blocker | Medium | High | CRO deal-by-deal validation required before Stage 1 commitment |
| Inference volume growth exhausts reserved capacity before term ends | Medium | High | Monitor utilization monthly; include volume growth rate in Stage 2 trigger review |
| Gross margin unrecovered at one-year term boundary; renewal decision unclear | Medium | High | Explicit renewal decision criteria defined in Stage 3 below |
| On-demand costs spike above 1.35× during demand volatility | Medium | Medium | Partial reserved capacity hedges worst-case on-demand exposure |
| Two-year lock-in becomes stranded cost if AI architecture shifts | Low–Medium | Medium | Require portability or credit provisions; if unavailable, treat as unmitigated risk in binary scenario |
| Enterprise customer defection before 30-day precondition window closes | Low–Medium | High | Sales to flag imminent deal decisions; CEO authorized to accelerate timeline if deal loss is confirmed |
| 50% capacity covers insufficient workload to address enterprise latency requirements | Medium | High | CTO workload coverage analysis required before Stage 1 commitment |
| Pricing action causes enterprise pushback before reliability improvements are demonstrable | Low–Medium | Medium | Sequence pricing changes after reliability improvements are in place |

---

## Decision Criteria

**1. Runway Floor — Board Ratification Required**
The company should not allow committed fixed costs to reduce runway below a Board-ratified minimum. Management proposes 18 months, contingent on Board confirmation that the underlying financing milestone assumption is valid. Under Finance's base-case, a full $9.6M/year commitment produces approximately 15 months of runway — below the proposed floor. A partial commitment is required to stay above it, subject to CFO cash flow modeling.

**2. Pipeline Validation Before Commitment**
The $6M at-risk pipeline must be validated deal-by-deal before Stage 1 commitment is executed. If the CRO review confirms that reliability is the primary blocker for less than $3M of the pipeline, the urgency case for even a partial commitment weakens materially and the Board should be notified before proceeding.

**3. Workload Coverage Confirmation**
The CTO must confirm what percentage of current inference workload 50% of reserved capacity covers. If 50% of reserved capacity is insufficient to meet enterprise latency commitments for the at-risk pipeline deals, the commitment percentage must be adjusted upward — or the reliability defense rationale does not hold.

**4. Margin Recovery as a Paired Obligation**
Any capacity commitment must be paired with a credible plan to recover gross margin toward 70%+ within four quarters, addressing both cost-per-unit and inference volume growth. A capacity contract without a volume management plan hedges part of the margin problem while leaving the rest unaddressed.

**5. Contract Flexibility**
Preference should be given to structures with expansion options, step-up clauses tied to ARR milestones, or portability provisions. A rigid all-or-nothing two-year contract is a last resort. If portability provisions are commercially unavailable, the Board should treat full two-year commitment as carrying unmitigated stranded-cost risk.

---

## Staged Option Structure

### Precondition Phase — 30 Days (Before Any Commitment)

Management must complete and report to the Board on all four items before contract execution is authorized:

| Precondition | Owner | Deadline | Go/No-Go Threshold |
|---|---|---|---|
| Confirm partial/phased contract availability with provider | CTO / Procurement | 21 days | Partial terms available; if not, invoke binary path |
| CRO deal-by-deal pipeline validation | CRO | 21 days | Reliability confirmed as primary blocker for ≥$3M of pipeline |
| CTO workload coverage analysis: what % of inference workload does 50% reserved capacity cover? | CTO | 21 days | Coverage sufficient to address latency commitments for at-risk deals |
| CFO three-scenario cash flow model with runway floor confirmation | CFO | 21 days | Staged commitment keeps runway ≥18 months (Board-ratified floor) |

If all four preconditions are met, management is authorized to execute Stage 1 without a further Board meeting. If any precondition fails, management returns to the Board within 30 days with a revised recommendation.

**Escalation protocol:** If the provider negotiation extends beyond 21 days without resolution, the CEO will notify the Board immediately. The maximum negotiation window is 30 days. If partial terms are not confirmed by day 30, the company defaults to on-demand capacity while the binary recommendation is prepared. Indefinite indecision is not an option.

### Stage 1 — Immediate Execution (Post-Preconditions)
Commit to approximately 50% of available reserved capacity (~$4.8M/year) on a one-year initial term with a renewal option. Simultaneously launch the inference pricing and volume review with a 60-day deadline.

### Stage 2 — Six-Month Gate Review
Evaluate against all five trigger thresholds before expanding commitment:

| Trigger | Threshold | Action if Met | Action if Not Met |
|---|---|---|---|
| ARR growth rate | ≥18% sustained | Expand to full reserved capacity | Maintain partial; reassess at Stage 3 |
| Gross margin | Recovery to ≥69% | Proceed with full commitment | Delay expansion; escalate pricing and volume action |
| Pipeline conversion | ≥$3M of validated pipeline converted | Expand | Investigate whether reliability remains the true blocker |
| Runway post-full-commitment | ≥18 months (Board-ratified floor) | Full commitment permissible | Full commitment deferred |
| Reserved capacity utilization | <85% of reserved capacity utilized | Sufficient headroom; expand | Assess stranded-cost risk before expanding |

All five thresholds should be met before expanding. If four of five are met, the CFO may recommend expansion with Board notification.

### Stage 3 — One-Year Term Boundary Review
At the one-year term boundary, the Board must make an explicit renewal decision regardless of Stage 2 outcome. If Stage 2 triggers were not met and margin remains