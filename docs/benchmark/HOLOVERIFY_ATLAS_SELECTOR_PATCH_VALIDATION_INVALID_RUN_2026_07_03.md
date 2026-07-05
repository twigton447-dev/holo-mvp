# HoloVerify Atlas Selector Patch Validation Invalid Run

Status: `INVALID_RUN_WORKER_CONTENT_CONTRACT_FAILURE`

Run folder:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z`

## Classification

This run is invalid for selector patch validation.

It is not a selector verdict result. It is not a scored Holo rescue result. It is not fresh benchmark evidence.

## What Happened

The same-six Atlas selector patch-validation lane started under the locked approval sentence for:

`SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`

Expected provider calls:

`60`

Observed provider calls:

`60`

The run failed closed at the final call:

| Field | Value |
| --- | --- |
| Call | `60` |
| Slot | `W3` |
| Role | `worker` |
| Provider | `minimax` |
| Model | `MiniMax-M2.5-highspeed` |
| Error | `W3_empty_text` |
| Finish reason | `length` |
| Input tokens | `619` |
| Output tokens | `2048` |
| Max output tokens | `2048` |
| Transport recovered | `false` |
| Raw output | `raw_provider_outputs/060_W3.json` |

The raw model output began with hidden thinking/prose and never produced a valid compact worker artifact before the output limit. The runtime stripped the hidden thinking text, leaving empty model-visible artifact text, then failed closed.

## Why It Was Not Scored

The runtime did not produce a complete valid Holo artifact set. The scoring map must only be loaded after a valid trace freeze. This run froze a failure trace, not a completed result.

Post-hoc scoring was not run.

## What This Means

This run does not validate or invalidate the selector patch.

The selector patch remains:

`UNVALIDATED_BY_LIVE_PATCH_REPLAY`

The failure class is:

`WORKER_CONTENT_CONTRACT_FAILURE`

Specific failure:

`W3_EMPTY_TEXT_AFTER_HIDDEN_THINKING_FILTER_AND_LENGTH_FINISH`

## What This Does Not Mean

Do not claim:

- The selector patch failed.
- The selector patch passed.
- Holo scored `12/12`.
- Holo scored anything on this rerun.
- MiniMax made a wrong verdict.
- This is benchmark evidence.

## Preserved Evidence

- Trace: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z/TRACE_PROVIDER_CALLS.jsonl`
- Summary: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z/blind_canary_live_summary.json`
- Raw failed output: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z/raw_provider_outputs/060_W3.json`

## Recommended Next Step

Do not rerun automatically.

Next valid move is a no-provider autopsy of the W3 compact worker contract failure, then a decision whether to harden the W3 worker prompt/contract or rerun under the same contract with a new explicit approval.
