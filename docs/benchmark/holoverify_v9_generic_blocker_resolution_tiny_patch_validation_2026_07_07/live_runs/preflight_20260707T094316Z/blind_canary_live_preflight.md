# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `c9087ce57bd39aab8e3e202192c1aea6df31ee2a6b3d7842f1a7832a6c829da5`
- Expected provider calls: `30`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v9_generic_blocker_resolution_tiny_patch_validation_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
