# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `False`
- Observed provider calls: `14` / `50`
- Provider failures: `1`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `tests/test_holoverify_blind_120_live_wrapper.py::test_preflight_does_not_read_120_scoring_map_bytes`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_blind_120_posthoc_2026_07_03.py --run-dir docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T024113Z`
- Failure: `G2_gov_contract_missing:route_verdict,repair_target,blocked_move`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
