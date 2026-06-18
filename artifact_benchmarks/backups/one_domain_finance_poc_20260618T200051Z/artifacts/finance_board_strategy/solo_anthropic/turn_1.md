# Board Strategy Memo: AI Infrastructure Capacity Decision

**To:** Board of Directors and Chief Financial Officer
**From:** Strategy & Finance
**Date:** [Current Quarter]
**Re:** Commit to Two-Year Reserved AI Capacity vs. Preserve Optionality for Six Months
**Classification:** Confidential — Board Use Only

---

## Executive Summary

We recommend a **staged commitment**: execute a one-year reserved capacity contract for approximately half the available reserved capacity now, with a structured six-month review gate that can accelerate to full two-year commitment if defined revenue and utilization triggers are met. A full immediate two-year commitment is not warranted given current runway risk; pure optionality is equally inadvisable given $6M of at-risk pipeline tied directly to AI feature reliability. The staged path balances cost discipline against competitive exposure.

---

## Explicit Assumptions

The following assumptions underpin this analysis. The Board should revisit the recommendation if any assumption proves materially incorrect.

1. **Inference cost trajectory:** Gross margin compression from 73% to 66% over three quarters is assumed to continue at a similar rate absent either pricing action or infrastructure cost reduction. No external market forecast is assumed.
2. **On-demand premium:** On-demand capacity is assumed to cost 1.35× the reserved price at expected utilization levels. Actual cost could be higher if demand spikes are more frequent or severe than anticipated.
3. **Pipeline attribution:** The $6M at-risk expansion pipeline attributed by Sales to AI feature reliability is taken at face value. The degree to which reliability improvements would convert this pipeline is uncertain and not independently verified in this memo.
4. **Runway calculation:** Finance's estimate that a full $9.6M/year commitment reduces runway from 24 months to 15 months assumes current ARR growth of 18% YoY and $31M cash with no debt. Runway sensitivity is linear to growth rate changes.
5. **Contract structure:** It is assumed that a partial or phased reserved capacity contract is commercially available from the infrastructure provider. If the provider requires an all-or-nothing commitment, the decision framework changes materially. *(Uncertainty: this has not been confirmed in the provided context.)*
6. **Enterprise requirements:** Data residency, audit logs, and latency commitments from enterprise customers are assumed to be addressable primarily through reserved capacity rather than architectural changes alone.
7. **No additional financing:** This analysis assumes no new capital raise within the decision window. If a financing event is probable, the runway constraint relaxes and the calculus shifts toward full commitment.

---

## The Core Tension

Two legitimate but conflicting imperatives are in conflict:

| Signal | Implication |
|---|---|
| Gross margin fell 7 points in three quarters | Fixed-cost infrastructure could stabilize unit economics |
| $6M expansion pipeline at risk due to reliability | Inaction has a measurable revenue cost |
| Full commitment cuts runway from 24 to 15 months | Downside scenario becomes existential if growth slows |
| On-demand costs 1.35× reserved at expected utilization | Staying fully on-demand is not "free" optionality |

The hidden trap in this decision is framing it purely as a cost question. The real question is whether the company can afford the **strategic cost of unreliability** relative to the **financial cost of lock-in**. Both carry risk; neither is a safe default.

---

## Decision Criteria

The Board should weigh the following criteria in reaching a final decision:

**1. Revenue Defense Priority**
If the $6M at-risk pipeline represents expansion from existing enterprise customers, churn risk compounds the pipeline loss. Reliability is not a feature preference — it is a contract prerequisite for this customer segment.

**2. Runway Floor**
The company should not allow committed fixed costs to reduce runway below 18 months under a base-case growth scenario. At 18% ARR growth and $31M cash, a full $9.6M/year commitment produces a 15-month runway — below this floor. A partial commitment preserving 18+ months of runway is the minimum acceptable posture.

**3. Margin Recovery Path**
Any capacity commitment must be paired with a credible plan to recover gross margin toward 70%+ within four quarters, either through inference pricing adjustments, efficiency improvements, or both. A capacity contract that locks in cost without a margin recovery plan worsens the unit economics problem.

**4. Contract Flexibility**
Preference should be given to contract structures that include expansion options, early termination rights, or step-up clauses tied to ARR milestones. A rigid two-year all-or-nothing contract is a last resort.

