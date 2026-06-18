# Board Strategy Memo: AI Infrastructure Capacity Decision

**To:** Board of Directors and Chief Financial Officer
**From:** Strategy & Finance
**Date:** [Current Quarter]
**Re:** Commit to Two-Year Reserved AI Capacity vs. Preserve Optionality for Six Months
**Classification:** Confidential — Board Use Only

---

## Executive Summary

We recommend a **staged commitment**: negotiate a partial reserved capacity agreement covering approximately 50% of available reserved capacity now, with a structured six-month gate review before any expansion to full commitment. This is not a compromise between the two original options — it is the superior path because both original options are dominated.

**Why not full two-year commitment now?** At $9.6M/year, a full commitment reduces runway from 24 months to approximately 15 months under Finance's base-case estimate. That runway level leaves insufficient buffer if ARR growth decelerates, and the Board has not confirmed a financing event that would relax this constraint.

**Why not pure six-month optionality?** On-demand capacity costs approximately 1.35× the reserved price at expected utilization. Optionality is not free — it carries a measurable cost premium on every dollar of inference consumed. Additionally, Sales attributes $6M of expansion pipeline to AI feature reliability concerns. Delay has a time-sensitive revenue cost that compounds if enterprise customers reach decision points before the six-month window closes.

The staged path addresses both risks simultaneously. It is contingent on the infrastructure provider offering partial or phased contract terms. If that proves unavailable, a contingency path is defined below.

---

## Explicit Assumptions

The Board should revisit this recommendation if any of the following assumptions proves materially incorrect.

1. **Inference cost trajectory:** Gross margin compression from 73% to 66% over three quarters is assumed to reflect inference usage growing faster than pricing adjustments. Reserved capacity stabilizes cost per unit at a fixed volume — it does not reduce total inference spend if usage continues to grow. If inference volume grows beyond reserved capacity, on-demand pricing applies to incremental usage and margin compression resumes. The margin recovery plan must address both cost-per-unit and volume growth.

2. **On-demand premium:** On-demand capacity costs approximately 1.35× the reserved price at expected utilization. Actual cost could be higher during demand spikes. The on-demand cost comparison in the Financial Snapshot requires confirmation of the company's current actual inference run-rate, which is not available in the data provided to this memo. *[CFO to confirm actual inference spend before Board vote.]*

3. **Pipeline attribution:** The $6M at-risk expansion pipeline reflects Sales attribution. Sales teams can over-attribute pipeline risk to product gaps. This figure should be stress-tested deal-by-deal before being treated as a reliable revenue defense figure. The CRO action item below specifically requires documentation of why reliability — rather than pricing, competitive alternatives, or feature gaps — is the primary blocker for each deal.

4. **Runway calculation:** Finance's estimate that a full $9.6M/year commitment reduces runway from 24 to 15 months is accepted as the planning baseline. A 50% commitment is directionally between these bounds, but the precise figure depends on operating burn rate, collections timing, and ARR growth trajectory — none of which are fully specified in available data. The CFO cash flow model (see Action Plan) must be completed before the Board votes on final contract terms.

5. **Partial contract availability:** The staged recommendation depends entirely on the infrastructure provider offering partial or phased reserved capacity. If the provider requires an all-or-nothing commitment, this staged path is unavailable. See Contingency Branch below.

6. **No near-term financing event:** This analysis assumes no capital raise within the decision window. If a financing event is probable within 12 months, the runway constraint relaxes and the calculus shifts toward full commitment. The Board should disclose any such expectation before approving this recommendation.

7. **Enterprise requirements addressable via reserved capacity:** Data residency, audit logs, and latency commitments from enterprise customers are assumed to be materially addressable through reserved infrastructure, not solely through architectural changes.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Growth slows below 18% YoY; commitment creates cash pressure | Medium | High | Stage commitment; maintain Board-ratified runway floor; CFO models monthly burn |
| $6M pipeline converts to churn without reliability improvement | Medium | High | Partial commitment addresses near-term reliability; CRO validates attribution deal-by-deal |
| Infrastructure provider requires all-or-nothing contract | Low–Medium | High | Negotiate before Board vote; if unavailable, invoke contingency branch within 30 days |
| On-demand costs spike above 1.35× due to demand volatility | Medium | Medium | Partial reserved capacity hedges worst-case on-demand exposure |
| Inference volume growth exhausts reserved capacity before term ends | Medium | Medium | Monitor utilization monthly; include volume growth rate in Stage 2 trigger review |
| Pricing action causes enterprise customer pushback or churn | Low–Medium | Medium | Sequence pricing changes after reliability improvements are demonstrable; communicate value before price |
| Two-year lock-in becomes stranded cost if AI architecture shifts | Low | Medium | Require contract portability or credit provisions; mandatory architecture review at 12-month gate |
| Gross margin continues to compress despite capacity commitment | Medium | High | Pair commitment with mandatory pricing and volume review within 60 days |
| Six-month delay causes enterprise customer defection before gate review | Low–Medium | High | Accelerate gate review to 90 days if Sales signals imminent deal loss |

