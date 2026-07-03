# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `b158cb6ed1eecb4bf2d84a7137b124e8cd6e9787713fdaa5105f3679ef889197`
- Expected provider calls: `30`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:held_v5_live_wrapper_does_not_read_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
