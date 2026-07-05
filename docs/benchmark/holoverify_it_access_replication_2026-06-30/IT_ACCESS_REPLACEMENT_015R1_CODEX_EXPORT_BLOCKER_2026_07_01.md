# IT Access Replacement 015R1 Codex Export Blocker

Created: 2026-07-01

## Classification

`IT_ACCESS_REPLACEMENT_015R1_CODEX_EXPORT_BLOCKED_AFTER_READINESS_PASS`

This is not a Holo result, not a benchmark verdict failure, and not a provider readiness failure.

## What Passed Inside Codex

- Replacement pair: `HV-ITAC-REP-015R1`
- Replacement freeze root: `6c61024da5f6c36c1ee5210b95efd1d7a1ed0caff60a11efe0ace1ca1e72dc4e`
- Replacement preflight: `PASS`
- MiniMax harmless health check: `PASS`
- MiniMax harmless worker-contract smoke: `PASS`

Fresh readiness evidence:

- `docs/benchmark/holoverify_it_access_replication_2026-06-30/minimax_health_checks/health_20260701T012546Z`
- `docs/benchmark/holoverify_it_access_replication_2026-06-30/minimax_worker_contract_smokes/smoke_20260701T012600Z`

Both readiness checks used harmless non-benchmark prompts only.

## What Was Blocked

The targeted replacement batch was not started inside Codex because it would export frozen benchmark packet/prompt content to external providers from this environment.

Blocked command intent:

```bash
python3 -B docs/benchmark/run_it_access_openai_w2_holo_batched_family_2026_06_30.py \
  --run-batch \
  --batch replacement_015r1 \
  --require-minimax-health \
  --require-minimax-worker-smoke
```

## Benchmark Effect

- Targeted replacement Holo batch started: `false`
- Replacement packet provider calls: `0`
- Solo calls: `0`
- Judge calls: `0`
- Benchmark content sent by Codex for replacement batch: `false`

## Required Next Move

Run the targeted replacement batch only from an authorized local shell/environment, not from Codex, using the external execution handoff.

Do not treat this blocker as evidence for or against HoloVerify quality.
