# Wave 3 Holo Target Batch 001 Staging

Batch: `WAVE3_HOLO_TARGET_BATCH_001`
Status: `PASS`
Claim boundary: Selected-target staging only; not scored until a clean live Holo run exists.

## Scope

- `pairs`: `12`
- `packets`: `24`
- `worker_calls`: `72`
- `gov_calls`: `48`
- `total_provider_calls`: `120`
- `solo_calls`: `0`
- `judge_calls`: `0`

## Selected Pairs

- `HV-BENC-REP-016` (Benefits / public casework controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `1`
- `HV-BKYC-REP-011` (Banking / KYC / AML controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `1`
- `HV-BKYC-REP-016` (Banking / KYC / AML controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `1`
- `HV-BKYC-REP-018` (Banking / KYC / AML controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `1`
- `HV-BKYC-REP-020` (Banking / KYC / AML controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `1`
- `HV-GOVP-REP-012` (Government procurement / grants controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `1`
- `HV-BENC-REP-001` (Benefits / public casework controls): `hard_allow`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `0`
- `HV-BENC-REP-015` (Benefits / public casework controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `0`
- `HV-BENC-REP-020` (Benefits / public casework controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `0`
- `HV-BKYC-REP-009` (Banking / KYC / AML controls): `hard_allow`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `0`
- `HV-GOVP-REP-006` (Government procurement / grants controls): `hard_allow`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `0`
- `HV-GOVP-REP-014` (Government procurement / grants controls): `hard_escalate`, `STRONG_SOLO_COLLAPSE`, not-KNEW `4`, wrong-verdict `0`

## Model Order

- `W1:xai/grok-3-mini:SOURCE_BOUNDARY_MAPPER`
- `G1:minimax/MiniMax-M2.5-highspeed:CONTROL_ROUTER`
- `W2:openai/gpt-5.4-mini:ADVERSARIAL_SCOPE_CHALLENGER`
- `G2:minimax/MiniMax-M2.5-highspeed:CONTROL_ROUTER`
- `W3:minimax/MiniMax-M2.5-highspeed:FINAL_COMPILER`

## Preflight Checks

- `all_pairs_have_two_siblings`: `True`
- `expected_judge_calls_0`: `True`
- `expected_solo_calls_0`: `True`
- `expected_total_provider_calls`: `True`
- `freeze_root_matches_expected`: `True`
- `frozen_assets_clean_in_git`: `True`
- `gov_cannot_choose_models`: `True`
- `model_visible_hashes_match`: `True`
- `no_prompt_leakage_hits`: `True`
- `packet_hashes_match`: `True`
- `pair_count_matches_selected_targets`: `True`
- `prompt_hashes_match`: `True`
- `solo_triage_complete`: `True`
- `solo_triage_expected_provider_calls`: `True`
- `solo_triage_no_gov_holo_judges`: `True`
- `solo_triage_no_provider_failures`: `True`

## Stop Rules

- No provider calls were made during staging.
- No solo or judge calls are part of this staged batch.
- Gov may not choose or alter models.
- No fallback or model substitution is allowed.
- Packet and prompt hashes must remain matched to the Wave3/Wave4 freeze before live execution.
