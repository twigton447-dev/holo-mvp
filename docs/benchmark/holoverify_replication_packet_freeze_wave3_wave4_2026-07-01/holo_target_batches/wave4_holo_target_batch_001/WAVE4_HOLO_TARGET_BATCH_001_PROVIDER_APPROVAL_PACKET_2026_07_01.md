# Wave 4 Holo Target Batch 001 Provider Approval Packet

Status: `PENDING_RUNTIME_LIVE_PREFLIGHT_REFRESH`
Approval granted by this packet: `False`
Approval packet SHA-256: `1e5920dcbc427774b83002b7e7d0f518171fb25f7ea161de4e529cc76197aa5a`
Live preflight root signature: `PENDING_RUNTIME_PREFLIGHT`

## Required Statement

`I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Expected Calls If Approved

- `gov_calls`: `60`
- `judge_calls`: `0`
- `packets`: `30`
- `pairs`: `15`
- `solo_calls`: `0`
- `total_provider_calls`: `150`
- `worker_calls`: `90`

## Runtime Refresh Required

Run the no-provider live preflight first. It will refresh this approval packet with the current live-preflight root and a new SHA-256.

## Template Command After Runtime Refresh

```bash
python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave4 --batch-number 1 --run-live --approval-packet-sha256 1e5920dcbc427774b83002b7e7d0f518171fb25f7ea161de4e529cc76197aa5a --approval-statement "I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without explicit approval.
- Do not use this template packet directly for live execution.
- Run the no-provider live preflight immediately before live execution to bind the approval packet to the current preflight root.
- Do not run solo or judges.
- Do not edit frozen packets or prompts.
- No fallback or model substitution.
