# HoloVerify 20-Pair Public Benchmark Update Draft

Source: `87b39f2 benchmark: freeze holoverify 20pair 3dna solo comparison`

Underlying frozen evidence source: `93118d7 benchmark: freeze holoverify 20pair 3dna and solo baseline`

Canonical public package lock root:

`5ffe3c41e5cf35324f9bb0518c24df118aad0eea15900abbb1d9996df1756695`

## Draft Public Update

On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed architecture solved 40/40 packets and 20/20 sibling pairs. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete one-shot solo collapse while Holo solved both siblings. The Holo run used about 2.06x the solo token budget and passed packet-identity and no-leakage audits.

## Evidence Snapshot

| Measure | Public package evidence |
| --- | --- |
| Canonical public package commit | `87b39f2` |
| Underlying frozen evidence commit | `93118d7` |
| Holo frozen run | 40/40 correct |
| Valid sibling pairs | 20/20 |
| Hard-ALLOW target pairs | 10/10 |
| Hard-ESCALATE target pairs | 10/10 |
| Guardrail siblings | 20/20 |
| Solo baseline calls | 120/120 |
| Solo KNEW/admissible outputs | 6/120 |
| Clean all-six-solo-fail sibling pairs | 14 |
| Mixed sibling pairs | 6 |
| Packet identity | PASS |
| No-provider local audit | PASS |
| Judges | 0 |
| No-leakage audit | PASS |
| Holo tokens | 426,002 |
| Solo tokens | 206,839 |
| Token ratio | about 2.06x |
| Public package lock root | `5ffe3c41e5cf35324f9bb0518c24df118aad0eea15900abbb1d9996df1756695` |

## Public Claim Boundaries

- This is an architecture result on one frozen action-boundary packet family.
- This is not a claim that Holo beats all models.
- This is not a claim of general model superiority.
- This is not a claim that Holo solved safety.
- This is not a claim that solo models cannot solve similar packets with other prompting, tools, memory, retries, or orchestration.
- Internal Holo misses must remain separate from external solo one-shot failures.
- Public registry publication still requires final human review.

## Limitations

- The benchmark remains internal until externally reviewed.
- The solo baseline is a mini-model one-shot baseline, not an exhaustive test of all possible solo prompting methods.
- The packet family is action-boundary specific and should not be generalized to every verification domain.
- The comparison isolates HoloVerify full architecture against one-shot solo baselines using the same mini-model families; it does not compare against every possible multi-call solo workflow.
- Internal Holo misses are evidence about governance correction inside the architecture, not standalone solo failures.
- The public package lock is distinct from the earlier full evidence package lock because it locks a later public-safe subset/memo/audit package.

## Suggested Short Version

HoloVerify completed a frozen 40-packet action-boundary benchmark using a 3-DNA governed architecture. It solved 40/40 packets and 20/20 sibling pairs. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete one-shot solo collapse while Holo solved both siblings. The Holo run used about 2.06x the solo token budget and passed packet-identity and no-leakage audits.
