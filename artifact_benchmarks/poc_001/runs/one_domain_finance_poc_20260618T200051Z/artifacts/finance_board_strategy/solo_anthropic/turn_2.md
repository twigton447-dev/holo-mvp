# Evidence and Risk Critique: AI Infrastructure Capacity Board Memo

**Role:** Evidence and Risk Critic
**Draft Under Review:** Turn 1 Board Strategy Memo
**Purpose:** Identify unsupported claims, missing nuance, hidden risks, weak evidence use, and failure modes. Provide concrete repair instructions.

---

## Overall Assessment

The draft is structurally sound and avoids the three flagged hidden traps (pure cost framing, ignoring lock-in, omitting trigger thresholds). However, it contains several evidentiary weaknesses, one material arithmetic problem, two logical gaps that a CFO will immediately challenge, and a set of risks that are either understated or absent entirely. Each issue is catalogued below with a specific repair instruction.

---

## Issue 1 — Material Arithmetic Error in the On-Demand Cost Comparison

**Location:** Financial Snapshot table, "Full on-demand" row.

**Problem:** The memo states on-demand costs "~$12.96M/year equivalent at 1.35×." This figure implies the company is currently spending $9.6M/year on reserved-equivalent capacity and multiplying by 1.35×. But the source context states that $9.6M/year is the *reserved* contract price, and on-demand costs 1.35× that *at expected utilization*. The memo treats the full $9.6M as the current baseline consumption, which is an assumption not supported by the provided data. We do not know the company's current actual inference spend. The $12.96M figure is therefore fabricated from an unverified baseline.

**Impact:** A CFO will immediately ask what the current actual inference cost is. If the company is spending less than $9.6M/year on inference today, the on-demand-vs-reserved comparison collapses. If it is spending more, the urgency of commitment increases. Either way, the memo cannot use $12.96M as a stated figure without grounding.

**Repair Instruction:** Replace the $12.96M figure with a bracketed placeholder: *"[Current inference spend × 1.35 — CFO to confirm actual run-rate before Board vote]."* Add a sentence in the Explicit Assumptions section acknowledging that the on-demand cost comparison requires confirmation of actual current inference expenditure, which is not provided in the available data. Do not present the $12.96M as a fact.

---

## Issue 2 — Runway Estimates Are Presented with False Precision

**Location:** Financial Snapshot table, "~19–20 months" runway estimates for the staged path.

**Problem:** The memo derives runway estimates directionally but presents "~19–20 months" as if it follows arithmetically from the provided data. The source context gives only two data points: $31M cash and a Finance warning that full commitment reduces runway from 24 to 15 months. The 19–20 month figure for a 50% commitment is interpolated linearly, which assumes cash burn is purely a function of the capacity contract cost. In reality, runway depends on operating burn rate, ARR growth timing, collections cycles, and other costs — none of which are provided. The interpolation is not supported by the context.

**Impact:** The Board and CFO will treat the 19–20 month figure as a modeled output. If Finance later produces a different number, the memo's credibility is damaged.

**Repair Instruction:** Replace "~19–20 months" with "*[Directional estimate: between 15 and 24 months depending on burn rate — requires CFO cash flow model].*" Add a footnote explicitly stating that the 19–20 month figure is a linear interpolation between two provided data points and should not be treated as a modeled runway projection. The action plan already calls for CFO modeling; the table should not pre-empt that work with a specific number.

---

## Issue 3 — The $6M Pipeline Attribution Is Accepted Uncritically

**Location:** Explicit Assumptions §3 and Decision Criteria §1.

**Problem:** The memo notes that the $6M pipeline attribution is "taken at face value" and "not independently verified," which is appropriately cautious. However, the Decision Criteria section then uses this figure as a near-certain revenue risk driver without preserving that uncertainty. Specifically, the statement "Reliability is not a feature preference — it is a contract prerequisite for this customer segment" is a strong causal claim that goes beyond what the data supports. The source context says Sales *attributes* $6M to reliability concerns. Sales teams routinely over-attribute pipeline risk to product gaps to accelerate infrastructure investment decisions.

**Impact:** If the Board approves the staged commitment partly on the basis of $6M at-risk pipeline and that pipeline was already at risk for other reasons (pricing, competition, product fit), the reliability investment will not recover it, and the memo's logic is undermined.

**Repair Instruction:** In Decision Criteria §1, add a qualifier: *"The $6M figure reflects Sales attribution and should be stress-tested. The CRO action item (14-day deadline) should specifically require deal-by-deal documentation of why reliability — rather than pricing, competitive alternatives, or feature gaps — is the primary blocker."* Soften the "contract prerequisite" language to: *"Enterprise customers have cited reliability as a stated requirement; the degree to which infrastructure commitment resolves their concerns versus other factors is unconfirmed."*

---

## Issue 4 — The Partial Contract Assumption Is Load-Bearing but Unverified

**Location:** Explicit Assumptions §5.

