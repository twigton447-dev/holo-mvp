# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7`
- Expected provider calls: `60`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:atlas_rescue_live_wrapper_does_not_read_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
