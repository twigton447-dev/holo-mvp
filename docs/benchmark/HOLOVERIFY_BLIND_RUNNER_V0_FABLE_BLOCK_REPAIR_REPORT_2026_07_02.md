# HoloVerify Blind Runner V0 Fable Block Repair Report

Status: SUPERSEDED_BY_SECOND_BLOCK_REPAIR

Date: 2026-07-02

Provider calls: `0`

Judge calls: `0`

Fable returned `BLOCK_CANARY`. Codex patched the no-provider blind runner
package before any live canary.

## Repair Summary

| Finding | Status | Repair |
| --- | --- | --- |
| F1 seed freedom / reseed loop | repaired | Seed now derives from the frozen bank hash. No author seed. No redraw loop. |
| F2 five synthetic prompt files | repaired | Prompt fixtures now cover all 20 canary packets, producing 100 prompt files. |
| F3 circular T1 detector validation | repaired | T1 now includes a synthetic dirty prompt detector-validation test. |
| F4 unfailable skew check | repaired | T5 now uses a one-sided exact binomial upper-tail check. |
| F5 runtime/scoring map leak | repaired | Runtime manifest and payloads are split from post-hoc scoring map. |
| F6 unpaired canary | repaired | Canary now samples 10 sibling pairs and includes both sides. |
| F7 decorative contradiction-free | repaired | `contradiction_free` now reflects blind structural gate failures. |
| F8 max token ceiling unchecked | repaired | Runner budget is 1024 and T6 checks `max_output_tokens`. |
| F9 last-artifact tie-break | repaired | Selector tie-break prefers earliest turn. |
| F10 entry-module-only AST scan | not fully closed | Runner imports remain small; import-closure scan should still be added before final live approval. |

## Supersession Note

This first block repair report was superseded after Fable's second
`BLOCK_CANARY` review. Use
`HOLOVERIFY_BLIND_RUNNER_V0_FABLE_SECOND_BLOCK_REPAIR_REPORT_2026_07_02.md`
for current status.

## Historical Local Result At This Stage

```text
25 passed, 0 skipped, 0 failed
```

## Independent Checks

- Prompt files scanned: `100`
- Suffix-channel hits: `0`
- Deterministic truth-token hits: `0`
- Runner static truth-reachability findings: `[]`
- Canary pairs: `10`
- Canary packets: `20`
- Sample first-turn rate: `0.9`
- Bank first-turn rate: `0.9043887147335423`
- One-sided binomial p-value: `0.7018792921880527`
- Skew violation: `false`

## Remaining Boundary

This remains no-provider. It is ready for Fable rereview, not live execution.
Live canary still requires explicit approval after rereview.
