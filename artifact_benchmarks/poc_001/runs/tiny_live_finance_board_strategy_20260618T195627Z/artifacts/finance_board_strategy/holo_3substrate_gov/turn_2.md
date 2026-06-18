# Evidence and Risk Critique: AI Infrastructure Capacity Commitment Memo

---

## Overall Assessment

The draft is structurally sound and avoids the three named traps (pure cost framing, ignoring lock-in, omitting trigger thresholds). However, it contains several unsupported inferences, incomplete quantifications, logical gaps, and an unfinished near-term action plan that would undermine board confidence. Each issue is identified below with a concrete repair instruction.

---

## Issue 1: The On-Demand Cost Premium Is Asserted Without Quantification

**Problem:** The draft repeatedly states that on-demand capacity costs "roughly 1.35x reserved price at expected utilization" but never translates this into a dollar figure the board can evaluate. The phrase "at expected utilization" is doing significant work here—the source context explicitly flags that demand is volatile, meaning actual on-demand costs could be materially higher or lower than the 1.35x figure implies.

**Hidden risk:** If utilization is lower than expected, on-demand may cost less than the reserved contract. If utilization spikes, on-demand costs could exceed the 1.35x estimate significantly. Neither scenario is surfaced.

**Repair instruction:** Add a quantified range. At $9.6M reserved per year, the 1.35x multiplier implies approximately $13.0M per year on-demand at expected utilization—a $3.4M annual premium, or $6.8M over two years. State this explicitly. Then add a sentence acknowledging that because demand is volatile, actual on-demand cost could be higher or lower, and that this uncertainty is unresolved in the current context.

---

## Issue 2: The $6M At-Risk Pipeline Is Treated as Both Certain and Uncertain Simultaneously

**Problem:** The draft uses the $6M figure to justify urgency in the risk register and the staged triggers, but also correctly notes in the assumptions that reliability concerns are "material but not fully quantified." These two treatments are in tension. The draft never clarifies what "at-risk" means operationally—whether these deals are actively stalling, have issued ultimatums, or are simply flagged by sales as sensitive.

**Hidden risk:** If the board interprets "at-risk" as imminent churn, the recommendation to wait six months looks reckless. If "at-risk" means loosely flagged, the urgency case weakens. The memo does not help the board distinguish between these.

**Repair instruction:** Add a sentence in the Analysis section explicitly stating that the $6M figure is a sales attribution and that the memo cannot confirm whether these deals have issued contractual requirements or hard timelines. Flag this as a key information gap that management must resolve in the first 30 days of the action plan.

---

## Issue 3: Reserved Capacity Is Assumed to Solve Reliability—This Is Not Proven

**Problem:** The draft correctly notes in Assumption 4 that enterprise requirements "may require more than just raw capacity." However, the Analysis section and Risk Register both treat reserved capacity as a likely solution to reliability and enterprise readiness. This is an unsupported inference. Data residency and audit logs are architectural and compliance requirements, not capacity requirements.

**Hidden risk:** The company could commit $19.2M over two years and still fail to meet enterprise requirements if the bottleneck is software architecture, compliance certification, or data handling—not compute availability.

**Repair instruction:** In the Risk Register, add a new row: "Reserved capacity does not resolve enterprise requirements (data residency, audit logs)—Impact: High; Direction if Commit Now: Unchanged unless architecture work is also funded; Direction if Wait: Neutral." In the Analysis section, add an explicit statement that management must confirm whether capacity reservation is a necessary condition, a sufficient condition, or neither for meeting enterprise commitments before any commitment is made.

---

## Issue 4: The Runway Calculation Is Incomplete and Potentially Misleading

**Problem:** The draft states finance warns runway could fall from 24 months to 15 months if growth slows. It does not clarify whether this scenario assumes the full $9.6M annual commitment is drawn immediately, whether it assumes a specific growth slowdown rate, or whether operating expenses are held flat. The board cannot evaluate the severity of this warning without those parameters.

**Hidden risk:** The 15-month runway figure may be conservative or optimistic depending on assumptions not visible in the context. Presenting it without qualification could either alarm the board unnecessarily or give false comfort.

**Repair instruction:** Add a caveat sentence: "The finance scenario assumes [parameters unknown from available context]; the board should request the underlying model before treating 15 months as a firm floor." Do not invent the parameters—label the gap explicitly.

---

## Issue 5: The Near-Term Action Plan Is Incomplete

**Problem:** The draft ends mid-sentence: "Over the next six months," with no content following. This is the most operationally critical section for a board memo and is entirely absent.

**Repair instruction:** Complete the action plan with at minimum five time-bound items:

- **Days 1–30:** Sales and Customer Success to qualify the $6M at-risk pipeline—determine whether deals have issued hard reliability or compliance requirements with deadlines.
- **Days 1–30:** Engineering to confirm whether reserved capacity is a necessary condition for meeting latency commitments, or whether architectural changes are required independently.
- **Days 30–60:** Finance to model on-demand cost actuals against the 1.35x estimate using current utilization data; update runway scenarios.
- **Days 60–90:** Negotiate with the infrastructure vendor to determine whether a partial reservation (e.g., 50% of capacity) or a shorter initial term is available, preserving some cost benefit while reducing lock-in.
- **Day 180:** Board decision gate—present updated pipeline data, margin trend, and vendor terms against the trigger thresholds defined in the memo.

---

## Issue 6: The Risk Register Omits a Staged or Partial Commitment Option

**Problem:** The Risk Register presents only two options: commit now or wait. The memo mentions staged options in the framing but does not carry this through to the risk register. A partial reservation—if contractually available—could reduce both the runway risk and the pipeline risk simultaneously.

**Repair instruction:** Add a third column or a footnote row in the Risk Register for a partial/staged commitment scenario, with the caveat that contract flexibility is unconfirmed in the available context and must be verified with the vendor.

---

## Summary of Required Repairs

| Issue | Severity | Action |
|---|---|---|
| On-demand cost not quantified in dollars | High | Add $13M