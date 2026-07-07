# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `True`
- Observed provider calls: `50` / `50`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:300dot_v7_fp_overblock_balanced_5pair_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_posthoc_2026_07_06.py --run-dir docs/benchmark/holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06/live_runs/run_20260707T012456Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