---

## Decision Criteria

**1. Runway Floor**
The company should not allow committed fixed costs to reduce runway below a Board-ratified minimum. Management proposes 18 months as this floor, on the basis that it provides sufficient time to reach the next ARR milestone at which external financing becomes available on favorable terms. *The Board should confirm or adjust this threshold based on financing strategy and risk appetite before approving any commitment.* Under Finance's base-case estimate, a full $9.6M/year commitment produces approximately 15 months of runway — below the proposed floor. A partial commitment is required to stay above it.

**2. Revenue Defense Priority**
Enterprise customers have cited reliability as a stated requirement for data residency, audit logs, and latency commitments. The degree to which infrastructure commitment resolves their concerns versus other factors is unconfirmed pending CRO deal-by-deal review. If reliability is confirmed as the primary blocker, partial commitment addresses the most acute cases; full commitment may be warranted at the six-month gate.

**3. Margin Recovery Path**
Any capacity commitment must be paired with a credible plan to recover gross margin toward 70%+ within four quarters, addressing both cost-per-unit and inference volume growth. A capacity contract that locks in cost without a volume management plan does not solve the margin problem — it hedges part of it.

**4. Contract Flexibility**
Preference should be given to structures with expansion options, step-up clauses tied to ARR milestones, or portability provisions. A rigid two-year all-or-nothing contract is a last resort and should trigger the contingency branch below.

**5. Pipeline Timing**
If enterprise customers are actively evaluating alternatives, a six-month delay may produce pipeline losses exceeding the cost savings from waiting. Sales must provide a concrete timeline on when at-risk deals reach decision points. If multiple deals close within 90 days, the gate review should be accelerated accordingly.

---

## Staged Option Structure

### Stage 1 — Immediate Action
Commit to approximately 50% of available reserved capacity (~$4.8M/year), structured as a one-year initial term with a renewal option. This provides sufficient reliability improvement to address the most acute enterprise customer concerns while preserving runway above the proposed 18-month floor. Simultaneously, initiate a formal inference pricing and volume review with a 60-day deadline.

### Stage 2 — Six-Month Gate Review
Evaluate against all four trigger thresholds before expanding commitment:

| Trigger | Threshold | Action if Met | Action if Not Met |
|---|---|---|---|
| ARR growth rate | ≥18% sustained | Expand to full reserved capacity | Maintain partial; reassess at 12 months |
| Gross margin | Recovery to ≥69% | Proceed with full commitment | Delay expansion; prioritize pricing and volume action |
| At-risk pipeline conversion | ≥$3M of $6M converted | Validate reliability as revenue driver; expand | Investigate whether reliability is the true blocker |
| Runway post-full-commitment | ≥18 months (Board-ratified floor) | Full commitment permissible | Full commitment deferred |
| Inference volume utilization | Reserved capacity <85% utilized | Capacity sufficient; expand | Assess whether full commitment creates stranded cost |

All thresholds should be met before expanding. If four of five are met, the CFO has discretion to recommend expansion with Board notification.

### Stage 3 — 12-Month Full Review
Conduct a full infrastructure strategy review at 12 months regardless of Stage 2 outcome. This review must include: updated AI architecture options, provider market conditions, ARR trajectory, and a mandatory assessment of whether the company's inference architecture has shifted in ways that affect the value of reserved accelerator capacity.

### Contingency Branch
If the infrastructure provider confirms that partial or phased contracts are not commercially available, management must return to the Board within 30 days with a revised binary recommendation. In that scenario, the decision criteria and risk register above apply directly to the binary choice between full two-year commitment and full on-demand. The Board should not treat approval of this memo as pre-authorization for a full commitment under those circumstances.

---

## Financial Snapshot

| Scenario | Annual Capacity Cost | Runway (Directional) | Margin Exposure |
|---|---|---|---|
| Full two-year commitment | $9.6M/year | ~15 months (Finance estimate) | Partially offset by fixed cost predictability; volume risk remains |
| Staged 50% commitment (Stage 1) | ~$4.8M/year | *[Between 15–24 months — CFO model required]* | Moderate on-demand volatility hedge |
| Full on-demand (no commitment) | *[Current inference run-rate × 1.35 — CFO to confirm]* | ~24 months nominal | Continued compression risk; no cost floor |
| **Recommended staged path** | **~$4.8M now; expand at gate** | **[CFO to model]** | **Managed exposure; volume monitoring required** |

*All runway figures are directional. The CFO cash flow model must be completed before the Board votes on final contract terms. The on-demand annual cost figure requires confirmation of actual current inference expenditure, which is not available in the data provided to this memo.*

---

## Near-Term Action Plan

| Action | Owner | Deadline |
|---|---|---|
| Confirm whether provider offers partial/phased contract terms; report to CEO | CTO / Procurement | 21 days |
| Model three cash flow scenarios (full, staged, on-demand) with monthly granularity; confirm runway floor | CFO | 21 days |
| Provide deal-by-deal documentation of $6M at-risk pipeline: primary blocker