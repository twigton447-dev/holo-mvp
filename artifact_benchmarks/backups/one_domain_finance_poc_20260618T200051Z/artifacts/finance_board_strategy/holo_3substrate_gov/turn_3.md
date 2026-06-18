# Board Strategy Memo: AI Infrastructure Capacity Commitment

## Recommendation

**Recommend preserving optionality for the next six months rather than committing immediately to the full two-year reserved AI infrastructure contract.**

This is the better board-level decision based on the current fact pattern because:

1. **The two-year commitment is large relative to liquidity and runway risk.** Reserved capacity would cost **$9.6M per year for two years** ($19.2M total), while the company has **$31M cash and no debt**. Finance warns that a full commitment could reduce runway from **24 months to 15 months if growth slows**. The $19.2M obligation equals approximately 46% of current cash.
2. **Reliability concerns are commercially material but the linkage to reserved capacity is unverified.** Gross margin has already fallen from **73% to 66%** over three quarters because inference usage increased faster than pricing changes. Sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability, but this figure reflects Sales attribution and has not been independently validated at the deal level.
3. **The decision is not simply “buy or wait.”** The board should preserve flexibility now, while using the next six months to gather evidence against explicit prerequisite gates and supporting triggers. The context does not establish that capacity constraints are the root cause of reliability issues or that reservation would materially improve the enterprise dimensions customers cite.

In short: **do not sign the full two-year contract now.** Instead, run a six-month decision window with a two-tier trigger framework. If the prerequisite gates and at least two supporting triggers are met, return to the board/CFO with a commitment recommendation.

---

## Decision Framing

The company is balancing two competing truths:

- **Reliability may defend revenue and expansion**, especially as enterprise customers ask for **data residency, audit logs, and latency commitments**.
- **A fixed two-year infrastructure obligation increases financial risk**, especially given the runway impact if growth slows.

The key board question is whether the company has enough evidence **today** to justify locking in a two-year fixed cost structure. Based on the provided context, the answer is **no, not yet**.

---

## Explicit Assumptions

Because the context is incomplete, the following assumptions are stated explicitly and should be validated during the six-month window:

1. **The linkage between reserved capacity and reliability is an unverified hypothesis.** The source context does not confirm that capacity constraints are a material driver of reliability issues versus product, architecture, or pricing factors, nor that reservation would improve the specific enterprise requirements customers request.
2. **On-demand capacity remains available during the next six months**, albeit at roughly **1.35x reserved price at expected utilization** and with volatility risk.
3. **The $6M at-risk expansion pipeline is Sales-attributed and unvalidated.** It has not been confirmed through deal-level evidence that infrastructure reservation would recover this amount.
4. **Enterprise requirements for data residency, audit logs, and latency commitments may require infrastructure changes**, but the context does not confirm that a full two-year reserved contract is necessary to meet them.
5. **Growth remains uncertain.** Finance explicitly warns that if growth slows, the full commitment materially compresses runway.
6. **No market forecast, customer-level commitments, or utilization forecast is available**, so the recommendation emphasizes staged decision-making.

---

## Decision Criteria

The board and CFO should evaluate the decision against five criteria:

### 1. Liquidity and runway protection
- Current cash is **$31M** with **no debt**.
- A full reserved commitment is **$19.2M total over two years** (~46% of cash).
- Finance warns runway could fall from **24 months to 15 months if growth slows**.

**Implication:** Any decision that materially reduces strategic flexibility must clear a high bar.

### 2. Revenue defense and expansion support
- Sales attributes **$6M of at-risk expansion pipeline** to AI feature reliability (unvalidated attribution).
- Enterprise customers are asking for **data residency, audit logs, and latency commitments**.

**Implication:** Reliability and enterprise-readiness are commercially material.

### 3. Gross margin trajectory
- Gross margin declined from **73% to 66%** over three quarters because inference usage increased faster than pricing changes.
- On-demand capacity costs roughly **1.35x reserved price at expected utilization**.

**Implication:** Margin pressure has two distinct drivers—compute unit cost and pricing/usage-mix discipline. Reserved capacity may address only the former.

### 4. Volatility and lock-in risk
- Demand is explicitly described as **volatile**.
- The contract is a **two-year** commitment.

**Implication:** Volatile demand weakens the case for immediate fixed-capacity lock-in.

### 5. Ability to meet enterprise requirements without overcommitting
- The context does not prove that a full two-year reservation is required immediately.

**Implication:** Test what can be delivered operationally before accepting full financial lock-in.

---

## Analysis

### Why not commit now

A full commitment now would convert a real but still partly unquantified commercial problem into a certain fixed financial obligation. Runway compression is severe. Demand volatility undermines confidence in utilization. The commercial upside is directionally clear but not yet quantified enough, and the capacity-reliability linkage remains an unverified hypothesis.

### Why not simply defer passively

