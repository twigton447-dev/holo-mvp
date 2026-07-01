# Wave 2 Holo Target Batch 001 - Solo vs Holo Comparison

Status: COMPLETE

This memo compares the completed Wave 2 Holo target batch against the already-frozen one-shot solo triage evidence. No providers or judges were run to create this comparison; it is derived from disk artifacts only.

## Bottom Line

Holo solved 18/18 selected packets and 9/9 sibling pairs in Batch 001. The same selected packets had 47/54 one-shot solo attempts fail the strict KNEW/admissible standard.

This is the machinery working: Holo did not merely produce a label. It ran the governed 3-DNA loop with deterministic gates, Gov seeing gate results, artifact preservation, final selector, trace accounting, and no-leakage checks.

## Scope

- Batch: `WAVE2_HOLO_TARGET_BATCH_001`
- Holo run: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_001/live_runs/run_20260701T042037Z`
- Selected pairs: 9
- Selected packets: 18
- Selection source: `WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json`
- Judges: 0
- New provider calls for this comparison: 0

## Metrics

| Metric | Value |
|---|---:|
| Solo attempts on selected packets | 54 |
| Solo KNEW/admissible | 7 |
| Solo not KNEW | 47 |
| Solo wrong verdict | 0 |
| Solo parse fail | 10 |
| Solo structural/evidence fail | 37 |
| Holo final packets correct/admissible | 18/18 |
| Holo valid sibling pairs | 9/9 |
| Holo provider calls | 90/90 |
| Holo worker calls | 54 |
| Holo Gov calls | 36 |
| Holo provider failures | 0 |
| Holo total tokens | 207467 |
| Selected solo total tokens | 62670 |
| Holo / selected solo token ratio | 3.310468x |
| Gov share of Holo tokens | 0.101052 |

## Pair Results

| Pair | Domain | Target bucket | Solo not KNEW | Holo target | Holo guardrail | Evidence class |
|---|---|---|---:|---|---|---|
| `HV-FINC-REP-004` | Finance close / revenue / expense recognition controls | hard_allow | 6/6 | ALLOW (PASS) | ESCALATE (PASS) | ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-010` | Finance close / revenue / expense recognition controls | hard_allow | 6/6 | ALLOW (PASS) | ESCALATE (PASS) | ALL_SIX_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-DPRV-REP-009` | Data privacy / customer data release controls | hard_allow | 5/6 | ALLOW (PASS) | ESCALATE (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-HRWF-REP-012` | HR / payroll / workforce controls | hard_escalate | 5/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-HRWF-REP-018` | HR / payroll / workforce controls | hard_escalate | 5/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-003` | Finance close / revenue / expense recognition controls | hard_allow | 5/6 | ALLOW (PASS) | ESCALATE (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-006` | Finance close / revenue / expense recognition controls | hard_allow | 5/6 | ALLOW (PASS) | ESCALATE (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-FINC-REP-013` | Finance close / revenue / expense recognition controls | hard_escalate | 5/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |
| `HV-HRWF-REP-019` | HR / payroll / workforce controls | hard_escalate | 5/6 | ESCALATE (PASS) | ALLOW (PASS) | STRONG_SOLO_COLLAPSE_HOLO_PAIR_SOLVED |

## Intra-Holo Correction Evidence

Holo had 1 non-final worker miss inside the governed loop, and the final selected artifact still ended correct/admissible.

| Turn | Packet | Model | Local verdict | Final status |
|---|---|---|---|---|
| `HV-FINC-REP-013-A_W1` | `HV-FINC-REP-013-A` | xai/grok-3-mini | ESCALATE | ALLOW / admissible=True |

## Token Accounting

- Holo tokens: 162552 input / 32815 output / 207467 total
- Holo worker tokens: 186502
- Holo Gov tokens: 20965
- Selected solo tokens: 29794 input / 23834 output / 62670 total
- Holo vs selected solo token ratio: 3.310468x

## Claim Boundaries

- This is a targeted Holo batch selected from prior frozen solo triage, not a full Wave 2 family run.
- Solo evidence is one-shot strict KNEW/admissible triage over the same frozen packets and same mini-model families.
- Not KNEW includes wrong verdicts, parse failures, and structural/evidence/action-boundary failures.
- No judge calls were used for this comparison.
- This supports action-boundary architecture evidence on selected seams; it is not a universal model-superiority claim.

## References

- Holo live results: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_001/live_runs/run_20260701T042037Z/live_results.json`
- Holo trace: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_001/live_runs/run_20260701T042037Z/TRACE_CALLS.jsonl`
- No-leakage audit: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_001/live_runs/run_20260701T042037Z/WAVE2_HOLO_TARGET_BATCH_001_NO_LEAKAGE_AUDIT.json`
- Comparison JSON: `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_001/WAVE2_HOLO_TARGET_BATCH_001_SOLO_VS_HOLO_COMPARISON_2026_07_01.json`
