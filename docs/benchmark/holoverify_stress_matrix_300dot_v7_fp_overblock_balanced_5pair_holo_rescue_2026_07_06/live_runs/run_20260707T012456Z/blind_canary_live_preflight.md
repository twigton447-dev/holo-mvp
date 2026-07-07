# HoloVerify Blind Canary Live Preflight

- Passed: `True`
- Runtime manifest hash: `9976a7cc767f2fd3162e95114dc9ac9991a520f50016f7927685bb53ad413550`
- Expected provider calls: `50`
- Env keys: `{'XAI_API_KEY': 'PRESENT', 'OPENAI_API_KEY': 'PRESENT', 'MINIMAX_API_KEY': 'PRESENT'}`
- Leakage hits: `0`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:300dot_v7_fp_overblock_balanced_5pair_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Attempt budget policy: `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`

No provider calls were made by preflight.
