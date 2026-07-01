# Wave 2 Holo Full-Family Remainder Batch 005 Staging

Created: `2026-07-01T06:21:52.495353+00:00`
Batch: `WAVE2_HOLO_TARGET_BATCH_005`
Selection mode: `full-family-remainder`
Claim boundary: Full-family remainder staging only; not selected-target evidence and not scored until a live Holo run exists.
Status: `PASS`

## Scope

- Pairs: `23`
- Packets: `46`
- Expected provider calls when live: `230`
- Worker calls: `138`
- Gov calls: `92`
- Solo calls: `0`
- Judge calls: `0`

## Selected Pairs

- `HV-DPRV-REP-002` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-003` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-004` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-006` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-010` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-011` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-016` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-DPRV-REP-017` (Data privacy / customer data release controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-FINC-REP-005` (Finance close / revenue / expense recognition controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-FINC-REP-008` (Finance close / revenue / expense recognition controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-FINC-REP-014` (Finance close / revenue / expense recognition controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-FINC-REP-018` (Finance close / revenue / expense recognition controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-002` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-003` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-004` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-005` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-008` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-009` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-011` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-013` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-014` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-015` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`
- `HV-HRWF-REP-016` (HR / payroll / workforce controls): `NON_TARGET_FULL_FAMILY_COMPLETION`, not_knew `MISSING_REPO_EVIDENCE`, priority `MISSING_REPO_EVIDENCE`

## Model Order

- `W1`: `xai/grok-3-mini` as `SOURCE_BOUNDARY_MAPPER`
- `G1`: `minimax/MiniMax-M2.5-highspeed` as `CONTROL_ROUTER`
- `W2`: `openai/gpt-5.4-mini` as `ADVERSARIAL_SCOPE_CHALLENGER`
- `G2`: `minimax/MiniMax-M2.5-highspeed` as `CONTROL_ROUTER`
- `W3`: `minimax/MiniMax-M2.5-highspeed` as `FINAL_COMPILER`

## Preflight Checks

- `freeze_root_matches_expected`: `True`
- `target_selection_sha_matches_expected`: `True`
- `pair_count_23`: `True`
- `packet_count_46`: `True`
- `all_pairs_have_two_siblings`: `True`
- `packet_hashes_match`: `True`
- `prompt_hashes_match`: `True`
- `model_visible_hashes_match`: `True`
- `no_prompt_leakage_hits`: `True`
- `gov_cannot_choose_models`: `True`
- `expected_provider_calls_230`: `True`
- `expected_solo_calls_0`: `True`
- `expected_judge_calls_0`: `True`
- `frozen_assets_clean_in_git`: `True`
- `no_selected_target_pairs_in_full_family_remainder`: `True`
- `full_family_remainder_pair_count_matches_available`: `True`

## Stop Rules

- No provider calls were made during staging.
- No solo or judge calls are part of this staged batch.
- Gov may not choose or alter models.
- No fallback or model substitution is allowed.
- Packet and prompt hashes must remain matched to the Wave 2 freeze before live execution.
- Full-family remainder batches are not selected-target proof and must not be merged into selected-target scoring language.
