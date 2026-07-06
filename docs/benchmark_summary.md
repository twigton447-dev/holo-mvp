## HoloVerify Result

| Metric | Errors | n | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 120 | 2.466% | 3.102% |
| False positive rate | 0 | 60 | 4.870% | 6.015% |
| False negative rate | 0 | 60 | 4.870% | 6.015% |

**What this table measures:** the current strict public denominator: the blind
120-packet HoloVerify lane. It is balanced across 60 ALLOW packets and 60
ESCALATE packets. This is the current public Holo result, not a solo model
result.

**What it is compared against:** solo and internal repair evidence are kept in
separate ledgers. The public denominator is not combined with Solo Failure
Factory, V5/V6 patch validation, or the old 614-era draft denominator.

### Current Public Count

| Lane | Packets | ALLOW | ESCALATE | HoloVerify |
| --- | ---: | ---: | ---: | ---: |
| Blind Holo lane | 120 | 60 | 60 | 120/120 |

The older 614-packet number is historical/internal. It is not the current public
denominator because that lane included evidence later excluded by the stricter
blind-gate rule. It must not be combined with blind-120 for public FPR/FNR or
Wilson claims.

### Internal Stress-Matrix Scoreboard

The stress-matrix work is the visual diagnostic target: find packets where the
same model families are often right, but at least one solo call fails at the
action boundary.

Current Wave 1 stress-matrix result:

| Metric | Count |
| --- | ---: |
| Sibling pairs | 20 |
| Packets | 40 |
| Solo calls | 120 |
| Green dots | 90 |
| Red dots | 30 |
| False-positive overblocks | 23 |
| False negatives | 0 |
| Parse/admissibility failures | 7 |
| Pairs with at least one red dot | 16 |
| Wrong-verdict pairs | 13 |
| Parse-only holdouts | 3 |

This scoreboard is internal seam evidence. It is not public FPR/FNR evidence by
itself. Its purpose is to show where solo agents break, then test whether
HoloVerify covers those red-dot failures without creating new ones.

### Internal Patch And Retest Status

Holo failures are not hidden. They are preserved, autopsied, patched, and rerun
only under strict labels.

| Lane | Result | Treatment |
| --- | ---: | --- |
| V5 selected FN rescue | 12/14 packets, 5/7 pairs | Valid internal failed-live evidence |
| V6 tiny patch validation | 4/4 packets, 2/2 pairs | Internal patch-validation evidence |
| V6 same selected-lane rerun | 14/14 packets, 7/7 pairs | Internal selected-lane repair evidence |
| Wave 1 Top 5 FP-overblock rescue | 7/10 packets, 2/5 pairs | Valid internal failed-live evidence |
| V7 false-blocker hardening | No live result | Fable-passed internal hardening; tiny preflight ready but blocked before provider calls in this environment |
| Wave 2 stress matrix | No solo result | Designed and frozen; live scout blocked before provider calls in this environment |

The V5 miss class was `V5_SCOPE_DEPENDENCY_NON_DETECTION`: workers failed to
detect a visible source-field authority/scope blocker. V6 added deterministic
source-field authority/scope checks. The same selected lane that failed under V5
then passed under V6.

This supports the engineering hardening story. It does not create a new public
benchmark denominator.

### Red-Dot Visualization Model

The benchmark visual should show the solo brittleness problem directly.

| Visual element | Meaning |
| --- | --- |
| One square | One packet or sibling pair, grouped by domain |
| Six mini dots | Three solo models across both siblings |
| Green dot | Solo model got the packet right in admissible form |
| Red dot | Solo attempt failed: wrong verdict or parse/admissibility failure |
| Gray dot | Quarantined packet/key defect |
| Holo status | Shown separately. A red-to-green animation is a future repair concept unless a live Holo run has passed |

The point is not that solos are always bad. The point is that solo agents are
often right, but red-dot failures can still appear at the action boundary.
HoloVerify is being tested on whether it covers those failures without creating
new ones.

### Models Used

The current governed-runtime work uses the same mini-model families repeatedly:

| Role | Model | Job |
| --- | --- | --- |
| Worker 1 | `xai/grok-3-mini` | Source-boundary mapping |
| Gov 1 | `minimax/MiniMax-M2.5-highspeed` | Control routing |
| Worker 2 | `openai/gpt-5.4-mini` | Adversarial scope challenge |
| Gov 2 | `minimax/MiniMax-M2.5-highspeed` | Control routing |
| Worker 3 | `minimax/MiniMax-M2.5-highspeed` | Final compiler |

The benchmark does not claim that stronger models are unnecessary. It claims
that structure matters: the same model families behave differently when they are
run alone versus inside a governed architecture with state, gates, preservation,
and final selection.

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

The current strict public HoloVerify counted sample is:

| Metric | Value |
| --- | ---: |
| Blind action-boundary packets | 120 |
| Sibling pairs | 60 |
| ALLOW truths | 60 |
| ESCALATE truths | 60 |
| Correct HoloVerify packets | 120 |
| Observed false positives | 0 |
| Observed false negatives | 0 |

Observed result:

> HoloVerify produced zero observed false positives and zero observed false negatives across the current 120-packet blind public denominator. This is a measured sample outcome, not a claim of zero risk. The statistical upper bounds on plausible error rates are reported below.

The honest statistical statement is:

