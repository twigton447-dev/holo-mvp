# Wave 3 Holo Target Batch 001 Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Approval granted by this packet: `False`
Approval packet SHA-256: `bd47046366f176eb2796fd3dbb661b5c2d36af76e60b3304bfaa7a00328ee426`

## Required Statement

`I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Expected Calls If Approved

- `gov_calls`: `48`
- `judge_calls`: `0`
- `packets`: `24`
- `pairs`: `12`
- `solo_calls`: `0`
- `total_provider_calls`: `120`
- `worker_calls`: `72`

## Command After Explicit Approval

```bash
python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave3 --batch-number 1 --run-live --approval-packet-sha256 bd47046366f176eb2796fd3dbb661b5c2d36af76e60b3304bfaa7a00328ee426 --approval-statement "I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without explicit approval.
- Do not run solo or judges.
- Do not edit frozen packets or prompts.
- No fallback or model substitution.
