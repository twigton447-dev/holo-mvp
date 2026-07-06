# HoloVerify Stress Matrix Wave 2 Solo Scout Partial Transport Failure Operational Note

Created: 2026-07-06

Classification: `WAVE2_SOLO_SCOUT_PARTIAL_TRANSPORT_FAILURE_INVALID_RUN`

Run folder:
`docs/benchmark/holoverify_stress_matrix_expansion_wave2_solo_scout_runs_2026_07_06/run_20260706T195419Z`

## Status

This run is preserved as an invalid transport-failure artifact.

It is not a valid Wave 2 solo result. It is not public benchmark evidence. It is not a global FPR/FNR result. It is not natural production-rate evidence.

Do not score this run. Do not rerun this run into a clean result.

## Observed Runtime

| Check | Result |
|---|---:|
| Expected provider calls | 180 |
| Observed provider calls | 41 |
| `TRACE_PROVIDER_CALLS.jsonl` rows | 41 |
| Raw provider outputs | 41 |
| Run prompt files | 41 |
| Provider failures | 1 |
| Scoring run | false |
| Scoring map loaded | false |
| Trace frozen before scoring | true |

Provider call distribution before stop:

| Provider / model | Calls |
|---|---:|
| `xai/grok-3-mini` | 14 |
| `openai/gpt-5.4-mini` | 14 |
| `minimax/MiniMax-M2.5-highspeed` | 13 |

## Failure

The transport failure occurred on call `41`:

- Provider: `openai`
- Model: `gpt-5.4-mini`
- Packet index: `14`
- Opaque runtime ID: `HVSMW2-51D01F29E914BADBD8D0`
- Failure class: `transient_network_error`
- Error type: `URLError`
- Error text: `<urlopen error [Errno 8] nodename nor servname provided, or not known>`
- Retryable: `true`
- Attempts recorded in failure payload: `3`

The failed raw provider output file exists and contains an empty text body plus the transport error payload:

`raw_provider_outputs/041_HVSMW2-51D01F29E914BADBD8D0_openai.json`

## Trace Binding

| Artifact | SHA-256 |
|---|---|
| `TRACE_PROVIDER_CALLS.jsonl` | `359de864ce44f8a89f8e9e8518dcb95f3d06f809cf4adbbe477a3f51cdb21cba` |
| `solo_one_shot_live_summary.json` | `f9ee284d9cfb7a5669e743c64e795bab146ab75541323704609273ce82330d7d` |
| `solo_one_shot_runtime_results.json` | `823b3678fe3f41837a80417f20f5e5336144033f82d0c644b74532e1f864061d` |
| `solo_one_shot_preflight.json` | `ee540586c2e2cd3992e56ba1818b0f8b58811f6ec8e19408cb6ce404520fc2a3` |

Runtime manifest:

- Path: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json`
- SHA-256: `428bdd3e1e24e2538bfc6e37989ff741e3efa2749da7dc3b86c863ead90fb39c`

## Claim Boundary

This artifact only proves that a partial provider execution was attempted and stopped by a transport failure after 41 observed provider calls.

It does not measure Wave 2 solo performance. It does not create a public denominator. It does not create FPR/FNR evidence. It does not support natural production-rate claims.

## Preservation

This note did not run providers, Holo live, solo live, Gov live, judges, scoring, reruns, or substitutions. The partial run folder was inspected and preserved as-is.
