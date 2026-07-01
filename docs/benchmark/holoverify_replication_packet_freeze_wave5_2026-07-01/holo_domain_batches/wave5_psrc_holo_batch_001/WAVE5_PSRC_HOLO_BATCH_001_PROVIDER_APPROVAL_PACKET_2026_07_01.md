# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_001`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `923a2f8c218f1ca503dc74d3d7f896bec100d7bdacec5d317b1f9207a7c2bca8`
Live preflight root signature: `38f38b2a5a54085e4d64837874e7ea19a380487be8f3209178a2e64e71f49478`

## Required Statement

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_001 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 923a2f8c218f1ca503dc74d3d7f896bec100d7bdacec5d317b1f9207a7c2bca8 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_001 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
