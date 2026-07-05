# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `11281707dff57b5da7ec5c9766a9bb94611b076a5a5badfe7ecd20d3a0aa0f40`
- Expected provider calls: `20`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v6_scope_dependency_gate_tiny_patch_validation_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
