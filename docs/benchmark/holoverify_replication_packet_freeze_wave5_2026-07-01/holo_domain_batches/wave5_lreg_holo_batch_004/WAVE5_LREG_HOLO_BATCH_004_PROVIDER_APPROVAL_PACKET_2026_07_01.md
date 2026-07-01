# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_LREG_HOLO_BATCH_004`
Family: `HV-LREG-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `845c2bebc264f34e5a417b4c3eb49f054a9ab3f272009901cea6cd6e7e1c2d4a`
Live preflight root signature: `f27c96c2c79bebb0392a40b21a2577ca63295592923e27ae4aec5440117b096d`

## Required Statement

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_004 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 845c2bebc264f34e5a417b4c3eb49f054a9ab3f272009901cea6cd6e7e1c2d4a --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_004 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
