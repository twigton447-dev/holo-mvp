# Board Strategy Memo: AI Infrastructure Capacity Commitment

## Recommendation

**Recommend preserving optionality for the next six months rather than committing immediately to the full two-year reserved AI infrastructure contract.**

This is the better board-level choice based on current facts because:

1. **Liquidity risk is material.** The company has **$31M cash and no debt**, and Finance warns that a full commitment could reduce runway from **24 months to 15 months if growth slows**.
2. **The contract is a meaningful fixed-cost lock-in.** Reserved capacity would cost **$9.6M per year for two years**, creating a two-year obligation at a time when demand is explicitly described as volatile.
3. **The operating problem is real but not yet fully quantified.** Reliability issues are affecting growth: Sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability, and enterprise customers are asking for **data residency, audit logs, and latency commitments**. However, the context does not establish that a full two-year reservation is the only way to address those requirements.
4. **Unit economics are already under pressure.** Gross margin has fallen from **73% to 66% over three quarters** because inference usage increased faster than pricing changes. Locking in fixed capacity may help cost relative to on-demand at expected utilization, but it does not by itself solve pricing or usage discipline.

Accordingly, the board should **defer the full commitment for six months**, while running a structured decision process with explicit triggers. The company should use that period to determine whether reliability-related revenue protection and expansion justify taking on a two-year fixed obligation.

---

## Decision Framing

The decision is not simply “reserved capacity is cheaper than on-demand.” A pure cost framing would be incomplete and potentially misleading.

The actual board question is:

> Should the company accept a two-year fixed-cost commitment now in order to improve AI feature reliability and enterprise readiness, or preserve cash and flexibility for six months while validating whether the revenue and margin benefits justify the lock-in?

This requires balancing two conflicting signals from the context:

- **Reliability may defend revenue but creates fixed cost.**
- **Waiting preserves cash but may weaken expansion pipeline.**

---

## Explicit Assumptions

Because the context is incomplete, the following assumptions are stated explicitly and should be validated during the six-month period:

1. **Reserved capacity would improve reliability relative to on-demand capacity.**  
   This is implied by the sales concern around AI feature reliability, but not directly proven in the context.

2. **Enterprise requirements such as data residency, audit logs, and latency commitments may require infrastructure and operational investment beyond raw capacity.**  
   The context does not say that reserved accelerator capacity alone satisfies these asks.

3. **On-demand capacity remains available during the next six months.**  
   The context gives a price comparison—on-demand costs roughly **1.35x** reserved price at expected utilization—but does not indicate supply unavailability.

4. **Demand volatility creates a real risk of underutilizing reserved capacity.**  
   This follows from the stated volatility, but the magnitude is not quantified.

5. **The $6M at-risk expansion pipeline is important but not equivalent to closed ARR.**  
   It is pipeline at risk, not contracted revenue.

6. **The company can monitor reliability, pipeline conversion, and margin over the next six months well enough to support a better-informed decision.**  
   The context does not specify current instrumentation, so this is an execution assumption.

---

## Key Facts Relevant to the Decision

- **Cash:** $31M  
- **Debt:** none  
- **ARR:** $42M, growing **18% year over year**  
- **Gross margin:** declined from **73% to 66%** over three quarters  
- **Cause of margin decline:** inference usage increased faster than pricing changes  
- **Reserved capacity cost:** **$9.6M per year for two years**  
- **On-demand cost:** roughly **1.35x reserved price at expected utilization**  
- **Demand profile:** volatile  
- **Customer asks:** data residency, audit logs, latency commitments  
- **Revenue risk signal:** **$6M of at-risk expansion pipeline** tied to AI feature reliability  
- **Finance warning:** full commitment could reduce runway from **24 months to 15 months if growth slows**

---

## Strategic Assessment

## Option 1: Commit now to the two-year reserved capacity contract

### Advantages
- Likely lowers infrastructure cost relative to on-demand **at expected utilization**, given the **1.35x** on-demand premium.
- May improve reliability and support stronger latency commitments.
- Could help defend the **$6M at-risk expansion pipeline** if reliability is the gating issue.
- Signals seriousness to enterprise customers asking for operational commitments.

### Disadvantages
- Creates a large fixed obligation: **$19.2M total over two years**.
- Materially increases downside risk to liquidity; Finance explicitly warns runway could fall from **24 months to 15 months if growth slows**.
- Locks the company in for two years despite volatile demand.
- Does not directly solve the root cause of margin compression if pricing still lags inference usage.
- May not fully address enterprise asks such as audit logs and data residency if those require additional work beyond capacity.

### Board view
This option is strongest if the board believes:
- reliability issues are already causing near-term revenue loss,
- reserved capacity is necessary to fix them,
- and the company can absorb the runway reduction.

The current context does not prove all three.

---

## Option 2: Preserve optionality for six months, then decide using triggers

### Advantages
- Protects liquidity and avoids immediate two-year lock-in.
- Allows management to validate whether reliability issues are truly the binding constraint on the **$6M** expansion pipeline.
- Creates time to determine whether enterprise asks are primarily capacity-related or require broader product/compliance work.
- Preserves flexibility while demand remains volatile.

### Disadvantages
- On-demand capacity is more expensive at expected utilization.
- Reliability issues may persist during the six-month period and could weaken expansion outcomes.
- Delay may reduce management’s ability to offer stronger latency commitments immediately.

### Board view
This option is preferable if the board prioritizes:
- runway preservation,
- avoiding irreversible commitments under uncertainty,
- and making the decision with clearer evidence on revenue protection and utilization.

