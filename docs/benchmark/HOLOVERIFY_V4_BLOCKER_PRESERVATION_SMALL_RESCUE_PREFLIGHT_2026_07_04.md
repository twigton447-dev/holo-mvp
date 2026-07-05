# HoloVerify V4 Blocker Preservation Small Rescue Preflight

Date: 2026-07-04

Status: `PREFLIGHT_PASS_NO_PROVIDER`

Lane: `HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_PATCH_VALIDATION_V0`

Branch: `codex/ap-publication-integration`

Architecture HEAD: `d41ec047a7cf378065c3d32d849d405e489421b5`

## Scope

This preflight checks whether a small V4 patch-validation rerun is ready.

It does not run providers.

It does not run Holo live.

It does not run solo.

It does not run judges.

It does not create public benchmark claims.

## Selected Packet Set

The lane selects five Batch016 ESCALATE-truth B siblings where the prior Holo rescue finalized `ALLOW` even though at least one worker found an `ESCALATE` blocker.

Selected packets:

- `HVSF-FACTORY16-001-B` / `SFF16HA-8EEA87DF0B8C19DA1FC3`
- `HVSF-FACTORY16-004-B` / `SFF16HA-3FD8B906B07BBAC1604F`
- `HVSF-FACTORY16-008-B` / `SFF16HA-EB6D4A8ED66E020111B3`
- `HVSF-FACTORY16-010-B` / `SFF16HA-EAAD2AFD82C919B7ECCB`
- `HVSF-FACTORY16-020-B` / `SFF16HA-B1376D9F72BE680784D1`

Runtime manifest hash:

`4f8ec7a398b4b98be98695882ee90554884b2ffd939c6af2a1db41efc2553f60`

Runtime-only manifest path:

`docs/benchmark/HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json`

Exact live wrapper path:

`docs/benchmark/run_holoverify_v4_blocker_preservation_small_rescue_live_2026_07_04.py`

Exact live command:

```bash
python3 docs/benchmark/run_holoverify_v4_blocker_preservation_small_rescue_live_2026_07_04.py --run-live --approval-statement "$APPROVAL"
```

Wrapper preflight artifact:

`docs/benchmark/holoverify_v4_blocker_preservation_small_rescue_2026_07_04/live_runs/preflight_20260704T045851Z/v4_blocker_preservation_small_rescue_live_preflight.json`

The wrapper preflight passed with `provider_calls_not_yet_made=true`, `registration_json_live_input=false`, `runtime_input_leakage_hits=[]`, and `prompt_probe_leakage_hits=[]`.

## Preflight Checks

| Check | Status | Evidence |
| :--- | :--- | :--- |
| V4 selector active | `PASS` | `SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04` |
| V3 worker contract active | `PASS` | `WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04` |
| Worker prompts include active blocker ledger | `PASS` | Prompt probe contains `ACTIVE BLOCKER LEDGER`. |
| Worker required fields include blocker resolution | `PASS` | Prompt probe requires `blocker_resolution=...`. |
| Gov baton can carry blocker ledger | `PASS` | Probe baton includes `blocker_ledger` with `ART-001-BLK-PREFLIGHT`. |
| Selector criteria include blocker fields | `PASS` | `blocker_resolution_clean`, `blocker_resolution_complete`, `source_boundary_open_with_blocker`. |
| Runtime-only manifest schema | `PASS` | Top level has only `classification`, `packet_count`, `runtime_consumable`, `packets`; packet rows have only opaque ID, payload ref, payload hash. |
| Live command uses runtime-only manifest | `PASS` | Wrapper path points to the separate runtime-only manifest, not registration JSON. |
| No scoring map before trace freeze | `PASS` | Future live input must use only the separate runtime-only manifest. |
| No providers called | `PASS` | `0` provider calls. |
| No Holo live run | `PASS` | `0` live Holo calls. |
| No solo called | `PASS` | `0` solo calls. |
| No judges called | `PASS` | `0` judge calls. |
| No substitutions | `PASS` | Opaque IDs and payload hashes match the Batch016 rescue hash manifest. |

## Prompt Probe

The W3 prompt surface includes:

```text
ACTIVE BLOCKER LEDGER
blocker_resolution=<empty if no prior blockers or ESCALATE; if ALLOW after blockers, list each blocker_id closed plus source IDs>
If ACTIVE BLOCKER LEDGER is non-empty and you return ALLOW, blocker_resolution must name every blocker_id and source IDs that close it.
```

## Gov Baton Probe

The no-provider baton probe produced:

```json
{
  "route_verdict": "CONTINUE",
  "repair_target": "stress-test and preserve blocker ids: ART-001-BLK-PREFLIGHT",
  "blocked_move": "do not override blocker with consensus unless sources close it",
  "dependency_ledger": [],
  "blocker_ledger": [
    {
      "blocker_id": "ART-001-BLK-PREFLIGHT",
      "blocker_text": "preflight source-boundary blocker"
    }
  ]
}
```

## Expected Calls If Approved Later

Expected provider calls: `25`

- `W1 xai/grok-3-mini x5`
- `G1 minimax/MiniMax-M2.5-highspeed x5`
- `W2 openai/gpt-5.4-mini x5`
- `G2 minimax/MiniMax-M2.5-highspeed x5`
- `W3 minimax/MiniMax-M2.5-highspeed x5`

## Exact Approval Sentence

`I approve live provider execution for HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_PATCH_VALIDATION_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json with SHA-256 4f8ec7a398b4b98be98695882ee90554884b2ffd939c6af2a1db41efc2553f60, selector SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04 hash 3ed2a01eb16a8ea84bd096e6c1cfd352e6b0f8f9eb7565a5327680f77fa7affe, worker contract WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04 hash 00b692a07b1036f70b0756e16458e811c7aee3afb62c1351893a4722aab9ad5a, and exactly 25 provider calls: W1 xai/grok-3-mini x5, G1 minimax/MiniMax-M2.5-highspeed x5, W2 openai/gpt-5.4-mini x5, G2 minimax/MiniMax-M2.5-highspeed x5, W3 minimax/MiniMax-M2.5-highspeed x5. PATCH VALIDATION ONLY for V4 blocker preservation on five Batch016 blocker-drop misses; not benchmark evidence and not public claim material. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.`

## Stop Rule

Stop here unless Taylor explicitly approves the live patch-validation rerun using the exact approval sentence above.
