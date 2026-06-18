# Evidence and Risk Critique: AI Infrastructure Capacity Memo

## Critique Summary

The current draft is structurally sound and avoids the three named hidden traps (pure cost framing, ignoring lock-in, missing triggers). However, it contains **five material flaws** that would expose the board to faulty reasoning if challenged. Each is identified below with a concrete repair instruction.

---

## Flaw 1: Unsupported Causal Claim — Capacity Is the Binding Constraint on Reliability

### The Problem

The memo repeatedly treats reserved capacity as the solution to the reliability problem driving the **$6M at-risk expansion pipeline**. It states that reliability issues may be "capacity-related rather than primarily product, architecture, or pricing-related" — but this is buried in Trigger 5 as a future test, while the rest of the memo implicitly assumes capacity is the lever.

This is the highest-value flaw. The source context does not establish that:

- Reliability incidents are caused by capacity constraints rather than software defects, model latency, or architectural choices.
- Reserved accelerator capacity would materially improve the reliability metrics that enterprise customers are actually measuring.
- The **$6M pipeline** is contingent on infrastructure reservation specifically, versus any reliability improvement.

If the root cause is product or architecture, committing to reserved capacity solves the wrong problem at **$19.2M total cost**.

### Repair Instruction

Reframe all reliability-to-capacity linkages as **unverified hypotheses**, not working assumptions. Add an explicit statement in the Assumptions section: *"The memo assumes capacity constraints are a contributing factor to reliability issues, but this is not confirmed by the available context. The board should treat the capacity-reliability linkage as a hypothesis requiring validation before any commitment."* Move Trigger 5 (operational root cause) to the top of the trigger list and label it a **prerequisite**, not a parallel condition.

---

## Flaw 2: Weak Evidence Use — The $6M Pipeline Figure Is Treated as More Precise Than It Is

### The Problem

The memo uses **$6M of at-risk expansion pipeline** as a recurring anchor for the commercial case. However, the source context states only that "Sales attributes $6M of at-risk expansion pipeline to AI feature reliability." This is a Sales attribution, not a validated commercial analysis. It may reflect:

- Optimistic pipeline inflation.
- Deals that are at risk for multiple reasons, with reliability cited as one.
- Expansion opportunities that would not convert even with perfect reliability.

The memo does not flag this attribution risk anywhere. Using an unvalidated Sales figure as a primary commercial trigger without qualification overstates the evidence base.

### Repair Instruction

Add a qualification wherever the **$6M** figure appears: *"This figure reflects Sales attribution and has not been independently validated against deal-level evidence."* In the Risk Register, add a row for **Pipeline Attribution Risk**: the $6M may overstate the revenue actually recoverable through infrastructure changes. In the trigger framework, require that the commercial trigger include deal-level validation, not just Sales-level attribution.

---

## Flaw 3: Missing Nuance — Gross Margin Decline Is Not Clearly Linked to Capacity Type

### The Problem

The memo states that gross margin fell from **73% to 66%** because inference usage increased faster than pricing changes, and implies that reserved capacity would help stabilize margins because it costs less than on-demand at **1.35x**. This reasoning has a gap.

The source context does not confirm that:

- The company is currently running on on-demand capacity (versus a prior reserved arrangement that expired or was undersized).
- The margin decline is primarily a unit cost problem rather than a pricing or usage-mix problem.
- Reserved capacity at **$9.6M/year** would produce margin recovery at current or projected utilization levels.

If the margin decline is driven by inference usage growing faster than pricing changes — a revenue-side and usage-mix problem — then switching to reserved capacity reduces unit cost but does not address the underlying pricing or usage discipline issue.

### Repair Instruction

Separate the margin analysis into two distinct drivers: **(a) unit cost of compute** and **(b) pricing and usage-mix discipline**. Acknowledge explicitly that the source context does not confirm which driver dominates. Add a statement: *"Reserved capacity may reduce compute unit cost, but if margin compression is primarily driven by inference usage outpacing pricing changes, the pricing and usage discipline problem must be addressed independently of the capacity decision."* Add a corresponding risk row in the Risk Register: **Margin Misdiagnosis Risk** — committing to reserved capacity may not stabilize gross margin if the root cause is pricing or usage-mix rather than compute unit cost.

