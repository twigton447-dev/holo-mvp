# HoloVerify V6 Scope Dependency Gate Tiny Patch-Validation Preflight

Date: 2026-07-05

Status: PASS.

This is a no-provider preflight only. It does not run Holo live, solo, judges, or providers.

## Scope

Lane:

`HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_V0`

Purpose:

Patch validation only for the V6 source-field authority/scope gate.

Not allowed:

- Public benchmark evidence
- Global FNR claim
- FP precision evidence
- General model superiority claim

## Selected Packets

| Pair | Sibling | Runtime ID | Purpose |
| :--- | :--- | :--- | :--- |
| `HVSF-FACTORY16-008` | A | `HVSF016HA-B2FBED6E9D535E4F3229` | Matching ALLOW sibling for add-on activation authority. |
| `HVSF-FACTORY16-008` | B | `HVSF016HA-4FD06F71B9FBAD305E84` | Failed Tier 3 ESCALATE fixture: add-on request only had renewal authority. |
| `HVSF-FACTORY16-019` | A | `HVSF016HA-0705182D345B199BF07B` | Matching ALLOW sibling for protocol_start clearance. |
| `HVSF-FACTORY16-019` | B | `HVSF016HA-BCE20453716AA96B9B48` | Failed Tier 3 ESCALATE fixture: protocol_start request only had scheduling clearance. |

## Artifacts

| Artifact | Path | SHA-256 |
| :--- | :--- | :--- |
| Runtime-only manifest | `docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json` | `11281707dff57b5da7ec5c9766a9bb94611b076a5a5badfe7ecd20d3a0aa0f40` |
| Live wrapper | `docs/benchmark/run_holoverify_v6_scope_dependency_gate_tiny_patch_validation_live_2026_07_05.py` | `ce8ee6f73eda81e119561b502606133bbeb262a9a234a205ca4edcf8f3db7f88` |
| Post-hoc scorer | `docs/benchmark/score_holoverify_v6_scope_dependency_gate_tiny_patch_validation_posthoc_2026_07_05.py` | `89dfb58c774fd55d4dcbc440a32cd8b26984538c25dcc361e030b26dfe0e0510` |
| Post-hoc scoring map | `docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/holoverify_v6_scope_dependency_gate_tiny_patch_validation_scoring_map_2026_07_05.json` | `21331ccae3d2d3626b6ce1fb3429d47f9bff5f69dcdb9fddf65a7cec37b90f5e` |
| Hash manifest | `docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/holoverify_v6_scope_dependency_gate_tiny_patch_validation_hash_manifest_2026_07_05.json` | `e4962c6b784506e0afa866bedc84a0fc01b81f6b23e9a0c2359823e1399d4083` |

## Runtime Safety

- V6 selector active: `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`
- Selector hash: `87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2`
- V4 worker contract active: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract hash: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Runtime manifest has no truth, expected verdict, scoring map, answer key, pair ID, sibling, prior-result, or failure-class fields.
- Live wrapper has no `SCORING_MAP` path.
- Post-hoc scoring is separate and may run only after trace freeze.
- No substitutions are enabled.

## Prompt Probe

Generated no-provider prompt probe:

`docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/preflight_20260704T233849Z/preflight_prompt_probe`

Results:

- Observed calls: `20`
- Prompt files: `20`
- Probe files total: `22`
- Prompt leakage hits: `[]`
- Prompt-probe directory hash: `cd6412fe7384fa46a06594f6c3a093313272606e3cf3597f804737b7b3d37664`

## Future Live Shape

If later approved, the live route is:

`W1 -> G1 -> W2 -> G2 -> W3`

Expected future provider calls:

- `W1 xai/grok-3-mini x4`
- `G1 minimax/MiniMax-M2.5-highspeed x4`
- `W2 openai/gpt-5.4-mini x4`
- `G2 minimax/MiniMax-M2.5-highspeed x4`
- `W3 minimax/MiniMax-M2.5-highspeed x4`

Total: `20`

## Exact Future Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 11281707dff57b5da7ec5c9766a9bb94611b076a5a5badfe7ecd20d3a0aa0f40, selector SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05 hash 87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 20 provider calls: W1 xai/grok-3-mini x4, G1 minimax/MiniMax-M2.5-highspeed x4, W2 openai/gpt-5.4-mini x4, G2 minimax/MiniMax-M2.5-highspeed x4, W3 minimax/MiniMax-M2.5-highspeed x4. PATCH VALIDATION ONLY for V6 source-field authority/scope gate across two known Tier 3 failed ESCALATE fixtures plus their matching ALLOW siblings; not public benchmark evidence, not a global FNR claim, and not FP precision evidence. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```
