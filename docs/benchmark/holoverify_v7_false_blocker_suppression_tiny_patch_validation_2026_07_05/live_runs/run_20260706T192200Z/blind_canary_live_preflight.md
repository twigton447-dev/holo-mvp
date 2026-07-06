# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `f1f55f0c5b69f8bffa9c9a770f1b21a845e51e7bab5b810156f799175e213db8`
- Expected provider calls: `30`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v7_false_blocker_suppression_tiny_patch_validation_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