Given the current facts, this is the more prudent choice.

---

## Decision Criteria

The board should evaluate the decision against five criteria:

1. **Liquidity preservation**  
   Does the choice maintain sufficient runway given the Finance warning that a full commitment could reduce runway from **24 months to 15 months if growth slows**?

2. **Revenue defense and expansion support**  
   Does the choice credibly protect the **$6M at-risk expansion pipeline** tied to AI feature reliability?

3. **Gross margin trajectory**  
   Does the choice improve or at least stop deterioration from the current **66% gross margin**, recognizing that usage growth has outpaced pricing changes?

4. **Flexibility under demand volatility**  
   Does the choice avoid overcommitting fixed cost when utilization is uncertain?

5. **Enterprise readiness**  
   Does the choice help the company meet customer asks for **data residency, audit logs, and latency commitments**, or at least clarify what is required?

---

## Recommended Path: Six-Month Staged Approach

The recommended course is **not inaction**. It is a staged approach with explicit thresholds.

### Stage 1: Preserve optionality now
For the next six months, do **not** sign the full two-year reserved capacity contract.

### Stage 2: Operate on on-demand capacity while collecting decision-grade evidence
Accept the higher on-demand cost temporarily in exchange for preserving cash and avoiding lock-in while management answers three unresolved questions:

- How much of the **$6M at-risk expansion pipeline** is truly blocked by AI reliability?
- Are enterprise asks for data residency, audit logs, and latency commitments primarily infrastructure issues or broader product/compliance issues?
- Is utilization stable enough that reserved capacity would be economically and operationally justified?

### Stage 3: Reassess at six months using trigger thresholds
At the end of six months, return to the board with a go/no-go recommendation based on the thresholds below.

---

## Trigger Thresholds for Reconsidering a Full Commitment

Because the brief requires trigger thresholds and the context does not provide enough data for precise numeric operating thresholds beyond the stated figures, the board should use the following **fact-based triggers**:

### Trigger to move toward commitment
Reconsider signing the two-year reserved contract if, within six months:

1. **The $6M at-risk expansion pipeline remains materially at risk specifically due to AI reliability**, not due to unrelated sales factors; and
2. **Management demonstrates that reserved capacity is necessary to support customer-required latency commitments or reliability levels**; and
3. **Finance confirms the company can absorb the fixed commitment without unacceptable runway compression relative to the current warning scenario**.

### Trigger to continue preserving optionality
Continue to defer a full commitment if, within six months:

1. **Reliability issues do not prove to be the primary cause of the at-risk pipeline**; or
2. **Enterprise asks are shown to depend materially on non-capacity work such as audit logs or data residency capabilities**; or
3. **Demand volatility remains too high to support confidence in reserved-capacity utilization**; or
4. **Runway risk remains elevated under slower-growth conditions**.

These thresholds are intentionally qualitative where the context lacks numeric detail. Management should convert them into measurable internal KPIs during the six-month period.

---

## Risk Register

| Risk | Why it matters | Direction of risk | Mitigation |
|---|---|---:|---|
| Runway compression | Finance warns full commitment could reduce runway from 24 months to 15 months if growth slows | High if commit now | Preserve optionality for six months; reassess with updated cash and growth outlook |
| Underutilized reserved capacity | Demand is volatile; two-year lock-in may exceed actual need | High if commit now | Delay commitment until utilization confidence improves |
| Revenue leakage from reliability issues | Sales attributes $6M of at-risk expansion pipeline to AI feature reliability | High if wait and reliability remains weak | Prioritize reliability improvements during six months; track pipeline impact explicitly |
| Continued gross margin pressure | Margin fell from 73% to 66% because inference usage outpaced pricing changes | High under either option | Pair infrastructure decision with pricing/usage discipline review |
| Misdiagnosing enterprise requirements | Data residency, audit logs, and latency commitments may not be solved by capacity alone | Medium | Separate infrastructure needs from product/compliance requirements before committing |
| Overweighting cost savings | On-demand is 1.35x reserved at expected utilization, but cost savings alone may not justify lock-in | Medium | Use multi-criteria decision framework, not pure cost framing |
| Delayed enterprise credibility | Waiting may weaken ability to make stronger commitments to customers | Medium | Use interim roadmap and targeted commitments where feasible |

---

## Near-Term Action Plan

Over the next six months, management should execute the following:

1. **Maintain capacity flexibility**
   - Continue using on-demand capacity rather than signing the full two-year reservation now.

2. **Quantify reliability-linked revenue risk**
   - Review the **$6M at-risk expansion pipeline** account by account.
   - Distinguish deals blocked by reliability from those blocked by other factors.

3. **Separate infrastructure from product/compliance gaps**
   - For enterprise asks—**data residency, audit logs, latency commitments**—identify which are solved by capacity and which require separate workstreams.

4. **Build a board decision dashboard**
   - Track gross margin from the current **66%** level.
   - Track AI inference usage versus pricing changes.
   - Track utilization stability and the effective cost difference between on-demand and reserved capacity.
   - Track pipeline outcomes tied to reliability.

5. **Return to the board in six months with a staged recommendation**
   - Present whether the evidence supports:
     - full commitment,
     - continued deferral,
     - or another staged structure if available.  
   The context does not provide alternative contract structures, so management should not assume them without evidence.

---

## Conclusion

The company has a real AI infrastructure problem, but it also has a real balance-sheet constraint. The facts support a cautious but active stance.

**Recommendation: preserve optionality for six months and do not commit immediately to the full two-year reserved capacity contract.**

This recommendation best reflects the current evidence because it:
