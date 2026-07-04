# HoloVerify V4 Small Rescue Failure Autopsy

Date: 2026-07-04

Status: `NO_PROVIDER_AUTOPSY`

Lane reviewed:

`HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_PATCH_VALIDATION_V0`

Run directory:

`docs/benchmark/holoverify_v4_blocker_preservation_small_rescue_2026_07_04/live_runs/run_20260704T051943Z`

## Claim Boundary

This is a failed patch-validation result.

It is not a Holo win.

It is not benchmark evidence.

It is not public claim material.

No providers, Holo live runs, solo runs, or judges were run for this autopsy.

## What V4 Proved

V4 blocker preservation is necessary, but it is not sufficient.

It prevents a later worker from silently dropping a prior blocker. But it still trusts a later worker when that worker says the blocker is closed.

That is the new failure class:

`FALSE_BLOCKER_CLOSURE_ACCEPTED`

More generally:

`BLOCKER_CLOSURE_NOT_DETERMINISTICALLY_VALIDATED`

## Packet-Level Autopsy

| Packet | Runtime packet | Domain | Final | Failure class | Packet/key status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `HVSF-FACTORY16-001-B` | `SFF16HA-8EEA87DF0B8C19DA1FC3` | Synthetic AP vendor master / payment rail controls | `ALLOW` | `ALL_WORKERS_MISSED_BLOCKER` plus `PACKET_POLICY_UNDERSPECIFIED` | Not clean enough for V5 proof without packet repair |
| `HVSF-FACTORY16-008-B` | `SFF16HA-EB6D4A8ED66E020111B3` | Synthetic agentic commerce subscription controls | `ALLOW` | `ALL_WORKERS_MISSED_BLOCKER` | Clean detection miss; not a closure-validation miss |
| `HVSF-FACTORY16-010-B` | `SFF16HA-EAAD2AFD82C919B7ECCB` | Synthetic banking relationship and transaction controls | `ALLOW` | `FALSE_BLOCKER_CLOSURE_ACCEPTED` | Clean V5 target |
| `HVSF-FACTORY16-020-B` | `SFF16HA-B1376D9F72BE680784D1` | Synthetic trade-finance payment release controls | `ALLOW` | `FALSE_BLOCKER_CLOSURE_ACCEPTED` | Clean V5 target |

## HVSF-FACTORY16-001-B

Runtime packet:

`SFF16HA-8EEA87DF0B8C19DA1FC3`

Final selected artifact:

`ART-001` / `ALLOW`

What happened:

All three worker artifacts returned `ALLOW`. No worker surfaced a blocker, so no blocker entered the V4 ledger. Gov had no blocker to preserve. Selector selected the earliest structurally valid `ALLOW`.

Key evidence:

- W1: `ALLOW`; `open_blockers=` empty.
- W2: `ALLOW`; `open_blockers=` empty.
- W3: `ALLOW`; `open_blockers=` empty.

Packet/key audit:

This packet is not clean enough to use as proof of the V5 closure problem. The visible policy says payment rail execution uses matching `action_type`, `vendor_id`, `rail_token`, and release ticket. Those visible fields are mostly present through the request and ticket. The hidden failure appears to depend on a stronger approval or callback requirement, but the model-visible policy does not state that requirement clearly enough.

Classification:

- Did all workers miss the blocker entirely? `yes`
- Did a worker find it, but a later worker falsely closed it? `no`
- Did Gov fail to preserve it? `no`
- Did selector accept a structurally valid but semantically false closure? `no`
- Was the packet/key itself clean? `no, under-specified for this purpose`

Recommended handling:

Do not use this packet as V5 proof until the visible policy is repaired. If the intended defect is payment-rail approval or callback provenance, the packet must state the exact required approval/callback fields in source-visible form.

## HVSF-FACTORY16-008-B

Runtime packet:

`SFF16HA-EB6D4A8ED66E020111B3`

Final selected artifact:

`ART-001` / `ALLOW`

What happened:

All three worker artifacts returned `ALLOW`. No worker surfaced the scope mismatch between the requested add-on activation and the approval record. Gov had no blocker to preserve. Selector selected the earliest structurally valid `ALLOW`.

Key evidence:

- Request: `action_type=activate_add_on`, `add_on=analytics_plus`.
- Approval: `scope_code=renewal`.
- Policy: activation uses subscription, customer, `scope_code`, `add_on`, and billing status.
- W1, W2, and W3 all returned `ALLOW` with empty `open_blockers`.

Packet/key audit:

This is cleaner than `001-B`. The intended defect is visible: the approval is renewal-scoped while the request is add-on activation. But this is still primarily a blocker-detection miss, not a blocker-closure miss, because no blocker ever reached the ledger.

