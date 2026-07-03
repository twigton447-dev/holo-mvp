# HoloVerify Blind 120 Firewall Preflight

Status: `NO_PROVIDER_FIREWALL_PREFLIGHT_PASS`

Created: `2026-07-03T00:57:21Z`

Provider calls made by this preflight: `0`

Judge calls made by this preflight: `0`

## Frozen Bank

Freeze root:

`63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba`

Primary files:

- `docs/benchmark/HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.md`
- `docs/benchmark/HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.json`
- `docs/benchmark/holoverify_blind_120_bank_2026_07_03/holoverify_blind_120_runtime_manifest_2026_07_03.json`
- `docs/benchmark/holoverify_blind_120_bank_2026_07_03/holoverify_blind_120_scoring_map_2026_07_03.json`
- `docs/benchmark/holoverify_blind_120_bank_2026_07_03/holoverify_blind_120_hash_manifest_2026_07_03.json`

## Local Assertions

- packets: `120`
- pairs: `60`
- ALLOW truths: `60`
- ESCALATE truths: `60`
- runtime payload files: `120`
- runtime IDs unique: `true`
- runtime manifest separate from scoring map: `true`
- provider calls: `0`
- judge calls: `0`
- hash manifest freeze root recomputed: `PASS`

## Firewall Probe

A no-provider mock prompt probe was run over the 120-packet runtime manifest.
It exercised the runtime prompt builder for:

- 120 packets
- 5 calls per packet
- 600 mock calls total

Results:

- runtime input leakage hits: `0`
- prompt leakage hits: `0`

Forbidden scan targets included:

- legacy packet IDs
- suffix-pattern answer channels
- `packet_truth`
- `legacy_truth`
- `legacy_packet_id`
- `deterministic_answer_key`
- `answer_key`
- `knew_terms`
- `allow_rule`
- `esc_rule`
- `target_bucket`
- `target_sibling`

## Claim Boundary

This preflight only verifies that the 120-packet blind bank is locally frozen
and runtime-firewall clean under mock execution.

It does not approve provider execution, solo runs, judges, scoring claims,
confidence intervals, or public benchmark updates.

