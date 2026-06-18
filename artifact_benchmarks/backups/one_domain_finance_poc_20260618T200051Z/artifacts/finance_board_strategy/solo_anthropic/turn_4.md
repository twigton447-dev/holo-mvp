# Board Strategy Memo: AI Infrastructure Capacity Decision

**To:** Board of Directors and Chief Financial Officer
**From:** Strategy & Finance
**Date:** [Current Quarter]
**Re:** Commit to Two-Year Reserved AI Capacity vs. Preserve Optionality for Six Months
**Classification:** Confidential — Board Use Only

---

## Hostile Critique: Pressure-Test of the Repaired Memo

*Role: Skeptical Executive / Domain Expert*
*Purpose: Surface remaining weaknesses, logical gaps, and decision-avoidance mechanisms that a rigorous Board or CFO would challenge.*

---

### Challenge 1 — The Staged Path Is Still a Decision-Avoidance Mechanism

**The problem:** The memo recommends a 50% partial commitment but cannot confirm that partial contracts are commercially available. The entire recommendation is therefore contingent on a negotiation outcome that has not occurred. The Board is being asked to approve a strategy whose primary structural feature — partial reserved capacity — may not exist as a product the provider sells.

**The deeper issue:** If the provider requires all-or-nothing terms, the memo's contingency branch instructs management to "return to the Board within 30 days with a revised binary recommendation." That means the Board may be making this decision twice, with the first vote producing no binding outcome. A skeptical CFO will ask: why are we convening a Board decision on a recommendation that is explicitly conditional on a commercial negotiation we have not yet attempted? The sequencing is inverted. Management should have tested partial contract availability *before* bringing this memo to the Board, not after.

**What the memo should do but does not:** Either confirm that partial contracts are available as a precondition for presenting this recommendation, or present the binary choice as the primary decision with the staged path as a preferred outcome to pursue in negotiation. As written, the memo presents the staged path as the recommendation and the binary as the fallback — but the binary may be the only real choice.

---

### Challenge 2 — The 50% Commitment Figure Has No Analytical Basis

**The problem:** The memo recommends committing to "approximately 50% of available reserved capacity" at "~$4.8M/year." This figure is arithmetically derived from halving the $9.6M contract price. There is no analysis of what 50% of reserved capacity actually covers in operational terms — what percentage of current inference workload it supports, whether it is sufficient to meet enterprise latency commitments, or whether it addresses the specific reliability concerns driving the $6M at-risk pipeline.

**The challenge a CTO will raise:** If 50% of reserved capacity covers only 40% of peak inference demand, the reliability improvement for enterprise customers may be negligible. The memo would then be spending $4.8M/year to partially address a problem while still losing the $6M pipeline. Conversely, if 50% of reserved capacity covers 90% of workload, the memo is leaving $4.8M of cost savings on the table by not committing fully.

**What is missing:** A utilization analysis connecting reserved capacity volume to actual inference workload. Without it, the 50% figure is arbitrary. The memo should either acknowledge this gap explicitly — *"the 50% figure is a financial placeholder pending CTO confirmation of workload coverage"* — or defer the specific commitment percentage to the CTO's technical assessment.

---

### Challenge 3 — The $6M Pipeline Attribution Remains Structurally Weak

**The problem:** The memo appropriately flags that Sales attribution should be stress-tested and calls for CRO deal-by-deal documentation. However, the recommendation is still partly justified by the $6M figure in the Executive Summary, where it is presented as a live revenue risk driving urgency. A skeptical Board member will note the contradiction: the memo simultaneously treats $6M as a reason to act now and acknowledges it may not be a reliable figure.

**The harder question:** If the CRO review reveals that reliability is the primary blocker for only $2M of the $6M pipeline — and the remaining $4M is at risk due to pricing, competitive alternatives, or feature gaps that infrastructure investment does not address — does the staged commitment still make sense at $4.8M/year? The memo does not answer this. The Stage 2 trigger threshold requires "$3M of $6M converted" to validate reliability as a revenue driver, but by that point the company has already spent $4.8M in Year 1. The validation comes after the spend, not before.

**What the memo should do:** Establish a minimum pipeline validation threshold *before* Stage 1 commitment, not only at the six-month gate. If the CRO review (21-day deadline) cannot confirm that reliability is the primary blocker for at least $3M of the pipeline, the urgency case for even a partial commitment weakens materially.

---

### Challenge 4 — Gross Margin Recovery Is Treated as a Parallel Track, Not a Prerequisite

**The problem:** The memo correctly notes that reserved capacity hedges cost-per-unit but does not solve volume-driven margin compression. It calls for a 60-day inference pricing and volume review. However, the memo does not establish any dependency between the pricing review outcome and the Stage 1 commitment decision. The company could commit $4.8M/year to reserved capacity and then discover in the pricing review that inference volume is growing at a rate that will exhaust reserved capacity within 12 months — at which point on-demand pricing resumes and margin compression continues.

