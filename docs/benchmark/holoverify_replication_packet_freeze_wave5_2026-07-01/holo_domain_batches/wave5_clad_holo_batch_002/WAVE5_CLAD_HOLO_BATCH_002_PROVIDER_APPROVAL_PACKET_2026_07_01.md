# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_CLAD_HOLO_BATCH_002`
Family: `HV-CLAD-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad`
Live preflight root signature: `dc4a047a6366142a8b44e2cb216668e7276a3ea9b3d4be07e17f9d2732a6da70`

## Required Statement

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_002 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_002 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