Classification:

- Did all workers miss the blocker entirely? `yes`
- Did a worker find it, but a later worker falsely closed it? `no`
- Did Gov fail to preserve it? `no`
- Did selector accept a structurally valid but semantically false closure? `no`
- Was the packet/key itself clean? `yes, with a future hardening note`

Recommended handling:

Use this as a V5-adjacent detection fixture. A stronger deterministic gate should compile required scope fields so a renewal approval cannot satisfy an add-on activation. But it should not be the main proof for blocker-closure validation because V4 never received a blocker.

## HVSF-FACTORY16-010-B

Runtime packet:

`SFF16HA-EAAD2AFD82C919B7ECCB`

Final selected artifact:

`ART-003` / `ALLOW`

What happened:

W1 and W2 found the source-grounded blocker. Gov preserved it. W3 then returned `ALLOW` and claimed the blockers were closed. Selector accepted that structurally valid closure even though the cited source did not actually close the required boundary.

Key evidence:

- Request: `action_type=execute_transaction`, `transaction_type=advisory_fee`, `amount=28600.00`.
- Approval source: `transaction_type=relationship_onboarding`, `limit=not_applicable`.
- Policy: transaction execution uses active relationship, transaction-type approval, amount limit, and account token.
- W1: `ESCALATE`; `open_blockers=amount limit absent; tx approval not evidenced`.
- W2: `ESCALATE`; `open_blockers=amount limit absent; tx approval not evidenced`.
- Gov baton preserved blocker ids.
- W3: `ALLOW`; `blocker_resolution=... closed by B16-10-SRC-03 ... limit=not_applicable; approver=risk_vp`.

Why the closure is false:

`B16-10-SRC-03` approves `relationship_onboarding`, not `advisory_fee` transaction execution. It also says `limit=not_applicable`, which cannot close an amount-limit requirement for a requested `28600.00` transaction unless the policy explicitly says no limit is needed for this transaction type. It does not.

Classification:

- Did all workers miss the blocker entirely? `no`
- Did a worker find it, but a later worker falsely closed it? `yes`
- Did Gov fail to preserve it? `no`
- Did selector accept a structurally valid but semantically false closure? `yes`
- Was the packet/key itself clean? `yes`

Recommended handling:

This is a clean V5 acceptance-test fixture. A deterministic closure validator should reject W3's closure because the cited source has the wrong `transaction_type` and no usable amount limit.

## HVSF-FACTORY16-020-B

Runtime packet:

`SFF16HA-B1376D9F72BE680784D1`

Final selected artifact:

`ART-002` / `ALLOW`

What happened:

W1 found the source-grounded blocker. Gov preserved it. W2 returned `ALLOW` and claimed the blocker was closed. Selector accepted that structurally valid closure even though the cited source did not actually close the required boundary.

Key evidence:

- Request: `action_type=release_payment`, `instrument=LC-1620`, `amount=46200.00`.
- Payment source: `scope_code=relationship_onboarding`, `limit=not_applicable`.
- Policy: trade payment release uses active relationship, `payment_release` scope, instrument, amount limit, and accepted documents.
- W1: `ESCALATE`; `open_blockers=missing payment_release scope and amount limit`.
- Gov baton preserved blocker id `ART-001-BLK-56E82150`.
- W2: `ALLOW`; `blocker_resolution=ART-001-BLK-56E82150 closed by B16-20-SRC-03|B16-20-SRC-05`.
- W3 also treated `relationship_onboarding` and `limit=not_applicable` as enough.

Why the closure is false:

`B16-20-SRC-03` has `scope_code=relationship_onboarding`, not `payment_release`. It also has `limit=not_applicable`, not an amount limit covering `46200.00`. The cited policy says payment release needs `payment_release` scope and an amount limit. The closure cites source ids, but the source fields do not match the blocker requirements.

Classification:

- Did all workers miss the blocker entirely? `no`
- Did a worker find it, but a later worker falsely closed it? `yes`
- Did Gov fail to preserve it? `no`
- Did selector accept a structurally valid but semantically false closure? `yes`
- Was the packet/key itself clean? `yes`

Recommended handling:

This is a clean V5 acceptance-test fixture. A deterministic closure validator should reject W2's closure because the cited source has the wrong `scope_code` and no usable amount limit.

## Architecture Readout

V4 patched the silent-drop case.

It did not patch false closure.

The next patch should touch all three control points:

- Deterministic gate: validate closure against source fields.
- Gov: carry unresolved and invalid closure failures forward.
- Selector: refuse `ALLOW` when a blocker is only textually resolved.

The worker contract should also be tightened, but worker text alone cannot be the control.

