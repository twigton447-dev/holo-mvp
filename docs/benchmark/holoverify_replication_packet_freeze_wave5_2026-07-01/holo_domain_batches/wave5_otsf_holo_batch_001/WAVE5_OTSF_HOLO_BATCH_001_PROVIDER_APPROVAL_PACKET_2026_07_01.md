# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_OTSF_HOLO_BATCH_001`
Family: `HV-OTSF-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `61e0230f017a3d117391a1fde7788f4f1f6d79f35fc585ecd74f4a1892ece97e`
Live preflight root signature: `73f49b9ed98cb0d6a1a195e97ebd46511927f6b8a81b1f3b51634f3c02f663e9`

## Required Statement

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 61e0230f017a3d117391a1fde7788f4f1f6d79f35fc585ecd74f4a1892ece97e --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
