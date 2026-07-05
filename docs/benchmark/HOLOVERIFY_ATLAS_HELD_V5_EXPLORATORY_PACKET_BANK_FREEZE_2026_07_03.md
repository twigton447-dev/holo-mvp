# HoloVerify Atlas Held V5 Exploratory Packet Bank Freeze

Status: `FROZEN_NO_PROVIDER_BANK`

Created: `2026-07-03T16:40:40.857907+00:00`

Provider / Solo / Judge calls made by this freeze: `0 / 0 / 0`

Freeze root: `039a699f9d8c1314472e0e04cae67a8b794ad085cef98bccfd9c42d843efe069`

## Scope

- Pairs: `3`
- Packets: `6`
- Truth counts: `{'ALLOW': 3, 'ESCALATE': 3}`
- Expected Holo calls: `30`

This is exploratory only. It does not approve provider execution or public claims.

## Validation

- `pair_count_3`: `True`
- `packet_count_6`: `True`
- `truth_balance`: `True`
- `runtime_leakage_clean`: `True`
- `runtime_ids_unique`: `True`
- `runtime_manifest_separate_from_scoring_map`: `True`
- `provider_calls_zero`: `True`
- `solo_calls_zero`: `True`
- `judge_calls_zero`: `True`

## Selected Rows

| Legacy packet | Truth | Opaque runtime ID | Failure classes |
| --- | --- | --- | --- |
| `HV-ATLAS-HELDV5-011-A` | `ALLOW` | `ATLASHELDV5-5AABB0A32B90FB69C1B5` | V5_BUSINESS_DAY_HOLIDAY_COUNT, HOP_DEPTH_LADDER |
| `HV-ATLAS-HELDV5-011-B` | `ESCALATE` | `ATLASHELDV5-16135C1C0D0F543E2F0B` | V5_BUSINESS_DAY_HOLIDAY_COUNT, HOP_DEPTH_LADDER |
| `HV-ATLAS-HELDV5-012-A` | `ALLOW` | `ATLASHELDV5-3DADEA2049204D2C3D10` | V5_TOXIC_ROLE_COMBINATION, HOP_DEPTH_LADDER |
| `HV-ATLAS-HELDV5-012-B` | `ESCALATE` | `ATLASHELDV5-63B663624CBFD039FFB2` | V5_TOXIC_ROLE_COMBINATION, HOP_DEPTH_LADDER |
| `HV-ATLAS-HELDV5-014-A` | `ALLOW` | `ATLASHELDV5-8EB79D8C6A54684873EE` | V5_COMPOSITE_QTY_UNIT_FX, HOP_DEPTH_LADDER |
| `HV-ATLAS-HELDV5-014-B` | `ESCALATE` | `ATLASHELDV5-98F8556057B49C9609B9` | V5_COMPOSITE_QTY_UNIT_FX, HOP_DEPTH_LADDER |
