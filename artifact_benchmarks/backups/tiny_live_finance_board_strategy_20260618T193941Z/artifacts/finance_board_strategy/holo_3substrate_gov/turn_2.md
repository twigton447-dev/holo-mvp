# Evidence and Risk Critique: Board Strategy Memo on AI Infrastructure Capacity

## Overall Assessment

The draft is structurally sound and avoids the most obvious traps (pure cost framing, ignoring lock-in). However, it contains several unsupported claims, incomplete risk treatments, logical gaps, and one critical section that is simply missing. Each issue is identified below with a concrete repair instruction.

---

## Issue 1: The "Preserve Optionality" Recommendation Understates Its Own Cost

**Problem:** The draft recommends on-demand capacity for six months but does not quantify what that costs relative to the reserved alternative. It states on-demand is "roughly 1.35x reserved price at expected utilization" but never translates that into a dollar figure the board can evaluate. The recommendation therefore appears to be free optionality, when it is not.

**Evidence gap:** The context provides enough data to approximate the cost differential. If reserved capacity costs $9.6M per year ($800K per month), then on-demand at 1.35x costs approximately $1.08M per month, or roughly $280K more per month than reserved. Over six months, the optionality premium is approximately $1.68M. The draft never surfaces this number.

**Repair instruction:** Add a sentence in the Recommendation section and in the Analysis section that explicitly states the estimated six-month cost of on-demand versus reserved. Acknowledge that "preserving optionality" carries a real cash cost of approximately $1.68M at expected utilization, and that this cost must be weighed against the runway and flexibility benefits. Label this estimate as approximate given demand volatility.

---

## Issue 2: The $6M At-Risk Pipeline Is Treated as a Floor, Not a Range

**Problem:** The draft repeatedly cites "$6M of at-risk expansion pipeline" as if it is a precise, reliable figure. The context attributes this to sales, which introduces selection bias and optimism risk. The draft does not acknowledge that sales-attributed pipeline figures are typically unverified and may overstate the reliability-revenue link.

**Evidence gap:** The context does not confirm that all $6M would convert if reliability improves, nor does it confirm that reliability is the sole or primary barrier. The draft acknowledges this briefly in the Analysis section but then uses the $6M figure without qualification in the Risk Register and Decision Criteria.

**Repair instruction:** Every reference to the $6M figure should carry a qualifier such as "sales-attributed" or "unverified." The Risk Register should include a row for the risk that the at-risk pipeline is overstated, with the consequence that the commercial case for commitment is weaker than presented. The trigger thresholds section should require independent validation of the pipeline figure, not just management assertion.

---

## Issue 3: The Near-Term Action Plan Is Incomplete — The Section Is Cut Off

**Problem:** The Near-Term Action Plan section ends mid-sentence: "Over the next." This is a critical deliverable requirement and it is missing entirely from the current draft.

**Repair instruction:** Complete the section. It should include at minimum: (a) a named owner for each action, (b) a time-bound milestone for each action within the six-month window, (c) specific actions on margin stabilization, enterprise requirement validation, pipeline verification, and contract negotiation exploration. Without this section, the memo does not meet the deliverable specification.

---

## Issue 4: The Risk Register Omits the Opportunity Cost of Waiting

**Problem:** The Risk Register includes "wait too long and lose expansion" but frames it vaguely as "revenue growth pressure." It does not quantify the downside. If the $6M pipeline is at risk and the company grows at 18% YoY on $42M ARR, losing or delaying $6M of expansion is not a minor item — it represents approximately 14% of current ARR. The register underweights this.

**Repair instruction:** Revise the "wait too long" risk row to note that $6M represents approximately 14% of current ARR. Upgrade the likelihood rating with a brief rationale. Add a note that if expansion slows, the runway sensitivity Finance identified (24 months to 15 months) could worsen further, creating a compounding risk rather than an independent one.

---

## Issue 5: Staged Options Are Presented Without Acknowledging the Negotiation Risk

**Problem:** Option C (staged or partial commitment) is described as the "preferred operating path if available," but the draft then says the board should not rely on it. This is contradictory. If it is preferred but unavailable, the board needs to understand what happens to the recommendation if the provider will not negotiate. The draft does not address this failure mode.

**Repair instruction:** Add a sentence explicitly stating: if the provider declines staged terms, the binary choice reverts to Option A or Option B, and the recommendation remains Option B. Remove the language calling Option C "preferred" unless the memo also explains what evidence would make it preferred over Option B.

---

## Issue 6: Gross Margin Analysis Does Not Distinguish Fixed from Variable Cost Effects

**Problem:** The draft correctly identifies that gross margin fell from 73% to 66% because inference usage rose faster than pricing changes. However, it does not distinguish between two different causes: (a) variable inference costs growing faster than revenue, and (b) the potential effect of adding $9.6M in fixed annual cost. These are different problems with different solutions. Conflating them weakens the analysis.

**Repair instruction:** Add a sentence clarifying that the current margin decline is driven by variable inference cost growth, not by fixed infrastructure cost. Then note that adding a $9.6M fixed annual commitment would create a second, independent margin pressure — one that does not flex down if utilization falls. This distinction strengthens the case for caution and is more precise than the current framing.

---

## Summary of Required Repairs

| Issue | Section Affected | Priority |
|---|---|---|
| Optionality cost not quantified (~$1.68M) | Recommendation, Analysis | High |
| $6M pipeline figure unqualified | All sections | High |
| Near-term action plan missing | Near-Term Action Plan | Critical |
| Opportunity cost of waiting understated | Risk Register | Medium |
| Option C contradiction | Staged Options | Medium |
| Margin analysis conflates fixed and variable cost | Analysis | Medium |