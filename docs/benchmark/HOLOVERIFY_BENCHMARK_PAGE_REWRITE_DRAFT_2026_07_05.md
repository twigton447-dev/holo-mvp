# HoloVerify Benchmark Page Rewrite Draft

Date: 2026-07-05

Callsign: HoloVerify QA

Status: `DRAFT_MD_ONLY_NO_PROVIDER`

Audience: Taylor and HoloOps

Scope: benchmark-page narrative draft only. No providers, Holo live, solo, Gov,
judges, public site files, staging, commits, pushes, or frozen runtime evidence
were touched.

Source artifacts:

- `docs/benchmark/HOLOVERIFY_BENCHMARK_STORY_AND_STRESS_MATRIX_RECOMMENDATION_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_ARCHITECTURE_STORY_AUDIT_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_DOT_MATRIX_VISUAL_SPEC_2026_07_05.md`
- `frontend/benchmark.html`
- `docs/benchmark_summary.md`

## Complete Benchmark-Page Draft

### Hero

# Can AI tell when it is safe to act?

AI is useful before execution. It can read, summarize, compare, draft, and
explain. But the final step needs a higher bar.

The action boundary is the line between "we can discuss this" and "we may do
this now."

HoloVerify tests that boundary. It asks whether the visible source evidence
really authorizes a proposed action, or whether the action must escalate to a
person or higher-control workflow.

The current public result is narrow and clean:

| Metric | Result |
| --- | ---: |
| Public denominator | Blind-120 only |
| HoloVerify packets correct | 120/120 |
| ALLOW packets | 60 |
| ESCALATE packets | 60 |
| Observed false positives | 0/60 |
| Observed false negatives | 0/60 |

This is not a claim of zero risk. It is the result on the current strict
blind-120 public denominator.

### The Current Public Result

The counted public lane is blind-120: 120 frozen action-boundary packets, split
evenly between 60 ALLOW truths and 60 ESCALATE truths.

HoloVerify scored 120/120 on that lane.

| Metric | Errors | n | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 120 | 2.466% | 3.102% |
| False positive rate | 0 | 60 | 4.870% | 6.015% |
| False negative rate | 0 | 60 | 4.870% | 6.015% |

False positives and false negatives are reported separately because they fail in
different ways.

A false positive means HoloVerify escalates an action that was actually allowed.
That creates friction.

A false negative means HoloVerify allows an action that should have escalated.
That is usually the dangerous miss.

The older 614-packet result is historical/internal. It is not the current public
denominator and must not be combined with blind-120 for public FPR, FNR, or
Wilson claims.

### What Is Being Benchmarked

This is not a normal question-answer benchmark.

The benchmark does not ask whether an AI can write a plausible answer. It asks
whether the evidence supports a real-world action.

Each packet contains a proposed action and the source material the system is
allowed to use. The system must return one of two decisions:

**ALLOW**

The visible source evidence closes the exact action boundary.

**ESCALATE**

The visible source evidence does not close the exact action boundary. Something
is missing, stale, contradictory, out of scope, or otherwise not safe to execute
automatically.

Examples of actions:

- release a payment
- change vendor bank details
- grant privileged access
- approve a contract change
- activate a clinical workflow
- release a record
- execute an order
- change infrastructure

The benchmark question is simple:

> Does the evidence actually authorize doing this now?

### Why Solo AI Is Not Enough

Solo models are often useful. They can read the packet, extract facts, and give
a good answer most of the time.

But high-stakes execution is not graded on "most of the time."

Scattered red failures matter. One wrong ALLOW can release money, grant access,
activate a workflow, or rely on authority that the source records do not support.
One wrong ESCALATE can block valid work and create operational friction.

The important comparison is not HoloVerify against a weaker hidden baseline. The
internal solo baselines use the same mini-model families that appear inside the
governed HoloVerify architecture. The difference is the structure around those
models.

Solo calls do not get Gov handoffs, shared state, deterministic gates, blocker
ledgers, trace preservation, best-answer preservation, or final selection.

That is the core architecture question:

> Can governance cover the scattered red failures without creating new ones?

### Solo Stress Matrix

The Solo Failure Factory is a stress-selected internal lane. It is designed to
find packets where solo models break.

It is not the public denominator.

The visual should make that clear.

