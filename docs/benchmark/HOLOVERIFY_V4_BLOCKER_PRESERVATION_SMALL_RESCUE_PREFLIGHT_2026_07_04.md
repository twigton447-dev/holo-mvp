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

`5dbc251615490d9c94ec136c594b0ea1024a759d2918f8e8f8a5e42be34a433e`

## Preflight Checks

| Check | Status | Evidence |
| :--- | :--- | :--- |
| V4 selector active | `PASS` | `SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04` |
| V3 worker contract active | `PASS` | `WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04` |
| Worker prompts include active blocker ledger | `PASS` | Prompt probe contains `ACTIVE BLOCKER LEDGER`. |
| Worker required fields include blocker resolution | `PASS` | Prompt probe requires `blocker_resolution=...`. |
| Gov baton can carry blocker ledger | `PASS` | Probe baton includes `blocker_ledger` with `ART-001-BLK-PREFLIGHT`. |
| Selector criteria include blocker fields | `PASS` | `blocker_resolution_clean`, `blocker_resolution_complete`, `source_boundary_open_with_blocker`. |
| No scoring map before trace freeze | `PASS` | Future live input must use only `runtime_manifest_no_truth`. |
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

`I approve live provider execution for HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_PATCH_VALIDATION_V0 using only the five opaque Batch016 runtime payloads registered in docs/benchmark/HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_REGISTRATION_2026_07_04.json with runtime_manifest_no_truth_sha256 5dbc251615490d9c94ec136c594b0ea1024a759d2918f8e8f8a5e42be34a433e, current selector SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04, current worker contract WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04, and exactly 25 provider calls: W1 xai/grok-3-mini x5, G1 minimax/MiniMax-M2.5-highspeed x5, W2 openai/gpt-5.4-mini x5, G2 minimax/MiniMax-M2.5-highspeed x5, W3 minimax/MiniMax-M2.5-highspeed x5. No solo, no judges, no scoring map before trace freeze, no substitutions, no public claims.`

## Stop Rule

Stop here unless Taylor explicitly approves the live patch-validation rerun using the exact approval sentence above.
