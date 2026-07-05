# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `c6f6ec46c67611a9d410430e04f9813ad66858485caa340f43b2b1efd9a2b732`
- Expected provider calls: `10`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v5_tier2_replacement_pair_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
