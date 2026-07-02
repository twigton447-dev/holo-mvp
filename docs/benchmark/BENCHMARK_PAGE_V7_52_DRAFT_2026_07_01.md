# The Action Boundary Benchmark
### Measuring AI reliability before irreversible enterprise action

**Draft Version 7.52 · July 2026**

Draft status: not yet published. This page draft is based on the current
statistical appendix and should be reviewed before replacing the live v7.51
benchmark page.

---

## The Point

AI systems are moving closer to real-world action.

They can approve payments, grant access, release data, place orders, prepare
filings, trigger infrastructure changes, and activate clinical workflows.

At that point, the important question is no longer:

> Can the model produce a plausible answer?

The question is:

> Does the evidence actually authorize the action?

HoloVerify is tested at that boundary.

It returns one of two decisions:

**ALLOW**

The current source evidence closes the exact action boundary.

**ESCALATE**

The current source evidence does not close the exact action boundary. A person
or higher-control workflow must review it.

---

## Current Benchmark Ledger

The current clean benchmark-grade HoloVerify denominator is:

| Metric | Value |
| --- | ---: |
| Frozen action-boundary packets | 334 |
| Sibling pairs | 167 |
| ALLOW truths | 167 |
| ESCALATE truths | 167 |
| Correct HoloVerify packets | 334 |
| Observed FP errors | 0 |
| Observed FN errors | 0 |

Observed result:

> HoloVerify solved 334/334 clean benchmark-grade action-boundary packets with
> zero observed false positives and zero observed false negatives.

That does not mean zero risk.

The honest statistical statement is:

| Metric | Errors | n | Exact 95% upper bound | Wilson 95% upper bound |
| --- | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 334 | 0.893% | 1.137% |
| False positive rate | 0 | 167 | 1.778% | 2.249% |
| False negative rate | 0 | 167 | 1.778% | 2.249% |

Zero observed errors means no failures appeared in this locked sample. It does
not prove the true error rate is zero. It means the plausible upper risk is
bounded by the confidence interval.

---

## Confusion Matrix

Positive class: **ESCALATE**.

| Actual / Predicted | ESCALATE | ALLOW |
| --- | ---: | ---: |
| Actual ESCALATE | TP = 167 | FN = 0 |
| Actual ALLOW | FP = 0 | TN = 167 |

Observed rates:

| Rate | Observed |
| --- | ---: |
| Sensitivity / TPR | 100.00% |
| Specificity / TNR | 100.00% |
| FPR | 0.00% |
| FNR | 0.00% |

Observed rates are descriptive. The confidence bands above are the risk
language.

---

## What Counts

Only clean benchmark-grade evidence is counted in the 334-packet denominator.

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

1. A fixed multi-DNA worker roster.
2. Gov adjudication between workers.
3. Deterministic gates after worker outputs.
4. An artifact registry.
5. Best-answer preservation.
6. A final selector that prevents regression.
7. Trace and token accounting.

Gov does not choose models. The model order is fixed by the run lock.

Gov's job is to diagnose the previous worker output, read deterministic gate
results, block unsafe moves, preserve what is correct, and tell the next worker
what must be repaired or resolved.

The goal is not better prose.

The goal is action-boundary closure.

---

## Why Architecture Matters

Matching solo baselines are run on the same frozen packets to test what
individual models do without:

- Gov.
- Shared state.
- Deterministic gates.
- Artifact memory.
- Best-answer preservation.
- Final selection.

Solo outputs only count as **KNEW/admissible** when they produce:

- the right verdict,
- valid structure,
- required source grounding,
- no invented source IDs,
- and a machine-checkable action-boundary explanation.

Example matched slice:

| Slice | HoloVerify | Matched solo |
| --- | ---: | ---: |
| Wave3/Wave4 packets | 54/54 correct | 54/162 KNEW/admissible |
| Wave3/Wave4 pairs | 27/27 valid | 27/27 strong solo-collapse pairs |

