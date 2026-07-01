# Wave 2 Holo Target Batch 003 Staging

Created: `2026-07-01T05:32:43.840999+00:00`
Batch: `WAVE2_HOLO_TARGET_BATCH_003`
Status: `PASS`

## Scope

- Pairs: `9`
- Packets: `18`
- Expected provider calls when live: `90`
- Worker calls: `54`
- Gov calls: `36`
- Solo calls: `0`
- Judge calls: `0`

## Selected Pairs

- `HV-HRWF-REP-001` (HR / payroll / workforce controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `10`
- `HV-DPRV-REP-001` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-DPRV-REP-014` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-DPRV-REP-015` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-DPRV-REP-018` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-DPRV-REP-020` (Data privacy / customer data release controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-FINC-REP-001` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-FINC-REP-007` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`
- `HV-FINC-REP-009` (Finance close / revenue / expense recognition controls): `STRONG_SOLO_COLLAPSE`, not_knew `4`, priority `9`

## Model Order

- `W1`: `xai/grok-3-mini` as `SOURCE_BOUNDARY_MAPPER`
- `G1`: `minimax/MiniMax-M2.5-highspeed` as `CONTROL_ROUTER`
- `W2`: `openai/gpt-5.4-mini` as `ADVERSARIAL_SCOPE_CHALLENGER`
- `G2`: `minimax/MiniMax-M2.5-highspeed` as `CONTROL_ROUTER`
- `W3`: `minimax/MiniMax-M2.5-highspeed` as `FINAL_COMPILER`

## Preflight Checks

- `freeze_root_matches_expected`: `True`
- `target_selection_sha_matches_expected`: `True`
- `pair_count_9`: `True`
- `packet_count_18`: `True`
- `all_pairs_have_two_siblings`: `True`
- `packet_hashes_match`: `True`
- `prompt_hashes_match`: `True`
- `model_visible_hashes_match`: `True`
- `no_prompt_leakage_hits`: `True`
- `gov_cannot_choose_models`: `True`
- `expected_provider_calls_90`: `True`
- `expected_solo_calls_0`: `True`
- `expected_judge_calls_0`: `True`
- `freeze_root_clean_in_git`: `True`

## Stop Rules

- No provider calls were made during staging.
- No solo or judge calls are part of this staged batch.
- Gov may not choose or alter models.
- No fallback or model substitution is allowed.
- Packet and prompt hashes must remain matched to the Wave 2 freeze before live execution.
