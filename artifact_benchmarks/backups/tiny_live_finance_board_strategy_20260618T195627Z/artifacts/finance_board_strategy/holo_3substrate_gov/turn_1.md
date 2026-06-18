# Board Strategy Memo: AI Infrastructure Capacity Commitment

## Recommendation

**Recommend preserving optionality for six months rather than committing immediately to the full two-year reserved AI infrastructure contract.**  
At the same time, management should use the next six months to test whether reliability-driven revenue protection and expansion justify taking on the fixed-cost lock-in.

This is the better choice based on the current facts because:

- The company has **$31M cash and no debt**, but finance warns that a full commitment could reduce runway from **24 months to 15 months if growth slows**.
- Gross margin has already declined from **73% to 66%** over three quarters because inference usage increased faster than pricing changes.
- A two-year reservation would add **$9.6M per year for two years** of fixed cost.
- There is a real commercial risk in waiting: sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability, and enterprise customers are asking for **data residency, audit logs, and latency commitments**.

Given these conflicting signals, the board should avoid an immediate full lock-in and instead adopt a **staged decision framework with explicit triggers**. The company should preserve cash and flexibility now, while gathering evidence on whether reliability improvements are necessary and sufficient to protect margin and expansion.

## Decision Framing

The decision is not simply “reserved capacity is cheaper than on-demand.” That would be a pure cost framing and would miss the strategic issue.

The actual board question is:

> Should the company accept a two-year fixed infrastructure obligation now in order to improve reliability and enterprise readiness, or wait six months to preserve runway and reassess with better evidence?

The trade-off is clear:

- **Commit now:** potentially improves reliability, supports enterprise requirements, and may defend expansion revenue; but creates a meaningful fixed-cost obligation and two-year lock-in.
- **Wait six months:** preserves cash and strategic flexibility; but may weaken the expansion pipeline and delay enterprise-grade commitments.

## Explicit Assumptions

Because the context is incomplete, the following assumptions are stated explicitly:

1. **The reserved capacity contract is effectively a full two-year commitment** at **$9.6M per year**, with meaningful lock-in and limited flexibility.  
2. **On-demand capacity remains available** during the next six months, at roughly **1.35x reserved price at expected utilization**, though actual cost may vary because demand is volatile.
3. **Reliability concerns are material but not fully quantified** beyond the stated **$6M at-risk expansion pipeline**.
4. **Enterprise asks for data residency, audit logs, and latency commitments** may require more than just raw capacity; the context does not confirm that a reservation alone solves all three.
5. **Growth uncertainty is meaningful**, as finance specifically warns runway could fall from **24 months to 15 months if growth slows**.
6. No market forecast, customer-level commitment, or pricing offset data is available; therefore no ROI model beyond the provided facts should be treated as proven.

## Decision Criteria

The board should evaluate the choice against five criteria:

1. **Runway preservation**  
   Does the decision maintain sufficient cash flexibility under slower-growth conditions?

2. **Gross margin protection**  
   Does the decision help stop or reverse the decline from **73% to 66%**, or does it risk worsening margin through fixed cost without pricing recovery?

3. **Revenue defense and expansion support**  
   Does the decision materially protect the **$6M at-risk expansion pipeline** tied to AI feature reliability?

4. **Enterprise readiness**  
   Does the decision improve the company’s ability to meet customer demands for **data residency, audit logs, and latency commitments**?

5. **Reversibility**  
   Does the decision preserve the ability to adapt if demand, utilization, or growth changes over the next six months?

Against these criteria, preserving optionality currently scores better on reversibility and runway, while immediate commitment scores better only if reliability improvements are both urgent and contractually dependent on reserved capacity—something not proven in the context.

## Analysis

### Why not commit now

A full commitment now would convert a variable infrastructure burden into a large fixed obligation: **$19.2M over two years**. For a company with **$31M cash**, that is material. The finance warning is especially important: if growth slows, runway could drop from **24 months to 15 months**. That is a board-level risk.

The company is also already experiencing margin pressure. Gross margin fell **7 points** over three quarters because inference usage outpaced pricing changes. A reserved contract may lower unit cost relative to on-demand at expected utilization, but it does not by itself solve the underlying issue that usage economics are currently outrunning monetization.

There is also a lock-in risk. If demand proves lower than expected, or if enterprise requirements require architecture changes beyond capacity, the company could be left with a two-year fixed commitment that does not fully address the commercial problem.

### Why not simply wait passively

Waiting has real downside. Sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability. Enterprise customers are explicitly asking for **data residency, audit logs, and latency commitments**. If the company cannot credibly address these needs, it may lose expansion momentum even if it preserves cash.

So the recommendation is not “do nothing.” It is to **preserve optionality while actively testing the case for commitment**.

## Staged Options and Trigger Thresholds

### Option A: Commit now to full two-year reservation
Use only if near-term evidence already shows that reserved capacity is necessary to secure reliability and enterprise commitments.  
**Current recommendation: do not choose now.**

### Option B: Preserve optionality for six months, then decide
**Recommended option.** Continue on-demand capacity while management gathers evidence and prepares a board decision package.

**Trigger thresholds for reconsidering commitment within six months:**
- If the **$6M at-risk expansion pipeline** converts from “at-risk” to likely lost absent reliability commitments, escalate.
- If enterprise deals increasingly require **latency commitments, data residency, and audit logs** that management cannot support credibly without reserved capacity, escalate.
- If runway risk worsens or growth slows further, do **not** commit; preserving cash becomes more important.
- If gross margin continues to deteriorate despite on-demand operation and no pricing response is available, reassess whether reservation improves economics enough to justify lock-in.  
  *Uncertainty: the context does not quantify the margin benefit at actual utilization.*

## Risk Register

| Risk | Impact | Direction if Commit Now | Direction if Wait 6 Months |
|---|---|---:|---:|
| Runway compression if growth slows | High | Worse | Better |
| Two-year lock-in | High | Worse | Better |
| Loss of expansion pipeline tied to reliability | High | Better if capacity solves reliability | Worse |
| Continued gross margin pressure | High | Unclear; may improve unit cost but adds fixed cost | Unclear; on-demand remains more expensive at expected utilization |
| Failure to meet enterprise requirements | High | Possibly better, but not proven | Worse unless mitigated operationally |
| Demand volatility | Medium/High | Worse if underutilized | Better |

## Near-Term Action Plan

Over the next six months,