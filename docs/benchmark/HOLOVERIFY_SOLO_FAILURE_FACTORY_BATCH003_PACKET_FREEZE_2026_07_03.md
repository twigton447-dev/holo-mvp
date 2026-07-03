# HoloVerify Solo Failure Factory Batch 003 Packet Freeze

Status: `FROZEN_NO_PROVIDER_SOLO_SCOUT_BANK`

Created: `2026-07-03T20:21:24.457529+00:00`

Provider / Solo / Holo / Gov / Judge calls made by this freeze: `0 / 0 / 0 / 0 / 0`

Freeze root: `986355428bd7f1f67337e26f5c054e0800dcea0658c302c879f1385401b5b242`

## Scope

- Pairs: `10`
- Packets: `20`
- Truth counts: `{'ALLOW': 10, 'ESCALATE': 10}`
- Target failure side counts: `{'ALLOW': 1, 'ESCALATE': 9}`
- Expected solo provider calls if approved later: `60`

This bank is for solo-failure discovery only. It does not approve provider execution, Holo execution, scoring claims, or public claims.

## Validation

- `pair_count_10`: `True`
- `packet_count_20`: `True`
- `truth_balance`: `True`
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

## Selected Rows

| Legacy packet | Truth | Target side | Opaque runtime ID | Seam family |
| --- | --- | --- | --- | --- |
| `HVSF-FACTORY3-001-A` | `ALLOW` | `ESCALATE` | `HVSF003-85CAD31CD3C3A84ADB79` | rebrand_callback_source_false_allow |
| `HVSF-FACTORY3-001-B` | `ESCALATE` | `ESCALATE` | `HVSF003-975F030E20A730205A21` | rebrand_callback_source_false_allow |
| `HVSF-FACTORY3-002-A` | `ALLOW` | `ESCALATE` | `HVSF003-FA6C71C53302F8E368F7` | rebrand_callback_source_false_allow |
| `HVSF-FACTORY3-002-B` | `ESCALATE` | `ESCALATE` | `HVSF003-0E1D5DC38C8041BB90B8` | rebrand_callback_source_false_allow |
| `HVSF-FACTORY3-003-A` | `ALLOW` | `ESCALATE` | `HVSF003-9D46CF4DDBD61D58FA6C` | refund_original_charge_vs_remaining_balance |
| `HVSF-FACTORY3-003-B` | `ESCALATE` | `ESCALATE` | `HVSF003-5B9EF06315AFE020DBA7` | refund_original_charge_vs_remaining_balance |
| `HVSF-FACTORY3-004-A` | `ALLOW` | `ESCALATE` | `HVSF003-0BF2E1DF0DFBD5DE33A0` | refund_original_charge_vs_remaining_balance |
| `HVSF-FACTORY3-004-B` | `ESCALATE` | `ESCALATE` | `HVSF003-0CA204955CC572C10F94` | refund_original_charge_vs_remaining_balance |
| `HVSF-FACTORY3-005-A` | `ALLOW` | `ALLOW` | `HVSF003-65F9A661E5CDC79C93E3` | numeric_variance_inside_tolerance_overblock |
| `HVSF-FACTORY3-005-B` | `ESCALATE` | `ALLOW` | `HVSF003-96C6F9E362FF24D6B78B` | numeric_variance_inside_tolerance_overblock |
| `HVSF-FACTORY3-006-A` | `ALLOW` | `ESCALATE` | `HVSF003-89C08862F3B64A0FD63D` | timezone_window_false_allow |
| `HVSF-FACTORY3-006-B` | `ESCALATE` | `ESCALATE` | `HVSF003-AF0ED6C613C131E8CBC5` | timezone_window_false_allow |
| `HVSF-FACTORY3-007-A` | `ALLOW` | `ESCALATE` | `HVSF003-1865583CE1A0400990A6` | timezone_window_false_allow |
| `HVSF-FACTORY3-007-B` | `ESCALATE` | `ESCALATE` | `HVSF003-50F8FAF8A4D3CC0A74E6` | timezone_window_false_allow |
| `HVSF-FACTORY3-008-A` | `ALLOW` | `ESCALATE` | `HVSF003-2388B02869F88C9C2104` | stale_authority_false_allow |
| `HVSF-FACTORY3-008-B` | `ESCALATE` | `ESCALATE` | `HVSF003-F7516949F8A4B6B8C0F3` | stale_authority_false_allow |
| `HVSF-FACTORY3-009-A` | `ALLOW` | `ESCALATE` | `HVSF003-1715B0F37528B6521625` | extension_record_wrong_user_false_allow |
| `HVSF-FACTORY3-009-B` | `ESCALATE` | `ESCALATE` | `HVSF003-F74FF396A130E8E029DF` | extension_record_wrong_user_false_allow |
| `HVSF-FACTORY3-010-A` | `ALLOW` | `ESCALATE` | `HVSF003-EF96910FAC31EB8A4BC4` | extension_record_wrong_user_false_allow |
| `HVSF-FACTORY3-010-B` | `ESCALATE` | `ESCALATE` | `HVSF003-491DD34657D5AF8E86F2` | extension_record_wrong_user_false_allow |
