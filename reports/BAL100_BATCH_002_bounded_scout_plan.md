# BAL100 Batch 002 Bounded Scout Plan

Date: `2026-06-18`
Batch: `BAL100-BATCH-002`
Seam: explained anomaly
Status: `bounded_scout_plan_prepared_gated_live_support_with_targeted_post_repair_rescout`

This is a plan plus gated runner support only. It did not run scout, live calls, Judge, QA, ablation, freeze, trace creation, HBB runner work, proof-credit changes, or push.

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

No generic scout runner was found. This lane now uses a bounded Batch 002 scout runner:

`benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py`

Default behavior remains no-live prompt-card planning. Live provider execution is available only behind explicit Taylor approval gates, exact 12-packet scope validation, and output-directory nonexistence checks.

## Targeted Post-Repair Rescout Mode

After the targeted repair commit `0d64f6f`, the runner also supports a narrower fail-closed mode for the repaired families only:

- `BAL100-BEC-EXPLAINED-ANOMALY-012`
- `BAL100-BEC-EXPLAINED-ANOMALY-013`
- `BAL100-BEC-EXPLAINED-ANOMALY-017`

Targeted packet scope:

| Family | Packet | Hypothesis |
|---|---|---|
| `BAL100-BEC-EXPLAINED-ANOMALY-012` | `BAL100-BEC-EXPLAINED-ANOMALY-012-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-012` | `BAL100-BEC-EXPLAINED-ANOMALY-012-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-013` | `BAL100-BEC-EXPLAINED-ANOMALY-013-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-013` | `BAL100-BEC-EXPLAINED-ANOMALY-013-B` | ESCALATE |
| `BAL100-BEC-EXPLAINED-ANOMALY-017` | `BAL100-BEC-EXPLAINED-ANOMALY-017-A` | ALLOW |
| `BAL100-BEC-EXPLAINED-ANOMALY-017` | `BAL100-BEC-EXPLAINED-ANOMALY-017-B` | ESCALATE |

Expected targeted row count: 6 packets x 5 providers = 30 rows.

Fail-closed exclusions for targeted mode:

- `BAL100-BEC-EXPLAINED-ANOMALY-011`
- `BAL100-BEC-EXPLAINED-ANOMALY-014`
- `BAL100-BEC-EXPLAINED-ANOMALY-015`
- `BAL100-BEC-EXPLAINED-ANOMALY-016`
- `BAL100-BEC-EXPLAINED-ANOMALY-018`

Targeted no-live dry-run command:

```bash
python3 -B benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py --targeted-post-repair-rescout --out-dir scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout
```

Targeted Taylor provider-transmission command:

```bash
BAL100_BATCH002_SCOUT_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION python3 -B benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py --targeted-post-repair-rescout --execute-provider-calls --operator Taylor --i-am-taylor-local --yes-send-draft-payloads-to-providers --timeout 90 --out-dir scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout
```

Targeted Codex/Co auditable provider-transmission command, if explicitly approved:

```bash
BAL100_BATCH002_SCOUT_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION BAL100_BATCH002_CODEX_SCOUT_APPROVED=I_APPROVE_CODEX_PROVIDER_TRANSMISSION python3 -B benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py --targeted-post-repair-rescout --execute-provider-calls --operator Taylor --allow-codex-provider-calls --yes-send-draft-payloads-to-providers --timeout 90 --out-dir scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout
```

Expected targeted output directory:

`scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout`

Expected targeted live outputs, if later approved:

- `scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout/results.jsonl`
- `scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout/summary.json`
- `scout_runs/BAL100-BATCH-002_targeted_post_repair_rescout/prompt_cards/`

The targeted mode remains scout/diagnostic-only: `benchmark_credit=false`, no official traces, no Judge, no QA/ablation, no freeze, no automatic prefreeze marking, and no scorecard or manifest proof-credit changes.

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

```bash
BAL100_BATCH002_SCOUT_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION python3 -B benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py --execute-provider-calls --operator Taylor --i-am-taylor-local --yes-send-draft-payloads-to-providers --timeout 90 --out-dir scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors
```

Codex/Co auditable provider-transmission command, if explicitly approved:

```bash
BAL100_BATCH002_SCOUT_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION BAL100_BATCH002_CODEX_SCOUT_APPROVED=I_APPROVE_CODEX_PROVIDER_TRANSMISSION python3 -B benchmark_factory/batches/run_BAL100_BATCH_002_bounded_scout.py --execute-provider-calls --operator Taylor --allow-codex-provider-calls --yes-send-draft-payloads-to-providers --timeout 90 --out-dir scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors
```

Expected live outputs, if later approved:

- `scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors/results.jsonl`
- `scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors/summary.json`
- `scout_runs/BAL100-BATCH-002_bounded_static_gate_survivors/prompt_cards/`

The live path is scout/diagnostic-only: `benchmark_credit=false`, no official traces, no Judge, no QA/ablation, no freeze, and no scorecard or manifest proof-credit changes.

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
- Stop if `--execute-provider-calls` is used without `BAL100_BATCH002_SCOUT_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION`.
- Stop in Codex/Co if `--allow-codex-provider-calls` and `BAL100_BATCH002_CODEX_SCOUT_APPROVED=I_APPROVE_CODEX_PROVIDER_TRANSMISSION` are not both present.
- Stop if the live output directory already exists.
- Stop if any future run attempts Judge, QA, ablation, freeze, trace creation, HBB rerun work, or proof-credit changes.

## Proof Credit

Proof-credit remains unchanged:

- Ready families: `BEC-PAIR-009`, `BEC-PAIR-010`
- Ready count: 2 pair families / 4 packets
- Batch 002 has no benchmark credit from this plan.
