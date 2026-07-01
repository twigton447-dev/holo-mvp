# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_TRES_HOLO_BATCH_002`
Family: `HV-TRES-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `453f3d3a322b9a0a340c2e093e9274b12ad0eb373814ac7561abae2313db563e`
Live preflight root signature: `b6e838eb2450ad60fea73c568bc6cba1d60254c386fcff97d3cf71a3a26d9d73`

## Required Statement

`I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_002 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Expected Calls If Approved

- `pairs`: `5`
- `packets`: `10`
- `worker_calls`: `30`
- `gov_calls`: `20`
- `total_provider_calls`: `50`
- `judge_calls`: `0`
- `solo_calls`: `0`

## Command After Explicit Approval

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 453f3d3a322b9a0a340c2e093e9274b12ad0eb373814ac7561abae2313db563e --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_002 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