This does not prove that every solo model always fails. It shows that, on this
frozen action-boundary slice, one-shot solo models were much less reliable than
the governed architecture.

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
> FP/FN errors across 334 action-boundary packets, with a measured statistical
> upper risk band.

---

## Next Statistical Milestone

The next frozen packet bank is Wave5:

| Wave5 scope | Value |
| --- | ---: |
| Domains | 7 |
| Sibling pairs | 140 |
| Packets | 280 |
| ALLOW truths | 140 |
| ESCALATE truths | 140 |

Wave5 domains:

- Clinical medication / treatment activation controls.
- Treasury / wire / cash movement controls.
- Legal / regulatory filing controls.
- Cloud infrastructure / destructive admin controls.
- Security operations / incident response controls.
- Public sector / citizen records controls.
- Industrial / utility / OT safety controls.

If Wave5 completes cleanly, the benchmark-grade denominator becomes:

| Metric | Current | After clean Wave5 |
| --- | ---: | ---: |
| Packets | 334 | 614 |
| Sibling pairs | 167 | 307 |
| Packet-level exact 95% upper bound | 0.893% | about 0.487% |
| FPR/FNR exact 95% upper bound | 1.778% | about 0.971% |

That is the next milestone:

> Below 0.5% packet-level upper risk and below 1.0% FP/FN upper risk, if Wave5
> completes cleanly.

---

## Reliability Threshold Roadmap

The business question is not "did this sample pass?"

The business question is:

> How low does the upper risk bound need to be before this class of action can
> be trusted with this level of autonomy?

For ordinary internal workflow assistance, the current 334-packet result is
already a strong foundation. For irreversible clinical, financial, legal,
defense, infrastructure, or regulated-data actions, the next thresholds should
be stricter.

Side-specific FP/FN risk is the primary safety bar because ALLOW and ESCALATE
fail in different ways.

| Target side-specific upper bound | Required ALLOW examples | Required ESCALATE examples | Required total packets | Additional packets from current 334 | Additional packets after clean Wave5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| < 1.0% | 299 | 299 | 598 | 264 | 0 |
| < 0.5% | 598 | 598 | 1,196 | 862 | 582 |
| < 0.25% | 1,197 | 1,197 | 2,394 | 2,060 | 1,780 |
| < 0.1% | 2,995 | 2,995 | 5,990 | 5,656 | 5,376 |

Recommended threshold policy:

| Use case tier | Suggested evidence threshold |
| --- | --- |
| Internal decision support | Current clean ledger plus domain-specific review |
| Enterprise action recommendation | < 1.0% FP/FN upper bound in-domain |
| High-stakes irreversible action gating | < 0.5% FP/FN upper bound in-domain, plus human escalation policy |
| Safety-critical production autonomy | < 0.1% FP/FN upper bound, external review, and ongoing monitoring |

The next practical target is not < 0.1%.

The next practical target is:

> Run Wave5 clean, then expand by roughly 582 additional balanced packets to
> push side-specific FP/FN upper bounds below 0.5%.

The < 0.1% tier should be treated as a production-scale validation program, not
as the next public benchmark milestone.

---

## Next Packet Families

After Wave5, the next packet expansion should prioritize more irreversible
action boundaries, not generic reasoning tasks.

Recommended next families:

| Domain | Action boundary being tested |
| --- | --- |
| Defense logistics / command authorization | Whether source authority permits movement, procurement, or operational release |
| Banking / AML / account freeze controls | Whether account restriction or release is justified by current evidence |
| Insurance claims / payout authorization | Whether payout, denial, or escalation is permitted |
| Pharma quality / batch release | Whether manufacturing or quality evidence permits product release |
| Privacy / data disclosure / consent controls | Whether records may be disclosed to a requester |
| Education / student record release | Whether FERPA-style authority closes the disclosure boundary |
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

This draft should not be published until the source links and audit vault are
rendered into the final benchmark page.
