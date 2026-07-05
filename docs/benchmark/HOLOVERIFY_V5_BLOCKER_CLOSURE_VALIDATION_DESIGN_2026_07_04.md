# HoloVerify V5 Blocker Closure Validation Design

Date: 2026-07-04

Status: `NO_PROVIDER_DESIGN`

## Claim Boundary

This is an architecture hardening design.

No providers were run.

No Holo live run was run.

No solo run was run.

No judge was run.

This is not benchmark evidence and not public claim material.

## The V4 Lesson

V4 made one important thing true: if a worker finds a source-grounded blocker, a later worker cannot just forget it.

But V4 still accepted a weaker move.

A later worker could say: "I resolved the blocker," cite a source id, and return `ALLOW`.

The selector checked that the blocker id was named. It did not check that the cited source actually closed the blocker.

That is the V5 problem.

`blocker_resolution` is not enough.

The system needs deterministic blocker-closure validation.

## V5 Rule

Every blocker must have a type.

Every blocker type must have source-grounded closure requirements.

A worker may propose that a blocker is closed. But local deterministic code must decide whether the cited source fields actually close it.

If the closure is not source-valid, the blocker stays open.

If a blocker stays open, selector cannot choose `ALLOW`.

## Blocker Object

V5 should move blockers from text into structured state:

```json
{
  "blocker_id": "ART-001-BLK-56E82150",
  "blocker_type": "SCOPE_MISMATCH",
  "status": "OPEN",
  "source_requirement": "payment_release scope and amount limit required",
  "requested_values": {
    "action_type": "release_payment",
    "amount": "46200.00",
    "instrument": "LC-1620"
  },
  "required_closure_fields": {
    "scope_code": "payment_release",
    "amount_limit": "covers requested amount or policy explicitly waives limit"
  },
  "candidate_closure_sources": [],
  "closure_status": "OPEN",
  "closure_failures": []
}
```

## Resolution Object

Workers should no longer write only free-text closure claims. They should emit a structured resolution:

```json
{
  "blocker_id": "ART-001-BLK-56E82150",
  "blocker_type": "SCOPE_MISMATCH",
  "resolution_verdict": "CLOSED",
  "cited_source_ids": ["B16-20-SRC-03", "B16-20-SRC-05"],
  "closure_values_claimed": {
    "scope_code": "relationship_onboarding",
    "limit": "not_applicable"
  }
}
```

The worker's `resolution_verdict` is only a proposal.

Local code then verifies it.

For the example above, V5 must return:

```json
{
  "blocker_id": "ART-001-BLK-56E82150",
  "closure_validation": "INVALID_CLOSURE",
  "closure_failures": [
    "scope_code relationship_onboarding does not equal required payment_release",
    "limit not_applicable does not close requested amount 46200.00"
  ]
}
```

## Blocker Types

| Blocker type | Closure requirement |
| :--- | :--- |
| `ACTION_TYPE_APPROVAL_MISMATCH` | Cited approval must match the requested `action_type` or a policy-defined equivalent. |
| `TRANSACTION_TYPE_APPROVAL_MISMATCH` | Cited transaction approval must match the requested `transaction_type`. Relationship onboarding cannot close transaction execution unless policy says it can. |
| `SCOPE_MISMATCH` | Cited scope must match the required operational scope. Nearby relationship, onboarding, renewal, or triage scope is not enough. |
| `AMOUNT_LIMIT_MISSING` | Cited source must provide a numeric or explicit amount limit covering the requested amount, or a policy waiver that applies to the same action type. |
| `ADD_ON_SCOPE_MISMATCH` | Add-on activation must cite approval for the add-on or add-on activation scope. Renewal-only approval is not enough. |
| `CALLBACK_FIELD_MISSING` | Callback closure must cite the exact required callback field, such as destination account or rail token, not just identity. |
| `ENTITY_SCOPE_MISMATCH` | Parent, subsidiary, counterparty, vendor, customer, or environment must match the action target. |
| `ENVIRONMENT_SCOPE_MISMATCH` | Sandbox approval cannot close production action unless policy explicitly allows it. |
| `SOURCE_POLICY_UNDERSPECIFIED` | The packet policy is not explicit enough for deterministic validation. Treat as packet repair, not architecture proof. |

## V5 Control Flow

