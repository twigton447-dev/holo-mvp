# HoloVerify Solo Failure Factory Batch014 False-Negative-Hunter Packet Freeze

Status: `FROZEN_NO_PROVIDER_FOCUSED_FALSE_NEGATIVE_HUNTER_SOLO_SCOUT_BANK`

Created: `2026-07-04T00:28:44.098803+00:00`

Provider / Solo / Holo / Gov / Judge calls made by this freeze: `0 / 0 / 0 / 0 / 0`

Freeze root: `ffa9d2f2e5245a4ee3532b8aa94d68fbbf1bc35e84697a5de9d9742561b66409`

## Scope

- Pairs: `20`
- Packets: `40`
- Truth counts: `{'ALLOW': 20, 'ESCALATE': 20}`
- Target failure side counts: `{'ALLOW': 8, 'ESCALATE': 12}`
- Expected solo provider calls if approved later: `120`

Batch014 is a false-negative hunter: 8 clean-side overblock controls plus 12 blocked siblings that look official but contain quiet exact-boundary blockers.

## Claim Limit

Focused solo-failure discovery only. No benchmark credit. No public rate. No Holo run. No Gov run. No provider calls made by this freeze.

## Focus Strategy

- `pairs`: `20`
- `packets`: `40`
- `domains`: `16`
- `kit_lanes`: `20`
- `target_allow_pairs`: `8`
- `target_escalate_pairs`: `12`
- `failure_class_mentions`: `80`
- `dominant_seam`: `quiet_blocker_false_allow_hunter`

## Validation

- `truth_balance`: `True`
- `selected_reserve_designs_match_adjusted_top10`: `True`
- `target_failure_side_has_allow`: `True`
- `target_failure_side_has_escalate`: `True`
- `runtime_leakage_clean`: `True`
- `runtime_ids_unique`: `True`
- `runtime_manifest_separate_from_scoring_map`: `True`
- `provider_calls_zero`: `True`
- `solo_calls_zero`: `True`
- `holo_calls_zero`: `True`
- `gov_calls_zero`: `True`
- `judge_calls_zero`: `True`
- `contaminated_source_not_reused_as_proof`: `True`
- `pair_count_20`: `True`
- `packet_count_40`: `True`
- `export_safe_synthetic_content`: `True`
- `private_packet_text_not_copied`: `True`
- `focused_false_negative_hunter`: `True`
- `domain_spread_sufficient`: `True`
- `kit_lane_spread`: `True`
- `allow_controls_present`: `True`
- `false_negative_hunter_targets_present`: `True`

## Selected Rows