**5. Competitive Timing**
If enterprise customers are actively evaluating alternatives due to reliability concerns, a six-month delay to preserve optionality may result in pipeline losses that exceed the cost savings from waiting. Sales must provide a concrete timeline on when at-risk deals will reach decision points.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Growth slows below 18% YoY; full commitment creates cash crisis | Medium | High | Stage commitment; maintain 18-month runway floor |
| $6M pipeline converts to churn without reliability improvement | Medium | High | Partial commitment addresses near-term reliability; monitor quarterly |
| Infrastructure provider requires all-or-nothing contract | Low–Medium | High | Negotiate partial or phased terms before Board decision; escalate if unavailable |
| On-demand costs spike above 1.35× due to demand volatility | Medium | Medium | Partial reserved capacity hedges against worst-case on-demand exposure |
| Gross margin continues to compress despite capacity commitment | Medium | High | Pair commitment with mandatory pricing review within 60 days |
| Two-year lock-in becomes stranded cost if AI architecture shifts | Low | Medium | Seek contract flexibility clauses; review at 12-month gate |
| Delay of six months causes enterprise customer defection | Low–Medium | High | Accelerate trigger review to 90 days if Sales signals imminent deal loss |

---

## Staged Option Structure

Rather than a binary choice, we recommend the following three-stage structure:

### Stage 1 — Immediate Action (Now)
- Commit to **50% of available reserved capacity** (approximately $4.8M/year), structured as a one-year initial term with a renewal option.
- This preserves runway above 18 months under base-case assumptions while providing sufficient reliability improvement to address the most acute enterprise customer concerns.
- Simultaneously, initiate a formal inference pricing review with a 60-day deadline to present margin recovery options to the CFO.

### Stage 2 — Six-Month Review Gate
At the six-month mark, evaluate against the following **trigger thresholds**:

| Trigger | Threshold | Action if Met | Action if Not Met |
|---|---|---|---|
| ARR growth rate | ≥18% sustained | Expand to full reserved capacity for remaining contract term | Maintain partial commitment; reassess at 12 months |
| Gross margin | Recovery to ≥69% | Proceed with full commitment | Delay expansion; prioritize pricing action |
| At-risk pipeline conversion | ≥$3M of $6M converted | Validate reliability as revenue driver; expand | Investigate whether reliability is the true blocker |
| Runway (post-commitment) | ≥18 months | Full commitment permissible | Full commitment deferred |

All four thresholds should be met before expanding to full commitment. If three of four are met, the CFO has discretion to recommend expansion with Board notification.

### Stage 3 — 12-Month Full Review
Regardless of Stage 2 outcome, conduct a full infrastructure strategy review at 12 months, incorporating updated AI architecture options, provider market conditions, and ARR trajectory. This review should assess whether a second-year renewal or renegotiation is warranted.

---

## Financial Snapshot

| Scenario | Annual Capacity Cost | Estimated Runway | Gross Margin Pressure |
|---|---|---|---|
| Full two-year commitment | $9.6M/year | ~15 months | Partially offset by fixed cost predictability |
| Staged 50% commitment (Stage 1) | ~$4.8M/year | ~19–20 months* | Moderate relief on on-demand volatility |
| Full on-demand (no commitment) | ~$12.96M/year equivalent at 1.35× | ~24 months nominal | Continued margin compression risk |
| **Recommended staged path** | **$4.8M now; expand at gate** | **~19–20 months*** | **Managed exposure** |

*Runway estimates are directional based on provided figures. Finance should model precise cash flow scenarios before Board vote.*

The on-demand path is not financially neutral. At 1.35× the reserved price, remaining fully on-demand at expected utilization costs more annually than the reserved contract — the optionality premium is real and ongoing.

---

## Near-Term Action Plan

| Action | Owner | Deadline |
|---|---|---|
| Negotiate partial/phased reserved capacity contract terms with provider | CTO / Procurement | 30 days |
| Model three cash flow scenarios (full, staged, on-demand) with monthly granularity | CFO | 21 days |
| Sales to provide deal-by-deal timeline on $6M at-risk pipeline | CRO | 14 days |
| Initiate inference pricing review; present options to CFO | Product / Finance | 60 days |
| Establish Stage 2 trigger threshold dashboard for six-month gate | Finance / BI | 45 days |
| Return to Board with final contract terms for approval | CEO / CFO | 45 days |

---

## Recommendation

**Approve the staged commitment path.** Authorize management to negotiate a partial reserved capacity agreement covering approximately 50% of available capacity, subject to contract flexibility terms acceptable to the CFO. Require a formal six-month gate review against the trigger thresholds defined above before any expansion to full commitment. Do not approve a full two-year commitment at this time given runway risk. Do not defer all action, as the on-demand alternative carries both higher expected cost and measurable revenue risk.

The decision before the Board is not whether to spend — it is how to sequence spending to protect both the balance sheet and the revenue base simultaneously.

---

*This memo is based solely on the financial and operational data provided. Figures marked with an asterisk are directional estimates pending CFO modeling. The Board should not rely on this memo as a substitute for detailed financial projections.*