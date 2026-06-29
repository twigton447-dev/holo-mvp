# HoloVerify 20-Pair Public Benchmark Update Draft

Source: read-only inspection of committed evidence at `93118d7 benchmark: freeze holoverify 20pair 3dna and solo baseline`.

Evidence root inspected:

`docs/benchmark/holoverify_20pair_3dna_2026-06-29/final_evidence_package_2026_06_29`

Additional committed autopsy inspected for the 14-pair subset:

`docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z/run_20260629T060938Z/comparison_autopsy_no_leakage.json`

## Draft Public Update

On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed architecture solved 40/40 packets and 20/20 sibling pairs. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete one-shot solo collapse while Holo solved both siblings. The Holo run used about 2.06x the solo token budget and passed packet-identity and no-leakage audits.

## Evidence Snapshot

| Measure | Committed evidence |
| --- | --- |
| Holo frozen run | 40/40 correct |
| Valid sibling pairs | 20/20 |
| Hard-ALLOW target pairs | 10/10 |
| Hard-ESCALATE target pairs | 10/10 |
| Guardrail siblings | 20/20 |
| Solo baseline calls | 120/120 |
| Solo KNEW/admissible outputs | 6/120 |
| All-six-solo-fail sibling pairs | 14 |
| Mixed sibling pairs | 6 |
| Packet identity | PASS |
| Final readiness assertions | PASS |
| Judges | 0 |
| No-leakage audit | PASS |
| Holo tokens | 426,002 |
| Solo tokens | 206,839 |
| Token ratio | about 2.06x |

## Public Claim Boundaries

- This is an architecture result on one frozen packet family, not a claim that Holo beats all models.
- This does not claim general model superiority.
- This does not claim Holo solved safety.
- This does not claim solo models cannot solve similar packets with other prompting, tools, memory, retries, or orchestration.
- Internal Holo misses must remain separate from external solo one-shot failures.
- The public registry should treat this as publication-ready only after final human review.

## Limitations

- The benchmark remains internal until externally reviewed.
- The solo baseline is a mini-model one-shot baseline, not an exhaustive test of all possible solo prompting methods.
- The packet family is action-boundary specific and should not be generalized to every verification domain.
- The comparison isolates HoloVerify full architecture against one-shot solo baselines using the same mini-model families; it does not compare against every possible multi-call solo workflow.
- Internal Holo misses are evidence about governance correction inside the architecture, not standalone solo failures.
- Public registry publication requires final review of wording, evidence paths, and lock roots.

## Editor Notes Before Publication

- The committed evidence at `93118d7` verifies the public claim numbers above.
- Claim-language risk: avoid saying "Holo is smarter" or "Holo always wins." The defensible claim is narrower: full architecture plus governance enforcement handled this frozen action-boundary bank while same-family one-shot solo baselines frequently failed.
- Lock-root discrepancy to reconcile before public release: the mission text lists final lock root `904fb31d351b8fdc57481f739ce7133687f036626561233883c9795af6dced77`, but `93118d7:FINAL_EVIDENCE_PACKAGE_LOCK_VALIDATION.json` reports `1681941a2a5c5eff6db9a5bf47d2159b360a29ab99a9f26586e3ebff5f5acebf`.
