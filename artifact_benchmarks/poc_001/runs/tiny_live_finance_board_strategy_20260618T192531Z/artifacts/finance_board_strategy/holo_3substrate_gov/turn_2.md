# Evidence and Risk Critique: AI Infrastructure Capacity Commitment Memo

## Overall Assessment

The current draft is structurally sound and correctly frames the decision as a revenue defense and strategic flexibility question rather than a unit-cost optimization. It avoids the most obvious hidden traps. However, several claims are inadequately evidenced, key risks are understated or missing, and the trigger thresholds remain too qualitative to be actionable. The staged decision framework exists in name but lacks the mechanical specificity the board needs to govern it. Concrete repair instructions follow each finding.

---

## Finding 1: The Revenue Defense Case Is Asserted, Not Demonstrated

**Flaw:** The memo states that committing to reserved capacity "may help defend" the $6 million at-risk expansion pipeline, but it does not interrogate whether reserved capacity is actually the mechanism that unlocks those expansions. The source context states that enterprise customers require **data residency, audit logs, and latency commitments**. Reserved accelerator capacity addresses latency and throughput reliability, but it does not directly deliver data residency or audit logs. The memo acknowledges this in passing but does not draw the logical consequence: reserved capacity may be necessary but is demonstrably insufficient to close the $6 million pipeline gap.

**Risk of leaving this unrepaired:** The board may approve the $9.6 million commitment believing it defends $6 million in revenue, when in fact the revenue defense requires a broader enterprise-readiness program. The capacity contract becomes a sunk cost that does not move the pipeline.

**Repair instruction:** Add a paragraph explicitly decomposing the $6 million at-risk pipeline by blocker type. State clearly that the context does not allow precise attribution, but that at least three distinct blockers are named—latency/reliability, data residency, and audit logs—and that reserved capacity addresses only one of them directly. Reframe the revenue defense case as conditional: capacity is a necessary but not sufficient condition for pipeline recovery, and the board should not treat the $6 million as fully recoverable through this contract alone.

---

## Finding 2: The Lock-In Risk Is Named But Not Quantified or Structured

**Flaw:** The risk register lists "strategic lock-in to provider" as a risk if the company commits now, with the mitigation "evaluate lock-in explicitly before signing." This is circular. The memo does not specify what lock-in actually means in financial or operational terms: the company would be obligated to pay **$19.2 million in total** over two years regardless of whether demand, product architecture, or customer requirements change. That is a commitment equal to **61.9% of current cash** and **45.7% of current ARR**. Neither figure appears in the memo.

**Risk of leaving this unrepaired:** The board may underestimate the magnitude of the lock-in because it is described qualitatively. A board member focused on the $9.6 million annual figure may not immediately register that the total two-year obligation is $19.2 million against $31 million cash.

**Repair instruction:** In the risk register and in the decision framing section, state the total two-year obligation explicitly as $19.2 million. Express it as a percentage of current cash (61.9%) and current ARR (45.7%). This makes the lock-in risk concrete and prevents the board from anchoring only on the annual figure.

---

## Finding 3: Trigger Thresholds Are Qualitative and Therefore Ungovernable

**Flaw:** The trigger thresholds section lists five conditions for early commitment, all phrased as "clear evidence," "confidence," and "evidence that." None are quantifiable using the numbers in the context pack. The memo acknowledges this limitation but frames it as a responsible constraint rather than a problem to solve. This is partially correct but incomplete. Several thresholds can be made more concrete using only the provided data.

**Risk of leaving this unrepaired:** Without quantified thresholds, the staged decision framework becomes a permission structure for indefinite deferral or, conversely, for premature commitment justified by selective evidence. The board cannot govern a trigger it cannot measure.

**Repair instruction:** Reconstruct the trigger thresholds using the numbers available. For example:

- **Pipeline trigger:** If sales can attribute more than half of the $6 million at-risk expansion pipeline to latency or reliability specifically (i.e., more than $3 million), the revenue defense case for capacity strengthens materially.
- **Margin trigger:** If gross margin falls below 66% in the next quarter, the inference cost problem is accelerating and the 1.35x on-demand premium becomes more costly to carry.
- **Runway trigger:** If ARR growth decelerates below 18% year-over-year, the Finance runway warning (24 months to 15 months) becomes more severe and the commitment threshold should rise, not fall.
- **Utilization trigger:** If on-demand spend in the next quarter implies annualized inference costs that exceed $9.6 million, the reserved contract becomes cost-neutral or favorable even under conservative utilization assumptions.

Label each threshold as derived from context-provided figures, and note that management must supply the underlying operational data to evaluate them.

---

## Finding 4: The Gross Margin Analysis Is Incomplete

**Flaw:** The memo correctly identifies the gross margin decline from 73% to 66% as a concern, but it does not connect this decline to the capacity decision with sufficient precision. The context states the decline occurred because **inference usage increased faster than pricing changes**. This means the margin problem has two levers: cost (infrastructure pricing) and revenue (customer pricing). Reserved capacity addresses only the cost lever, and only partially, since the 1.35x on-demand premium applies at **expected utilization**, which the context flags as volatile. If utilization is lower than expected, the reserved contract may not deliver the cost savings assumed.

**Risk of leaving this unrepaired:** The board may believe the capacity contract is a margin recovery tool when it is, at best, a partial cost-side intervention. The pricing-side lever—adjusting what customers pay for AI features—is not addressed in the memo at all, even though it is implied by the context.

**Repair instruction:** Add a sentence in the gross margin section stating explicitly that the margin decline has two components—inference cost and customer pricing—and that reserved capacity addresses only the cost component, and only if utilization meets or exceeds expected levels. Note that the pricing-side lever is outside the scope of this memo but should be addressed in parallel.

---

## Finding 5: The Near-Term Action Plan Is Truncated

**Flaw:** The near-term action plan ends mid-sentence ("Track") and does not complete