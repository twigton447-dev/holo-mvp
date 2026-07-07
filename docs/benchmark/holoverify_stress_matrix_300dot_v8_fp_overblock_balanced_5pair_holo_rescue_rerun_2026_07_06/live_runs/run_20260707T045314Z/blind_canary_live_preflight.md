# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `5853f5d8257109199b4a98a18b11f8a9b339d5555093b8c1d89fccb89acd2f3c`
- Expected provider calls: `50`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:300dot_v8_fp_overblock_balanced_5pair_rerun_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
