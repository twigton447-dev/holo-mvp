# Evidence and Risk Critique: AI Infrastructure Capacity Memo

**Role:** Evidence and Risk Critic
**Turn:** 2 of 6
**Draft Under Review:** Turn 1 Initial Builder Draft

---

## Overall Assessment

The draft is structurally sound and avoids the most obvious traps (pure cost framing, ignoring lock-in, omitting thresholds). However, it contains several unsupported inferences, underweighted risks, and logical gaps that would expose the memo to challenge from a rigorous CFO or board member. The following critique is organized by section, with concrete repair instructions for each finding.

---

## Finding 1: The Runway Derivation Is Presented as Fact

**Location:** Assumption 4; Risk Register row 6

**Problem:** The memo states that a full commitment "reduces runway from 24 to 15 months" and then derives a figure of "approximately $640K per month in incremental cash consumption." The source context provides the 24-to-15-month runway impact as Finance's warning, not as a verified calculation. The $640K/month figure is the memo's own arithmetic, but it is presented without labeling the derivation method or acknowledging that it depends on an unstated current burn rate. A CFO will immediately ask: what is the current monthly burn, and does this math hold? If the current burn rate is not confirmed, the derived figure is speculative.

**Repair Instruction:** Label the $640K figure explicitly as a derived estimate pending Finance confirmation. Add a parenthetical noting the implicit assumption: that the $9.6M annual contract cost is entirely incremental to current infrastructure spend. If the company is already spending some amount on on-demand capacity that would be displaced, the net incremental cost — and therefore the runway impact — is lower. The memo must either confirm the net incremental figure or flag it as unresolved.

---

## Finding 2: The "50% Reservation" Recommendation Lacks a Capacity Basis

**Location:** Staged Option Structure, Phase 1

**Problem:** The memo recommends reserving "50% of the full reserved volume" at "~$4.8M annually." This is arithmetically consistent with halving the $9.6M contract, but the source context does not establish what 50% of reserved capacity actually covers in operational terms. Does 50% reservation satisfy the latency and uptime SLAs that enterprise customers require? If not, the partial reservation may fail to defend the $6M pipeline at all, undermining the central rationale for acting now rather than waiting. The memo assumes partial reservation is sufficient to "signal commitment" without evidence that signals — rather than contractual guarantees — satisfy enterprise procurement requirements.

**Repair Instruction:** Add a conditional qualifier: the Phase 1 partial reservation defends pipeline value *only if* the vendor can extend data residency, audit log, and latency SLAs on partial reserved capacity. If full SLA coverage requires full reservation, the staged structure collapses and the binary choice re-emerges. Flag this as a pre-signing validation requirement, not merely a negotiating preference.

---

## Finding 3: The $6M Pipeline Attribution Is Treated Too Generously

**Location:** Assumption 3; Core Tension section; Decision Criteria

**Problem:** The memo correctly labels the $6M figure as "directionally credible but not independently verified," but then uses it at face value in the decision criteria and risk register. The phrase "sales attributes" in the source context is a significant qualifier — sales teams routinely overattribute pipeline risk to infrastructure gaps when other factors (pricing, competition, procurement cycles) may be equally or more responsible. The memo does not surface this attribution risk explicitly, which means the Board may overweight the pipeline defense argument.

**Repair Instruction:** In the Decision Criteria section, add a sentence noting that the $6M figure reflects sales-team attribution and may overstate the causal link between infrastructure reliability and pipeline conversion. Recommend that Sales provide deal-level evidence (e.g., written customer requirements, RFP language, lost-deal post-mortems) before the Phase 2 gate. The Phase 2 trigger threshold of "$3M of at-risk pipeline converted" should also note that conversion alone does not confirm infrastructure was the deciding factor.

---

## Finding 4: The Risk Register Omits Vendor Concentration Risk

**Location:** Risk Register

**Problem:** The risk register addresses financial, operational, and technology risks but does not mention vendor concentration. A two-year reserved capacity commitment with a single infrastructure vendor creates dependency that affects negotiating leverage on renewal, pricing, and SLA enforcement. If the vendor raises prices, degrades service, or is acquired, the company has limited recourse mid-contract. This is a material governance risk for a board-level document.

**Repair Instruction:** Add a row to the risk register: *Vendor concentration and mid-contract leverage loss* — Likelihood: Low–Medium; Impact: Medium; Mitigation: Negotiate most-favored-nation pricing clauses, SLA credit provisions, and a defined dispute resolution process before signing. Confirm whether the contract includes any termination-for-convenience provision, even at a penalty.

---

## Finding 5: The Technology Obsolescence Risk Is Underweighted

**Location:** Risk Register row 4

**Problem:** The memo lists technology shift risk (more efficient accelerators) as Medium likelihood / Medium impact and suggests negotiating "annual capacity flex provisions." This is reasonable but understated. A two-year lock-in in AI infrastructure is a long horizon given the current pace of hardware development. The memo does not quantify what "flex provisions" means in practice — whether that is a volume reduction right, a hardware substitution clause, or something else — and does not acknowledge that vendors may resist meaningful flex terms precisely because they are pricing the reservation at a discount.

**Repair Instruction:** Strengthen this risk entry. Note that flex provisions are a negotiating objective, not an assumed outcome, and that the vendor's willingness to grant them should be treated as a material contract condition. If the vendor refuses meaningful flex terms, the technology obsolescence risk rating should be elevated to High, and the Board should factor that into the Phase 1 go/no-go decision.

---

## Finding 6: The Near-Term Action Plan Is Incomplete

**Location:** Near-Term Action Plan section (truncated in draft)

**Problem:** The draft was cut off before the Near-Term Action Plan was completed. This is a required deliverable element. Its absence means the memo cannot be evaluated for completeness, and the Board would receive an unfinished document.

**Repair Instruction:** Complete the Near-Term Action Plan in the next draft. It should include: (1) owner assignments for each action, (2) deadlines tied