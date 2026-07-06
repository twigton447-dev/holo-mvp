# HoloVerify Stress Matrix Wave 2 Solo Scout Transport Timeout Operational Note

Created: 2026-07-06

Classification: `WAVE2_SOLO_SCOUT_TRANSPORT_TIMEOUT_INVALID_RUN`

Run folder:
`docs/benchmark/holoverify_stress_matrix_expansion_wave2_solo_scout_runs_2026_07_06/run_20260706T201513Z`

## Status

This run is preserved as an invalid transport-timeout artifact.

It is not a valid Wave 2 solo result. It is not public benchmark evidence. It is not a global FPR/FNR result. It is not natural production-rate evidence.

Do not score this run. Do not rerun this run into a clean result.

## Observed Runtime

| Check | Result |
|---|---:|
| Expected provider calls | 180 |
| Observed provider calls | 1 |
| `TRACE_PROVIDER_CALLS.jsonl` rows | 1 |
| Raw provider outputs | 1 |
| Run prompt files | 1 |
| Preflight prompt-probe files | 60 |
| Provider failures | 1 |
| Scoring run | false |
| Scoring map loaded | false |
| Trace frozen before scoring | true |

Provider call distribution before stop:

| Provider / model | Calls |
|---|---:|
| `xai/grok-3-mini` | 1 |
| `openai/gpt-5.4-mini` | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 0 |

## Failure

The transport timeout occurred on call `1`:

- Provider: `xai`
- Model: `grok-3-mini`
- Packet index: `1`
- Opaque runtime ID: `HVSMW2-0BF7C91D11D4CCED7DA5`
- Failure class: `timeout`
- Error type: `timeout`
- Error text: `The read operation timed out`
- Retryable: `false`
- Attempts recorded in failure payload: `1`
- Elapsed milliseconds: `240186`

The failed raw provider output file exists and contains an empty text body plus the transport timeout payload:

`raw_provider_outputs/001_HVSMW2-0BF7C91D11D4CCED7DA5_xai.json`

## Trace Binding

| Artifact | SHA-256 |
|---|---|
| `TRACE_PROVIDER_CALLS.jsonl` | `02d8fcd581386f0963a7a612c61e81f3ea59b02eecd0bd8f97399ea6c67c52c8` |
| `solo_one_shot_live_summary.json` | `b3088245ac4ceb8902739ef9c86bc40ddb7a2ca12ae4edf31124e5cccebb35fe` |
| `solo_one_shot_runtime_results.json` | `8dbfdffa28076d7c3ac74b59d1974f92324c6c2da22926eba1d25a2846c2e343` |
| `solo_one_shot_preflight.json` | `a57d09e4f032904eae137087d5c85fe2660f1046b8827a8377b0d30bd6f75aa7` |

Runtime manifest:

- Path: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json`
- SHA-256: `428bdd3e1e24e2538bfc6e37989ff741e3efa2749da7dc3b86c863ead90fb39c`

## Claim Boundary

This artifact only proves that a provider execution was attempted and stopped by a timeout on the first provider call.

It does not measure Wave 2 solo performance. It does not create a public denominator. It does not create FPR/FNR evidence. It does not support natural production-rate claims.

## Preservation

This note did not run providers, Holo live, solo live, Gov live, judges, scoring, reruns, or substitutions. The failed run folder was inspected and preserved as-is.
