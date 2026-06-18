# Board Strategy Memo: AI Infrastructure Capacity Commitment Decision

**To:** Board of Directors and Chief Financial Officer  
**From:** Strategy Team  
**Date:** [Current]  
**Subject:** Recommendation on Two-Year Reserved Accelerator Capacity Contract

## Recommendation
Preserve optionality for six months rather than executing the two-year reserved accelerator capacity contract now. This approach maintains the current 24-month runway while monitoring pipeline and utilization signals that could justify a later commitment. A full immediate lock-in would reduce runway to 15 months under the stated downside scenario and introduce fixed-cost exposure inconsistent with volatile demand.

## Current Situation
The company reports $31M cash with no debt and $42M ARR growing at 18% year-over-year. Gross margin has declined from 73% to 66% over three quarters as inference usage has outpaced pricing adjustments. Reserved accelerator capacity is priced at $9.6M per year for two years. On-demand capacity costs approximately 1.35× the reserved rate at expected utilization levels, though demand remains volatile. Enterprise customers require data residency, audit logs, and latency commitments. Sales has attributed $6M of at-risk expansion pipeline to AI feature reliability concerns. Finance has flagged that full commitment could compress runway from 24 months to 15 months if growth slows.

## Explicit Assumptions
- Current cash position, ARR, growth rate, and gross-margin trajectory remain as stated; no external forecasts are applied.
- On-demand pricing premium and reserved pricing hold at the given multiples.
- The $6M at-risk pipeline figure is accepted as provided and is treated as sensitive to AI reliability.
- Runway compression to 15 months occurs only under the scenario explicitly warned by Finance.
- Customer requirements for data residency, audit logs, and latency can be met through on-demand capacity in the near term.
- No additional capital raises or material changes to operating expenses are assumed.

## Decision Criteria
The decision will be governed by three observable thresholds to be reviewed at the six-month mark:
1. Expansion pipeline retention: If more than 50% of the $6M at-risk pipeline converts without reserved capacity, optionality is validated.
2. Utilization volatility: If on-demand spend exceeds 1.35× reserved pricing for three consecutive months at greater than 70% of expected volume, a staged commitment may be triggered.
3. Runway protection: Cash position must remain above the level that would produce a 15-month runway after any incremental commitment.

These criteria directly address the conflicting signals between revenue defense and cash preservation.

## Risk Register
- **Runway compression (High likelihood, High impact):** Immediate two-year commitment reduces runway to 15 months if growth slows, limiting strategic flexibility.
- **Demand volatility (High likelihood, Medium impact):** On-demand costs at 1.35× may exceed reserved pricing during low-utilization periods, eroding the 66% gross margin further.
- **Pipeline erosion (Medium likelihood, High impact):** Delaying commitment risks loss of the $6M at-risk expansion if enterprise customers perceive reliability shortfalls.
- **Two-year lock-in (High likelihood, Medium impact):** Reserved capacity creates a fixed $19.2M obligation that cannot be adjusted if inference demand patterns shift.
- **Margin pressure persistence (Medium likelihood, Medium impact):** Continued inference growth without pricing offsets sustains the three-quarter gross-margin decline.
- **Customer commitment credibility (Low likelihood, Medium impact):** On-demand capacity may prove insufficient for data-residency or latency SLAs, weakening enterprise positioning.

## Near-Term Action Plan (Next Six Months)
- Month 1: Establish a monthly dashboard tracking on-demand spend versus the 1.35× benchmark, pipeline conversion of the $6M at-risk amount, and cash runway under current burn.
- Month 1–2: Negotiate with the provider for a six-month deferral clause or staged reservation option exercisable at the six-month review point, preserving the ability to lock in pricing without immediate full commitment.
- Month 2–3: Pilot enhanced on-demand configurations to test latency and audit-log capabilities against enterprise requirements; document any gaps.
- Month 3–6: Conduct bi-monthly reviews against the three decision criteria; prepare a go/no-go memo for the Board at month six.
- Contingency trigger: If two of the three criteria are breached before month six, convene an ad-hoc Board call to evaluate partial reservation of one year only.

## Conclusion
The immediate commitment trades material runway reduction and lock-in risk for uncertain pipeline protection. Preserving optionality for six months allows the company to observe actual utilization and conversion data before committing $19.2M. This staged approach directly mitigates the hidden traps of pure cost framing and two-year lock-in while keeping all provided facts and constraints in view. A final decision will be brought to the Board once the six-month thresholds are measured.