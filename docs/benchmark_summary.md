## HoloVerify Result

| Metric | Errors | n | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 614 | 0.487% | 0.622% |
| False positive rate | 0 | 307 | 0.971% | 1.236% |
| False negative rate | 0 | 307 | 0.971% | 1.236% |

**What this table measures:** the full HoloVerify governed architecture across
614 clean frozen action-boundary packets. This is the Holo result, not a solo
model result.

**What it is compared against:** the same mini-model families run alone as
one-shot solo baselines. Solo gets one call per packet. No Gov, no shared state,
no deterministic rescue layer, and no final selector.

### Frozen and Hash-Locked Records

A frozen packet is a benchmark case saved before the run: source facts, action
boundary, prompt, audit rules, and expected verdict are fixed before any model
answers.

A hash lock is a SHA-256 fingerprint of a packet, prompt, trace, or evidence
package. If the file changes later, the hash changes too.

This matters because HoloEngine is publishing a vendor benchmark in a category
where no standard action-boundary test already existed. The hash-locked record
helps reviewers see that the questions, prompts, Holo state, traces, token
accounting, Gov calls, and final selections were not rewritten after the result.

In production, the same idea becomes a client evidence pack: the verdict, policy
version, controlling source IDs, reasoning summary, Gov/worker trace,
deterministic gate results, token accounting, and final-selection rationale can
be stored by the customer or delivered to an auditor as a tamper-evident record
of why the system allowed or escalated the action.

For insurance, compliance, and regulated operations, that means a claims team,
coverage reviewer, risk officer, or regulator can see the exact evidence path
behind a decision instead of reconstructing it from chat logs or a final
paragraph.

## On This Page

