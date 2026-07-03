# Fable Blind 120 Live Wrapper Review Handoff

Status: `READY_FOR_READ_ONLY_REVIEW`
Date: 2026-07-03

## Purpose

Review the no-provider 120-packet blind live wrapper before any provider execution.

This is a runtime-firewall review only. It does not approve Holo execution, solo runs, judges, scoring, public claims, or error-rate claims.

## Current Committed Bank

- Freeze package commit: `b225ec7567dcee984541c4184d492e0eefcc287f`
- Freeze root: `63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba`
- Runtime manifest hash: `c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1`
- Scoring map hash: `b5f3c219c473aa2821540aca7cf84e5fc8d2441f977f69d9df226aad550ed166`
- Packets: `120`
- Pairs: `60`
- ALLOW truths: `60`
- ESCALATE truths: `60`

## Files To Review

- `docs/benchmark/run_holoverify_blind_120_live_2026_07_03.py`
- `docs/benchmark/score_holoverify_blind_120_posthoc_2026_07_03.py`
- `docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py`
- `tests/test_holoverify_blind_120_live_wrapper.py`
- `tests/test_holoverify_blind_canary_live_wrapper.py`
- `docs/benchmark/holoverify_blind_120_bank_2026_07_03/holoverify_blind_120_runtime_manifest_2026_07_03.json`
- `docs/benchmark/holoverify_blind_120_bank_2026_07_03/holoverify_blind_120_scoring_map_2026_07_03.json`

## Live Scope The Wrapper Locks

- Lane: `HOLOVERIFY_BLIND_120_RUNTIME_FIREWALL_V0`
- Expected provider calls: `600`
- Packets: `120`
- Call sequence per packet: `W1`, `G1`, `W2`, `G2`, `W3`
- W1: `xai/grok-3-mini`
- G1: `minimax/MiniMax-M2.5-highspeed`
- W2: `openai/gpt-5.4-mini`
- G2: `minimax/MiniMax-M2.5-highspeed`
- W3: `minimax/MiniMax-M2.5-highspeed`
- Solo calls: `0`
- Judge calls: `0`
- No substitutions
- No public claims

## What Changed After Fable Hardening Review

- Created a 120-specific live wrapper that pins the runtime to the committed blind-120 manifest and freeze root.
- Created a separate 120-specific post-hoc scorer with the scoring map path isolated outside the live wrapper.
- Patched the shared preflight helper so disabled solo/judge counts may be represented as either `0` or `null`; this keeps the committed runtime bank unchanged.
- Added no-provider tests proving the wrapper expects 600 calls, rejects wrong approval text, has no scoring map path, and does not read the 120 scoring map during preflight.

## Local Validation

Commands run:

```bash
python3 -m py_compile docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py docs/benchmark/run_holoverify_blind_120_live_2026_07_03.py docs/benchmark/score_holoverify_blind_120_posthoc_2026_07_03.py docs/benchmark/score_holoverify_blind_canary_posthoc_2026_07_03.py holoverify_blind_runner_v0.py
python3 -m pytest tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_blind_canary_live_wrapper.py -q
python3 -m pytest tests/test_blind_lane*.py tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_blind_canary_live_wrapper.py -q
```

Observed results:

- `py_compile`: PASS
- 120/canary wrapper tests: `31 passed`
- Blind suite plus wrapper tests: `50 passed, 12 skipped`
- Provider calls: `0`
- Judge calls: `0`

## Review Questions For Fable

1. Does the 120 live wrapper truly pin to the committed blind-120 runtime manifest and freeze root?
2. Does the live wrapper have any scoring-map path, answer-key path, or truth-reachability path?
3. Does the post-hoc scorer remain separate and trace-hash-bound?
4. Are the approval string, packet count, and 600-call scope sufficiently locked?
5. Are there any remaining ways for the live process to read the scoring map before trace freeze?
6. Is this ready for an explicit provider-approval gate, or should another no-provider patch happen first?

## Allowed Conclusion If Clean

If clean, the only approved conclusion is:

> The 120-packet blind live wrapper has no detected answer-key channel under the current no-provider firewall tests and is ready for explicit provider-approval consideration.

Do not treat this as a Holo result, score result, solo comparison, public benchmark result, or error-rate claim.
