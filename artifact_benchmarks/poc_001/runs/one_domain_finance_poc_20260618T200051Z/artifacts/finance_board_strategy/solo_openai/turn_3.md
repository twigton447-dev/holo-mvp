# Board Strategy Memo: AI Infrastructure Capacity Commitment

## Recommendation

**Based on current evidence, management should not sign the full two-year reserved AI capacity contract now. Instead, the company should preserve optionality for six months and run an active validation and remediation program, then return to the board with a trigger-based recommendation.**

This is a **conditional deferral**, not a passive delay. The rationale is that the revenue-defense case is plausible, but the current context does **not establish that a full two-year reservation is necessary** or sufficient to solve the company’s AI reliability and enterprise-readiness issues. At the same time, Finance warns that a full commitment could reduce runway from **24 months to 15 months if growth slows**, which makes an immediate two-year fixed-cost lock-in a material balance-sheet decision.

The trade-off is real:

- **Committing now** may improve reliability and lower infrastructure cost relative to on-demand pricing at expected utilization.
- **Waiting six months** preserves cash and flexibility, but likely carries a meaningful cost premium if utilization tracks expectations, because on-demand pricing is roughly **35% higher** than reserved pricing at expected utilization.

The board should therefore treat this as a decision between **liquidity protection and possible revenue defense**, not as a simple cost optimization exercise.

---

## Decision Framing

The board is not deciding whether reserved capacity is cheaper in theory. It is deciding whether the company should accept a **two-year fixed obligation** now in order to address reliability concerns that may be affecting expansion, despite incomplete evidence on:

1. whether reserved capacity is required to solve the reliability issue,
2. whether it would address the full set of enterprise customer asks, and
3. whether the company can absorb the lock-in if growth slows.

This matters because the company is facing **both**:

- a **cost problem**: on-demand is more expensive than reserved at expected utilization; and
- a **monetization problem**: gross margin fell from **73% to 66%** over three quarters because inference usage increased faster than pricing changes.

A capacity reservation may reduce unit cost relative to on-demand, but the stated cause of margin erosion is that usage outpaced pricing. **Infrastructure procurement alone is therefore unlikely to restore gross margin without parallel pricing or usage-discipline actions.**

---

## Explicit Assumptions

The context is incomplete in several important areas. The recommendation depends on the following assumptions, which should be tested during the six-month period:

1. **Reserved capacity would improve reliability relative to on-demand.**  
   This is plausible, but not directly proven in the context.

2. **On-demand capacity remains available over the next six months.**  
   The context provides a price comparison but does not indicate supply unavailability.

3. **Demand volatility creates a meaningful risk of underutilizing reserved capacity.**  
   Volatility is stated; the magnitude is not.

4. **The $6M at-risk expansion pipeline is not the same as closed ARR.**  
   It is a meaningful signal, but not contracted revenue.

5. **Latency commitments may be more directly influenced by infrastructure capacity than data residency or audit logs.**  
   The context does not say reserved capacity alone satisfies all enterprise asks.

6. **Six months may or may not be enough to resolve the uncertainty.**  
   This is an execution assumption, not a fact.

---

## Relevant Facts

- **Cash:** $31M
- **Debt:** none
- **ARR:** $42M
- **Growth:** 18% year over year
- **Gross margin:** declined from 73% to 66% over three quarters
- **Cause of margin decline:** inference usage increased faster than pricing changes
- **Reserved capacity cost:** $9.6M per year for two years
- **On-demand cost:** roughly 1.35x reserved price at expected utilization
- **Demand:** volatile
- **Enterprise asks:** data residency, audit logs, latency commitments
- **Revenue risk signal:** $6M of at-risk expansion pipeline tied to AI feature reliability
- **Finance warning:** full commitment could reduce runway from 24 months to 15 months if growth slows

---

## Strategic Assessment of Options

## Option A: Commit now to the full two-year reserved contract

### Potential benefits
- Lowers infrastructure cost relative to on-demand **at expected utilization**.
- May improve reliability and support stronger latency commitments.
- May help defend the **$6M at-risk expansion pipeline** if reliability is the primary blocker.
- May strengthen enterprise credibility.

### Key drawbacks
- Creates a **$19.2M total two-year obligation**.
- Introduces material fixed-cost risk while demand is explicitly volatile.
- Could compress runway materially in a slower-growth scenario.
- Does not by itself solve the stated cause of margin decline if pricing still lags inference usage.
- May not address all enterprise asks. Of the stated requirements, **latency commitments** may be more capacity-related, while **data residency and audit logs** may require additional product, architecture, or compliance work beyond the reservation itself.

### Board implication
This option is justified only if management can show that:
- reliability risk is materially threatening the identified **$6M** pipeline,
- reserved capacity is required to address that risk,
- and the company can absorb the runway impact.

The current context does not prove those conditions.

---

## Option B: Preserve optionality for six months, then decide using triggers

### Potential benefits
- Avoids immediate two-year lock-in.
- Preserves liquidity against the downside runway scenario.
- Allows management to determine whether the reliability issue is truly the binding constraint on the **$6M** expansion pipeline.
- Creates time to separate capacity needs from broader enterprise-readiness gaps.

### Key drawbacks
- Waiting is not free. At expected utilization, on-demand pricing is roughly **35% higher** than reserved pricing.
- Reliability issues may continue to pressure expansion during the six-month period.
- If reliability remains weak during the wait period, the company may not only delay expansion but also reinforce customer concerns about enterprise readiness.

### Board implication
This option is appropriate if the board concludes that the evidence today is insufficient to justify a full two-year commitment, but strong enough to warrant an active six-month operating program.

