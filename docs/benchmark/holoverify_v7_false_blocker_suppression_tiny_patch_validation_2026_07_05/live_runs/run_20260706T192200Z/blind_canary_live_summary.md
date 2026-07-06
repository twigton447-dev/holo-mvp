# HoloVerify Blind Canary Live Summary

- Runtime firewall passed: `False`
- Observed provider calls: `30` / `30`
- Provider failures: `0`
- Trace frozen: `True`
- Live wrapper has scoring-map path: `False`
- Scoring-map read guard: `manual_no_provider_preflight:v7_false_blocker_suppression_tiny_patch_validation_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_v7_false_blocker_suppression_tiny_patch_validation_posthoc_2026_07_05.py --run-dir docs/benchmark/holoverify_v7_false_blocker_suppression_tiny_patch_validation_2026_07_05/live_runs/run_20260706T192200Z`
- Failure: `None`

This run is a blind runtime-firewall trace only until the separate post-hoc scoring script is run. It is not an error-rate claim.
