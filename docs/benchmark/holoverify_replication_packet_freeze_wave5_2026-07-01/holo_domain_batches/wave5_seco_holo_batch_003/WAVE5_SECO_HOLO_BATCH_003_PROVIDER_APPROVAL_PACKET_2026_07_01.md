# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_003`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `82203b28715ebde7c3b6b5024038091adae4edf809264b29f684369433f51d97`
Live preflight root signature: `d5fc4b743ab2d80ac29897c86ddc65926625678aaac55e0d4de98c3f5eb39b7a`

## Required Statement

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_003 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 82203b28715ebde7c3b6b5024038091adae4edf809264b29f684369433f51d97 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_003 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
