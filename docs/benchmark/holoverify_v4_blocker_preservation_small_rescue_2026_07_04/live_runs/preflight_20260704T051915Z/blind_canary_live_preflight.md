# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `4f8ec7a398b4b98be98695882ee90554884b2ffd939c6af2a1db41efc2553f60`
- Expected provider calls: `25`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v4_small_rescue_live_wrapper_uses_runtime_only_manifest_and_does_not_read_registration_json`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
