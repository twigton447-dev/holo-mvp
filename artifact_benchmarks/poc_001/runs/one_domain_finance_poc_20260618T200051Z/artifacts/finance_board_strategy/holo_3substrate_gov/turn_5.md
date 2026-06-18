# Board Strategy Memo: AI Infrastructure Capacity Commitment

**To:** Board of Directors and CFO
**From:** Management
**Subject:** Two-Year AI Infrastructure Capacity Contract — Recommendation and Decision Framework
**Classification:** Board Confidential

---

## Recommendation

**Do not sign the full two-year reserved AI infrastructure contract now. Preserve optionality for a structured six-month validation window, then return to the board with a trigger-based commitment decision.**

This recommendation rests on four findings:

1. The $19.2M total obligation (~46% of $31M cash) creates severe runway risk under a growth-slowdown scenario, reducing runway from 24 months to 15 months per Finance.
2. The causal link between reserved capacity and the reliability problems driving the Sales-attributed $6M at-risk expansion pipeline is an unverified hypothesis, not an established fact.
3. Waiting six months at expected utilization carries an estimated incremental on-demand premium of approximately **$1.68M** — a real but bounded cost that is justified by the evidence gaps that must be closed before a $19.2M irreversible commitment is appropriate.
4. Future reservation availability and pricing are **not confirmed**. The board should understand that "preserve optionality" does not mean a guaranteed option exists at month six; it means avoiding an irreversible commitment today while actively working to resolve uncertainty.

---

## Why Six Months, Not Three or Twelve

The six-month window is not arbitrary. It is the minimum interval required to complete three sequential workstreams that cannot be compressed without producing unreliable evidence:

- **Root cause diagnosis** (30–60 days) requires observing reliability incidents across a meaningful usage sample under current on-demand conditions, separating capacity constraints from product, architecture, and pricing drivers.
- **Deal-level pipeline validation** (60–90 days) requires re-qualifying the $6M at-risk expansion pipeline against actual customer requirements, not Sales attribution.
- **Margin stabilization assessment** (90–180 days) requires testing whether pricing or usage-mix changes can arrest the 73%→66% gross margin decline before attributing the problem to compute unit cost alone.

Three months is insufficient to complete all three workstreams with defensible evidence. Twelve months is unnecessary if the evidence is clear by month six — and the $1.68M incremental cost of waiting argues against extending the window without cause. Six months is the minimum credible validation period.

---

## Cost of Waiting

At expected utilization, reserved capacity costs $9.6M per year. On-demand costs approximately 1.35× that figure, or roughly $12.96M per year. The annual premium for on-demand versus reserved at expected utilization is therefore approximately **$3.36M**. Over six months, the implied incremental cost of waiting is approximately **$1.68M**.

This figure is directionally correct but subject to demand volatility. If utilization runs below expected levels, the realized premium will be lower. If utilization is high and sustained, the premium may be higher and the company may simultaneously face reliability pressure. The board should treat $1.68M as the central estimate of the financial cost of the validation window, not as a ceiling.

This cost is real. The recommendation is that it is worth paying to avoid locking in $19.2M before the prerequisite evidence exists.

---

## Explicit Assumptions

The following assumptions underpin this recommendation and must be validated during the six-month window:

1. **Capacity-reliability linkage is unverified.** The source context does not establish that capacity constraints are a material driver of reliability issues. The root cause may be product, architecture, or pricing factors. This is the highest-risk assumption in the analysis.
2. **Future reservation availability is unknown.** The $9.6M/year reserved price and the specific capacity block may not be available on comparable terms at month six. The board is not preserving a guaranteed option; it is avoiding an irreversible commitment while uncertainty is high.
3. **The $6M at-risk expansion pipeline is Sales-attributed and unvalidated.** It has not been confirmed at the deal level that infrastructure reservation would recover this amount.
4. **On-demand capacity remains available during the window**, at approximately 1.35× reserved price at expected utilization, with demand volatility risk.
5. **Growth trajectory is uncertain.** Finance's runway warning is conditioned on growth slowing; the base case is 18% YoY ARR growth on $42M ARR, but this is not guaranteed.
6. **No intermediate contract structures** (partial reservation, shorter term, phased commitment) are described in the available context. The board is choosing between full commitment and on-demand; no hybrid option is confirmed to exist.

---

## Risk Register

