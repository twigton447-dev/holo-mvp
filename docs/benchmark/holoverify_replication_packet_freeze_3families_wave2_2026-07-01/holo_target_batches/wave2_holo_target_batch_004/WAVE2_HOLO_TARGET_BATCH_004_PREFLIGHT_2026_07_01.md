# Wave 2 Holo Target Batch 004 Staging

Created: `2026-07-01T06:11:59.241463+00:00`
Batch: `WAVE2_HOLO_TARGET_BATCH_004`
Status: `PASS`

## Scope

- Pairs: `10`
- Packets: `20`
- Expected provider calls when live: `100`
- Worker calls: `60`
- Gov calls: `40`
- Solo calls: `0`
- Judge calls: `0`

## Selected Pairs

- `HV-FINC-REP-016` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-DPRV-REP-005` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-DPRV-REP-007` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-DPRV-REP-008` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-FINC-REP-002` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-FINC-REP-017` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-FINC-REP-020` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-HRWF-REP-006` (HR / payroll / workforce controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-HRWF-REP-007` (HR / payroll / workforce controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`
- `HV-HRWF-REP-010` (HR / payroll / workforce controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `8`

## Model Order

- `W1`: `xai/grok-3-mini` as `SOURCE_BOUNDARY_MAPPER`
- `G1`: `minimax/MiniMax-M2.5-highspeed` as `CONTROL_ROUTER`
- `W2`: `openai/gpt-5.4-mini` as `ADVERSARIAL_SCOPE_CHALLENGER`
- `G2`: `minimax/MiniMax-M2.5-highspeed` as `CONTROL_ROUTER`
- `W3`: `minimax/MiniMax-M2.5-highspeed` as `FINAL_COMPILER`

## Preflight Checks

- `freeze_root_matches_expected`: `True`
- `target_selection_sha_matches_expected`: `True`
- `pair_count_10`: `True`
- `packet_count_20`: `True`
- `all_pairs_have_two_siblings`: `True`
- `packet_hashes_match`: `True`
- `prompt_hashes_match`: `True`
- `model_visible_hashes_match`: `True`
- `no_prompt_leakage_hits`: `True`
- `gov_cannot_choose_models`: `True`
- `expected_provider_calls_100`: `True`
- `expected_solo_calls_0`: `True`
- `expected_judge_calls_0`: `True`
- `frozen_assets_clean_in_git`: `True`

## Stop Rules

- No provider calls were made during staging.
- No solo or judge calls are part of this staged batch.
- Gov may not choose or alter models.
- No fallback or model substitution is allowed.
- Packet and prompt hashes must remain matched to the Wave 2 freeze before live execution.
