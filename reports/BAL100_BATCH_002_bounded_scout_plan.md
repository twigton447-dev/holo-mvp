# BAL100 Batch 002 Bounded Scout Plan

Date: `2026-06-18`
Batch: `BAL100-BATCH-002`
Seam: explained anomaly
Status: `bounded_scout_plan_prepared_no_live`

This is a plan and no-live runner support only. It did not run scout, live calls, Judge, QA, ablation, freeze, trace creation, HBB runner work, proof-credit changes, or push.

## Survivor Set

Static gate source: `reports/BAL100_BATCH_002_static_kill_gate.json`

| Classification | Count |
|---|---:|
| `scout_ready` | 6 |
| `repair_before_scout` | 2 |
| `kill_before_scout` | 0 |

Scout only these families:

- `BAL100-BEC-EXPLAINED-ANOMALY-011`
- `BAL100-BEC-EXPLAINED-ANOMALY-012`
- `BAL100-BEC-EXPLAINED-ANOMALY-013`
- `BAL100-BEC-EXPLAINED-ANOMALY-015`
- `BAL100-BEC-EXPLAINED-ANOMALY-017`
- `BAL100-BEC-EXPLAINED-ANOMALY-018`

Exclude:

| Family | Static gate status | Reason |
|---|---|---|
| `BAL100-BEC-EXPLAINED-ANOMALY-014` | `repair_before_scout` | repair wording/source contrast before scout |
| `BAL100-BEC-EXPLAINED-ANOMALY-016` | `repair_before_scout` | repair wording/source contrast before scout |

## Packets

| Family | Packet | Hypothesis |
|---|---|---|
| `BAL100-BEC-EXPLAINED-ANOMALY-011` | `BAL100-BEC-EXPLAINED-ANOMALY-011-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-011` | `BAL100-BEC-EXPLAINED-ANOMALY-011-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-012` | `BAL100-BEC-EXPLAINED-ANOMALY-012-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-012` | `BAL100-BEC-EXPLAINED-ANOMALY-012-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-013` | `BAL100-BEC-EXPLAINED-ANOMALY-013-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-013` | `BAL100-BEC-EXPLAINED-ANOMALY-013-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-015` | `BAL100-BEC-EXPLAINED-ANOMALY-015-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-015` | `BAL100-BEC-EXPLAINED-ANOMALY-015-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-017` | `BAL100-BEC-EXPLAINED-ANOMALY-017-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-017` | `BAL100-BEC-EXPLAINED-ANOMALY-017-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-018` | `BAL100-BEC-EXPLAINED-ANOMALY-018-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-018` | `BAL100-BEC-EXPLAINED-ANOMALY-018-B` | ESCALATE |

Expected row count: 12 packets x 5 providers = 60 rows.

## Runner

Existing Batch 001 scout runner pattern is reusable, but `benchmark_factory/batches/run_BAL100_BATCH_001_five_mini_scout.py` is not directly reusable because it is hardwired to:

- `BAL100-BATCH-001`
- Batch 001 packet glob
- Batch 001 family filters
- Callback-provenance prompt language

No generic scout runner was found. This commit adds a bounded Batch 002 no-live planner:

`benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py`

The new runner only builds no-live prompt cards and a scout plan. It intentionally refuses `--execute-provider-calls`.

## Commands

No-live dry-run command:

```bash
python3 -B benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py --out-dir scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors
```

Expected no-live output directory:

`scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors`

Expected no-live outputs:

- `scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors/scout_plan.json`
- `scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors/prompt_cards/`

Taylor provider-transmission command:

`UNAVAILABLE`

Reason: this task adds only no-live Batch 002 bounded scout support. The new runner has no provider transport code and refuses `--execute-provider-calls`. A future provider-enabled runner change plus explicit Taylor approval would be required before provider transmission.

## Provider Roster

| Provider | Model |
|---|---|
| openai | `gpt-4o-mini` |
| anthropic | `claude-haiku-4-5-20251001` |
| gemini | `gemini-2.5-flash-lite` |
| xai | `grok-3-mini` |
| minimax | `MiniMax-Text-01` |

## Stop Conditions

- Stop if git branch is not `holo-builder-freeze-manifest-gate-001` or git status is not clean before any future live scout.
- Stop if the static-gate survivor set is not exactly families `011`, `012`, `013`, `015`, `017`, and `018`.
- Stop if any `repair_before_scout` family, including `014` or `016`, is selected.
- Stop if expected rows differ from 12 packets x 5 providers = 60.
- Stop if any prompt card exposes `expected_verdict`, `spec_target_verdict`, `_builder`, `_internal`, or answer-key metadata in the model-visible user payload.
- Stop if any future provider-enabled runner lacks an explicit Taylor-local approval gate.
- Stop if any future run attempts Judge, QA, ablation, freeze, trace creation, HBB rerun work, or proof-credit changes.

## Proof Credit

Proof-credit remains unchanged:

- Ready families: `BEC-PAIR-009`, `BEC-PAIR-010`
- Ready count: 2 pair families / 4 packets
- Batch 002 has no benchmark credit from this plan.
