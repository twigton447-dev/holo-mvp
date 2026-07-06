# HoloVerify Stress Matrix Wave 1 FP-Overblock Holo Rescue Preflight

Date: 2026-07-05

Status: PASS

This package is for internal Wave 1 FP-overblock Holo rescue only. It is not public benchmark evidence, not a global FPR/FNR claim, not FP precision evidence, and not natural production rate evidence.

## Source Inputs

- `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_RESCUE_CURATION_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_RESCUE_CURATION_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_2026_07_05.json`
- `docs/benchmark/holoverify_stress_matrix_expansion_wave1_solo_scout_runs_2026_07_05/run_20260705T215904Z/stress_matrix_wave1_solo_posthoc_score.json`

## Selected Pairs

- `HVSM-W1-005`
- `HVSM-W1-011`
- `HVSM-W1-019`
- `HVSM-W1-009`
- `HVSM-W1-013`

Each selected pair has both siblings present, for 5 pairs / 10 packets.

## Runtime Binding

- Runtime-only manifest: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_FP_OVERBLOCK_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- Runtime manifest SHA-256: `ab8eba80b1423db68acc04b9497298d4e7c22384318fc6570c26ecbca9e9d586`
- Post-hoc scoring map SHA-256: `5d263b161a5be73530781f291a4971bcfa1301c830ffa42a5da5f456c17409bb`
- Selector: `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`
- Selector SHA-256: `87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Future live geometry: 50 provider calls
- Route: `W1 -> G1 -> W2 -> G2 -> W3` across 10 packets

## Preflight Checks

Canonical preflight folder:

`docs/benchmark/holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05/live_runs/preflight_20260705T232041Z/`

Checks passed:

- Runtime manifest parses and contains exactly 10 packets.
- Runtime packet rows contain only `opaque_runtime_id`, `runtime_payload_ref`, and `runtime_payload_sha256`.
- Runtime manifest content contains no truth, expected verdict, answer key, scoring map, pair ID, sibling, prior solo result, prior Holo result, ALLOW, or ESCALATE strings.
- Prompt probe produced exactly 50 call records.
- Prompt probe route is exactly `W1 -> G1 -> W2 -> G2 -> W3` for every packet.
- Prompt probe role counts are W1 x10, G1 x10, W2 x10, G2 x10, W3 x10.
- Selector is trace-visible as `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`.
- Worker contract is trace-visible as `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`.
- Live wrapper has no scoring-map path before trace freeze.
- Scoring is post-hoc and trace-bound only.
- Solo calls are disabled.
- Judge calls are disabled.
- No provider trace file was created during package build.
- No raw provider output directory was created during package build.
- No providers, Holo live, solo live, Gov live, or judges were run.

## Exact Future Approval Sentence

I approve live provider execution for HOLOVERIFY_STRESS_MATRIX_WAVE1_FP_OVERBLOCK_HOLO_RESCUE_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_FP_OVERBLOCK_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 ab8eba80b1423db68acc04b9497298d4e7c22384318fc6570c26ecbca9e9d586, selector SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05 hash 87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 50 provider calls: W1 xai/grok-3-mini x10, G1 minimax/MiniMax-M2.5-highspeed x10, W2 openai/gpt-5.4-mini x10, G2 minimax/MiniMax-M2.5-highspeed x10, W3 minimax/MiniMax-M2.5-highspeed x10. INTERNAL WAVE 1 FP OVERBLOCK HOLO RESCUE ONLY; not public benchmark evidence, not a global FPR/FNR claim, not FP precision evidence, and not natural production rate evidence. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
