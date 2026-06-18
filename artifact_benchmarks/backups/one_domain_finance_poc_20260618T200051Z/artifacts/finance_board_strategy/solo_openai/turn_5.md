# Board Strategy Memo: AI Infrastructure Capacity Contract

## Recommendation

**Recommendation: do not sign the full two-year reserved AI infrastructure contract now. Preserve optionality for up to six months, continue on-demand capacity during that period, and run a tightly managed review that can return to the board earlier if evidence becomes decisive.**

This is a **conditional deferral**, not a passive wait. The board decision today is whether to accept a **two-year fixed obligation** now or preserve flexibility while management determines whether reserved capacity is truly required to defend revenue and meet enterprise requirements.

The case for committing now is real:

- Sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability.
- Enterprise customers are asking for **data residency, audit logs, and latency commitments**.
- On-demand capacity costs roughly **1.35x** reserved price at expected utilization.

The case against committing now is also real:

- Reserved capacity costs **$9.6M per year for two years**, a **$19.2M** lock-in.
- Demand is explicitly **volatile**.
- Finance warns a full commitment could reduce runway from **24 months to 15 months if growth slows**.
- Gross margin fell from **73% to 66%** over three quarters because inference usage increased faster than pricing changes.

**Board judgment:** current facts support preserving optionality because the company has not yet shown that a full two-year reservation is necessary, sufficient, and financeable under downside conditions. However, the principal risk in deferring is that the company may spend more on on-demand capacity while still allowing reliability concerns to weaken expansion, making waiting both commercially and economically costly.

## What Board Approval Is Requested Today

Approve the following:

1. **Defer** the full two-year reserved capacity commitment now.
2. **Continue on-demand capacity** for up to six months.
3. Require management to return with a **trigger-based recommendation** supported by evidence on:
   - the **$6M at-risk expansion pipeline**,
   - whether reserved capacity is actually required for reliability or latency commitments,
   - the path to gross margin stabilization from the current **66%**,
   - and the runway impact relative to the current **24-to-15-month** warning.
4. Require an **earlier return before six months** if evidence becomes clear sooner.

## Why Six Months

Six months should be treated as a **bounded management review window**, not as a claim that all uncertainty will resolve by then. It is long enough to test whether reliability is truly the binding issue in the identified expansion pipeline, whether enterprise asks are primarily capacity-related or broader, and whether management can present a credible financial case. It is also short enough to avoid open-ended drift.

If evidence becomes decisive earlier, management should return earlier. If evidence remains inconclusive at six months, that itself is decision-relevant and argues against taking a two-year lock-in based on weak proof.

## Explicit Assumptions

The context is incomplete in several areas. This recommendation depends on the following assumptions, which should be tested during the review window:

1. **Reserved capacity would improve reliability relative to on-demand.**  
   Plausible, but not directly proven in the context.

2. **On-demand capacity remains available during the review period.**  
   The context gives a price comparison, not a supply constraint.

3. **Demand volatility creates meaningful underutilization risk for a reserved contract.**  
   Volatility is stated; magnitude is not.

4. **The $6M at-risk expansion pipeline is meaningful but not equivalent to closed ARR.**  
   It is a sales signal, not contracted revenue.

5. **Reserved capacity may help latency and reliability more directly than data residency or audit logs.**  
   The context does not show that the contract solves all enterprise asks.

6. **Six months can improve decision quality if actively managed.**  
   This is an execution assumption, not a fact.

## Decision Criteria

The board should judge the decision against five criteria:

1. **Runway protection**  
   Can the company absorb the commitment given the warning that runway could fall from **24 months to 15 months if growth slows**?

2. **Revenue defense**  
   Does the decision credibly protect the identified **$6M at-risk expansion pipeline** tied to AI reliability?

3. **Gross margin stabilization**  
   Does the decision help address the decline from **73% to 66%**, recognizing that the stated cause is usage growing faster than pricing changes?

4. **Flexibility under volatility**  
   Does the decision avoid locking in fixed cost before utilization confidence improves?

5. **Enterprise readiness**  
   Does the decision address customer asks for latency commitments, while clarifying what additional work is needed for data residency and audit logs?

## Strategic Assessment

### Option A: Commit now to the full two-year reserved contract

**Potential benefits**
- Lower cost than on-demand at expected utilization.
- Possible improvement in reliability and support for latency commitments.
- Possible defense of the **$6M at-risk expansion pipeline** if reliability is the true blocker.
- Stronger enterprise posture.

**Key drawbacks**
- Creates a **$19.2M** two-year obligation.
- Adds fixed cost while demand is volatile.
- Could materially compress runway in a slower-growth case.
- Does not by itself solve the stated cause of margin erosion, since inference usage increased faster than pricing changes.
- The reservation may help with latency and reliability, but the context does not show that it addresses the full enterprise buying criteria; if **data residency** and **audit logs** are the primary blockers, the contract could add fixed cost without unlocking the targeted expansion.

**Board implication**  
Commit now only if management can show that reliability is clearly the binding issue, reserved capacity is required to solve it, and the runway impact is acceptable.

### Option B: Preserve optionality for up to six months

**Potential benefits**
- Avoids immediate two-year lock-in.
- Preserves liquidity and downside flexibility.
- Allows management to separate capacity needs from broader enterprise-readiness gaps.
- Creates time to determine whether the **$6M** pipeline risk is truly reliability-driven.

