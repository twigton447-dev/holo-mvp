# Board Strategy Memo: AI Infrastructure Capacity Commitment

## Recommendation

**Recommend preserving optionality for six months rather than committing immediately to the full two-year reserved AI infrastructure contract.**  
At the same time, management should use the next six months to test whether reliability-driven revenue protection and expansion justify taking on the fixed-cost lock-in.

This is the better choice based on the current facts because:

- The company has **$31M cash and no debt**, but finance indicates a full commitment could reduce runway from **24 months to 15 months if growth slows**.
- Gross margin has already declined from **73% to 66%** over three quarters because inference usage rose faster than pricing changes.
- A two-year reservation would add **$9.6M per year for two years** of fixed cost.
- There is a real commercial issue: enterprise customers want **data residency, audit logs, and latency commitments**, and sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability.

The decision is therefore not whether reliability matters; it does. The question is whether the company should lock in two years of capacity now, before it has enough evidence that the revenue protection and expansion benefits outweigh the cash and margin risk. Based on the provided context, the answer is **no, not yet**.

## Core Assumptions

The recommendation depends on the following explicit assumptions drawn from incomplete information:

1. **The reserved contract is a firm two-year commitment** at **$9.6M per year**, and the lock-in meaningfully reduces flexibility.
2. **On-demand capacity is available** during the next six months, though at roughly **1.35x reserved price at expected utilization**.
3. **Demand is volatile**, so actual utilization may differ from expected utilization; this increases the risk of overcommitting to reserved capacity.
4. **Reliability gaps are commercially meaningful**, as shown by the **$6M at-risk expansion pipeline** and enterprise requests for operational commitments.
5. The company’s current financial profile is meaningful to the board: **$42M ARR**, **18% YoY growth**, **$31M cash**, **no debt**, and a runway sensitivity that could fall from **24 months to 15 months if growth slows**.
6. Context is incomplete on whether a smaller reservation, phased reservation, or provider-specific contractual flexibility is available. Therefore, this memo does **not** assume such options exist, but it recommends exploring them.

## Decision Criteria

The board should evaluate the choice against five criteria:

1. **Runway preservation**  
   Avoid decisions that materially compress runway before the revenue benefit is proven.

2. **Gross margin protection**  
   Reverse or at least stabilize the decline from **73% to 66%**, rather than adding fixed cost without pricing or utilization confidence.

3. **Revenue defense and expansion support**  
   Improve AI reliability enough to protect the **$6M at-risk expansion pipeline** and support enterprise requirements.

4. **Flexibility under uncertainty**  
   Preserve the ability to adapt if demand, usage mix, or growth changes over the next six months.

5. **Commitment quality**  
   Only accept a two-year lock-in if management can show that the operational and commercial benefits are durable and measurable.

## Analysis

A full commitment now offers one clear advantage: lower unit cost versus on-demand capacity at expected utilization. Since on-demand is about **1.35x** the reserved price, reservation likely improves economics if utilization is sustained and if the company truly needs the capacity to meet enterprise reliability requirements.

However, the current context argues against immediate full commitment for three reasons.

### 1. Cash and runway risk are material

The company has **$31M cash** and no debt. A contract costing **$9.6M annually for two years** is large relative to that cash balance. Finance explicitly warns that a full commitment could reduce runway from **24 months to 15 months if growth slows**. That is a major strategic cost, not just an operating expense.

### 2. Margin pressure is already visible

Gross margin has fallen from **73% to 66%** over three quarters because inference usage increased faster than pricing changes. This means the company has not yet demonstrated that AI usage economics are under control. Locking in two years of infrastructure before proving pricing, packaging, or usage discipline could harden a margin problem rather than solve it.

### 3. The commercial signal is real, but not yet quantified enough for a two-year lock-in

Enterprise customers are asking for **data residency, audit logs, and latency commitments**, and sales sees **$6M of at-risk expansion pipeline** tied to AI feature reliability. This is important, but the context does not establish that a full two-year reservation is the only way to address those requirements, nor does it quantify how much of the at-risk pipeline would actually convert if reliability improves.

That uncertainty favors a staged approach.

## Staged Options

### Option A: Commit now to full two-year reservation
**Pros:** lower expected unit cost; stronger reliability posture.  
**Cons:** major fixed-cost lock-in; runway compression risk; may worsen downside if growth slows.

### Option B: Preserve optionality for six months
**Pros:** protects cash; allows validation of demand, reliability impact, and margin response; avoids immediate two-year lock-in.  
**Cons:** higher near-term capacity cost; risk that reliability issues continue to pressure expansion.

### Option C: Seek staged or partial commitment
This is the preferred operating path **if available**, but availability is uncertain from the context. Management should attempt to negotiate:
- smaller reserved blocks,
- phased ramp commitments,
- or contractual checkpoints.

Because the context does not confirm these are possible, the board should not rely on them, but should direct management to pursue them.

## Trigger Thresholds for Revisit

Revisit the full reservation decision within six months if management can show:

1. **Reliability-linked revenue evidence:** a clear reduction in the **$6M at-risk expansion pipeline** attributable to improved AI reliability.
2. **Margin stabilization evidence:** gross margin stops deteriorating from the current **66%** level, or management demonstrates a credible path to offset inference cost growth.
3. **Enterprise requirement evidence:** data residency, audit logs, and latency commitments are confirmed as gating items for meaningful expansion, not just preferences.
4. **Runway protection evidence:** finance confirms the commitment no longer creates unacceptable downside relative to the current **24-month to 15-month** sensitivity.

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---:|---|
| Commit too early and lock in excess fixed cost | Runway compression; lower flexibility | Medium | Delay six months; seek staged terms |
| Wait too long and lose expansion | Revenue growth pressure; weaker enterprise credibility | Medium | Prioritize reliability work now using on-demand capacity |
| Margin continues to deteriorate | Lower profitability and valuation resilience | High | Track inference economics and pricing response before long-term commit |
| Demand volatility makes reservation inefficient | Underutilized capacity | Medium | Use six-month observation period; set utilization triggers |
| Enterprise requirements exceed current capability | Expansion delays | Medium | Focus roadmap on data residency, audit logs, latency commitments |

## Near-Term Action Plan

Over the next