# Evidence and Risk Critique: AI Infrastructure Capacity Contract Board Strategy Memo

**Role:** Evidence and Risk Critic
**Turn:** 2 of 6
**Purpose:** Identify unsupported claims, missing nuance, hidden risks, weak evidence use, and failure modes. Provide concrete repair instructions for each finding.

---

## Finding 1: The "50% Partial Commitment" Figure Is Invented

**Problem:** The memo's central recommendation — committing to "approximately 50% of the offered volume" — has no basis in the source context. The context pack states the contract is offered at $9.6 million per year for two years. It does not state that partial tranches are available, what increment sizes the provider offers, or whether a 50% split is commercially meaningful. The memo acknowledges this risk in Assumption 5 but then proceeds to build the entire recommendation on the unverified premise.

**Severity:** High. This is the load-bearing number in the recommendation. If the contract is all-or-nothing, the staged framework collapses.

**Repair instruction:** Reframe the recommendation as conditional. Lead with: *"If partial commitment is negotiable, we recommend an initial tranche not to exceed $X annually [derive from runway math, not an arbitrary 50%]. If the contract is all-or-nothing, the full-commitment decision criteria in Section 5 apply."* Derive the partial tranche ceiling from the runway constraint: the board has stated 20 months as a floor, so back-calculate the maximum annual fixed obligation that preserves that buffer at base-case growth, and use that number — not 50%.

---

## Finding 2: Runway Math Is Incomplete and Partially Contradictory

**Problem:** The memo states Finance warns that full commitment reduces runway from 24 months to 15 months. It then states the base case assumes 18% ARR growth "partially offsets" cash consumption — but provides no arithmetic to support this. The reader cannot verify whether the 15-month figure already incorporates 18% growth or assumes zero growth. The memo also sets a decision threshold of "runway not below 20 months" for the partial commitment without showing whether a partial commitment actually achieves that.

**Severity:** High for a CFO audience. The CFO will immediately ask for the arithmetic.

**Repair instruction:** Add a simple three-row sensitivity table using only the numbers in the context pack: (a) full commitment at base-case growth, (b) partial commitment at base-case growth, (c) full commitment at growth slowdown. Acknowledge explicitly that the context pack does not define "growth slowdown" and label that cell as uncertain. Do not invent a slowdown percentage; instead, note that Finance should supply this input before the board vote.

---

## Finding 3: The $6 Million Pipeline Attribution Is Treated as Fact Without Qualification

**Problem:** The memo states the sales team "attributes" $6 million of at-risk expansion pipeline to AI feature reliability. The source context uses the word "attributes," which is a soft causal claim, not a verified revenue forecast. The memo briefly acknowledges this in Assumption 1 but then treats the $6 million as a hard number throughout the risk register and decision criteria without flagging the evidentiary weakness again.

**Severity:** Medium-High. A board member or CFO who pushes on this will correctly note that sales attribution is often optimistic and self-serving.

**Repair instruction:** Every time the $6 million figure appears in the risk register or decision criteria, append a parenthetical: *(sales-attributed; independent validation recommended before board vote).* Add a pre-decision action item: "Request CRM-level deal data from sales leadership to verify pipeline stage, decision timeline, and whether infrastructure commitments are the stated blocker or a contributing factor."

---

## Finding 4: Gross Margin Analysis Conflates Two Distinct Problems

**Problem:** The memo correctly identifies that gross margin fell from 73% to 66% over three quarters due to inference cost growth outpacing pricing. It then implies that reserved capacity will "arrest this decline." This is only partially true. Reserved capacity lowers unit cost relative to on-demand (by approximately 1/1.35, or roughly 26%), but it does not address the volume growth of inference usage, which is the other driver of margin compression. If inference volume continues to grow faster than revenue, margin will continue to decline even with reserved pricing.

**Severity:** Medium. The memo does note in the risk register that "reserved capacity addresses unit cost, not product pricing," but this caveat is buried and not surfaced in the executive summary or situation assessment.

**Repair instruction:** Add one sentence to the Situation Assessment: *"Reserved capacity reduces unit cost but does not address inference volume growth. A parallel workstream on usage-based repricing or inference optimization is required; this memo does not evaluate that workstream."* Elevate the repricing caveat from the risk register into the near-term action plan as a named workstream with an owner.

---

## Finding 5: The Risk Register Omits a Critical Counterparty Risk

**Problem:** The risk register does not include the risk that the cloud provider uses a two-year commitment to extract unfavorable terms at renewal, or that the provider's accelerator roadmap changes in ways that make the reserved capacity less competitive by year two. The context pack does not provide information about provider terms, but the memo should surface this as a named uncertainty rather than ignoring it.

**Severity:** Medium. Two-year infrastructure lock-in is explicitly flagged as a hidden trap in the source context, and the risk register addresses it only partially (noting "exit or renegotiation clauses at 12-month review" without acknowledging that such clauses may not be available).

**Repair instruction:** Add a row to the risk register: *"Provider roadmap or pricing terms deteriorate in year two; reserved capacity becomes architecturally or economically inferior. Likelihood: uncertain (context incomplete). Mitigant: negotiate most-favored-nation pricing clause and architecture portability terms before signing; label as a legal/procurement pre-condition, not a post-signing hope."*

---

## Finding 6: Decision Criteria Thresholds Are Asserted Without Derivation

**Problem:** The memo sets specific thresholds — 15% ARR growth floor, $4 million pipeline conversion, 70% utilization, 66% gross margin baseline — without explaining how these numbers were derived. Some are drawn from the context pack (66% margin, 18% growth), but others (15% floor, 70% utilization, $4 million conversion) appear to be editorial choices presented as analytical conclusions.

**Severity:** Medium. A board will ask