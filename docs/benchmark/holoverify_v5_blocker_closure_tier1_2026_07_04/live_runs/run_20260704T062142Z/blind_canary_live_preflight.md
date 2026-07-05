# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `edd7ed59e0647c7695c62cf76ecb2f27b6d0b9b8ac8c25a21977607130c63a8d`
- Expected provider calls: `10`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v5_tier1_live_wrapper_uses_runtime_only_manifest_and_does_not_read_registration_json`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