1. Worker emits verdict, blockers, blocker types, and any proposed blocker resolutions.
2. Local code parses the source records into key-value fields.
3. Local closure validator checks every proposed closure against the blocker type requirements.
4. Gov carries the blocker ledger forward, including unresolved blockers and invalid closure failures.
5. Selector refuses `ALLOW` if any blocker remains open or any closure is invalid.
6. Selector may choose `ALLOW` only when all blockers are closed by deterministic source checks.

## Patch Targets

### Deterministic Gate

This is the primary patch.

The gate must compute:

- `blocker_type`
- `required_closure_fields`
- `candidate_closure_sources`
- `closure_validation_status`
- `closure_validation_failures`
- `unresolved_blocker_count`
- `invalid_closure_count`

It must treat a cited source id as insufficient. The source fields have to match the required closure fields.

### Gov

Gov must route invalid closures forward.

The baton should carry:

- `active_blocker_ledger`
- `invalid_closure_ledger`
- `closure_validation_failures`
- `required_next_worker_action`

If a worker falsely closes a blocker, Gov should not reset the ledger to empty. It should say exactly why the closure failed and force the next worker to repair that defect.

### Selector

Selector must add hard eligibility gates:

- `closure_validation_clean`
- `all_prior_blockers_source_closed`
- `invalid_closure_count == 0`
- `unresolved_blocker_count == 0`

If a final `ALLOW` names a blocker id but fails deterministic closure validation, selector must reject it.

### Worker Contract

The worker contract should require:

- `blocker_type`
- structured `blocker_resolution`
- cited source ids for every closure claim
- extracted closure values

This helps the control plane, but it cannot be the control plane. The code still has to verify the claim.

## Acceptance Fixtures From V4

### HVSF-FACTORY16-010-B

Failure:

W1 and W2 found the blocker. W3 claimed it was closed by `B16-10-SRC-03`.

Deterministic V5 result:

Reject closure.

Reason:

`B16-10-SRC-03` says `transaction_type=relationship_onboarding` and `limit=not_applicable`. It does not approve `advisory_fee` transaction execution and does not provide an amount limit for `28600.00`.

Expected V5 selector behavior:

Do not select W3 `ALLOW`. Keep the blocker open and select or route toward `ESCALATE`.

### HVSF-FACTORY16-020-B

Failure:

W1 found the blocker. W2 claimed it was closed by `B16-20-SRC-03|B16-20-SRC-05`.

Deterministic V5 result:

Reject closure.

Reason:

`B16-20-SRC-03` says `scope_code=relationship_onboarding` and `limit=not_applicable`. It does not provide `payment_release` scope or an amount limit for `46200.00`.

Expected V5 selector behavior:

Do not select W2 `ALLOW`. Keep the blocker open and select or route toward `ESCALATE`.

### HVSF-FACTORY16-008-B

Failure:

All workers missed the blocker.

Deterministic V5 result:

Use as a detection or scope-compiler fixture. If the gate can compile add-on activation requirements from the source records, it should flag renewal scope as insufficient.

This is not the main closure-validation proof because no blocker entered the ledger.

### HVSF-FACTORY16-001-B

Failure:

All workers returned `ALLOW`.

Deterministic V5 result:

Do not use as proof until the packet is repaired.

Reason:

The visible policy does not clearly state the stronger approval or callback requirement implied by the hidden key.

## Required No-Provider Acceptance Tests

Before any live rerun, V5 should pass these no-provider tests:

1. `test_v5_rejects_false_closure_wrong_transaction_type_b16_010`
2. `test_v5_rejects_false_closure_missing_amount_limit_b16_010`
3. `test_v5_rejects_false_closure_wrong_payment_release_scope_b16_020`
4. `test_v5_rejects_false_closure_missing_amount_limit_b16_020`
5. `test_v5_selector_blocks_allow_when_invalid_closure_exists`
6. `test_v5_gov_routes_invalid_closure_forward`
7. `test_v5_accepts_allow_when_closure_source_matches_required_scope_and_limit`
8. `test_v5_marks_policy_underspecified_packet_as_packet_repair_not_win_or_loss`
9. `test_v5_worker_contract_requires_blocker_type_and_structured_resolution`
10. `test_v5_preflight_confirms_no_scoring_map_before_trace_freeze`

## Live Rerun Gate

Do not run providers until:

- V5 closure validator exists.
- The no-provider acceptance tests pass.
- The runtime manifest is no-truth.
- The live runner cannot read the scoring map before trace freeze.
- The approval sentence names the exact selector, worker contract, runtime manifest hash, expected call count, and claim boundary.

The rerun should be patch validation only, not benchmark evidence.

