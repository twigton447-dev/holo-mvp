# Wave 4 Holo Target Batch 001 Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Approval granted by this packet: `False`
Approval packet SHA-256: `9bee4a37c394c91a2407ddfdf02743df9d685f614a246a599226a767e95003ed`

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

## Command After Explicit Approval

```bash
python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave4 --batch-number 1 --run-live --approval-packet-sha256 9bee4a37c394c91a2407ddfdf02743df9d685f614a246a599226a767e95003ed --approval-statement "I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without explicit approval.
- Do not run solo or judges.
- Do not edit frozen packets or prompts.
- No fallback or model substitution.
