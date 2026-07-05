# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `4806a1bf224bfd1c58495a119e16a5fc84c3374ccca1628fe4c525a43ab7333d`
- Expected provider calls: `70`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v5_tier2_fn_rescue_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
