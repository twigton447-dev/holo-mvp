# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `True`
- Observed provider calls: `70` / `70`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v5_tier2_fn_rescue_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_v5_blocker_closure_tier2_fn_rescue_posthoc_2026_07_04.py --run-dir docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