| Metric | Errors | n | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 120 | 2.466% | 3.102% |
| False positive rate | 0 | 60 | 4.870% | 6.015% |
| False negative rate | 0 | 60 | 4.870% | 6.015% |

Exact and Wilson are two standard ways to put a confidence band around an error
rate. They answer the same basic question:

> Given this many tests and this many observed errors, how high could the real
> error rate plausibly still be?

Zero observed errors means no failures appeared in this locked sample. It does
not prove the true error rate is zero. It means the plausible upper risk is
bounded by the confidence interval.

In simpler terms:

> We saw zero errors in the 120-packet blind public denominator. Statistics still requires humility:
> the real error rate could be above zero, so we report the upper bound.

The stricter false-positive and false-negative side-specific number is higher
because each side has half the examples: 60 ALLOW and 60 ESCALATE.

---

## Reliability Threshold Roadmap

The business question is not "did this sample pass?"

The business question is:

> How low does the upper risk bound need to be before this class of action can
> be trusted with this level of autonomy?

Side-specific false-positive and false-negative risk is the primary safety bar
because ALLOW and ESCALATE fail in different ways.

| Target Wilson side-specific upper bound | Required ALLOW examples | Required ESCALATE examples | Required total packets | Additional packets from current 120 |
| --- | ---: | ---: | ---: | ---: |
| < 1.0% | 381 | 381 | 762 | 642 |
| < 0.5% | 765 | 765 | 1,530 | 1,410 |
| < 0.25% | 1,533 | 1,533 | 3,066 | 2,946 |
| < 0.1% | 3,838 | 3,838 | 7,676 | 7,556 |

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

If HoloVerify gets 120 out of 120 packets right, the observed error rate is 0%.
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
| Actual ESCALATE | Correctly escalated = 60 | Missed escalation = 0 |
| Actual ALLOW | Wrongly escalated = 0 | Correctly allowed = 60 |

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

The solo baselines use the same mini-model families that appear inside the
governed HoloVerify architecture.

The difference is not model strength. The difference is the control system
around those models.

For the solo baseline, each model receives exactly one independent call per
packet. No Gov, no baton, no deterministic repair layer, and no final selector.

Current stress-matrix status:

| Lane | Status | Treatment |
| --- | --- | --- |
| Wave 1 solo scout | 120 solo calls, 90 green, 30 red | Internal stress-matrix evidence |
| Wave 1 Top 5 Holo rescue | 7/10 packets, 2/5 pairs | Failed internal hardening evidence |
| V7 false-blocker hardening | Fable-passed, preflight-ready, no live result | Internal hardening only |
| Wave 2 stress matrix | 30 pairs / 60 packets frozen but unrun | No Wave 2 result yet |

Solo outputs only count as **KNEW/admissible** when they produce the right
verdict, valid structure, required source grounding, no invented source IDs,
and a machine-checkable action-boundary explanation.

So the solo column is stricter than "did it sound right?"

It asks:

> Did the one-shot model actually know why the action should ALLOW or ESCALATE,
> in a form that could survive an audit?

This does not prove that every solo model always fails.

It shows something narrower and more useful:

> Solo agents can look mostly competent and still fail at exactly the wrong
> action boundary. HoloVerify is being tested on whether it covers those red-dot
> failures without creating new ones.

That is the benchmark's main architecture question.

---

## What Counts

Only the blind-120 lane is counted in the current strict public denominator.

Included:

- 120 frozen blind packets.
- 60 ALLOW and 60 ESCALATE truths.
- Locked traces.
- Runtime-manifest separation from the scoring map.
- Trace-bound post-hoc scoring.
- No judges in the public statistical denominator.

Excluded:

- Canaries.
- Precursors.
- Old 614-era denominator material.
- Solo Failure Factory and stress-matrix seam discovery.
- V5/V6/V7 patch-validation and selected-lane repair evidence.
- Wave 1 Top 5 rescue evidence.
- Wave 2 frozen-but-unrun material.
- HoloBuild quality rows.
- Packet/key defects.
- Anything without a clean blind root package.

This matters because benchmark credibility depends as much on what is excluded
as on what is counted.

---

## Evidence Families

The public family table should be regenerated from the blind-120 manifest before
publication. The internal atlas already covers domains including AP, vendor
master, agentic commerce, IAM, SaaS controls, clinical activation, banking,
privacy, security, treasury, public-sector records, legal, infrastructure, and
industrial controls.

Other locked evidence exists, but is not counted in the public denominator:

| Evidence | Why separate |
| --- | --- |
| Wave 1 stress matrix | Seam discovery and red-dot source evidence, not public FPR/FNR denominator |
| Wave 1 Top 5 Holo rescue | Internal failed-live evidence that exposed a false-blocker gap |
| V5/V6/V7 repair lanes | Internal hardening and selected-lane repair evidence |
| Wave 2 stress matrix | Frozen but unrun; no Wave 2 solo result exists yet |
| Old 614-era material | Historical/internal unless re-admitted under the strict blind rule |
| HoloBuild mini-suites | Product quality evidence, not HoloVerify public action-boundary denominator |

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
- Wave 1, V7, or Wave 2 internal evidence is public benchmark evidence.
- V7 has a live validation result. It does not yet.

This benchmark does claim:

> On the current strict blind-120 public denominator, HoloVerify has produced
> zero observed false-positive or false-negative errors across 120
> action-boundary packets. The old 614-packet number is historical/internal and
> is not the current public denominator.

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
