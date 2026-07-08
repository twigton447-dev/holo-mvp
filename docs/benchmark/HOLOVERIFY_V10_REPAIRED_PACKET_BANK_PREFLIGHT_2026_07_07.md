# HoloVerify V10 Repaired Packet Bank Preflight - 2026-07-07

Classification: **NO_PROVIDER_PREFLIGHT_PASS**

Lane: `HOLOVERIFY_V10_REPAIRED_PACKET_BANK_VALUE_TUPLE_VALIDATION_V0`

## Runtime Package

- Runtime manifest: `docs/benchmark/HOLOVERIFY_V10_REPAIRED_PACKET_BANK_RUNTIME_MANIFEST_NO_TRUTH_2026_07_07.json`
- Runtime manifest SHA-256: `4408116c815b7436c81c8345d53c7f1aa19bf4623b6f559256c2f75093b07fb8`
- Package root: `docs/benchmark/holoverify_v10_repaired_packet_bank_2026_07_07`
- Post-hoc scoring map: `docs/benchmark/holoverify_v10_repaired_packet_bank_2026_07_07/holoverify_v10_repaired_packet_bank_scoring_map_2026_07_07.json`
- Post-hoc scoring map SHA-256: `8671d65caaabd758baafafc2909785464cd8a2ebc49d9e0a876f755408fdb4be`

## Active Runtime Identities

- Selector: `SELECTOR_V9_GENERIC_BLOCKER_RESOLUTION_2026_07_06`
- Selector hash: `cb53549bcc01d882836fc47e68e1ec5610b302cdbd8ddfd1967f7fac5a235416`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract hash: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`

## No-Provider Prompt Probe

- Prompt probe folder: `docs/benchmark/holoverify_v10_repaired_packet_bank_2026_07_07/preflight_prompt_probe_20260707T170108Z`
- TRACE_CALLS SHA-256: `e507f7d869389b2e2fe35f8cdadecff3c12451fb3d695d0409aa84ffc915b05e`
- Call records: `30`
- Prompt files: `30`
- Route check: `W1 -> G1 -> W2 -> G2 -> W3` x6 = `True`
- `TRACE_PROVIDER_CALLS.jsonl`: absent = `True`
- `raw_provider_outputs`: absent = `True`
- Live run folder: absent = `True`

## Validation Checks

- JSON parse: `True`
- Runtime packet rows opaque-only: `True`
- Runtime payload leakage hits: `0`
- Scoring map post-hoc only: `True`
- Prompt probe exactly 30 call records: `True`

## Future Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_V10_REPAIRED_PACKET_BANK_VALUE_TUPLE_VALIDATION_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V10_REPAIRED_PACKET_BANK_RUNTIME_MANIFEST_NO_TRUTH_2026_07_07.json with SHA-256 4408116c815b7436c81c8345d53c7f1aa19bf4623b6f559256c2f75093b07fb8, selector SELECTOR_V9_GENERIC_BLOCKER_RESOLUTION_2026_07_06 hash cb53549bcc01d882836fc47e68e1ec5610b302cdbd8ddfd1967f7fac5a235416, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 30 provider calls: W1 xai/grok-3-mini x6, G1 minimax/MiniMax-M2.5-highspeed x6, W2 openai/gpt-5.4-mini x6, G2 minimax/MiniMax-M2.5-highspeed x6, W3 minimax/MiniMax-M2.5-highspeed x6. INTERNAL REPAIRED PACKET BANK VALUE-TUPLE VALIDATION ONLY for the three V9/V10 failed ALLOW families with matched ESCALATE controls; not public benchmark evidence, not a HoloEngine win, not a global FPR/FNR claim, not FP precision evidence, not production-rate evidence, and not production-safety evidence. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```

## Claim Boundary

Internal repaired packet-bank validation only. Not public benchmark evidence. Not a HoloEngine win. Not global FPR/FNR. Not FP precision. Not production-rate evidence. Not production-safety evidence.
