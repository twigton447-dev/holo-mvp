# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `True`
- Observed provider calls: `50` / `50`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `tests/test_holoverify_blind_120_live_wrapper.py::test_preflight_does_not_read_120_scoring_map_bytes`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_blind_120_posthoc_2026_07_03.py --run-dir docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T032844Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
