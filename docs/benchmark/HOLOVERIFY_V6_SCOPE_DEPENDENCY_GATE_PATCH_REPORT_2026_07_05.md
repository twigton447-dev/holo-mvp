# HoloVerify V6 Scope Dependency Gate Patch Report

Date: 2026-07-05

Status: no-provider patch implemented.

## Scope

This patch addresses the Tier 3 FN Holo rescue misses documented in:

- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_FAILURE_AUTOPSY_2026_07_05.json`

The failure class was `V5_SCOPE_DEPENDENCY_NON_DETECTION`: the packets contained visible source-field scope mismatches, but no worker emitted the blocker, so V5 blocker-closure validation never activated.

## Target Fixtures

| Packet | Deterministic defect | V6 result |
| :--- | :--- | :--- |
| `HVSF-FACTORY16-008-B` / `HVSF016HA-4FD06F71B9FBAD305E84` | `action_type=activate_add_on`, but `APP` authority has `scope_code=renewal` and no matching `add_on=analytics_plus`. | Deterministic dependency check requires `ESCALATE`. |
| `HVSF-FACTORY16-019-B` / `HVSF016HA-BCE20453716AA96B9B48` | `action_type=protocol_start`, but `CLR` authority has `scope_code=scheduling`; policy requires `scope_code=protocol_start`. | Deterministic dependency check requires `ESCALATE`. |

## Implementation

Changed `holoverify_blind_runner_v0.py`:

- Bumped selector identity to `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`.
- Added deterministic source-field authority/scope dependency checks.
- Added `authority_scope_add_on_activation`.
- Added `authority_scope_protocol_start`.
- Reused the existing V5 gate path:
  - deterministic mismatch fails the worker gate;
  - deterministic dependency blockers are emitted into the blocker ledger;
  - dependency ledger and blocker ledger are carried into the Gov baton;
  - selector treats the artifact as not deterministic-clean and cannot select it as a final `ALLOW`.

The worker contract remains:

- `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`

## Acceptance Tests Added

New file:

- `tests/test_holoverify_v6_scope_dependency_gate.py`

Tests added:

- `test_v6_rejects_add_on_activation_when_authority_scope_is_renewal_and_add_on_field_missing_b16_008`
- `test_v6_rejects_protocol_start_when_clearance_scope_is_scheduling_b16_019`
- `test_v6_allows_matching_add_on_activation_sibling`
- `test_v6_allows_matching_protocol_start_sibling`
- `test_v6_dependency_ledger_emitted_for_source_visible_scope_mismatch`
- `test_v6_gov_baton_carries_deterministic_scope_blocker`
- `test_v6_selector_blocks_allow_with_unresolved_deterministic_scope_blocker`
- `test_v6_no_packet_prompt_or_failed_evidence_mutation`

Existing selector-version assertions were updated to the V6 selector identity.

## Validation

Commands run:

```bash
python3 -m py_compile holoverify_blind_runner_v0.py
python3 -m pytest -q tests/test_holoverify_v6_scope_dependency_gate.py tests/test_holoverify_blind_selector_repair_regression.py tests/test_holoverify_v5_blocker_closure_validation.py
python3 -m pytest -q tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py
```

Results:

- `py_compile`: PASS
- Focused no-provider pytest: PASS, `33 passed`
- No-provider wrapper selector-identity regression pytest: PASS, `37 passed`
- Providers called: no
- Holo live run: no
- Solo run: no
- Judges called: no

## Evidence Preservation

The old failed Tier 3 run remains preserved. No frozen runtime evidence, prompt files, raw provider outputs, traces, or packet payloads were edited.

Preserved hashes checked:

| File | SHA-256 |
| :--- | :--- |
| `TRACE_CALLS.jsonl` | `eb1247c8e7bd3861b7d01a612911fcedfe71766b5b848eeddbac818d5b09c64d` |
| `TRACE_PROVIDER_CALLS.jsonl` | `c68d0393776083a9afdd813a356cefbc7b9f4857ff5608cf048fa3e5e01a41ce` |
| `blind_canary_runtime_results.json` | `0d930d414153fbcbec1bf9d28133d71ee1cd1a369bc03efc147131d2f650d213` |
| `raw_provider_outputs/006_W1.json` | `359448a8cbd17806d2b378f224f154aabb84ce3529edfbcaa154382411c9c4fc` |
| `raw_provider_outputs/016_W1.json` | `b5b254b9a65d32740d0fcf9221828789c5e0d59c4f728603f5e6bdae4ea6ac5e` |

## Readiness

V6 is ready for a tiny no-provider preflight package.

Recommended next validation lane:

- Patch-validation only.
- Use the two known failed ESCALATE fixtures and their two matching ALLOW siblings.
- Full HoloGov route if later approved.
- No public benchmark claim.
- No provider execution until a separate exact approval sentence is issued.
