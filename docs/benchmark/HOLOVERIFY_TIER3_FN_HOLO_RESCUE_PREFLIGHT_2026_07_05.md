# HoloVerify Tier 3 FN Holo Rescue Preflight

- Passed: `True`
- Lane: `HOLOVERIFY_TIER3_FN_HOLO_RESCUE_V0`
- Runtime manifest: `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- Runtime manifest SHA-256: `d570c6f6d8f55d36da7401eb32f8c7531c58d7fdd71274addf917edef5646de5`
- Scoring map: `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/holoverify_tier3_fn_holo_rescue_scoring_map_2026_07_05.json`
- Scoring map SHA-256: `50684b99d8e56c5532942a51597b5ac65e21a562e354152286ec70cc189c9625`
- Hash manifest: `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/holoverify_tier3_fn_holo_rescue_hash_manifest_2026_07_05.json`
- Hash manifest SHA-256: `36b8b1e73d62b7606650001d5dac1b22d6cba34e952a792605379c3da91ab463`
- Live wrapper: `docs/benchmark/run_holoverify_tier3_fn_holo_rescue_live_2026_07_05.py`
- Post-hoc scorer: `docs/benchmark/score_holoverify_tier3_fn_holo_rescue_posthoc_2026_07_05.py`
- Prompt probe: `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/preflight_20260704T194756Z/preflight_prompt_probe`
- Prompt files: `70`
- Mock observed calls: `70`
- Packet-key defects: `0`
- Expected future provider calls: `70`
- Route: `W1 -> G1 -> W2 -> G2 -> W3`

## Selected Pairs

- `HVSF-FACTORY16-008`
- `HVSF-FACTORY16-019`
- `HVSF-FACTORY2-005`
- `T3FN-MINE-006`
- `T3FN-MINE-010`
- `T3FN2-MINE-003`
- `T3FN3-MINE-003`

Reserve pair not included: `T3FN3-MINE-009`

## Stop Rules

- No provider calls were made.
- No Holo live run was made.
- No solo run was made.
- No judges were run.
- The scoring map is post-hoc only and is not a live input.
- This is patch-validation/rescue material only, not public benchmark claim material.

## Exact Future Approval Sentence

I approve live provider execution for HOLOVERIFY_TIER3_FN_HOLO_RESCUE_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 d570c6f6d8f55d36da7401eb32f8c7531c58d7fdd71274addf917edef5646de5, selector SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 939c1ffbba74e9a526d454979b52980513d952eae4077cc817283380e596a1ec, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 70 provider calls: W1 xai/grok-3-mini x14, G1 minimax/MiniMax-M2.5-highspeed x14, W2 openai/gpt-5.4-mini x14, G2 minimax/MiniMax-M2.5-highspeed x14, W3 minimax/MiniMax-M2.5-highspeed x14. SELECTED CLEAN FN_FALSE_ALLOW HOLO RESCUE ONLY across seven selected sibling pairs; not public benchmark evidence, not a global FNR claim, and not FP precision evidence. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
