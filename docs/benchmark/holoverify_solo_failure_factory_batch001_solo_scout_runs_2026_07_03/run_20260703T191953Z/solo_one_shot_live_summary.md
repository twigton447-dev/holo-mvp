# HoloVerify Blind 120 Solo One-Shot Live Summary

- Runtime passed: `False`
- Observed provider calls: `19` / `60`
- Trace frozen before scoring: `True`
- Failure: `{"attempt": 1, "error": "The read operation timed out", "error_type": "timeout", "model": "grok-3-mini", "provider": "xai", "retryable": false, "transport_retry_failures": []}`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_solo_failure_factory_batch001_solo_scout_2026_07_03.py --run-dir docs/benchmark/holoverify_solo_failure_factory_batch001_solo_scout_runs_2026_07_03/run_20260703T191953Z`

This is a solo baseline trace only until the separate post-hoc scorer loads the hidden scoring map.
