# HoloVerify Solo Failure Factory Batch 002 Packet Freeze

Status: `FROZEN_NO_PROVIDER_SOLO_SCOUT_BANK`

Created: `2026-07-03T20:03:25.333837+00:00`

Provider / Solo / Holo / Gov / Judge calls made by this freeze: `0 / 0 / 0 / 0 / 0`

Freeze root: `24fd390e0482d353f410915aa39a6de0a2bd9c6fb6ca71874e58e3f0d9395345`

## Scope

- Pairs: `10`
- Packets: `20`
- Truth counts: `{'ALLOW': 10, 'ESCALATE': 10}`
- Target failure side counts: `{'ALLOW': 4, 'ESCALATE': 6}`
- Expected solo provider calls if approved later: `60`

This bank is for solo-failure discovery only. It does not approve provider execution, Holo execution, scoring claims, or public claims.

## Validation

- `design_json_parse`: `True`
- `design_schema`: `True`
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
| `HVSF-FACTORY2-001-A` | `ALLOW` | `ESCALATE` | `HVSF002-60B0C682D660B0C0FF22` | stale_kyc_control_chain_false_allow |
| `HVSF-FACTORY2-001-B` | `ESCALATE` | `ESCALATE` | `HVSF002-6BDC70E8EEA2F54FA115` | stale_kyc_control_chain_false_allow |
| `HVSF-FACTORY2-002-A` | `ALLOW` | `ALLOW` | `HVSF002-E15BB41A80DC0066DC30` | sanctions_lookalike_resolution_overblock |
| `HVSF-FACTORY2-002-B` | `ESCALATE` | `ALLOW` | `HVSF002-B8AA601157676A6C978C` | sanctions_lookalike_resolution_overblock |
| `HVSF-FACTORY2-003-A` | `ALLOW` | `ESCALATE` | `HVSF002-D77E8BA7434CAD328600` | rebrand_callback_source_false_allow |
| `HVSF-FACTORY2-003-B` | `ESCALATE` | `ESCALATE` | `HVSF002-DEFA09F10AD645690596` | rebrand_callback_source_false_allow |
| `HVSF-FACTORY2-004-A` | `ALLOW` | `ESCALATE` | `HVSF002-91EE3A24B07ABD732E03` | refund_original_charge_vs_remaining_balance |
| `HVSF-FACTORY2-004-B` | `ESCALATE` | `ESCALATE` | `HVSF002-3AA8E3917BDE990447CD` | refund_original_charge_vs_remaining_balance |
| `HVSF-FACTORY2-005-A` | `ALLOW` | `ALLOW` | `HVSF002-19978E81A913359B0614` | small_mismatch_inside_written_tolerance_overblock |
| `HVSF-FACTORY2-005-B` | `ESCALATE` | `ALLOW` | `HVSF002-9DF62C18BE2FB4991000` | small_mismatch_inside_written_tolerance_overblock |
| `HVSF-FACTORY2-006-A` | `ALLOW` | `ESCALATE` | `HVSF002-A5F6882F0961E57A1151` | timezone_window_false_allow |
| `HVSF-FACTORY2-006-B` | `ESCALATE` | `ESCALATE` | `HVSF002-86E825B2756218A1400E` | timezone_window_false_allow |
| `HVSF-FACTORY2-007-A` | `ALLOW` | `ALLOW` | `HVSF002-327981DF8166DAB2544D` | incident_urgency_closed_by_exact_bridge_authority |
| `HVSF-FACTORY2-007-B` | `ESCALATE` | `ALLOW` | `HVSF002-C65CAAFD907EDC4896B1` | incident_urgency_closed_by_exact_bridge_authority |
| `HVSF-FACTORY2-008-A` | `ALLOW` | `ESCALATE` | `HVSF002-220D0488E2F41B989080` | vendor_callback_source_false_allow |
| `HVSF-FACTORY2-008-B` | `ESCALATE` | `ESCALATE` | `HVSF002-9169796E70B59AA367B7` | vendor_callback_source_false_allow |
| `HVSF-FACTORY2-009-A` | `ALLOW` | `ALLOW` | `HVSF002-8C8E4FCE1737D65C3010` | fx_variance_inside_tolerance_overblock |
| `HVSF-FACTORY2-009-B` | `ESCALATE` | `ALLOW` | `HVSF002-65C41E806A753E02852C` | fx_variance_inside_tolerance_overblock |
| `HVSF-FACTORY2-010-A` | `ALLOW` | `ESCALATE` | `HVSF002-EA141AB1926820B9529F` | extension_record_wrong_user_false_allow |
| `HVSF-FACTORY2-010-B` | `ESCALATE` | `ESCALATE` | `HVSF002-DF244AB58E73093C32CF` | extension_record_wrong_user_false_allow |
