# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `cffd32a0b6e033bdb7f9a2bc46f83333993fe67cab8a06e12699cb6815fc5ef3`
- Expected provider calls: `100`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:batch015_fn_rescue_live_wrapper_does_not_read_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
