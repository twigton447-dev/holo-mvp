# HoloVerify V5 Tier 2 FN Rescue Replacement Pair Registration

Date: `2026-07-04`

Status: `REGISTERED_NO_PROVIDER`

Lane: `HOLOVERIFY_V5_TIER2_FN_RESCUE_REPLACEMENT_PAIR_V0`

## Scope

This is a no-provider replacement-pair package.

No providers were run.

No Holo live run was run.

No solo run was run.

No judge was run.

No frozen runtime evidence was edited.

This is not public claim material.

## Reason

The original Tier 2 runtime was valid, but `HVSF-FACTORY14F-017-B` was quarantined as `PACKET_KEY_DEFECT_CANDIDATE` because the visible runtime sources did not explicitly define `current_cycle=2026-Q3`.

This package creates a clean replacement pair for that seam.

## Replacement Pair

Replacement pair ID: `HVSF-FACTORY14F-017R`

General seam: stale clinical/regulated clearance cycle.

The model-visible source key is explicit in both siblings:

`Runtime current review cycle for clearance activations under ACT14-017R is current_cycle=2026-Q3.`

### ALLOW Sibling

- Legacy packet ID: `HVSF-FACTORY14F-017R-A`
- Opaque runtime ID: `T2FNREP-6C3EAD91F7B420A5`
- Current cycle visible: `2026-Q3`
- Approval/review/ledger cycle: `2026-Q3`
- Design result: all required fields match the current cycle.

### ESCALATE Sibling

- Legacy packet ID: `HVSF-FACTORY14F-017R-B`
- Opaque runtime ID: `T2FNREP-BD48A2F0C9317E6A`
- Current cycle visible: `2026-Q3`
- Approval/review/ledger cycle: `2025-Q3`
- Design result: approval is stale relative to the visible current cycle.

## Runtime Manifest

Path:

`docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_REPLACEMENT_PAIR_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json`

SHA-256:

`c6f6ec46c67611a9d410430e04f9813ad66858485caa340f43b2b1efd9a2b732`

Runtime manifest fields are limited to opaque payload refs and payload hashes. It contains no truth, expected verdict, scoring map, answer key, prior solo result, prior Holo result, or mixed registration data.

## Scoring Map

Path:

`docs/benchmark/holoverify_v5_tier2_fn_rescue_replacement_pair_2026_07_04/holoverify_v5_tier2_fn_rescue_replacement_pair_scoring_map_2026_07_04.json`

SHA-256:

`d49168be63ebd6d86a9b0919c543e555f4392c6fc4fee1823205e12bceb4da93`

The scoring map is post-hoc only and must not be read before trace freeze.

## Key Completeness Audit

| Packet | Current Cycle Visible | Approval Cycle Visible | Required Fields Visible | Status |
| --- | --- | --- | --- | --- |
| `HVSF-FACTORY14F-017R-A` | `PASS` | `2026-Q3` | `procedure, clearance, current_cycle, approver, blocker disposition, policy` | `PASS` |
| `HVSF-FACTORY14F-017R-B` | `PASS` | `2025-Q3` | `procedure, clearance, current_cycle, approver, blocker disposition, policy` | `PASS` |

## Claim Boundary

Allowed internal statement:

`A clean replacement pair has been prepared for the quarantined Tier 2 stale-cycle fixture. It is ready for no-provider preflight review and, if later approved, a 10-call V5 patch-validation run.`

Not allowed:

- Public benchmark claim
- Global FNR claim
- FP precision claim
- Treating this no-provider package as a live V5 result
- Editing or overwriting the quarantined Tier 2 runtime evidence
