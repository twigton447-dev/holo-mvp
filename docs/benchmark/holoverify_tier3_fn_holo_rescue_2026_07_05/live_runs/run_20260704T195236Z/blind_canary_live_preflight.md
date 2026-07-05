# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `d570c6f6d8f55d36da7401eb32f8c7531c58d7fdd71274addf917edef5646de5`
- Expected provider calls: `70`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:tier3_fn_holo_rescue_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
