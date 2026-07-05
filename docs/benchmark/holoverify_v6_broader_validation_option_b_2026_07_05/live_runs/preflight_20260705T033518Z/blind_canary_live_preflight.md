# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `a849152c6e2c86835f7108b95aa1f168242908e169ffe3fcf35274fd3b10cfd0`
- Expected provider calls: `100`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v6_broader_validation_option_b_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
