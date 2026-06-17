# Balanced 100-Packet Benchmark Factory Plan v0.1

## What Benchmark Are We Building?

A balanced action-boundary benchmark factory: 50 sibling-pair families, each with one defensible `ALLOW` packet and one material-blocker `ESCALATE` packet. The target corpus is 100 evidence-grade packets total.

This is a plan and tracker only. It does not generate packets, freeze packets, create traces, run Judge, or claim proof credit.

## Why 100 Packets?

Rob's criterion is statistically meaningful sample size with half `ALLOW` and half `ESCALATE`. A 100-packet target is large enough to avoid anecdote-driven proof while still small enough to inspect, freeze, trace, judge, and repair rigorously.

Current checkout inventory should not be described as 261 evidence-grade packets. Historical ledger rows remain scout material unless promoted through the current evidence pipeline.

## Why 50 ALLOW / 50 ESCALATE?

A system that always escalates can look strong on risk-catching but fails legitimate business execution. A system that always allows can look efficient but misses blockers. A 50/50 split forces both precision and recall at the action boundary.

## Why Pairwise Sibling Families?

Each family uses the same action boundary and the same artifact structure where possible. The verdict changes because of one material evidence delta, not because the ALLOW and ESCALATE packets are different kinds of cases. This makes the benchmark harder to game and easier to adjudicate.

## Five Seams

| Seam | Domain | Planned Families | Planned Packets |
|---|---|---:|---:|
| BEC callback provenance | BEC | 10 | 20 |
| AP duplicate / true-up / PO authority | AP | 10 | 20 |
| IAM geo-jump / separation-of-duties delegation | IAM | 10 | 20 |
| DFARS source-control provenance | DFARS | 10 | 20 |
| PE consolidation period-scope | PE | 10 | 20 |


Total: 50 pair families, 100 packets, 50 `ALLOW`, 50 `ESCALATE`.

## What Exists Already?

| Family | ALLOW Packet | ESCALATE Packet | Status | Proof Credit |
|---|---|---|---|---|
| BEC-PAIR-001 | `HBB-BEC-001` | `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL` | `regression_protected` | Not ready: needs post-patch rerun |
| BEC-PAIR-002 | `HBB-BEC-002-HARD-ALLOW` | `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` | `regression_protected` | Not ready: needs post-patch rerun |

Both existing pairs are useful working examples of the loop. They are not counted as clean proof wins yet because each had a judged HoloGov loss that was patched and regression-protected after the trace.

## What Still Needs To Be Generated?

- 48 new sibling-pair families.
- 96 new packets.
- 8 additional BEC callback-provenance families to complete the BEC seam.
- 10 AP authority/reconciliation families.
- 10 IAM geo/SOD/delegation families.
- 10 DFARS source-control families.
- 10 PE period-scope families.

## What Should Not Be Counted Yet?

- The 165 historical `benchmark_ledger.csv` rows: scout material only.
- The rough 49 packet-like files in the checkout: mixed status, not all evidence-grade.
- Any HBB-BEC-001 or HBB-BEC-002 result as proof-credit-ready until a post-patch rerun exists.
- Any planned family in this manifest as a generated packet.

## Next Production Batch

`BAL100-BATCH-001`: BEC callback provenance.

- 8 new sibling-pair families.
- 16 packets.
- Completes the BEC seam when combined with HBB-BEC-001 and HBB-BEC-002.
- No packet generation should occur until the family FactGraphs, artifact templates, material deltas, static lint gates, and freeze workflow are ready.

## Evidence Pipeline Gate

Every packet must move through:

`draft -> prefreeze_reviewed -> frozen -> ledgered -> dry_run_passed -> live_traced -> judged -> loss_autopsied when needed -> regression_protected when patched -> proof_credit_ready`

No shortcut converts historical scout material into benchmark credit.

## Manifest Files

- `benchmark_factory/balanced_100_packet_manifest_v0_1.json`
- `reports/balanced_100_packet_factory_plan.json`

## Non-Actions In This Task

No live calls, traces, Judge, QA Attacker, ablation, freeze, packet edits, frozen edits, source-packet edits, or push.
