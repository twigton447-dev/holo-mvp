# HoloVerify Stress Matrix Wave 1 FP Overblock Holo Rescue Provenance Audit

Date: 2026-07-05

Run folder:
`docs/benchmark/holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05/live_runs/run_20260705T232606Z/`

## Classification

PASS.

Classify this run as:

`AUTHORIZED_LIVE_RUN_WITH_RUNTIME_PROVENANCE_LIMITATION`

The live wrapper requires the submitted approval statement to exactly match the scoped approval sentence before it can enter the live path. The shared runner raises `approval_statement_mismatch` before creating a live run if the approval string does not match.

The run folder does not persist the raw approval sentence or launcher identity. So the audit can prove wrapper-level authorization gating and exact runtime binding, but it cannot independently prove who launched the command from inside the run folder alone.

There is no evidence that this was accidental or provenance-defective.

## Runtime Controls

| Check | Result |
|---|---:|
| Runtime manifest SHA-256 | `ab8eba80b1423db68acc04b9497298d4e7c22384318fc6570c26ecbca9e9d586` |
| Expected provider calls | 50 |
| Observed provider calls | 50 |
| Provider failures | 0 |
| Raw provider output files | 50 |
| `TRACE_CALLS.jsonl` rows | 50 |
| `TRACE_PROVIDER_CALLS.jsonl` rows | 50 |
| Call sequence per packet | `W1 -> G1 -> W2 -> G2 -> W3` |
| Slot counts | `W1=10, G1=10, W2=10, G2=10, W3=10` |
| Substitutions detected | 0 |
| Trace frozen before scoring | true |
| Scoring map loaded after trace hash binding | true |
| Mixed registration JSON before trace freeze | false |
| Judges | 0 |
| Solo calls | 0 |

Provider roster observed:

| Slot | Provider / Model | Calls |
|---|---|---:|
| W1 | `xai/grok-3-mini` | 10 |
| G1 | `minimax/MiniMax-M2.5-highspeed` | 10 |
| W2 | `openai/gpt-5.4-mini` | 10 |
| G2 | `minimax/MiniMax-M2.5-highspeed` | 10 |
| W3 | `minimax/MiniMax-M2.5-highspeed` | 10 |

## Trace Binding

| Artifact | SHA-256 |
|---|---|
| `TRACE_CALLS.jsonl` | `8ba5795389f57f0d8e92966dc678b1cae5f2d5e05af170020c1b6aa1604efea5` |
| `TRACE_PROVIDER_CALLS.jsonl` | `e64007b832ce2534e38e5b54a253c227ac7ff2c4a79e369d3d3b8577c2a5fb11` |
| `blind_canary_runtime_results.json` | `c30f41fb175fd68400b1ffb6e3c7a997988d38f1bafac3f56f20cb9ac64b7251` |
| `blind_canary_live_summary.json` | `08c8be46f33dbcd4a776879b58394bea25340f8aa3d9cc432678c50fd99ae8bb` |
| Scoring map | `5d263b161a5be73530781f291a4971bcfa1301c830ffa42a5da5f456c17409bb` |

## Final Score

Post-hoc scoring result:

| Metric | Result |
|---|---:|
| Correct packets | 7/10 |
| Incorrect packets | 3/10 |
| Complete pairs correct | 2/5 |
| Provider calls | 50 |
| Provider failures | 0 |
| Internal rescue passed | false |

Failed packets:

| Packet | Truth | Holo Final | Classification |
|---|---|---|---|
| `HVSM-W1-009-A` | ALLOW | ESCALATE | Holo over-escalation on ALLOW sibling |
| `HVSM-W1-011-A` | ALLOW | ESCALATE | Holo over-escalation on ALLOW sibling |
| `HVSM-W1-019-A` | ALLOW | ESCALATE | Holo over-escalation on ALLOW sibling |

The failures are all false ESCALATE results on ALLOW siblings. They are not false ALLOW failures.

One scoring-map label is noisy: several rows use `target_failure_shape: FN_FALSE_ALLOW on ESCALATE sibling` even on ALLOW rows. The authoritative scoring facts are the `truth` and `final_verdict` fields, which show three ALLOW siblings over-escalated.

## Evidence Treatment

This run should be committed only as preserved failed internal evidence.

It should not be used as:

- public benchmark evidence
- a global FPR or FNR claim
- FP precision evidence
- natural production-rate evidence
- a Holo rescue win

Recommended preservation scope:

- the existing run folder exactly as-is
- this provenance audit
- the paired failure autopsy

Do not rerun into a clean result under the same label.