Preserving optionality should not mean inaction. Revenue and expansion may be exposed. Enterprise readiness may lag. Gross margin pressure may continue. The right answer is **active deferral** with structured evidence collection.

---

## Staged Options

### Option 1: Commit now to the full two-year reserved contract
**Pros**  
- Lower expected infrastructure cost than on-demand at expected utilization.  
- May improve reliability and support enterprise commitments.  
- Could help defend the **$6M at-risk expansion pipeline**.

**Cons**  
- Creates **$19.2M** total fixed obligation (~46% of cash).  
- Could reduce runway from **24 months to 15 months if growth slows**.  
- Locks in despite volatile demand and incomplete evidence on root cause.

**Board view:** Too much irreversible commitment relative to current uncertainty.

### Option 2: Preserve optionality for six months with explicit triggers
**Pros**  
- Protects liquidity and runway while uncertainty is resolved.  
- Allows management to test whether reliability improvements materially affect expansion.  
- Creates a fact base on utilization, enterprise requirements, and margin impact.

**Cons**  
- On-demand remains more expensive at expected utilization.  
- Reliability issues may continue to pressure expansion in the interim.

**Board view:** Best balance of financial prudence and commercial responsiveness.

### Option 3: Defer without a structured trigger framework
**Pros**  
- Maximum short-term cash preservation.

**Cons**  
- Fails to address the commercial problem.  
- Risks continued margin erosion and pipeline slippage.

**Board view:** Not recommended.

---

## Trigger Framework for Reconsidering a Commitment

A return to the board for approval of a reserved commitment requires the following two-tier structure.

**Prerequisite gates (both must be met; non-negotiable):**  
1. **Operational root cause confirmed.** Management demonstrates that capacity constraints are a material driver of reliability issues (as opposed to product, architecture, or pricing factors). The current context does not establish this linkage.  
2. **Liquidity acceptable under downside scenario.** Finance confirms that runway remains acceptable even if growth slows, addressing the existing warning that runway could fall to 15 months.

**Supporting triggers (at least two of three must be met):**  
3. **Commercial trigger.** The **$6M at-risk expansion pipeline** (Sales-attributed) is validated at the deal level as contingent on AI reliability improvements that require reservation.  
4. **Enterprise requirement trigger.** A material share of active enterprise opportunities explicitly requires **data residency, audit logs, and latency commitments** that cannot be credibly met without reservation.  
5. **Margin trigger.** Gross margin does not stabilize from the current **66%** level, and management models that reserved capacity would improve economics under observed usage levels after separating compute-cost from pricing/usage-mix drivers.

---

## Risk Register

| Risk | Description | Directional Impact | Mitigation |
|---|---|---:|---|
| Runway compression | Full commitment could reduce runway from 24 months to 15 months if growth slows; $19.2M equals ~46% of cash | High | Preserve optionality now; require CFO revalidation before commitment |
| Underutilized reserved capacity | Demand is volatile; company may pay for unused capacity | High | Delay full commitment until usage and demand patterns are clearer |
| Expansion loss from weak reliability | Sales attributes $6M of at-risk expansion pipeline to AI feature reliability (unvalidated) | High | Prioritize reliability work during six-month window; validate at deal level |
| Margin misdiagnosis | Gross margin fell from 73% to 66% as inference usage outpaced pricing changes; reserved capacity addresses only unit cost, not pricing/usage discipline | High | Separate compute-cost from pricing/usage drivers before commitment |
| Enterprise deal friction | Customers ask for data residency, audit logs, and latency commitments | Medium/High | Build a requirements map and determine what can be delivered without full reservation |
| Two-year lock-in | Contract reduces flexibility if demand, product mix, or growth changes | High | Use staged decision process and board triggers |
| Technology obsolescence | Two-year accelerator reservation may not align with future AI architecture (uncertainty: incomplete context) | Medium | Monitor product and inference approach changes during window |
| Passive delay | Waiting without milestones could worsen pipeline and margin | High | Adopt a six-month action plan with monthly review cadence |

---

## Near-Term Action Plan

### Next 30 days
1. **Create a board-level AI capacity dashboard** tracking gross margin trend from the current **66%** baseline, AI-related reliability incidents and commercial impact, and the **$6M at-risk expansion pipeline** separately.  
2. **Map enterprise requirements** for active opportunities, documenting where **data residency, audit logs, and latency commitments** are required.  
3. **CFO scenario review** reconfirming runway impact under current and downside planning assumptions.

### Next 60–90 days
4. **Determine root cause of reliability issues**, separating capacity constraints from product, architecture, and pricing issues.  
5. **Quantify commercial linkage** by validating whether the **$6M at-risk expansion pipeline** is still at risk and whether reliability improvements change deal outcomes at the deal level.  
6. **Assess margin stabilization options**, evaluating whether gross margin pressure can be reduced through pricing or usage controls.

### By six months
7. **Return to the board with a trigger-based recommendation** only if both prerequisite gates and at least two supporting triggers are satisfied.