| Risk | Financial / Commercial Impact | Likelihood | Mitigation |
|---|---|---|---|
| Runway compression from full commitment | Runway falls from 24 to 15 months if growth slows; $19.2M = ~46% of cash | High if growth slows | Preserve optionality now; require CFO revalidation before any commitment |
| Future reservation unavailable or repriced | Later commitment may cost more or be unavailable; optionality is not guaranteed | Unknown — context does not confirm | Engage provider to understand availability horizon; treat as a time-sensitive inquiry |
| Expansion loss from reliability weakness | Sales attributes $6M pipeline at risk; unvalidated but directionally material | Medium | Prioritize root cause diagnosis; validate at deal level within 90 days |
| Margin misdiagnosis | GM fell 73%→66%; reserved capacity addresses unit cost only, not pricing/usage discipline | High | Separate compute-cost from pricing drivers before commitment |
| Underutilized reserved capacity | Volatile demand may result in paying for unused capacity under a two-year lock-in | Medium-High | Delay commitment until usage patterns are clearer |
| Enterprise deal friction | Customers require data residency, audit logs, latency commitments; delivery path unclear | Medium-High | Map requirements against what can be delivered without full reservation |
| Continued on-demand cost premium | ~$1.68M incremental cost over six months at expected utilization | Quantified and accepted | Treat as the explicit price of the validation window |
| Two-year technology lock-in | Accelerator reservation may not align with future AI architecture evolution | Medium | Monitor product and inference approach changes during window |
| Passive delay without milestones | Waiting without structured gates worsens pipeline and margin | High if unmanaged | Enforce monthly review cadence and gate discipline |

---

## Trigger Framework

A return to the board for commitment approval requires the following two-tier structure. Both prerequisite gates are non-negotiable. At least two of three supporting triggers must also be satisfied.

**Prerequisite Gates (both required):**

1. **Root cause confirmed with defined evidence standard.** Management demonstrates, using reliability incident data, latency measurements, and capacity utilization logs, that capacity constraints are a *primary* driver of reliability issues — not merely a contributing factor alongside product or architecture causes. Partial or ambiguous evidence does not satisfy this gate. The standard is: capacity constraints explain the majority of reliability incidents that enterprise customers have cited or that correlate with pipeline risk.

2. **Downside runway acceptable.** CFO confirms in writing that, under a defined growth-slowdown scenario, runway remains above a board-approved minimum threshold after the full commitment. Finance's existing warning that runway could fall to 15 months must be directly addressed and resolved.

**Supporting Triggers (at least two of three required):**

3. **Commercial trigger.** The $6M at-risk expansion pipeline is re-qualified at the deal level, with documented evidence that specific opportunities are contingent on AI reliability improvements that require reserved capacity specifically.

4. **Enterprise requirement trigger.** A material share of active enterprise opportunities explicitly requires data residency, audit logs, or latency commitments that management confirms cannot be credibly delivered on on-demand infrastructure.

5. **Margin trigger.** Gross margin has not stabilized from the current 66% level, and management demonstrates — after separating compute-cost from pricing/usage-mix drivers — that reserved capacity would materially improve unit economics under observed utilization.

**Default posture if gates are unmet at month six:** If both prerequisite gates are not satisfied by month six, the board does not commit. Management extends the on-demand posture, presents a revised timeline with specific evidence milestones, and returns only when gate conditions are met. The board should not treat month six as a forced decision point. The default is continued on-demand operation, not commitment under pressure.

---

## Near-Term Action Plan

**Days 1–30**
- CFO publishes a board-level AI capacity dashboard tracking: gross margin trend from the 66% baseline; AI-related reliability incidents and their commercial impact; and the $6M at-risk pipeline as a separately tracked line item.
- Management maps enterprise requirements across all active opportunities, documenting which of data residency, audit logs, and latency commitments are required and whether any can be met without reservation.
- Management initiates a conversation with the capacity provider to understand whether the current reserved pricing and capacity block will remain available and for how long. This is an information-gathering step, not a negotiation.

**Days 30–90**
- Engineering and infrastructure teams complete root cause analysis of reliability incidents, applying the evidence standard defined in Prerequisite Gate 1.
- Sales re-qualifies the $6M at-risk pipeline at the deal level, producing documented evidence of whether and how infrastructure reservation affects specific opportunities.
- Finance models gross margin trajectory under on-demand continuation, separating compute unit cost from pricing and usage-mix drivers.

**Days 90–180**
- Management assesses whether pricing or usage-mix changes can arrest margin decline independent of reservation.
- Monthly board review confirms gate and trigger status against defined evidence standards.
- At month six: management presents a gate-and-trigger scorecard. If both prerequisite gates and at least two supporting triggers are satisfied, management returns with a commitment recommendation. If not, the default posture applies and a revised milestone plan is presented.

---

## Summary

The board is being asked to decide between a $19.2M two-year fixed commitment and a structured six-month validation window that carries an estimated $1.68M incremental on-demand premium at expected utilization. The recommendation is to accept that premium in exchange for resolving three material uncertainties: whether capacity is actually the binding constraint on reliability, whether the $6M pipeline risk is real and reservation-dependent, and whether the company can absorb the commitment without unacceptable runway compression. The board should also note that the option to commit later is not guaranteed — future reservation availability and pricing are unknown — which makes the six-month window a period of active, time-sensitive evidence collection, not passive delay.