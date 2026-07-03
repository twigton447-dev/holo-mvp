# HoloVerify Solo Failure Factory Rescue Hardening Patch

Date: 2026-07-03  
Scope: no-provider hardening after `run_20260703T210421Z` autopsy.  
Provider calls: 0  
Judge calls: 0  
Solo calls: 0  
Live Holo calls: 0

## Why This Patch Exists

The 13-pair Solo Failure Factory Holo rescue run completed cleanly but scored only 19/26 packets and 7/13 pairs.

The autopsy found three concrete failure modes:

1. Correct W1 answers were disqualified by `short_final_answer`.
2. Wrong W2 answers won tie-breaks after W1 was disqualified.
3. All workers missed stale senior authorization on high-risk relationship packets.

This patch hardens the runner against those exact failure modes without touching frozen packets, packet truths, scoring maps, raw outputs, or live traces.

## Patch Summary

### 1. New selector policy

Old:

`SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`

New:

`SELECTOR_V3_DEPENDENCY_AWARE_REPAIR_2026_07_03`

Selector hash:

`2ccc65cd993c93e18297937026d59b6c335a4dc9503e7dbe4b0d76b2d948cdd5`

Worker contract unchanged:

`WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03`

Worker contract hash:

`d5fdea3133f2bcdea0a9c16f1261081a8fe5ca8264f2a2f0a7e43d41c69a0320`

### 2. Short final answers are warnings, not sole disqualifiers

`short_final_answer` no longer fails an otherwise complete artifact. It is recorded under `warnings`.

This is important because the failed run had concise but correct W1 outputs that were excluded from selector consensus.

### 3. Dependency-aware deterministic gate

The gate now computes source-derived checks for:

- refund remaining balance,
- refund tolerance variance,
- local-to-UTC change-window conversion,
- high-risk senior authorization inside the 12-month review cycle.

These checks use only model-visible source records. They do not read packet truth, sibling labels, scoring maps, or legacy answer keys.

### 4. Gov dependency ledger

The Gov baton now carries a source-derived `dependency_ledger` into later worker prompts.

When a deterministic mismatch exists, the baton says:

- repair target: resolve dependency mismatch,
- blocked move: do not collapse separate required controls into general approval,
- ledger: the computed source-derived dependency check.

### 5. Selector fail-closed behavior

If no artifact is structurally valid after deterministic checks, the selector returns:

`selected_artifact_id = null`

with:

`selector_blocked_reason = no_structurally_valid_artifact`

This prevents the system from blessing an unsafe ALLOW when every worker contradicts a deterministic source-boundary check.

## No-Provider Replay Against Frozen Run

The patched gate/selector was replayed locally against the already-frozen raw outputs from:

`docs/benchmark/holoverify_solo_failure_factory_holo_rescue_2026_07_03/live_runs/run_20260703T210421Z`

Original scored result:

- 19/26 packets correct
- 7/13 pairs fully correct
- 7 packet misses

Patched replay result:

- 23/26 packets correct
- 3 packets fail closed with `NO_FINAL_ARTIFACT`
- 0 unsafe selected ALLOWs on stale high-risk authorization packets

Fixed by replay:

| Pair | Sibling | Old final | Patched replay | Reason |
|---|---:|---:|---:|---|
| `HVSF-FACTORY-009` | B | ALLOW | ESCALATE | Refund remaining balance check + W1/W3 corroboration. |
| `HVSF-FACTORY-010` | A | ESCALATE | ALLOW | Time-window check + W1/W3 corroboration. |
| `HVSF-FACTORY-010` | B | ALLOW | ESCALATE | Time-window check + W1/W3 corroboration. |
| `HVSF-FACTORY2-005` | B | ALLOW | ESCALATE | Tolerance delta check + W1/W3 corroboration. |

Fail-closed after replay:

| Pair | Sibling | Old final | Patched replay | Reason |
|---|---:|---:|---:|---|
| `HVSF-FACTORY3-008` | B | ALLOW | NO_FINAL_ARTIFACT | All workers contradicted stale senior authorization check. |
| `HVSF-FACTORY4-008` | B | ALLOW | NO_FINAL_ARTIFACT | All workers contradicted stale senior authorization check. |
| `HVSF-FACTORY4-010` | B | ALLOW | NO_FINAL_ARTIFACT | All workers contradicted stale senior authorization check. |

## Tests

No-provider validation passed:

- `py_compile` for patched runner and wrappers
- `tests/test_holoverify_blind_selector_repair_regression.py`
- `tests/test_holoverify_blind_canary_live_wrapper.py`
- `tests/test_holoverify_blind_120_live_wrapper.py`
- `tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py`

Result:

`50 passed`

## Claim Boundary

Allowed internal claim:

The V3 no-provider patch fixes four of the seven prior wrong packet outcomes when replayed against frozen raw outputs, and converts the three unanimous stale-authorization false ALLOWs into fail-closed no-final-artifact outcomes.

Not allowed:

- public benchmark claim,
- new error-rate denominator,
- claim that Holo solved the 13-pair rescue set,
- claim that V3 is validated by live providers,
- claim that deterministic gates prove general superiority.

## Next Valid Move

If Taylor approves, the next live step should be a **patch-validation-only rerun** of the same 13-pair rescue set under:

`SELECTOR_V3_DEPENDENCY_AWARE_REPAIR_2026_07_03`

This would test whether the dependency ledger changes live worker behavior on the three stale-authorization seams, not just posthoc selector replay.

