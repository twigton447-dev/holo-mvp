# HoloVerify Atlas Selector Repair Patch Report

Status: `PATCHED_MORE_NO_PROVIDER`

## Why This Patch Exists

The six-pair Atlas Holo rescue run completed structurally cleanly but scored `11/12`.

The failing packet was:

`HV-ATLAS-DISC-033-B`

Autopsy showed:

| Turn | Verdict | Status |
| --- | --- | --- |
| `W1` | `ESCALATE` | Correct |
| `W2` | `ALLOW` | Wrong intermediate drift |
| `W3` | `ESCALATE` | Correct repair |
| Final selector | `ALLOW` | Wrong artifact selected |

The failure was not provider transport, not Gov parsing, and not all-worker reasoning failure. The failure was:

`FINAL_SELECTOR_CHOSE_WRONG_INTERMEDIATE_ARTIFACT_DESPITE_LATER_WORKER_REPAIR`

## Patch

Patched:

`holoverify_blind_runner_v0.py`

Selector criteria now add two blind, truth-free fields:

- `verdict_consensus_count`
- `final_turn_consensus_repair`

The selector still does not see truth, expected verdict, sibling side, or scoring-map fields.

Selector policy version:

`SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`

Selector policy hash:

`32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6`

New behavior:

If the final worker agrees with a prior structurally valid worker after an intervening contradictory artifact, the selector can prefer the final source-grounded repair over a wrong middle artifact that merely has slightly more cited evidence.

## Fable PATCH_MORE Follow-Up

Fable correctly flagged that this is not just a narrow bugfix. It makes consensus dominance explicit.

Architecture decision:

- Among structurally valid artifacts, verdict consensus outranks citation volume.
- A final-turn repair bonus applies only when the final worker agrees with a prior structurally valid worker after an intervening contradiction.
- A lone final-turn dissenter does not override a two-of-three structurally valid consensus.
- Within the same consensus/repair tier, citation count and section completeness remain secondary structural tie-breaks.

Documented 2^3 verdict-grid behavior:

| W1 | W2 | W3 | Selected artifact |
| --- | --- | --- | --- |
| ALLOW | ALLOW | ALLOW | `ART-002` |
| ALLOW | ALLOW | ESCALATE | `ART-002` |
| ALLOW | ESCALATE | ALLOW | `ART-003` |
| ALLOW | ESCALATE | ESCALATE | `ART-003` |
| ESCALATE | ALLOW | ALLOW | `ART-003` |
| ESCALATE | ALLOW | ESCALATE | `ART-003` |
| ESCALATE | ESCALATE | ALLOW | `ART-002` |
| ESCALATE | ESCALATE | ESCALATE | `ART-002` |

## Regression Fixture

Added:

`tests/test_holoverify_blind_selector_repair_regression.py`

Fixture pattern:

- `W1=ESCALATE`
- `W2=ALLOW`
- `W3=ESCALATE`
- truth hidden from runtime
- selector must choose `ART-003`
- full 2^3 verdict-grid behavior is asserted
- truth-swap markers over the full grid cannot change selection
- selector version/hash is stamped in fixture output and live preflight summaries

## Local Validation

No providers were called by this patch work.

Commands run:

```bash
python3 -m py_compile holoverify_blind_runner_v0.py tests/test_holoverify_blind_selector_repair_regression.py
python3 -m pytest tests/test_holoverify_blind_selector_repair_regression.py -q
BLIND_RUNNER_MODULE=holoverify_blind_runner_v0 python3 -m pytest tests/test_blind_lane_t4_selector_sweep.py -q
BLIND_RUNNER_MODULE=holoverify_blind_runner_v0 python3 -m pytest tests/test_blind_lane_t2_poisoned_spec.py tests/test_blind_lane_t3_hash_chain.py tests/test_blind_lane_t4_selector_sweep.py tests/test_blind_lane_t6_budget_parity.py -q
python3 -m pytest tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py -q
zsh -lc 'set -a; source .env; set +a; python3 -B docs/benchmark/run_holoverify_atlas_holo_rescue_live_2026_07_03.py --preflight'
```

Results after PATCH_MORE follow-up:

- selector regression/grid tests: `6 passed`
- T4 selector sweep: `3 passed`
- T2/T3/T4/T6 blind suite subset: `15 passed`
- canary/120 wrapper tests: `33 passed`
- Atlas rescue preflight after patch: `PASS`

## Next Step

Have Fable review this selector patch before rerunning providers.

If approved, run a fresh Atlas Holo rescue lane. Do not mutate or reinterpret the prior `11/12` run as clean.
