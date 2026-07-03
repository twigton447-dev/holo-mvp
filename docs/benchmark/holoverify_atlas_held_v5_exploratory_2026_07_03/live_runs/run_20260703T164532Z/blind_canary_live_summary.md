# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `True`
- Observed provider calls: `30` / `30`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:held_v5_live_wrapper_does_not_read_scoring_map_bytes`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_atlas_held_v5_exploratory_posthoc_2026_07_03.py --run-dir docs/benchmark/holoverify_atlas_held_v5_exploratory_2026_07_03/live_runs/run_20260703T164532Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
