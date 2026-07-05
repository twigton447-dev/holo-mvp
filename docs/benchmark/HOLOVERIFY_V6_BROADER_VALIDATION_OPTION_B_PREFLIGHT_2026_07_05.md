# HoloVerify V6 Broader Validation Option B Preflight

Date: 2026-07-05

Status: PASS

This is an internal broader V6 validation package only. It is not public benchmark evidence, not a global FNR/FPR claim, not FP precision evidence, and not general model superiority evidence. The strict public denominator remains blind-120 only.

## Runtime Binding

- Label: HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_V0
- Runtime-only manifest: `docs/benchmark/HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- Runtime manifest SHA-256: `a849152c6e2c86835f7108b95aa1f168242908e169ffe3fcf35274fd3b10cfd0`
- Selector: `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`
- Selector SHA-256: `87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Expected future provider calls: 100
- Expected route: `W1 -> G1 -> W2 -> G2 -> W3` across 20 packets

## Lane Composition

| Lane | Pairs | Packets | Selected pairs |
| :--- | ---: | ---: | :--- |
| Source-field authority/scope FN | 4 | 8 | `T3FN3-MINE-001`, `T3FN3-MINE-004`, `T3FN3-MINE-007`, `T3FN3-MINE-009` |
| Blocker-closure | 2 | 4 | `HVSF-FACTORY5-005`, `HVSF-FACTORY7X-013` |
| Exact-boundary FP overblock | 2 | 4 | `HVSF-FACTORY15FP-010`, `HVSF-FACTORY15FP-014` |
| Parse/admissibility held out | 1 | 2 | `HVSF-FACTORY13X-018` |
| Packet/key defect quarantine | 1 | 2 | `HVSF-FACTORY14F-017R` |

## Preflight Checks

Canonical preflight folder:

`docs/benchmark/holoverify_v6_broader_validation_option_b_2026_07_05/live_runs/preflight_20260705T033518Z/`

Checks passed:

- Runtime manifest parses and contains 20 packets.
- Runtime manifest contains no truth, expected verdict, answer key, scoring map, pair ID, sibling, prior solo result, prior Holo result, or failure-class fields.
- Prompt probe produced exactly 100 call records.
- Prompt probe route is exactly `W1 -> G1 -> W2 -> G2 -> W3` for every packet.
- Prompt probe role counts are W1 x20, G1 x20, W2 x20, G2 x20, W3 x20.
- Selector is trace-visible as `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`.
- Worker contract is trace-visible as `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`.
- Live wrapper has no scoring-map path before trace freeze.
- Scoring is post-hoc and trace-bound only.
- Solo calls are disabled.
- Judge calls are disabled.
- No provider trace file was created during package build.
- No raw provider output directory was created during package build.

## Exact Future Approval Sentence

I approve live provider execution for HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 a849152c6e2c86835f7108b95aa1f168242908e169ffe3fcf35274fd3b10cfd0, selector SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05 hash 87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 100 provider calls: W1 xai/grok-3-mini x20, G1 minimax/MiniMax-M2.5-highspeed x20, W2 openai/gpt-5.4-mini x20, G2 minimax/MiniMax-M2.5-highspeed x20, W3 minimax/MiniMax-M2.5-highspeed x20. INTERNAL BROADER V6 VALIDATION ONLY across separated source-field FN, blocker-closure, exact-boundary FP overblock, parse/admissibility held-out, and packet-key quarantine lanes; not public benchmark evidence, not a global FNR/FPR claim, not FP precision evidence, not general model superiority, and the strict public denominator remains blind-120 only. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
