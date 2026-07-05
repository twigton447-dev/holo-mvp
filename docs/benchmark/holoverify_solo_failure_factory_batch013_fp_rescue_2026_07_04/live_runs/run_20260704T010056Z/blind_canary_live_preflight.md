# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `39fcdb352ecce3b3ede2579216a422714c2af197772b7f0e67068daa7f80ac65`
- Expected provider calls: `50`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:batch013_fp_rescue_live_wrapper_does_not_read_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