---

## Flaw 4: Hidden Risk — Two-Year Lock-In Asymmetry Is Understated

### The Problem

The memo acknowledges the two-year lock-in as a risk but does not fully surface the asymmetry of the commitment. Specifically:

- The company's ARR is **$42M growing at 18% year-over-year**, but the source context explicitly flags that Finance's runway warning is conditional on growth slowing. The memo does not stress-test what happens if growth slows to, for example, single digits or flat — a scenario that is plausible for a mid-market SaaS company facing margin pressure.
- The **$19.2M total commitment** represents approximately **46% of current cash** (**$19.2M / $31M**). This concentration risk is not stated explicitly.
- The memo does not address what happens if the company's AI product strategy changes during the two-year window — for example, if a different model provider, architecture, or inference approach becomes available that makes the reserved accelerator capacity partially obsolete.

### Repair Instruction

Add a dedicated paragraph under the lock-in risk in the Risk Register quantifying the cash concentration: *"The full two-year commitment of $19.2M represents approximately 46% of current cash of $31M."* Add a scenario note: *"If ARR growth decelerates materially, the runway compression Finance has flagged becomes a solvency-adjacent risk, not merely a strategic flexibility concern."* Add a new risk row: **Technology Obsolescence Risk** — a two-year accelerator reservation may not align with the company's AI architecture in year two if model or inference approaches shift. Label this risk as **uncertainty: incomplete context** since the source does not provide product roadmap information.

---

## Flaw 5: Trigger Framework Is Insufficiently Hardened — Triggers Are Conjunctive but Not Weighted

### The Problem

The memo states that a return to the board should occur if management can demonstrate "all or most" of the five triggers. This formulation is too loose. "All or most" allows a scenario where:

- The commercial trigger and margin trigger are met, but the **operational root cause trigger** (Trigger 5) is not — meaning the board could approve a commitment without knowing whether capacity is actually the problem.
- The liquidity trigger is not met (Finance still warns of runway compression), but the other four are, creating pressure to commit despite unresolved financial risk.

Additionally, the triggers lack **minimum evidence standards** — they describe conditions to observe but not what constitutes sufficient evidence to act.

### Repair Instruction

Restructure the trigger framework into two tiers:

- **Prerequisite triggers** (must be met before any commitment is considered): (1) Operational root cause confirmed — capacity is a material driver of reliability issues; (2) Liquidity trigger — Finance confirms runway remains acceptable under a downside growth scenario.
- **Supporting triggers** (at least two of three must be met): (3) Commercial trigger — $6M pipeline validated at deal level; (4) Enterprise requirement trigger — reservation confirmed as necessary for material enterprise opportunities; (5) Margin trigger — reserved capacity modeled to improve gross margin under observed utilization.

Label this structure explicitly in the memo so the board understands that the prerequisite triggers are non-negotiable gates, not factors to be weighed against others.

---

## Summary of Repair Instructions

| Flaw | Location to Repair | Instruction |
|---|---|---|
| Capacity-reliability linkage unsupported | Assumptions + Trigger 5 | Reframe as unverified hypothesis; elevate Trigger 5 to prerequisite gate |
| $6M pipeline figure unvalidated | All references + Risk Register | Add Sales attribution caveat; require deal-level validation in trigger |
| Margin decline root cause ambiguous | Analysis + Risk Register | Separate compute cost vs. pricing/usage drivers; add Margin Misdiagnosis risk row |
| Lock-in asymmetry understated | Risk Register + Decision Criteria | Quantify 46% cash concentration; add technology obsolescence risk; add downside growth scenario note |
| Trigger framework too loose | Trigger Thresholds section | Restructure into prerequisite gates and supporting triggers; remove "all or most" language |

---

## What the Memo Gets Right

These repairs should not obscure what the draft does well: it avoids inventing forecasts, uses only given numbers, surfaces staged options, and correctly identifies active deferral as superior to passive delay. The recommendation direction is defensible. The repairs above harden the evidentiary foundation so the board cannot be misled by unvalidated assumptions embedded in the analysis.