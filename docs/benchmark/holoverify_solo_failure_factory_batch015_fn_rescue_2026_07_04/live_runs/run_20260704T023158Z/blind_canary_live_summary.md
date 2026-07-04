# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `True`
- Observed provider calls: `100` / `100`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:batch015_fn_rescue_live_wrapper_does_not_read_scoring_map_bytes`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_solo_failure_factory_batch015_fn_rescue_posthoc_2026_07_04.py --run-dir docs/benchmark/holoverify_solo_failure_factory_batch015_fn_rescue_2026_07_04/live_runs/run_20260704T023158Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
