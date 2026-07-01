# Wave 2 Holo Target Batch 002 - Solo vs Holo Comparison

Status: COMPLETE

This memo compares the completed Wave 2 Holo target batch 002 against the already-frozen one-shot solo triage evidence. No providers or judges were run to create this comparison; it is derived from disk artifacts only.

## Bottom Line

Holo solved 18/18 selected packets and 9/9 sibling pairs in Batch 002. The same selected packets had 36/54 one-shot solo attempts fail the strict KNEW/admissible standard.

Batch 002 extends the Wave 2 signal beyond the first hot seam pocket: these were the next highest-priority remaining solo-collapse targets after Batch 001, and Holo again cleared the full governed loop.

## Scope

- Batch: `WAVE2_HOLO_TARGET_BATCH_002`
- Holo run: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_002/live_runs/run_20260701T045827Z`
- Selected pairs: 9
- Selected packets: 18
- Selection source: `WAVE2_HOLO_TARGET_BATCH_002_REGISTRATION_2026_07_01.json`
- Judges: 0
- New provider calls for this comparison: 0

## Metrics

| Metric | Value |
|---|---:|
| Solo attempts on selected packets | 54 |
| Solo KNEW/admissible | 18 |
| Solo not KNEW | 36 |
| Solo wrong verdict | 9 |
| Solo parse fail | 9 |
| Solo structural/evidence fail | 18 |
| Holo final packets correct/admissible | 18/18 |
| Holo valid sibling pairs | 9/9 |
| Holo provider calls | 90/90 |
| Holo worker calls | 54 |
| Holo Gov calls | 36 |
| Holo provider failures | 0 |
| Holo total tokens | 206630 |
| Selected solo total tokens | 67120 |
| Holo / selected solo token ratio | 3.078516x |
| Gov share of Holo tokens | 0.104278 |

## Pair Results

| Pair | Domain | Target bucket | Solo not KNEW | Holo target | Holo guardrail | Evidence class |
|---|---|---|---:|---|---|---|
| `HV-FINC-REP-011` | Finance close / revenue / expense recognition controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-DPRV-REP-012` | Data privacy / customer data release controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-DPRV-REP-013` | Data privacy / customer data release controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-DPRV-REP-019` | Data privacy / customer data release controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-012` | Finance close / revenue / expense recognition controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-015` | Finance close / revenue / expense recognition controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-019` | Finance close / revenue / expense recognition controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-HRWF-REP-017` | HR / payroll / workforce controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-HRWF-REP-020` | HR / payroll / workforce controls | hard_escalate | 4/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |

## Intra-Holo Correction Evidence

Holo had 5 non-final worker misses inside the governed loop, and the final selected artifacts still ended correct/admissible.

| Turn | Packet | Model | Local verdict | Final status |
|---|---|---|---|---|
| `HV-DPRV-REP-012-A_W1` | `HV-DPRV-REP-012-A` | xai/grok-3-mini | ESCALATE | ALLOW / admissible=True |
| `HV-FINC-REP-012-A_W1` | `HV-FINC-REP-012-A` | xai/grok-3-mini | ESCALATE | ALLOW / admissible=True |
| `HV-FINC-REP-015-A_W1` | `HV-FINC-REP-015-A` | xai/grok-3-mini | ESCALATE | ALLOW / admissible=True |
| `HV-FINC-REP-019-A_W1` | `HV-FINC-REP-019-A` | xai/grok-3-mini | ESCALATE | ALLOW / admissible=True |
| `HV-HRWF-REP-017-A_W1` | `HV-HRWF-REP-017-A` | xai/grok-3-mini | ESCALATE | ALLOW / admissible=True |

## Token Accounting

- Holo tokens: 160123 input / 33084 output / 206630 total
- Holo worker tokens: 185083
- Holo Gov tokens: 21547
- Selected solo tokens: 29616 input / 26612 output / 67120 total
- Holo vs selected solo token ratio: 3.078516x

## Claim Boundaries

- This is a targeted Holo batch selected from prior frozen solo triage, not a full Wave 2 family run.
- Solo evidence is one-shot strict KNEW/admissible triage over the same frozen packets and same mini-model families.
- Not KNEW includes wrong verdicts, parse failures, and structural/evidence/action-boundary failures.
- No judge calls were used for this comparison.
- This supports action-boundary architecture evidence on selected seams; it is not a universal model-superiority claim.

## References

- Holo live results: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_002/live_runs/run_20260701T045827Z/live_results.json`
- Holo trace: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_002/live_runs/run_20260701T045827Z/TRACE_CALLS.jsonl`
- No-leakage audit: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_002/live_runs/run_20260701T045827Z/WAVE2_HOLO_TARGET_BATCH_002_NO_LEAKAGE_AUDIT.json`
- Comparison JSON: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_002/WAVE2_HOLO_TARGET_BATCH_002_SOLO_VS_HOLO_COMPARISON_2026_07_01.json`