- [Result and counted families](#holoverify-result)
- [Frozen packets, Holo state, and hash locks](#frozen-and-hash-locked-records)
- [Current benchmark ledger](#current-benchmark-ledger)
- [How HoloVerify works](#how-holoverify-works)
- [How policies are handled and design partner API](#how-policies-are-handled)
- [Cost and safety premium](#cost)
- [Audit sources](#audit-sources)

### Counted Families in the 614

| Family | Domain | Packets | HoloVerify |
| --- | --- | ---: | ---: |
| Kit C / Clinical Activation | Clinical-regulated activation controls | 40 | 40/40 |
| AP / Vendor-Master Payment Controls | AP, procurement, and vendor-bank controls | 40 | 40/40 |
| Agentic Commerce Order Execution | Refunds, purchases, fulfillment, credits, and order-release controls | 40 | 40/40 |
| IT Access Permission Change | Admin access, role escalation, offboarding, and break-glass controls | 40 | 40/40 |
| Wave2-4 Expansion | HR, privacy, finance, government, benefits, banking, defense admin, insurance, and utilities | 174 | 174/174 |
| Wave5 Completed 7-Domain Expansion | Medical, treasury, legal, infrastructure, security, public-sector, and operational technology controls | 280 | 280/280 |

### Holo vs Solo, By Domain

This is the clean matched solo comparison slice: the same 100 packets were run
through HoloVerify and through the same three mini-model families as one-shot
solo baselines.

| Domain | Holo KNEW | Solo KNEW | Solo audit-failure rate | Solo failure mix |
| --- | ---: | ---: | ---: | --- |
| HR / payroll / workforce controls | 22/22 | 22/66 | 66.7% | 1 wrong verdict, 10 parse fails, 33 structural/evidence fails |
| Data privacy / customer data release controls | 16/16 | 26/48 | 45.8% | 1 wrong verdict, 3 parse fails, 18 structural/evidence fails |
| Banking / KYC / AML controls | 10/10 | 10/30 | 66.7% | 4 wrong verdicts, 6 parse fails, 10 structural/evidence fails |
| Benefits / public casework controls | 8/8 | 8/24 | 66.7% | 1 wrong verdict, 2 parse fails, 13 structural/evidence fails |
| Finance close / revenue / expense controls | 8/8 | 14/24 | 41.7% | 2 wrong verdicts, 2 parse fails, 6 structural/evidence fails |
| Government procurement / grants controls | 6/6 | 6/18 | 66.7% | 1 wrong verdict, 4 parse fails, 7 structural/evidence fails |
| Defense administration / logistics controls | 12/12 | 12/36 | 66.7% | 2 wrong verdicts, 3 parse fails, 19 structural/evidence fails |
| Insurance claims / coverage controls | 14/14 | 14/42 | 66.7% | 0 wrong verdicts, 8 parse fails, 20 structural/evidence fails |
| Energy / utilities / infrastructure controls | 4/4 | 4/12 | 66.7% | 1 wrong verdict, 2 parse fails, 5 structural/evidence fails |

Solo audit-failure rate means the solo output was not KNEW/admissible: it had
the wrong verdict, failed to parse, or lacked the required source-grounded
structure. That is stricter than "sounded plausible."

Important scope note: the Holo-vs-solo table above uses the matched 100-packet
solo comparison slice. The domain Wilson table below uses the full current
614-packet Holo denominator.

### Holo Domain Risk Bounds

The benchmark starts strong overall, then gets more detailed by domain. The
grand-total Wilson number is not the same as the domain-level Wilson number.
Each domain has its own denominator, so each domain has its own 95% upper bound.

| Counted Holo domain | Packets | Errors | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Kit C / Clinical activation controls | 40 | 0 | 7.216% | 8.762% |
| AP / Vendor-master payment controls | 40 | 0 | 7.216% | 8.762% |
| Agentic commerce order execution | 40 | 0 | 7.216% | 8.762% |
| IT access permission change | 40 | 0 | 7.216% | 8.762% |
| HR workforce controls | 40 | 0 | 7.216% | 8.762% |
| Data privacy release controls | 40 | 0 | 7.216% | 8.762% |
| Finance close / control overrides | 40 | 0 | 7.216% | 8.762% |
| Benefits enrollment controls | 8 | 0 | 31.234% | 32.441% |
| Banking / KYC controls | 10 | 0 | 25.887% | 27.753% |
| Defense administration controls | 12 | 0 | 22.092% | 24.249% |
| Government / public sector controls | 6 | 0 | 39.304% | 39.033% |
| Insurance claims controls | 14 | 0 | 19.264% | 21.531% |
| Energy / utilities controls | 4 | 0 | 52.713% | 48.989% |
| Medical treatment activation controls | 40 | 0 | 7.216% | 8.762% |
| Treasury / wire controls | 40 | 0 | 7.216% | 8.762% |
| Legal / regulatory filing controls | 40 | 0 | 7.216% | 8.762% |
| Cloud infrastructure controls | 40 | 0 | 7.216% | 8.762% |
| Security operations controls | 40 | 0 | 7.216% | 8.762% |
| Public-sector records controls | 40 | 0 | 7.216% | 8.762% |
| Operational technology / industrial safety controls | 40 | 0 | 7.216% | 8.762% |

### Models Used

HoloVerify's current locked roster:

| Role | Model | Job |
| --- | --- | --- |
| Worker 1 | `xai/grok-3-mini` | Source-boundary mapping |
| Gov 1 | `minimax/MiniMax-M2.5-highspeed` | Control routing |
| Worker 2 | `openai/gpt-5.4-mini` | Adversarial scope challenge |
| Gov 2 | `minimax/MiniMax-M2.5-highspeed` | Control routing |
| Worker 3 | `minimax/MiniMax-M2.5-highspeed` | Final compiler |

Same models, run alone on the matched 100-packet solo comparison slice:

| Solo model | Calls | KNEW/admissible | Solo audit-failure rate | Wrong verdict | Parse fail | Structural/evidence fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `openai/gpt-5.4-mini` | 100 | 82/100 | 18% | 0 | 0 | 18 |
| `minimax/MiniMax-M2.5-highspeed` | 100 | 26/100 | 74% | 0 | 40 | 34 |
| `xai/grok-3-mini` | 100 | 8/100 | 92% | 13 | 0 | 79 |

---

## What Is HoloEngine?

HoloEngine is an AI control system for high-stakes actions. It is designed for
cases where an AI system may approve, release, grant, execute, escalate, or
prepare something that affects the real world.

The core question is simple:

> Does the evidence actually authorize the action?

HoloEngine is designed for domains such as:

- payments, AP, procurement, and vendor-master changes
- agentic commerce and order execution
- IT access, admin permissions, and offboarding
- clinical and regulated workflow activation
- treasury, legal, compliance, cloud, security, public-sector, and industrial
  controls

HoloVerify is the action-boundary verifier inside HoloEngine.

It returns one of two decisions:

**ALLOW**

The current source evidence closes the exact action boundary.

**ESCALATE**

The current source evidence does not close the exact action boundary. A person
or higher-control workflow must review it.

Plainly:

- **ALLOW** means "the paperwork really supports doing this now."
- **ESCALATE** means "do not do this automatically; something important is
  missing, stale, contradictory, or outside the evidence."

---

## Plain-English Terms

This page uses a few benchmark terms. Here is what they mean.

| Term | Meaning |
| --- | --- |
| Packet | One frozen test case: a proposed action plus the documents and facts the AI is allowed to use. |
| Sibling pair | Two related packets. One should ALLOW and the other should ESCALATE. The difference is usually narrow, so the system has to read carefully. |
| Clean denominator | The set of packets we are willing to count publicly. Canaries, drafts, broken runs, and diagnostic tests are kept separate. |
| False positive | Holo says ESCALATE when the action was actually allowed. This creates friction. |
| False negative | Holo says ALLOW when the action should have escalated. This is usually the dangerous miss. |
| KNEW/admissible | A solo model did not merely guess the right verdict. It gave the right verdict in a structured, source-grounded way that local checks could audit. |
| Gov | The controller between worker models. Gov reads the last output and gate results, then tells the next worker what to preserve, repair, or block. |
| Deterministic gate | Local code, not an AI opinion. It checks required sections, source IDs, missing evidence, and action-boundary rules. |
| Final selector | A local rule that can keep the best valid answer instead of blindly trusting the last answer. |

---

## Current Benchmark Ledger

The current clean benchmark-grade HoloVerify counted sample is:

| Metric | Value |
| --- | ---: |
| Frozen action-boundary packets | 614 |
| Sibling pairs | 307 |
| ALLOW truths | 307 |
| ESCALATE truths | 307 |
| Correct HoloVerify packets | 614 |
| Observed false positives | 0 |
| Observed false negatives | 0 |

Observed result:

> HoloVerify produced zero observed false positives and zero observed false negatives across 614 clean benchmark-grade action-boundary packets. This is a measured sample outcome, not a claim of zero risk. The statistical upper bounds on plausible error rates are reported below.

The honest statistical statement is:

| Metric | Errors | n | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 614 | 0.487% | 0.622% |
| False positive rate | 0 | 307 | 0.971% | 1.236% |
| False negative rate | 0 | 307 | 0.971% | 1.236% |

Exact and Wilson are two standard ways to put a confidence band around an error
rate. They answer the same basic question:

> Given this many tests and this many observed errors, how high could the real
> error rate plausibly still be?

Zero observed errors means no failures appeared in this locked sample. It does
not prove the true error rate is zero. It means the plausible upper risk is
bounded by the confidence interval.

In simpler terms:

> We saw zero errors in 614 counted packets. Statistics still requires humility:
> the real error rate could be above zero, so we report the upper bound.

Plain English: this moved the benchmark from roughly under 0.68% packet-level
Wilson risk to roughly under 0.62% packet-level Wilson risk.

The stricter false-positive and false-negative side-specific number is higher
because each side has half the examples: 307 ALLOW and 307 ESCALATE.

---

## Reliability Threshold Roadmap

The business question is not "did this sample pass?"

The business question is:

> How low does the upper risk bound need to be before this class of action can
> be trusted with this level of autonomy?

Side-specific false-positive and false-negative risk is the primary safety bar
because ALLOW and ESCALATE fail in different ways.

| Target side-specific upper bound | Required ALLOW examples | Required ESCALATE examples | Required total packets | Additional packets from current 614 |
| --- | ---: | ---: | ---: | ---: |
| < 1.0% | 299 | 299 | 598 | 0 |
| < 0.5% | 598 | 598 | 1,196 | 582 |
| < 0.25% | 1,197 | 1,197 | 2,394 | 1,780 |
| < 0.1% | 2,995 | 2,995 | 5,990 | 5,376 |

Recommended threshold policy:

| Use case tier | Suggested evidence threshold |
| --- | --- |
| Internal decision support | Current clean ledger plus domain-specific review |
| Enterprise action recommendation | < 1.0% false-positive / false-negative upper bound in-domain |
| High-stakes irreversible action gating | < 0.5% false-positive / false-negative upper bound in-domain, plus human escalation policy |
| Safety-critical production autonomy | < 0.1% false-positive / false-negative upper bound, external review, and ongoing monitoring |

The < 0.1% tier should be treated as a production-scale validation program, not
as the next public benchmark milestone.

---

## How To Read The Statistics

The observed score is what happened in the test.

The upper bound is what the test lets us responsibly say about the unknown real
error rate.

That distinction matters.

If HoloVerify gets 614 out of 614 packets right, the observed error rate is 0%.
But the real world is larger than the sample. A perfect sample does not prove a
perfect system.

So we report a **95% upper bound**.

Plainly:

> If the real error rate were higher than this upper bound, seeing zero errors
> in a sample this large would be statistically unlikely.

We show two common confidence methods:

| Method | What it means | Why we show it |
| --- | --- | --- |
| Exact binomial upper bound | A conservative one-sided bound based directly on the binomial model. | This is the headline risk number because it is simple and conservative for zero-error runs. |
| Wilson score upper bound | A widely used confidence interval for proportions that behaves better than naive percentages in small samples. | This gives a second standard view, usually a little wider here. |

We use a **one-sided** upper bound because the safety question is not "could the
error rate be lower?" It is:

> How high could the real error rate still plausibly be?

Side-specific bounds matter too. ALLOW and ESCALATE fail differently:

- A false ALLOW can let an unsafe action proceed.
- A false ESCALATE can block a valid action and create operational friction.

That is why the page reports both the overall packet error bound and separate
false-positive / false-negative bounds.

The practical rule:

> Observed accuracy tells you what happened. The upper bound tells you how much
> uncertainty remains.

---

## Confusion Matrix

Positive class: **ESCALATE**.

That means we treat "the system correctly stopped or escalated the action" as
the positive event.

| Actual / Predicted | ESCALATE | ALLOW |
| --- | ---: | ---: |
| Actual ESCALATE | Correctly escalated = 307 | Missed escalation = 0 |
| Actual ALLOW | Wrongly escalated = 0 | Correctly allowed = 307 |

Observed rates:

| Rate | Observed |
| --- | ---: |
| Sensitivity / true positive rate | 100.00% |
| Specificity / true negative rate | 100.00% |
| False positive rate | 0.00% |
| False negative rate | 0.00% |

Observed rates describe what happened in the sample. The confidence bands above
are the risk language.

---

## Holo Versus The Same Models Alone

The central comparison is not "Holo used stronger models."

It did not.

The matched solo baselines used the same mini-model families that were used
inside the governed HoloVerify architecture.

The difference was not model strength.

The difference was the control system around those models.

For the solo baseline, each model received exactly one independent call per
packet. No Gov, no shared state, no deterministic rescue layer, and no final
selector were available to the solo runs.

- Gov reviewed worker outputs between turns.
- Each worker received the current state instead of starting from scratch.
- Local code checked worker outputs after every turn.
- The system saved the best valid answer it had seen so far.
- The final answer could not quietly drop important proof from an earlier valid answer.
- Every call, token count, gate result, and final-selection reason was logged.

Solo outputs only count as **KNEW/admissible** when they produce the right
verdict, valid structure, required source grounding, no invented source IDs,
and a machine-checkable action-boundary explanation.

So the solo column is stricter than "did it sound right?"

It asks:

> Did the one-shot model actually know why the action should ALLOW or ESCALATE,
> in a form that could survive an audit?

| Evidence slice | HoloVerify | Same models alone, one-shot | What it shows |
| --- | ---: | ---: | --- |
| Clinical Activation Boundary Controls | 40/40 packets | 6/120 KNEW/admissible | Broad solo collapse; Holo solved both siblings across 20 pairs |
| Vendor-Master Payment Controls | 40/40 packets | 53/120 KNEW/admissible | Solo sometimes succeeded, but every pair still had strict one-shot failures |
| Wave3/Wave4 focused slice | 54/54 packets | 54/162 KNEW/admissible | 27/27 strong solo-collapse pairs in the focused expansion |
| Wave2B5 + Wave3/Wave4 matched expansion | 100/100 packets | 116/300 KNEW/admissible | Larger matched slice with same-model solo instability preserved |

This does not prove that every solo model always fails.

It shows something narrower and more useful:

> The same model families that were brittle as isolated one-shot decision makers
> became reliable when placed inside the governed HoloVerify architecture.

That is the benchmark's main architecture finding.

---

## What Counts

Only clean benchmark-grade evidence is counted in the 614-packet denominator.

Included:

- Frozen packets.
- Locked traces.
- Hash-checked prompts and payloads.
- Full HoloVerify governed architecture runs.
- Balanced ALLOW/ESCALATE sibling pairs.
- No prompt leakage.
- No judges in the clean statistical denominator.

Excluded:

- Canaries.
- Precursors.
- HoloBuild quality rows.
- Missing-evidence rows.
- Public-copy drafts.
- Anything without a clean root package.

This matters because benchmark credibility depends as much on what is excluded
as on what is counted.

---

## Evidence Families

| Family | Domain | Packets | Pairs | HoloVerify |
| --- | --- | ---: | ---: | ---: |
| Clinical Activation Boundary Controls | Clinical-regulated activation controls | 40 | 20 | 40/40 |
| Vendor-Master Payment Controls | AP / procurement / vendor-master controls | 40 | 20 | 40/40 |
| Agentic Commerce Order Execution | Order execution controls | 40 | 20 | 40/40 |
| IT Access Permission Change | Access / privilege controls | 40 | 20 | 40/40 |
| Wave2-4 Expansion | HR, privacy, finance, government, benefits, banking, defense admin, insurance, utilities | 174 | 87 | 174/174 |
| Wave5 Completed 7-Domain Expansion | Medical, treasury, legal, infrastructure, security, public-sector, and operational technology controls | 280 | 140 | 280/280 |

Other locked evidence exists, but is not counted in the clean denominator:

| Evidence | Why separate |
| --- | --- |
| Agentic Commerce all-six collapse canary | Lock-rooted canary, not full-family denominator |
| Hard ALLOW false-positive precursor | Frozen precursor, not clean denominator |
| D11 HoloBuild mini-suite | HoloBuild quality evidence, not HoloVerify action-boundary denominator |

---

## How HoloVerify Works

HoloVerify is not a single model.

It is a governed verification architecture.

Each packet is processed through:

1. A fixed set of worker models.
2. Gov review between workers.
3. Local code checks after worker outputs.
4. A saved record of each worker answer.
5. Best-answer preservation.
6. A final selector that prevents regression.
7. Trace and token accounting.

Gov does not choose models. The model order is fixed by the run lock.

Gov's job is to diagnose the previous worker output, read the local gate
results, block unsafe moves, preserve what is correct, and tell the next worker
what must be repaired or resolved.

The local deterministic layer then decides whether the artifact is admissible.
Gov does not get to wave through a failed gate.

This is the key design choice:

> Models can argue. Code enforces the boundary.

The goal is not better prose.

The goal is action-boundary closure.

---

## How Policies Are Handled

For a design partner, policies are not treated as background instructions or
model vibes. They become a versioned policy pack that HoloVerify can cite,
hash, and enforce.

Concrete example: **AP / vendor-master payment release**.

A design partner would provide:

| Input | Example |
| --- | --- |
| Policy pack | Current AP release policy, vendor-bank-change policy, callback policy, emergency exception policy |
| System records | Invoice, PO, approval chain, vendor-master record, bank-change ticket, callback log |
| Action request | "Release invoice INV-10422 for payment" or "Approve vendor bank change" |
| Boundary definition | What evidence must exist before the action may proceed |
| Integration target | ERP, AP workflow, vendor-master system, ticketing queue, or payment-release service |

The policy pack is versioned and pinned. A result should say which policy version
was used. If the policy is missing, stale, ambiguous, or not mapped to the
requested action, HoloVerify should not guess. It should return `ESCALATE`.

## Design Partner API Example

In a design-partner deployment, HoloVerify would usually sit in front of an
irreversible action as a verification API.

Example request:

```json
{
  "action_id": "ap_release_10422",
  "domain": "vendor_master_payment_controls",
  "policy_pack_id": "ap_policy_pack_v2026_07",
  "action": "release_payment",
  "action_boundary": "invoice payment release requires current PO match, approval-chain closure, vendor-master bank match, and callback closure for any bank-change signal",
  "source_records": [
    {"source_id": "INV-10422", "type": "invoice", "uri": "erp://invoices/10422"},
    {"source_id": "PO-7781", "type": "purchase_order", "uri": "erp://po/7781"},
    {"source_id": "VM-ACME", "type": "vendor_master", "uri": "erp://vendors/acme"},
    {"source_id": "CB-991", "type": "callback_log", "uri": "tickets://callback/991"}
  ]
}
```

Example response:

```json
{
  "verdict": "ESCALATE",
  "binding_class": "SOURCE_BOUNDARY_OPEN",
  "policy_pack_id": "ap_policy_pack_v2026_07",
  "controlling_policy_ids": ["AP-PAY-004", "AP-BANK-CHANGE-002"],
  "missing_dependency": "callback log does not match the vendor-master bank-change ticket",
  "cited_source_ids": ["VM-ACME", "CB-991"],
  "trace_id": "hverify_trace_01J...",
  "trace_hash": "sha256:...",
  "decision_rationale": "payment release remains open because the callback record does not close the bank-change dependency",
  "evidence_pack_uri": "grc://hverify/evidence/ap_release_10422",
  "safe_next_step": "hold payment and route to AP reviewer"
}
```

The response is not only a yes/no decision. It can include or point to an
immutable decision evidence pack: the policy version, cited records, clear
rationale, Gov/worker trace, deterministic gate results, token accounting, and
final-selector reason. That gives audit, compliance, insurance, legal, and
operations teams a record they can store in GRC, ERP, claims, ticketing, or
case-management systems.

Physically, this means:

1. The AP system prepares a payment or bank-change action.
2. Before release, it calls HoloVerify with the action, policy pack, and source
   records.
3. HoloVerify normalizes the request into an action-boundary packet.
4. The deterministic layer checks required policy fields, source IDs, timing,
   missing dependencies, and impossible shortcuts.
5. Gov and workers reason over the bounded packet, not the entire enterprise.
6. The final selector returns the best admissible ALLOW or ESCALATE artifact.
7. The AP system either proceeds, holds the action, or opens a review ticket.

The first design-partner phase should be **shadow mode**: HoloVerify observes
real actions and records ALLOW/ESCALATE recommendations without blocking the
workflow. After enough agreement and audited misses, the partner can move to a
gate mode for selected high-risk actions.

HoloVerify does not need to own the ERP. It needs a narrow API boundary before
the irreversible action.

---

## Relation To Factuality Benchmarks

Benchmarks like AA-Omniscience measure factual recall and hallucination. They
reward correct answers, punish bad guesses, and treat abstention as better than
hallucination when the model does not know.

HoloVerify applies a related discipline at the action boundary.

When the source evidence does not authorize an action, the correct behavior is
not a confident paragraph.

The correct behavior is:

> ESCALATE.

AA-Omniscience tests whether models know when not to answer.

HoloVerify tests whether AI systems know when not to act.

Reference:

- https://artificialanalysis.ai/evaluations/omniscience

---

## Cost

HoloVerify is not cheaper than a one-shot model.

It is a safety premium.

The system spends more tokens because it uses multiple worker turns, Gov
adjudication, deterministic gates, state preservation, artifact tracking, and
final selection.

Recent matched slices show token ratios around 2x to 3.2x, depending on packet
family and context size.

The practical question is:

> Is this action important enough to justify a verification premium?

For low-risk chat, often no.

For money movement, clinical activation, privileged access, legal filing, data
release, or infrastructure changes, often yes.

---

## What This Does Not Claim

This benchmark does not claim:

- HoloVerify has zero real-world risk.
- HoloVerify is universally superior to every model.
- HoloVerify replaces qualified human review in clinical, legal, financial, or
  defense contexts.
- The tested packets cover every possible enterprise failure mode.
- One-shot solo baselines represent every possible solo prompting method.

This benchmark does claim:

> On the current clean locked denominator, HoloVerify has produced zero observed
> false-positive or false-negative errors across 614 action-boundary packets,
> with a measured statistical upper risk band.

---

## Next Packet Families

The next packet expansion should prioritize more irreversible
action boundaries, not generic reasoning tasks.

Recommended next families:

| Domain | Action boundary being tested |
| --- | --- |
| Defense logistics / command authorization | Whether source authority permits movement, procurement, or operational release |
| Banking / AML / account freeze controls | Whether account restriction or release is justified by current evidence |
| Insurance claims / payout authorization | Whether payout, denial, or escalation is permitted |
| Pharma quality / batch release | Whether manufacturing or quality evidence permits product release |
| Privacy / data disclosure / consent controls | Whether records may be disclosed to a requester |
| Education / student record release | Whether student records can be released under current authority |
| Export control / customs / restricted shipment release | Whether shipment can proceed under current screening evidence |
| Real estate / mortgage / escrow release | Whether funds, documents, or approvals may be released |
| Manufacturing quality hold / supplier substitution | Whether an exception can override a quality hold |
| Tax / regulatory payment controls | Whether a filing, remittance, or exception is currently authorized |
| Customer account security / MFA reset | Whether identity proof closes the account-change boundary |
| Energy trading / credit-limit controls | Whether a trade, override, or exposure increase is permitted |
| Legal discovery / privilege / litigation hold release | Whether documents can be released or must be escalated |
| Healthcare claims / prior authorization | Whether coverage or authorization evidence closes the payment/action boundary |

Each family should preserve the existing structure:

- 20 sibling pairs.
- 40 packets.
- 10 hard-ALLOW target pairs.
- 10 hard-ESCALATE target pairs.
- ALLOW and ESCALATE sibling for every pair.
- Same frozen packet discipline.
- Same no-leakage and packet-identity checks.
- Same matched solo baseline after Holo freeze.

---

## Audit Sources

Primary current sources:

- `docs/benchmark/HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_WAVE3_WAVE4_FINAL_EVIDENCE_MEMO_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_REPLICATION_PACKET_FREEZE_WAVE5_7DOMAIN_2026_07_01.md`

The benchmark should feel like an audit ledger: clear about what was counted,
clear about what was excluded, and clear about how much uncertainty remains.

---

## The Ask

We are looking for one or two enterprise design partners in financial services,
procurement, compliance operations, healthcare operations, infrastructure, or
regulated data workflows who want to pressure-test Holo against real
action-boundary decisions before we scale.

If your team is preparing to let AI recommend, approve, release, or execute
high-stakes actions, the question is not whether the model sounds careful.

The question is whether the evidence actually closes the boundary.

**Taylor Wigton**  
taylorw@hologroup.io