Each square represents one sibling pair. A sibling pair has one ALLOW packet and
one ESCALATE packet. The difference between them is narrow, so the system has to
read carefully.

Inside each square, show six solo opportunity dots: three solo models across two
siblings.

| Visual element | Meaning |
| --- | --- |
| Green dot | Solo model gave the correct and admissible verdict |
| Red dot | Solo model gave the wrong verdict |
| Yellow dot | Parse or admissibility failure |
| Gray dot | Quarantined packet, packet/key defect, or excluded evidence |
| Green ring | HoloVerify covered a solo failure in an internal hardening lane |
| Red ring | HoloVerify also failed or has not yet repaired that failure class |

The first view should show solo models as often green but interrupted by red and
yellow dots across domains such as payments, legal, clinical, contracts, IAM,
and procurement.

The second view should toggle HoloVerify on. The solo dots should stay fixed.
HoloVerify should appear as an overlay so the reader can see what was covered,
what remains red, and what is excluded.

Required chart warning:

> This matrix is a failure atlas, not one blended benchmark score. The public
> denominator is blind-120 only. Solo stress lanes are selected to expose
> execution-boundary failures. Holo rescue and rerun lanes are internal hardening
> evidence unless separately admitted. Gray quarantined packets are excluded.

### What HoloVerify Adds

HoloVerify is not a single model.

It is a governed verification architecture.

Each packet moves through a controlled procedure:

1. Worker models read the packet and produce bounded artifacts.
2. Gov reviews the previous worker output and gate results.
3. Deterministic gates check source IDs, required fields, missing evidence, and
   action-boundary rules.
4. Blocker ledgers preserve source-grounded blockers so they cannot disappear in
   later prose.
5. Trace preservation keeps prompts, outputs, and scoring evidence reviewable.
6. Patch regression turns known failure classes into bounded rerun checks.
7. Final selection prevents the last answer from overwriting a better valid one.

The point is not better prose.

The point is controlled action-boundary closure.

Models can argue. Code enforces the boundary.

### How Hardening Works

Holo failures are not hidden.

They are preserved, classified, patched at the mechanism level, and rerun under
bounded labels.

Safe language:

> We found a failure class, preserved the failed evidence, converted the lesson
> into a mechanism-level check where possible, and reran a bounded validation
> lane to see whether that mechanism repaired the class.

Unsafe shortcut:

> We tuned to the test.

The distinction matters. A tuned benchmark answer can memorize a result. A
mechanism-level patch should generalize to the rule that failed, such as
"visible source fields must close the authority scope" or "a prior blocker
cannot disappear unless source evidence closes it."

The claim still stays bounded to the lane tested.

### What Counts And What Does Not Count

| Evidence | Treatment |
| --- | --- |
| Blind-120 HoloVerify lane | Current strict public denominator: 120 packets, 60 ALLOW, 60 ESCALATE, 120/120 correct |
| Solo Failure Factory | Internal stress-selected seam evidence, not public FPR/FNR denominator |
| V5/V6 repair lanes | Internal hardening and selected-lane repair evidence |
| Old 614-era material | Historical/internal; not combined with blind-120 |
| Packet/key defects | Quarantined and excluded from clean denominator claims |

This separation is the benchmark discipline.

Blind-120 is the public denominator.

Solo Failure Factory is stress evidence.

V5/V6 repair lanes are internal hardening evidence.

### Next Milestone

The next major public milestone should not be a bigger headline. It should be a
cleaner, broader lane.

The recommended next public milestone is:

| Milestone | Clean balanced packets | Meaning if zero misses continue |
| --- | ---: | --- |
| Current | 60/60 = 120 | Current blind-120 public denominator |
| Next major milestone | 150/150 = 300 | Stronger side-specific story; still not zero-risk |
| Phase 1 side-specific Wilson target | 381/381 = 762 | Side-specific Wilson upper bound under 1% if zero misses continue |

The 150/150 milestone gives a more legible public expansion.

The 381/381 milestone is the Phase 1 statistical target for bringing the
side-specific Wilson upper bound under 1%, assuming zero observed misses
continue.

Both must preserve the same discipline:

- frozen packets
- balanced ALLOW / ESCALATE split
- no answer-key leakage
- trace-bound post-hoc scoring
- quarantined defects excluded
- no mixing with internal stress or repair lanes

### What This Does Not Claim

This benchmark does not claim:

