# HoloVerify Benchmark Page Simple Draft

Date: 2026-07-05

Status: draft only. Not public-site HTML.

## Goal

Make the benchmark understandable to someone who has never heard of HoloVerify.

Keep the first screen short. Do not make people learn our internal language before
they understand the point.

## Above The Fold

# Can AI tell when it is safe to act?

AI is good at reading, summarizing, and finding possibilities.

But the final step is different.

Should money move?
Should access be granted?
Should a filing go out?
Should a treatment or workflow start?

That last step is the action boundary.

HoloVerify tests whether AI can protect that boundary.

## Current Public Result

The current public test is narrow and clean.

| Measure | Result |
| --- | ---: |
| Public test packets | 120 |
| Allow cases | 60 |
| Escalate cases | 60 |
| HoloVerify correct | 120/120 |
| False positives observed | 0/60 |
| False negatives observed | 0/60 |

This does not mean zero risk.

It means HoloVerify made zero observed mistakes on this public blind-120 test.
The older 614 result is historical/internal and is not part of this public
number.

## What Is Being Tested

This is not a trivia test.

This is not a writing test.

This is not asking whether AI can sound right.

Each packet asks one practical question:

> Does the evidence really support doing this now?

There are only two valid answers:

| Answer | Meaning |
| --- | --- |
| Allow | The evidence supports the action. |
| Escalate | The evidence does not support the action, so a person or higher-control workflow should review it. |

## Why This Matters

A solo AI model can be right most of the time.

That is still not enough for high-stakes work.

If a model is right 95 times out of 100, that can look strong on a school test.
It is not strong enough if the 5 misses can move money, grant access, approve a
contract, or start a clinical workflow.

The problem is not that AI is useless.

The problem is that AI is brittle at the last step.

## What We Saw In Solo Models

We tested solo models because they are the normal way people imagine autonomous
AI working.

One model gets the packet.
One model gives the answer.
No shared state.
No control layer.
No second system preserving blockers.

The models were often right.

But the failures were scattered. Different models failed in different places and
for different reasons.

That is the problem.

In high-stakes work, scattered red dots are enough to stop the rollout.

## The Red And Green Matrix

The matrix should show this visually.

Each square is one paired test.

Inside the square are six dots:

- three models
- two sibling cases
- one Allow side
- one Escalate side

Green means the solo model got it right.

Red means the solo model made the wrong action-boundary call.

Yellow means the answer failed the required format or admissibility rules.

Gray means the packet was quarantined and should not count.

The solo view should look mostly green, with red and yellow dots scattered
across domains.

That is the point.

The problem is not total collapse.

The problem is that even strong models still leave enough red to be unsafe at
the final action step.

## What HoloVerify Adds

HoloVerify is not one model making one call.

It is a controlled decision process.

It uses models for the work they are good at:

- reading sources
- finding relevant facts
- explaining the case
- noticing possible blockers

Then it adds controls around them:

- required source evidence
- worker and Gov turns
- blocker tracking
- deterministic checks
- preserved traces
- final selection rules
- regression tests when something fails

The goal is simple:

Do not let a confident answer override missing evidence.

## The Holo View

The second matrix view should keep the same solo dots.

Then turn HoloVerify on.

If Holo covers a solo failure, the red dot gets a green ring or a green overlay.

If Holo also fails, it stays red and links to the failure class.

If the packet was flawed, it stays gray.

This is how we show the work honestly.

We do not hide failures.
We classify them, patch the system when the failure is real, and rerun the
right regression lane.

## What Counts

| Evidence | Public Status |
| --- | --- |
| Blind-120 HoloVerify test | Current public denominator |
| Solo Failure Factory | Internal stress evidence |
| V5/V6 repair runs | Internal hardening evidence |
| Old 614 result | Historical/internal |
| Packet defects | Quarantined |

This separation matters.

The public number is blind-120.

The red-dot matrix is a failure atlas.

The repair runs show hardening.

They should not be blended into one score.

## Next Milestones

The next goal is a larger clean public test.

| Milestone | Size |
| --- | ---: |
| Current public test | 60 Allow + 60 Escalate = 120 |
| Next major milestone | 150 Allow + 150 Escalate = 300 |
| Phase 1 statistical target | 381 Allow + 381 Escalate = 762 |

The goal is not to make the easiest test bigger.

The goal is to keep finding hard cases, keep the evidence clean, and keep the
public claims separated from internal hardening work.

## Short Version For The Page

AI can help before execution.

But the last step needs a higher bar.

HoloVerify tests whether evidence really supports a proposed action before that
action executes.

The current public blind test is 120 packets: 60 Allow and 60 Escalate.
HoloVerify scored 120/120, with zero observed false positives and zero observed
false negatives.

That does not prove zero risk.

It means the system passed this strict public lane.

The red/green matrix shows why this matters: solo models are often right, but
their failures are scattered across domains. In high-stakes work, scattered red
dots are enough to require a governed action-boundary layer.

## Plain Labels

Use these labels instead of jargon:

| Avoid | Use |
| --- | --- |
| action-boundary proof discipline | deciding whether it is safe to act |
| denominator | counted test set |
| false positive | blocked something that was allowed |
| false negative | allowed something that should have escalated |
| admissibility failure | answer failed the required format |
| stress-selected lane | hard-case test set |
| internal hardening evidence | engineering evidence |
| packet/key defect | flawed test case |

## Claim Safety

Do not say:

- HoloVerify proves safe AI.
- HoloVerify has zero risk.
- HoloVerify beats all models.
- The old 614 result is part of the public denominator.
- The red/green stress matrix is the public FPR/FNR denominator.
- Internal repair runs are public benchmark proof.

Safe sentence:

> HoloVerify passed the current blind-120 public test. The red/green matrix shows
> internal stress evidence about where solo models can fail, and how HoloVerify
> is being hardened against those failures.