---

## Decision Criteria

The board should evaluate the decision against five criteria:

1. **Runway protection**  
   Does the choice preserve acceptable liquidity given the Finance warning of a potential reduction from **24 months to 15 months** if growth slows?

2. **Revenue defense**  
   Does the choice credibly protect the identified **$6M at-risk expansion pipeline** tied to AI reliability?

3. **Gross margin stabilization**  
   Does the choice support recovery from the current **66% gross margin**, recognizing that lower infrastructure cost alone may not solve a pricing-versus-usage mismatch?

4. **Flexibility under volatility**  
   Does the choice avoid overcommitting fixed cost before utilization confidence improves?

5. **Enterprise readiness**  
   Does the choice address customer asks for latency commitments, and clarify what additional work is required for data residency and audit logs?

---

## Recommended Path: Six-Month Staged Approach

### Stage 1: Do not sign the full two-year contract now
Maintain on-demand capacity for the next six months.

### Stage 2: Run an active validation and remediation program
Use the six months to answer four questions:

1. Is the **$6M at-risk expansion pipeline** still at risk, and specifically because of AI reliability?
2. Is reserved capacity required to support the latency and reliability commitments customers are requesting?
3. Are data residency and audit logs primarily non-capacity gaps?
4. Is there a credible path to stabilize gross margin from the current **66%** level through both infrastructure and pricing/usage actions?

### Stage 3: Return to the board with trigger-based evidence
At six months, management should present a go/no-go recommendation anchored to the thresholds below.

---

## Trigger Thresholds

Because the context does not provide enough data for new numeric operating KPIs, the thresholds below are anchored to the known figures and framed as board-usable proof points.

### Trigger to approve a full commitment at six months
Return with a recommendation to sign the full two-year contract only if management can show all of the following:

1. **The identified $6M expansion pipeline remains materially at risk due to AI reliability**, not primarily due to unrelated sales factors.
2. **Reserved capacity is required** to support the reliability or latency commitments customers are asking for.
3. **Finance concludes the runway impact is acceptable** relative to the current warning that a full commitment could reduce runway from **24 months to 15 months if growth slows**.
4. **Management presents a credible path to gross margin stabilization from the current 66% level**, including actions beyond infrastructure procurement alone.

### Trigger to continue preserving optionality
Continue to defer a full commitment if any of the following are true at six months:

1. The reliability-linked risk to the **$6M pipeline** is not substantiated.
2. Enterprise asks remain primarily concentrated in **data residency** or **audit logs**, rather than capacity-driven latency or reliability.
3. Gross margin remains under pressure because pricing still lags inference usage.
4. Runway risk remains close to the downside case flagged by Finance.
5. Utilization confidence remains weak because demand volatility is still high.

---

## Risk Register

| Risk | Why it matters | Direction of risk | Mitigation |
|---|---|---:|---|
| Runway compression | Finance warns full commitment could reduce runway from 24 months to 15 months if growth slows | High if commit now | Defer full commitment; reassess with updated cash and growth outlook |
| Underutilized reserved capacity | Demand is volatile and the contract locks in two years of fixed cost | High if commit now | Wait for better utilization evidence |
| Revenue leakage from reliability issues | Sales attributes $6M of at-risk expansion pipeline to AI feature reliability | High if wait | Prioritize reliability remediation and track pipeline impact account by account |
| Continued gross margin pressure | Margin fell from 73% to 66% because usage outpaced pricing changes | High under either option | Pair infrastructure decision with pricing and usage-discipline review |
| Misdiagnosing enterprise requirements | Data residency and audit logs may require work beyond capacity | Medium | Separate capacity issues from product, architecture, and compliance gaps |
| Six-month learning period may be inconclusive | Pipeline conversion and remediation may take longer than six months | Medium if wait | Set a midpoint review and define required evidence early |
| Customer trust erosion during wait period | Ongoing reliability issues could reinforce concerns about enterprise readiness | Medium if wait | Use the six months for active remediation, not observation only |
| Overweighting cost savings | On-demand is cheaper to avoid lock-in but more expensive at expected utilization; neither fact alone decides the issue | Medium | Use a multi-criteria board framework |

---

## Near-Term Action Plan

Over the next six months, management should:

1. **Maintain flexibility**
   - Continue on-demand capacity rather than signing the full two-year reservation now.

2. **Quantify the revenue risk**
   - Review the **$6M at-risk expansion pipeline** account by account.
   - Distinguish reliability blockers from other causes.

3. **Separate enterprise requirements**
   - Map customer asks into:
     - latency/reliability issues that may be capacity-related, and
     - data residency/audit log issues that may require separate workstreams.

4. **Address margin, not just capacity**
   - Build a plan to address the stated cause of margin decline: inference usage increasing faster than pricing changes.

5. **Create a board dashboard**
   - Track gross margin from the current **66%** level.
   - Track AI usage versus pricing changes.
   - Track utilization stability.
   - Track reliability-linked pipeline outcomes.
   - Track the runway implications of a full commitment against the current **24-to-15-month** warning range.

6. **Hold a midpoint review**
   - Return to the board or finance committee before the six-month mark if evidence already shows either:
     - the reliability-linked revenue risk is clearly substantiated, or
     - the runway risk remains too severe to justify commitment.

---

## Conclusion

**Recommendation: do not sign the full two-year reserved AI capacity contract now. Preserve optionality for six months and use that period for active validation and remediation.**

This recommendation best fits the current evidence because it:

- **preserves liquidity** against a downside scenario in which runway could fall from **24 months to 15 months**,
-