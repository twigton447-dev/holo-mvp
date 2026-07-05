# HoloVerify Blind 120 Solo One-Shot Live Summary

- Runtime passed: `False`
- Observed provider calls: `51` / `120`
- Trace frozen before scoring: `True`
- Failure: `{"attempt": 1, "error": "<urlopen error [Errno 8] nodename nor servname provided, or not known>", "error_type": "URLError", "model": "MiniMax-M2.5-highspeed", "provider": "minimax", "retryable": false, "transport_retry_failures": []}`
- Post-hoc scoring command: `python3 -B docs/benchmark/score_holoverify_solo_failure_factory_batch011_kit_abc_solo_scout_2026_07_03.py --run-dir docs/benchmark/holoverify_solo_failure_factory_batch011_kit_abc_solo_scout_runs_2026_07_03/run_20260703T235608Z`

This is a solo baseline trace only until the separate post-hoc scorer loads the hidden scoring map.
