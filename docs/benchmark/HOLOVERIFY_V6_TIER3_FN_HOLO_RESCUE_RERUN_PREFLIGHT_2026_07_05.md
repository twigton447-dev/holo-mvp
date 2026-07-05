# HoloVerify V6 Tier 3 FN Holo Rescue Rerun Preflight

Label: `HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_V0`

Status: PASS

Scope: Mechanical same-set rerun of the failed V5 Tier 3 FN Holo rescue lane under V6. Internal patch-validation / selected-lane repair evidence only. Not public benchmark evidence, not a global FNR claim, not FP precision evidence, and not general model superiority.

Canonical preflight folder: `docs/benchmark/holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05/live_runs/preflight_20260705T022511Z`
Current HEAD: `b6dcc03e84ffb09b52d0ebb1b437e48fc86dc407`

## Runtime Binding

- Runtime-only manifest: `docs/benchmark/HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- Runtime manifest SHA-256: `05ce391eff4f495d91f3cb8187185166a6e218903280b747e1a59ac6991ca0da`
- Post-hoc scoring map SHA-256: `90c73ec8b683c074f2ebcdb6ce054bb222e584371420a47e49963f99b8eb5928`
- Selector: `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`
- Selector hash: `87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract hash: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`

## Geometry

- Packets: `14`
- Route: `W1 -> G1 -> W2 -> G2 -> W3`
- Expected future provider calls: `70`
- Provider calls during preflight/package build: `0`

## Preflight Checks

- `content_contract_attempt_budget`: `True`
- `env_keys_present`: `True`
- `expected_call_count`: `True`
- `judge_calls_disabled`: `True`
- `live_run_attempt_budget`: `True`
- `packet_count`: `True`
- `payloads_present`: `True`
- `posthoc_scoring_script_present`: `True`
- `prompt_probe_leakage`: `True`
- `provider_calls_not_yet_made`: `True`
- `provider_counts`: `True`
- `runtime_consumable`: `True`
- `runtime_input_leakage`: `True`
- `scoring_map_path_absent_from_live_wrapper`: `True`
- `solo_calls_disabled`: `True`
- `source_runtime_manifest_hash`: `True`

## V6 Scope Gate Probe

- `add_on_allow_sibling_passes`: `True`
- `add_on_bad_rejected`: `True`
- `gov_baton_carries_blocker_ledger`: `True`
- `gov_baton_carries_dependency_ledger`: `True`
- `protocol_allow_sibling_passes`: `True`
- `protocol_bad_rejected`: `True`
- `selector_blocks_unresolved_scope_blocker`: `True`

Known failed B-side fixtures covered by deterministic V6 probe:

- `HVSF-FACTORY16-008-B`: `authority_scope_add_on_activation`
- `HVSF-FACTORY16-019-B`: `authority_scope_protocol_start`

## Exact Future Approval Sentence

I approve live provider execution for HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 05ce391eff4f495d91f3cb8187185166a6e218903280b747e1a59ac6991ca0da, selector SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05 hash 87c7774d37399d3d786585e1a81dff8eb61f181a0b3e1e86b3f103dd1ab22be2, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 70 provider calls: W1 xai/grok-3-mini x14, G1 minimax/MiniMax-M2.5-highspeed x14, W2 openai/gpt-5.4-mini x14, G2 minimax/MiniMax-M2.5-highspeed x14, W3 minimax/MiniMax-M2.5-highspeed x14. MECHANICAL SAME-SET RERUN of the failed V5 Tier 3 FN Holo rescue lane under V6; internal patch-validation / selected-lane repair evidence only; not public benchmark evidence, not a global FNR claim, not FP precision evidence, and not general model superiority. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
