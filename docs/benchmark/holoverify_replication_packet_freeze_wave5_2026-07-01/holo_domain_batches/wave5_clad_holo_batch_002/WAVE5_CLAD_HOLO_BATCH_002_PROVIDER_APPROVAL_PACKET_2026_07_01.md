# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_CLAD_HOLO_BATCH_002`
Family: `HV-CLAD-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `eb988b7c83cad89ca3d709e3ca8d0e19b1a238164e8be73e9c60e3d2fc184b54`
Live preflight root signature: `43620c517234c86892c8ba53c01dda46bc2917f9254979e7ffd5bd939890b9aa`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 eb988b7c83cad89ca3d709e3ca8d0e19b1a238164e8be73e9c60e3d2fc184b54 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_002 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
