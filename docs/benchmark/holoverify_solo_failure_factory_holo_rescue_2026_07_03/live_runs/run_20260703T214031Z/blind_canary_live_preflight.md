# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `20a614b9de95c7cb7953fd70d5d820ccf1135dea2f738edd0ab859b12ae1c346`
- Expected provider calls: `130`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:solo_failure_factory_rescue_live_wrapper_does_not_read_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
