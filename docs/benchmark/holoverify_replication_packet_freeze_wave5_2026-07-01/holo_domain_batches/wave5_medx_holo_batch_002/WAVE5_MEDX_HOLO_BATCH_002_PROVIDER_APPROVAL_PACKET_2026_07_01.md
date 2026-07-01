# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_MEDX_HOLO_BATCH_002`
Family: `HV-MEDX-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `83b68cbc2c3775ed28d78e4de0045768d17ef9ab3d8de8a6f92cdb295329e0b1`
Live preflight root signature: `bc3b93bb3c1b2f8485b38d06170775834dee3b1c6d7ccd3a091daed6d6220bfb`

## Required Statement

`I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_002 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 83b68cbc2c3775ed28d78e4de0045768d17ef9ab3d8de8a6f92cdb295329e0b1 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_002 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