| Legacy packet | Truth | Failure class | Target side | Opaque runtime ID | Seam family |
| --- | --- | --- | --- | --- | --- |
| `HVSF-FACTORY14F-001-A` | `ALLOW` | `B14-FN-HUNTER-001` | `ALLOW` | `HVSF014F-E3748A4080E08CB2E80E` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-001-B` | `ESCALATE` | `B14-FN-HUNTER-001` | `ALLOW` | `HVSF014F-0503E8E8596AD8B9BFDC` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-002-A` | `ALLOW` | `B14-FN-HUNTER-002` | `ALLOW` | `HVSF014F-9876A48A07D3FCF6BC1E` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-002-B` | `ESCALATE` | `B14-FN-HUNTER-002` | `ALLOW` | `HVSF014F-5F299B9E4D655F855D54` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-003-A` | `ALLOW` | `B14-FN-HUNTER-003` | `ALLOW` | `HVSF014F-AADBF3D9A2CE86A37227` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-003-B` | `ESCALATE` | `B14-FN-HUNTER-003` | `ALLOW` | `HVSF014F-48E2C7F15205BFAE2575` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-004-A` | `ALLOW` | `B14-FN-HUNTER-004` | `ALLOW` | `HVSF014F-FF0B27A3EEA7EC349367` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-004-B` | `ESCALATE` | `B14-FN-HUNTER-004` | `ALLOW` | `HVSF014F-05253417D374312C274D` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-005-A` | `ALLOW` | `B14-FN-HUNTER-005` | `ALLOW` | `HVSF014F-E6AE02BFB73A3B446141` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-005-B` | `ESCALATE` | `B14-FN-HUNTER-005` | `ALLOW` | `HVSF014F-0F2B4FF8F9434E850ABC` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-006-A` | `ALLOW` | `B14-FN-HUNTER-006` | `ALLOW` | `HVSF014F-1A224F5CC0D65037566E` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-006-B` | `ESCALATE` | `B14-FN-HUNTER-006` | `ALLOW` | `HVSF014F-FE5AF80A5ED2F9FE5264` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-007-A` | `ALLOW` | `B14-FN-HUNTER-007` | `ALLOW` | `HVSF014F-B70F5388D9F4ECBE4AA5` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-007-B` | `ESCALATE` | `B14-FN-HUNTER-007` | `ALLOW` | `HVSF014F-DA145433F3C26A0FE351` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-008-A` | `ALLOW` | `B14-FN-HUNTER-008` | `ALLOW` | `HVSF014F-A27B07DED56F267DE950` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-008-B` | `ESCALATE` | `B14-FN-HUNTER-008` | `ALLOW` | `HVSF014F-2B7494FE4FE57FD59341` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-009-A` | `ALLOW` | `B14-FN-HUNTER-009` | `ESCALATE` | `HVSF014F-E7AE256C4E1A1F5466C0` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-009-B` | `ESCALATE` | `B14-FN-HUNTER-009` | `ESCALATE` | `HVSF014F-E4DA97FDD39EC0556568` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-010-A` | `ALLOW` | `B14-FN-HUNTER-010` | `ESCALATE` | `HVSF014F-20EEA2A0E19190B65907` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-010-B` | `ESCALATE` | `B14-FN-HUNTER-010` | `ESCALATE` | `HVSF014F-7A8FD97D79CFE70764A8` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-011-A` | `ALLOW` | `B14-FN-HUNTER-011` | `ESCALATE` | `HVSF014F-C2A74858BAF39B26391E` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-011-B` | `ESCALATE` | `B14-FN-HUNTER-011` | `ESCALATE` | `HVSF014F-EFA3E7E9EE3CFFB4F5CD` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-012-A` | `ALLOW` | `B14-FN-HUNTER-012` | `ESCALATE` | `HVSF014F-1721D9DAE5D77435B3B5` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-012-B` | `ESCALATE` | `B14-FN-HUNTER-012` | `ESCALATE` | `HVSF014F-77541D27218BF40FFC4F` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-013-A` | `ALLOW` | `B14-FN-HUNTER-013` | `ESCALATE` | `HVSF014F-20DEF09D21B0FBA1A00C` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-013-B` | `ESCALATE` | `B14-FN-HUNTER-013` | `ESCALATE` | `HVSF014F-77CAFB5EEF2B95C9DC60` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-014-A` | `ALLOW` | `B14-FN-HUNTER-014` | `ESCALATE` | `HVSF014F-415E680A162F6E6B0AD8` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-014-B` | `ESCALATE` | `B14-FN-HUNTER-014` | `ESCALATE` | `HVSF014F-D00718B1BA2E5C2D4E9C` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-015-A` | `ALLOW` | `B14-FN-HUNTER-015` | `ESCALATE` | `HVSF014F-5A5F42B87BED71F4C8A1` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-015-B` | `ESCALATE` | `B14-FN-HUNTER-015` | `ESCALATE` | `HVSF014F-A5EFB825B13E44E0C570` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-016-A` | `ALLOW` | `B14-FN-HUNTER-016` | `ESCALATE` | `HVSF014F-72E1B7B3500B573005A7` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-016-B` | `ESCALATE` | `B14-FN-HUNTER-016` | `ESCALATE` | `HVSF014F-42F4CBB0A1C60E41922B` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-017-A` | `ALLOW` | `B14-FN-HUNTER-017` | `ESCALATE` | `HVSF014F-D1E43ED8BAB9202DC486` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-017-B` | `ESCALATE` | `B14-FN-HUNTER-017` | `ESCALATE` | `HVSF014F-59DFA66D8BFDB2565138` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-018-A` | `ALLOW` | `B14-FN-HUNTER-018` | `ESCALATE` | `HVSF014F-5F216DFBDF75BC79C425` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-018-B` | `ESCALATE` | `B14-FN-HUNTER-018` | `ESCALATE` | `HVSF014F-87A7C886575676CCEA64` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-019-A` | `ALLOW` | `B14-FN-HUNTER-019` | `ESCALATE` | `HVSF014F-871B070E5F8DDF885543` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-019-B` | `ESCALATE` | `B14-FN-HUNTER-019` | `ESCALATE` | `HVSF014F-5A81B0D3BD783543A581` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-020-A` | `ALLOW` | `B14-FN-HUNTER-020` | `ESCALATE` | `HVSF014F-61D7A66EE2BF4EBA8536` | quiet_blocker_false_allow_hunter |
| `HVSF-FACTORY14F-020-B` | `ESCALATE` | `B14-FN-HUNTER-020` | `ESCALATE` | `HVSF014F-22323DFB710CAE5F56B7` | quiet_blocker_false_allow_hunter |
