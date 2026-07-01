# Wave 4 Holo Target Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Approval granted by this packet: `False`
Approval packet SHA-256: `72a30cdb008d1ecac29433ee9bc1bf823beeaeaf23d1b091595375a8d43b736c`
Live preflight root signature: `808e579bb56984877ce884a7ee1bec8297b37fdb66d7b2aadfe17aacd50a96cf`

## Required Statement

`I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Expected Calls If Approved

- `pairs`: `15`
- `packets`: `30`
- `worker_calls`: `90`
- `gov_calls`: `60`
- `total_provider_calls`: `150`
- `judge_calls`: `0`
- `solo_calls`: `0`

## Command After Explicit Approval

```bash
python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave4 --batch-number 1 --run-live --approval-packet-sha256 72a30cdb008d1ecac29433ee9bc1bf823beeaeaf23d1b091595375a8d43b736c --approval-statement "I explicitly approve provider calls for WAVE4_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE4_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without explicit approval.
- Use this approval packet only for the current checkout state and current live-preflight root.
- Do not rerun solo or judges.
- Do not edit frozen packets or prompts.
- No fallback or model substitution.
