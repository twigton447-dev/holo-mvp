# HoloVerify V5 Tier 1 Post-Hoc Claim Boundary Patch

Date: `2026-07-04`

Status: `NO_PROVIDER_REPORTING_PATCH_COMPLETE`

Run folder:

`docs/benchmark/holoverify_v5_blocker_closure_tier1_2026_07_04/live_runs/run_20260704T062142Z`

## Scope

This patch fixes post-hoc score reporting language and denominator fields only.

No providers were run.

No Holo live run was rerun.

No solo run was run.

No judge was run.

No runtime trace, prompt, or raw provider output was modified.

## Defect

Stats Subagent classified the first post-hoc score artifact as:

`POSTHOC_CLAIM_BOUNDARY_DENOMINATOR_DEFECT`

The run controls were clean, and the packet score was clean, but the score artifact used pair-level language for a Tier 1 run that included only B-side packets.

Problematic fields:

- `pair_count: 2`
- allowed claim said: `Holo solved both siblings...`

That was wrong for Tier 1. Tier 1 has:

- `2` packets
- `0` complete sibling pairs
- no public denominator
- no FPR/FNR claim
- no pair-level claim

## Patch

The post-hoc scorer now reports:

- `packet_count`
- `correct_count`
- `incorrect_count`
- `pair_count` as complete sibling pairs only
- `complete_pair_count`
- `legacy_pair_group_count`
- `partial_pair_group_count`
- `pair_count_note`

For the Tier 1 run, the corrected score is:

| Field | Value |
| --- | ---: |
| `packet_count` | `2` |
| `correct_count` | `2` |
| `incorrect_count` | `0` |
| `pair_count` | `0` |
| `complete_pair_count` | `0` |
| `legacy_pair_group_count` | `2` |
| `partial_pair_group_count` | `2` |

The allowed internal claim now reads:

`V5 Tier 1 patch validation passed on 2/2 selected ESCALATE-side false-closure packets after blind runtime execution and post-freeze scoring.`

## Claim Boundary

Allowed:

`V5_TIER1_PATCH_VALIDATION_PASSED` if independent post-patch audit confirms the corrected score artifact.

Not allowed:

- public error-rate claim
- general model superiority claim
- complete-pair claim
- both-siblings claim
- FPR/FNR claim
- benchmark denominator claim

## Files Patched

- `docs/benchmark/score_holoverify_solo_failure_factory_batch016_hard_authority_ambiguity_holo_rescue_posthoc_2026_07_04.py`
- `docs/benchmark/holoverify_v5_blocker_closure_tier1_2026_07_04/live_runs/run_20260704T062142Z/solo_failure_factory_batch016_hard_authority_rescue_posthoc_score_trace_bound_v1.json`

## Validation

The corrected post-hoc scorer was rerun locally against the frozen trace folder only.

No provider calls occurred.

JSON validation passed for the corrected score artifact.

