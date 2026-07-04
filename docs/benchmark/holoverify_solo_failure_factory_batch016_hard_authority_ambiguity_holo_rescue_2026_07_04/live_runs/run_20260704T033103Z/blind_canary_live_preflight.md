# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `20bd23a08b5685d5bd3cb4f64527b1debc0052d49e7ca1a5ef9dfdca1b4a80a2`
- Expected provider calls: `140`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:batch016_hard_authority_rescue_live_wrapper_does_not_read_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
