# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1`
- Expected provider calls: `600`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `tests/test_holoverify_blind_120_live_wrapper.py::test_preflight_does_not_read_120_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
