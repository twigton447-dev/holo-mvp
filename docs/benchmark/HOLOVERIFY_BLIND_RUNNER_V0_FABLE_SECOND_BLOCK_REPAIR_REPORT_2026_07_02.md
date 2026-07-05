# HoloVerify Blind Runner V0 Fable Second Block Repair Report

Status: REPAIRED_NO_PROVIDER_READY_FOR_FABLE_THIRD_REVIEW

Date: 2026-07-02

Provider calls: `0`

Judge calls: `0`

Fable returned a second `BLOCK_CANARY`. Codex patched the no-provider package
again before any live calls.

## Repair Summary

| Finding | Status | Repair |
| --- | --- | --- |
| F1 runtime manifest ABAB ordering leak | repaired | Runtime manifest is sorted by opaque runtime ID hash order. T5 now checks truth parity and sibling adjacency. |
| F2 runtime manifest carries bank hash / reconstructable mapping | repaired | Runtime manifest no longer carries bank hash or seed material. Opaque IDs use a private salt stored only in the post-hoc scoring map. |
| F3 bank freedom | repaired | First-turn bank is frozen to `holoverify_blind_canary_bank_2026_07_02.json`; manifest pins its hash and T5 asserts equality. |
| F4 weak scoring-map isolation | partially repaired | Runtime/scoring split tests were added. Import-closure AST scan remains the main residual open item. |

## Current Local Result

```text
28 passed, 0 skipped, 0 failed
```

## Independent Checks

- Prompt files scanned: `100`
- Suffix-channel hits: `0`
- Deterministic truth-token hits: `0`
- Runner static truth-reachability findings: `[]`
- Runtime manifest keys: classification, created_at_utc, judge_calls, packet_count, packets, provider_calls, runtime_consumable, runtime_field_policy
- Frozen bank hash: `a686aaf1eb4bb7e7ec49a82fbae540b8bdb78a3569e4f100bdb15ac6ddb303e7`
- Canary pairs: `10`
- Canary packets: `20`
- Sample first-turn rate: `0.9`
- Bank first-turn rate: `0.9043887147335423`
- One-sided binomial p-value: `0.7018792921880527`
- Skew violation: `false`

## Remaining Boundary

This remains no-provider. It is ready for Fable third review, not live
execution. The import-closure scanner remains the main known residual hardening
item.
