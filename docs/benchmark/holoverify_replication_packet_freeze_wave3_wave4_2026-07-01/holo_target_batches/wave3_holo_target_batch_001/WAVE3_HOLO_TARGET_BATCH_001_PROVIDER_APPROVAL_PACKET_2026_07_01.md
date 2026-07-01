# Wave 3 Holo Target Batch 001 Provider Approval Packet

Status: `PENDING_RUNTIME_LIVE_PREFLIGHT_REFRESH`
Approval granted by this packet: `False`
Approval packet SHA-256: `1b9888d431324dc8e22d6b1dc4feab33a34fffaaae88eaebd565a5b1a43a1ca8`
Live preflight root signature: `PENDING_RUNTIME_PREFLIGHT`

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

## Runtime Refresh Required

Run the no-provider live preflight first. It will refresh this approval packet with the current live-preflight root and a new SHA-256.

## Template Command After Runtime Refresh

```bash
python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave3 --batch-number 1 --run-live --approval-packet-sha256 1b9888d431324dc8e22d6b1dc4feab33a34fffaaae88eaebd565a5b1a43a1ca8 --approval-statement "I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without explicit approval.
- Do not use this template packet directly for live execution.
- Run the no-provider live preflight immediately before live execution to bind the approval packet to the current preflight root.
- Do not run solo or judges.
- Do not edit frozen packets or prompts.
- No fallback or model substitution.