**The CFO's challenge:** The memo targets gross margin recovery to ≥69% as a Stage 2 trigger for expanding commitment. But if margin has not recovered by the six-month gate, the memo's guidance is to "maintain partial; reassess at 12 months." This means the company could be paying $4.8M/year for reserved capacity while margin continues to compress, with no exit mechanism from the partial commitment. The one-year initial term creates a floor on this exposure, but the memo does not explicitly state what happens if the one-year term ends with margin still below 69% and the pipeline still at risk.

**What is missing:** A stated outcome for the scenario in which Stage 2 triggers are not met at six months and the one-year term approaches expiration. Does the company renew the partial commitment, allow it to lapse, or escalate to full commitment despite unmet triggers? The memo is silent on this.

---

### Challenge 5 — The Runway Floor Is Still Not Grounded in Financing Reality

**The problem:** The memo proposes 18 months as the minimum runway floor and offers a rationale: *"18 months provides sufficient time to reach the next ARR milestone at which external financing becomes available on favorable terms."* This is an improvement over the prior draft, but it introduces a new unverified claim. What is the next ARR milestone? At 18% YoY growth on $42M ARR, the company reaches approximately $50M ARR in roughly 12 months. The memo does not state whether $50M ARR is the financing threshold, whether the financing market supports that assumption, or whether the Board has any basis for believing external capital will be available at that milestone.

**The challenge:** If the financing assumption is wrong — if the company needs $60M ARR or a different metric to access favorable financing — then 18 months of runway may be insufficient, and the staged commitment may still create unacceptable cash risk. The Board is being asked to ratify a runway floor derived from an unstated financing assumption.

**Repair needed:** The memo should either present the financing milestone explicitly — *"the Board has indicated that $X ARR or [specific milestone] is the threshold for Series [X] financing"* — or acknowledge that the 18-month floor is a proposed policy threshold requiring Board ratification based on the Board's own financing strategy, not a figure derived from available data.

---

### Challenge 6 — The Action Plan Has No Escalation Protocol for Missed Deadlines

**The problem:** The near-term action plan assigns 21-day deadlines to the CTO, CFO, and CRO. The memo does not specify what happens if these deadlines are missed. In a mid-market SaaS company, a 21-day cross-functional deliverable involving infrastructure negotiation, cash flow modeling, and deal-by-deal pipeline review is aggressive. If the CTO cannot confirm partial contract availability within 21 days because the provider requires a longer negotiation cycle, the entire staged path is in limbo.

**The practical risk:** The Board approves the staged recommendation. The CTO begins negotiating. At day 25, the provider has not responded. At day 30, the CFO model is complete but the contract terms are unknown. The six-month gate review is now operating on an uncertain foundation. Meanwhile, enterprise customers are still evaluating alternatives.

**What is missing:** An explicit escalation protocol — *"if partial contract terms are not confirmed within 21 days, the CEO will convene an emergency Board call to determine whether to proceed with full commitment, full on-demand, or extend the negotiation window by [X] days"* — and a stated maximum negotiation window beyond which the company defaults to on-demand to avoid indefinite indecision.

---

### Challenge 7 — The Two-Year Lock-In Risk Is Understated in the Contingency Branch

**The problem:** The contingency branch instructs the Board that if partial contracts are unavailable, management will return with a binary recommendation. The risk register includes "stranded capacity from AI architecture shift" at Low/Medium likelihood. However, the two-year lock-in is explicitly flagged as a hidden trap in the source context, and the memo's treatment of it in the contingency scenario is thin.

**The specific concern:** If the company is forced into a binary choice and selects full two-year commitment, it is locking $19.2M of total capacity cost into a two-year window during which AI inference architecture is evolving rapidly. The memo recommends requiring "contract portability or credit provisions" as a mitigation, but does not assess the likelihood that a provider offering reserved accelerator capacity will agree to portability provisions — or what "portability" means in practice if the company's architecture migrates to a different model type or provider.

**What the memo should acknowledge:** The portability mitigation may not be commercially available. If it is not, the two-year lock-in risk is unmitigated, and the Board should treat full commitment as carrying a material stranded-cost risk that is not offset by the revenue defense case unless the $6M pipeline attribution is confirmed and the margin recovery plan is credible.

---

### Net Assessment

The repaired memo is materially stronger than the initial draft. It eliminates the arithmetic error, appropriately brackets unverified figures, adds a contingency branch, and surfaces the margin compression causality issue. However, five structural problems remain that a rigorous Board session will surface:

1. The recommendation is contingent on a commercial negotiation that has not occurred and should be sequenced differently.
2. The 50% commitment figure lacks operational grounding in actual workload coverage.
3. The pipeline validation threshold should precede Stage 1 commitment, not follow it.
4. The memo is silent on the scenario in which Stage 2 triggers are unmet at the one-year term boundary.
5. The 18-month runway floor rests on an unstated financing assumption that the Board has not confirmed.

**The memo is approvable as a framework for further management work. It is not yet approvable as a final commitment authorization.** The Board should direct management to resolve items 1, 3, and 