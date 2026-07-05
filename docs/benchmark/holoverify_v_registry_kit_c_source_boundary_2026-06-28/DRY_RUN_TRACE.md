# Dry Run Trace: HoloVerify-V Kit C Source-Boundary Candidate

Classification: `REGISTRY_GRADE_CANDIDATE_DRY_RUN`

## Declared Generation Calls

| Call | Lane | Provider | Model | Pair | Packet |
| ---: | --- | --- | --- | --- | --- |
| 1 | `SOLO_EQUAL_CALL_RAW_PACKET` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` |
| 2 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` |
| 3 | `SOLO_EQUAL_CALL_RAW_PACKET` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` |
| 4 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` |
| 5 | `SOLO_EQUAL_CALL_RAW_PACKET` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` |
| 6 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` |
| 7 | `SOLO_EQUAL_CALL_RAW_PACKET` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` |
| 8 | `HOLOVERIFY_V_GOV_REPLAY` | minimax | `MiniMax-M2.5-highspeed` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` |

## Expected Counts

```json
{
  "total_provider_calls": 8,
  "solo_calls": 4,
  "holo_gov_calls": 4,
  "worker_calls": 0,
  "judge_calls": 0
}
```

## Pre-Run Hash Lock

The runner must create `PRE_RUN_MANIFEST.json` before live provider calls. The
manifest includes:

- packet payload hashes
- Solo prompt hashes
- HoloVerify-V prompt hashes
- frozen worker evidence hashes
- model roster
- scoring rubric
- root signature

## Live Scope

Run only:

- `SOLO_EQUAL_CALL_RAW_PACKET`
- `HOLOVERIFY_V_GOV_REPLAY`

Do not run:

- live workers
- judges
- repairs
- reruns
- model substitutions
- fallback models

## Post-Generation Status

If all eight calls complete and deterministic gates pass, status is:

`frozen_pending_judge`

The package is not `benchmark_locked` until independent adjudication is run.