**Key drawbacks**
- On-demand is roughly **35% more expensive** than reserved at expected utilization.
- Reliability issues may continue to pressure expansion during the review period.
- If reliability is in fact the gating issue, waiting could prove to be the more expensive mistake.

**Board implication**  
This option is appropriate only if the six-month period is actively managed to produce a better decision, not used as a default delay.

## Gross Margin Implication

The company has both a **cost problem** and a **monetization problem**. Gross margin fell from **73% to 66%** because inference usage increased faster than pricing changes. Reserved capacity may improve unit cost relative to on-demand, but **without parallel pricing or usage-discipline changes, the company risks converting a variable-cost margin problem into a fixed-cost margin problem**.

That is a central reason not to treat this as a procurement-only decision.

## Trigger Thresholds

Because the context does not provide enough data to set new numeric operating targets without inventing facts, the thresholds below are framed as **binary board approval tests** anchored to the known figures: the **$6M at-risk pipeline**, the current **66% gross margin**, and the **24-to-15-month runway warning**.

### Trigger to return early, before six months
Management should return before six months if either of the following becomes clear:

1. **Reliability is clearly the binding constraint** on the identified **$6M at-risk expansion pipeline**, and management concludes reserved capacity is required to support the needed reliability or latency commitments.
2. **Runway risk remains too severe** to support a full commitment under the downside case flagged by Finance.

### Trigger to approve a full commitment
Recommend approval only if management can show **all** of the following:

1. The identified **$6M at-risk expansion pipeline** remains materially at risk specifically because of AI reliability.
2. Reserved capacity is required to support the reliability or latency commitments customers are requesting.
3. Finance concludes the runway impact is acceptable relative to the current warning that a full commitment could reduce runway from **24 months to 15 months if growth slows**.
4. Management presents a credible path to gross margin stabilization from the current **66%**, including actions beyond infrastructure procurement.

### Trigger to continue preserving optionality
Continue to defer if **any** of the following are true:

1. The reliability-linked risk to the **$6M pipeline** is not substantiated.
2. Enterprise blockers are primarily **data residency** or **audit logs**, rather than capacity-driven latency or reliability.
3. Gross margin pressure remains primarily a pricing-versus-usage issue.
4. Runway risk remains close to the downside case flagged by Finance.
5. Utilization confidence remains weak because demand volatility is still high.

## Risk Register

| Risk | Why it matters | Direction of risk | Mitigation |
|---|---|---:|---|
| Runway compression | Finance warns full commitment could reduce runway from 24 months to 15 months if growth slows | High if commit now | Defer full commitment; reassess with updated cash and growth outlook |
| Underutilized reserved capacity | Demand is volatile and the contract locks in two years of fixed cost | High if commit now | Wait for better utilization evidence |
| Revenue leakage from reliability issues | Sales attributes $6M of at-risk expansion pipeline to AI feature reliability | High if wait | Prioritize reliability remediation and track pipeline impact |
| Continued gross margin pressure | Margin fell from 73% to 66% because usage outpaced pricing changes | High under either option | Pair infrastructure decision with pricing and usage-discipline review |
| Misdiagnosing enterprise requirements | Data residency and audit logs may require work beyond capacity | Medium | Separate capacity issues from product/compliance gaps |
| Passive deferral / weak execution | Waiting only adds value if management actively improves decision quality | Medium if wait | Assign owners, midpoint review, and board-ready evidence requirements |
| Inconclusive review window | Six months may not fully resolve uncertainty | Medium if wait | Treat six months as a bounded review window and return earlier if evidence is decisive |
| Customer trust erosion during wait | Ongoing reliability issues could reinforce enterprise concerns | Medium if wait | Use the period for active remediation, not observation only |

## Near-Term Action Plan

### Priority 1: Commercial diagnosis first
- Review the **$6M at-risk expansion pipeline** account by account.
- Determine whether reliability is the actual blocker versus other sales factors.
- Escalate to the board early if reliability is clearly the binding issue.

### Priority 2: Technical diagnosis second
- Determine whether reserved capacity is actually required for the reliability and latency commitments customers are requesting.
- Separately map customer asks for **data residency** and **audit logs** to confirm whether they are non-capacity workstreams.

### Priority 3: Financial decision package third
- Reassess the runway impact of a full commitment against the current **24-to-15-month** warning.
- Present a plan to stabilize gross margin from the current **66%**, including actions on pricing or usage discipline in addition to infrastructure choices.
- Track utilization stability to test whether volatility remains too high for a two-year lock-in.

### Governance
- Establish a board dashboard covering:
  - gross margin,
  - AI usage versus pricing changes,
  - reliability-linked pipeline outcomes,
  - utilization stability,
  - and runway implications of a full commitment.
- Hold a midpoint review during the six-month window.
- Return earlier if evidence clearly supports either commitment or continued deferral.

## Conclusion

**Recommendation: preserve optionality for up to six months rather than commit now to the full two-year reserved AI capacity contract.**

This is the stronger board decision on current facts because it protects liquidity, respects the two-year lock-in, and avoids treating a mixed revenue, cost, and enterprise-readiness problem as a simple procurement choice. At the same time, the board should recognize that waiting is not free: it may mean higher on-demand cost and continued commercial risk if reliability is truly the gating issue.

**Board approval requested today:** defer the full two-year commitment, continue on-demand capacity for up to six months, and require management to return with a trigger-based recommendation supported by evidence on pipeline risk, capacity necessity, gross-margin path, and runway impact.