# HoloVerify V6 Tiny Patch-Validation Post-Live Architecture Audit

CALLSIGN: ARCHITECTURE AUDIT SUBAGENT

Date: 2026-07-05

Status: PASS

Checkpoint audited: 6e5c61b92cf7bfe38bc696d82925169f62b78d87

Valid scored run:
`docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/run_20260705T014301Z`

Separate failed transport/sandbox attempt:
`docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/run_20260705T014145Z`

Audit constraints observed by this audit: no providers run, no Holo live run, no solo run, no judges run, no staging, no commit, no push.

## Bottom Line

PASS. The successful V6 tiny patch-validation run is trace-complete, trace-bound, and internally scoped as patch validation only. The valid run contains exactly 20 provider calls, no provider failures, the expected W1 -> G1 -> W2 -> G2 -> W3 route repeated four times, and a post-hoc score of 4/4 packets and 2/2 pairs. The failed DNS/network attempt is preserved separately, has no runtime results or post-hoc score file, and is excluded from the valid scored run.

No required patch before commit was found by this audit.

## Verification Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| Valid run has exactly 20/20 provider calls | PASS | `blind_canary_live_summary.json` reports `expected_provider_calls: 20`, `observed_provider_calls: 20`; `TRACE_PROVIDER_CALLS.jsonl` has 20 rows. |
| Provider failures in valid run = 0 | PASS | `blind_canary_live_summary.json` and lane summary both report `provider_failures: []`; parsed provider trace has 0 failed calls. |
| Route is W1 -> G1 -> W2 -> G2 -> W3 x4 | PASS | Provider and call traces contain slot sequence `W1,G1,W2,G2,W3` repeated for four packets; slot counts are W1/G1/W2/G2/W3 = 4 each. |
| Post-hoc score is 4/4 packets and 2/2 pairs | PASS | `v6_scope_dependency_gate_tiny_patch_validation_posthoc_score_trace_bound_v1.json` reports `correct_count: 4`, `packet_count: 4`, `pairs_both_siblings_correct: 2`, `pair_count: 2`. |
| Failed packets = [] | PASS | Post-hoc score reports `failed_packets: []`. |
| Failed DNS/network attempt preserved separately and excluded from scoring | PASS | Failed run `run_20260705T014145Z` has one failed W1 xai transport row, no runtime results file, and no post-hoc score file. Valid score binds only to `run_20260705T014301Z`. |
| V6 selector active | PASS | Valid run summaries and runtime results report `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05` with selector SHA `87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2`. |
| V4 worker contract active | PASS | Valid run summaries and runtime results report `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04` with worker contract SHA `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`. |
| Deterministic V6 source-field authority/scope gate visible in traces | PASS | W2 prompts for the two ESCALATE fixtures include `deterministic_scope_dependency_gate`, active blocker ledger entries, deterministic dependency ledger entries, and required verdict `ESCALATE`; ALLOW sibling W2 prompts include empty active blocker ledgers and required verdict `ALLOW`. |
| ESCALATE fixtures corrected for intended V6 reason | PASS | Score rows show `HVSF-FACTORY16-008-B` and `HVSF-FACTORY16-019-B` selected `ESCALATE`, with checks `authority_scope_add_on_activation` and `authority_scope_protocol_start`. Runtime artifact selection shows initial ALLOW artifacts gate-failed and final ART-003 selected. |
| ALLOW siblings remain allowed | PASS | Score rows show `HVSF-FACTORY16-008-A` and `HVSF-FACTORY16-019-A` selected `ALLOW` and correct. |
| No scoring map loaded before trace freeze | PASS | Valid live summary reports `trace_frozen_before_scoring: true`, `live_wrapper_has_scoring_map_path: false`, and `posthoc_scoring_required_after_trace_freeze: true`. Post-hoc score reports `scoring_map_loaded_after_trace_hash_binding: true`. |
| No mixed registration JSON used before trace freeze | PASS | Lane summary reports `mixed_registration_json_loaded_before_trace_freeze: false`. |
| Raw provider outputs and prompts preserved | PASS | Valid run contains 20 prompt files and 20 raw provider output files, plus `TRACE_CALLS.jsonl` and `TRACE_PROVIDER_CALLS.jsonl`. |
| Trace hashes bind correctly to post-hoc score | PASS | Recomputed hashes match post-hoc binding for `TRACE_CALLS.jsonl`, `TRACE_PROVIDER_CALLS.jsonl`, and `blind_canary_runtime_results.json`; post-hoc score file hash is `ea1853c3c2c4602bc92d4f6c8ad1485ae137a8d689ae4da0d93991578de4bf9f`. |
| Claim boundary remains internal patch-validation only | PASS | Lane summary and post-hoc score both mark `patch_validation_only: true` and explicitly disallow public benchmark, global FNR, FP precision, and model-superiority claims. |

## Run Evidence

Valid run trace hashes:

- `TRACE_CALLS.jsonl`: `2e995222601ba0381d0979dade640d3af54e7c63368de7a7f8588ce1fa2cf7c8`
- `TRACE_PROVIDER_CALLS.jsonl`: `5bf2d56b4552ede1af8206b4450f03ee528160c0b6b80dc349d56fbc5cf8dfcc`
- `blind_canary_runtime_results.json`: `58ff087743ee219346a9c35f9d1323cd111c1f133591e001286f3e2ba805fa1b`
- `v6_scope_dependency_gate_tiny_patch_validation_posthoc_score_trace_bound_v1.json`: `ea1853c3c2c4602bc92d4f6c8ad1485ae137a8d689ae4da0d93991578de4bf9f`

Score rows:

- `HVSF-FACTORY16-008-A`: selected `ALLOW`, truth `ALLOW`, correct, check `authority_scope_add_on_activation`.
- `HVSF-FACTORY16-008-B`: selected `ESCALATE`, truth `ESCALATE`, correct, check `authority_scope_add_on_activation`.
- `HVSF-FACTORY16-019-A`: selected `ALLOW`, truth `ALLOW`, correct, check `authority_scope_protocol_start`.
- `HVSF-FACTORY16-019-B`: selected `ESCALATE`, truth `ESCALATE`, correct, check `authority_scope_protocol_start`.

## Failed Attempt Containment

The failed transport/sandbox attempt at `run_20260705T014145Z` is preserved as a separate run directory. It contains one failed W1 provider row with a DNS/network transport error, `observed_provider_calls: 1`, `passed_runtime_firewall: false`, `runtime_result_ref: null`, and no post-hoc score file. This run is not used as the valid scored patch-validation run.

## Claim Boundary

Allowed claim: V6 corrected the two known Tier 3 scope-dependency fixtures under tiny patch validation while preserving the matching ALLOW siblings in this four-packet internal lane.

Disallowed claims: public benchmark evidence, general HoloVerify benchmark improvement, global false-negative-rate improvement, false-positive precision claim, model-superiority claim, or any claim outside this four-packet patch-validation lane.

## Finding

PASS. The V6 tiny patch-validation run is architecturally valid for internal patch-validation evidence. No blocker or required patch was found by this audit.