**Problem:** The entire staged recommendation depends on the ability to execute a 50% partial reserved capacity contract. The memo correctly flags this as uncertain but then proceeds to build the entire action plan, financial table, and recommendation around it. If the provider requires a full commitment or nothing, the staged path is not available and the binary choice the memo sought to avoid becomes unavoidable.

**Impact:** The Board could approve the staged path, management could begin negotiations, and discover within two weeks that partial contracts are not offered — at which point the memo has provided no guidance on what to do. The recommendation effectively defers the hardest decision.

**Repair Instruction:** Add a contingency branch to the Near-Term Action Plan: *"If the infrastructure provider confirms that partial or phased contracts are not commercially available, management must return to the Board within 30 days with a revised binary recommendation: full two-year commitment or full on-demand. In that scenario, the decision criteria and risk register in this memo apply directly to the binary choice."* This prevents the staged path from becoming a decision-avoidance mechanism.

---

## Issue 5 — Gross Margin Compression Causality Is Assumed, Not Established

**Location:** Explicit Assumptions §1 and Decision Criteria §3.

**Problem:** The memo assumes that gross margin compression from 73% to 66% is driven by inference costs increasing faster than pricing. This is stated in the source context, but the memo then assumes that a reserved capacity contract will *stabilize* margin. Reserved capacity reduces per-unit cost relative to on-demand but does not reduce total inference spend if usage continues to grow. If inference volume grows at the rate implied by the margin compression, a fixed reserved contract may be fully consumed within months, returning the company to on-demand pricing for incremental usage.

**Impact:** The Board may approve the commitment believing it solves the margin problem. It does not — it hedges the cost of a defined volume. If usage grows beyond reserved capacity, margin compression resumes.

**Repair Instruction:** Add a sentence to Explicit Assumptions §1: *"Reserved capacity stabilizes the cost of a fixed inference volume. If inference usage continues to grow at the rate implied by recent margin compression, the reserved capacity may be exhausted before the contract term ends, and on-demand pricing will apply to incremental volume. The margin recovery plan must therefore address both cost-per-unit and volume growth."* Add "inference volume growth rate" as a monitored metric in the Stage 2 trigger threshold table.

---

## Issue 6 — The 18-Month Runway Floor Is Asserted Without Justification

**Location:** Decision Criteria §2.

**Problem:** The memo establishes 18 months as the minimum acceptable runway floor but provides no basis for this threshold. It is not derived from the source context, a financing timeline, or a stated Board policy. It appears to be an arbitrary round number between 15 months (full commitment) and 24 months (no commitment).

**Impact:** The CFO will ask why 18 months and not 20 or 16. Without a rationale, the floor looks like it was chosen to make the staged path work mathematically rather than to reflect genuine financial risk tolerance.

**Repair Instruction:** Either ground the 18-month floor in a specific rationale — *"18 months provides sufficient runway to reach the next ARR milestone at which external financing becomes available on favorable terms"* (if that is the Board's view) — or present it explicitly as a proposed policy threshold requiring Board ratification: *"Management proposes 18 months as the minimum runway floor. The Board should confirm or adjust this threshold based on financing strategy and risk appetite."*

---

## Issue 7 — Two Risks Are Absent from the Risk Register

**Problem:** Two material risks present in the source context are not represented in the risk register.

**Risk A — Pricing action failure:** The memo calls for a 60-day inference pricing review but does not register the risk that pricing changes cause customer pushback or churn, particularly among the enterprise customers whose reliability requirements are already creating pipeline tension. Raising prices on customers simultaneously asking for better SLAs is a compounding risk.

**Risk B — Stranded capacity from AI architecture shift:** This is mentioned briefly in the risk register ("Low / Medium") but the rationale is thin. The two-year lock-in is specifically flagged as a hidden trap in the source context. The risk deserves a more explicit treatment: if the company's AI feature set migrates to a different inference architecture (e.g., smaller models, edge inference, or a different provider), reserved accelerator capacity becomes a sunk cost with no exit.

**Repair Instruction:** Add both risks to the register with explicit mitigations. For pricing risk: *"Mitigation: sequence pricing changes after reliability improvements are demonstrable; communicate value before price."* For architecture shift: *"Mitigation: require contract portability or credit provisions; set architecture review as a mandatory agenda item at the 12-month gate."*

---

## Issue 8 — The Recommendation Does Not Address the Original Binary Question

**Location:** Executive Summary and Recommendation.

**Problem:** The brief asks whether to commit to a two-year contract *now* or preserve optionality for *six months*. The memo recommends a staged path that is neither option. While this is strategically defensible, the memo does not explicitly close the loop by explaining why the original two options are both dominated by the staged path. A Board member who came in favoring one of the two original options needs to understand why their preferred path is inferior — not just that a third path exists.

**Repair Instruction:** Add a short paragraph to the Executive Summary titled "Why Not the Original Two Options?" with two sentences each: one explaining why full immediate two-year commitment is dominated (runway risk exceeds revenue benefit at current growth confidence), and one explaining why pure six-month optionality is dominated (on-demand is not cost-free; pipeline risk is time-sensitive). This closes the argument rather than leaving it implicit.

---

## Summary of Repair Priority

| Priority