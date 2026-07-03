# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `1cee61c1d73214a605d2ee5ae3ab4f9b54eb7a8e3c1f6bb8faf6640cd4ea29fd`
- Expected provider calls: `50`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `tests/test_holoverify_blind_120_live_wrapper.py::test_preflight_does_not_read_120_scoring_map_bytes`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
