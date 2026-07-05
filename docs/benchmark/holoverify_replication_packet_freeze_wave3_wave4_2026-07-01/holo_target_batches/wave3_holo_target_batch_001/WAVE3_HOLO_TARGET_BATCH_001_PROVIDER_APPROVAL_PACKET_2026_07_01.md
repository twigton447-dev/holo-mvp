# Wave 3 Holo Target Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Approval granted by this packet: `False`
Approval packet SHA-256: `4cb9571846cad4b6f6e57dbc406d044320ff9283c5b73c2f2bf5dfbb81d3a066`
Live preflight root signature: `4fa40081fa4d54c56c6fbf463a70a98d90fa62d8d27b12b67e59bc23ef271ba6`

## Required Statement

`I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Expected Calls If Approved

- `pairs`: `12`
- `packets`: `24`
- `worker_calls`: `72`
- `gov_calls`: `48`
- `total_provider_calls`: `120`
- `judge_calls`: `0`
- `solo_calls`: `0`

## Command After Explicit Approval

```bash
python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave wave3 --batch-number 1 --run-live --approval-packet-sha256 4cb9571846cad4b6f6e57dbc406d044320ff9283c5b73c2f2bf5dfbb81d3a066 --approval-statement "I explicitly approve provider calls for WAVE3_HOLO_TARGET_BATCH_001 only, exactly as scoped in WAVE3_HOLO_TARGET_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without explicit approval.
- Use this approval packet only for the current checkout state and current live-preflight root.
- Do not rerun solo or judges.
- Do not edit frozen packets or prompts.
- No fallback or model substitution.
