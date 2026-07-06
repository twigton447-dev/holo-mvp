# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `True`
- Observed provider calls: `50` / `50`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:wave1_fp_overblock_holo_rescue_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_posthoc_2026_07_05.py --run-dir docs/benchmark/holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05/live_runs/run_20260705T232606Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