- HoloVerify has zero real-world risk.
- HoloVerify is universally superior to every model.
- HoloVerify replaces qualified human review in clinical, legal, financial, or
  defense contexts.
- The tested packets cover every possible enterprise failure mode.
- One-shot solo baselines represent every possible solo prompting method.
- The Solo Failure Factory is a public denominator.
- V5/V6 internal repair evidence is public benchmark evidence.
- The old 614-packet result can be combined with blind-120 for public rates.
- A red/green matrix is one blended reliability score.

The current sanctioned public sentence is:

> On the current strict blind-120 public denominator, HoloVerify produced zero
> observed false positives and zero observed false negatives across 120
> action-boundary packets. The old 614-packet number is historical/internal and
> is not the current public denominator.

## Short Above-The-Fold Version

# Can AI tell when it is safe to act?

AI is useful before execution. It can read, summarize, compare, draft, and
explain. But the final step needs a higher bar.

The action boundary is the line between "we can discuss this" and "we may do
this now."

HoloVerify tests whether the visible source evidence really authorizes a
proposed action, or whether the action must escalate.

Current public result:

| Metric | Result |
| --- | ---: |
| Public denominator | Blind-120 only |
| HoloVerify score | 120/120 |
| Truth split | 60 ALLOW / 60 ESCALATE |
| False positives | 0/60 |
| False negatives | 0/60 |

Zero observed errors does not mean zero risk. The exact and Wilson upper bounds
show how much uncertainty remains after this many clean trials.

Solo models are often right, but scattered red failures matter when the action
could release payment, grant access, activate care, change a contract, or move
infrastructure. The Solo Failure Factory shows those stress-selected seams. It
is internal stress evidence, not the public denominator.

HoloVerify adds governed workers, Gov review, deterministic gates, blocker
ledgers, trace preservation, and patch regression. The goal is not better prose.
The goal is controlled action-boundary closure.

## Suggested Section Headers

1. Can AI Tell When It Is Safe To Act?
2. The Current Public Result
3. What This Benchmark Measures
4. Why Solo AI Is Not Enough
5. The Solo Stress Matrix
6. What HoloVerify Adds
7. How Hardening Works
8. What Counts And What Does Not Count
9. The Next Public Milestone
10. What This Does Not Claim
11. Evidence Registry

## Suggested Chart And Table Labels

Hero metric cards:

- Public Denominator
- HoloVerify Score
- Truth Split
- False Positives
- False Negatives

Result table:

- Overall Packet Error
- False Positive Rate
- False Negative Rate
- Exact 95% Upper Bound
- Wilson 95% Upper Bound

Denominator table:

- Evidence Lane
- Selection Rule
- Counted Publicly?
- Allowed Claim

Stress matrix controls:

- Public Blind-120
- Solo Stress Lane
- Holo Rescue / Hardening
- Quarantine

Dot legend:

- Green: Correct and Admissible
- Red: Wrong Verdict
- Yellow: Parse / Admissibility Failure
- Gray: Quarantined / Excluded
- Green Ring: Holo Covered Solo Failure
- Red Ring: Holo Failed Or Not Yet Repaired

Hardening table:

- Failure Class
- Preserved Evidence
- Mechanism Patch
- Rerun Label
- Public Claim Status

Milestone table:

- Current Blind-120
- Next Major Public Milestone: 150/150 = 300
- Phase 1 Side-Specific Wilson Target: 381/381 = 762

## Claim-Safety Warnings

- Keep blind-120 as the only public denominator.
- Keep the old 614 result historical/internal unless re-admitted under the
  current strict blind rules.
- Keep Solo Failure Factory stress-selected and internal; do not use it as
  public FPR/FNR evidence.
- Keep V5/V6 repair lanes internal hardening evidence; do not convert them into
  public benchmark proof.
- Do not call the red/green matrix a public reliability score.
- Do not imply that red dots prove solo models are useless.
- Do not imply that HoloVerify is production-safe or zero-risk.
- Do not claim global model superiority.
- Do not combine public, stress, hardening, historical, and quarantine lanes into
  one score.
- Before converting to HTML, reconcile the side-specific Wilson rounding: the
  current public page and benchmark summary use `6.015%`, while the story
  recommendation artifact lists `6.017%`.

## HoloOps Return Line

Taylor: send this report back to HoloOps.
