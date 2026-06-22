# D13 Trace-Based Baseline Failure Report

Created: 2026-06-22

## Scope

This report uses committed D13 evidence only. It does not run providers, judge, score, rerun Holo, rerun solo, unblind, or modify sealed anonymization maps.

Evidence commits:

- `9fef8e1` - Add D13 treasury sanctions payment release packet
- `ec1d893` - Preserve D13 Holo-only live run evidence
- `0ac1f67` - Preserve D13 solo Opus baseline evidence
- `98717cd` - Preserve D13 blind held-out judging evidence
- `695ba7f` - Patch solo baseline completeness eligibility gate
- `25ae69d` - Preserve corrected D13 solo Opus rerun failure evidence

## Packet Identity

- Packet id: `d13_treasury_sanctions_payment_release_001`
- Domain: `D13 Treasury Sanctions / Payment Release`
- Packet path: `artifact_benchmarks/holo_factory/mini_scouts/d13_treasury_sanctions_payment_release_001`
- Source count: `10`
- Source mix: `3 strong`, `3 useful_normal`, `1 stale_tempting`, `1 contradictory_or_complicating`, `1 weak_or_limited`, `1 table_chart_stat_element`
- `source_packet.json` hash: `716fbc94608107d10d58c4de144d6cbce92c184c7f7c102d2f1581bb6b567801`
- `task_brief.md` hash: `6de175acfda7f0d215574d0d00a26259ecf6e1b2858c431efa0966acc57fcdfa`
- `source_manifest.json` hash: `0ba970e2b1e19516e350b27a7a47b3d4de30492c0d1676ea97e29554f66c1928`
- `packet_lock.json` hash: `c3d9a58418c8a2cd0c7bf648e398b76465266816e36390346acb5cef04c90c6e`
- `freeze_manifest.json` records `freeze_status: FROZEN_NO_PROVIDER_PACKET_ONLY`
- D13 packet validator result: `D13_MINI_SCOUT_PACKET_VALIDATION_PASS`

## Holo Run

- Run id: `d13_treasury_sanctions_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T193904Z`
- Status: `HOLOBUILD_MINI_SCOUT_LIVE_GENERATION_COMPLETE`
- Final artifact hash: `f2284d2b492de8c8256d51ca248579e9c193ea6de8a5fede1cce3820ec6195ff`
- Provider calls: `9`
- Repair calls: `3`
- Scores generated: `0`
- Proof credit eligible: `true`
- Architecture status: `eligible_if_all_turn_audits_pass_and_deterministic_gate_passes`

Proof-clean gates from committed `artifact_metadata.json`:

- `deterministic_gate_pass: true`
- `required_roles_all_completed: true`
- `role_compliance_all_pass: true`
- `intermediate_completeness_all_pass: true`
- `state_audit_all_pass: true`
- `registry_acceptance_all_pass: true`
- `no_failed_required_turn_consumed_by_final: true`
- `prompt_card_hashes_present: true`
- `final_artifact_completeness_pass: true`
- `final_word_band_pass: true`
- `final_repair_succeeded_if_used: true`
- `final_synthesis_blocked: false`

Independent deterministic final-artifact check:

- Word count: `1237`
- Word band: `pass`
- Final completeness: `pass`
- Clean ending: `true`
- Required sections present: `bottom_line`, `risks_of_acting`, `risks_of_waiting`, `next_steps`, `claim_boundaries`
- Deterministic failures: `[]`

## Solo Opus Attempt 1

- Run id: `d13_treasury_sanctions_payment_release_001_solo_opus_4_8_baseline_live_20260622T194909Z`
- Status: `HOLOBUILD_MINI_SCOUT_LIVE_GENERATION_COMPLETE`
- Final artifact hash: `a981bf6935f08bf674d6d0237562f86673d8290b8b4c21068c0155f0745abc06`
- Provider calls: `6`
- Input tokens: `53522`
- Output tokens: `21019`
- Recorded baseline eligibility at the time: `true`

Why it was later invalidated:

The original solo baseline metadata recorded `baseline_eligible: true`, but the eligibility path did not yet require final-artifact completeness. Commit `695ba7f` patched the solo baseline gate so eligibility requires deterministic gate pass, final word-band pass, and final artifact completeness pass. The deterministic completeness addendum then marked the earlier `baseline_eligible=true` value invalid under corrected validation.

Corrected deterministic check for attempt 1:

- Word count: `1032`
- Deterministic gate status: `pass`
- Final word band: `pass`
- Final artifact completeness: `fail`
- Clean ending: `false`
- Claim boundaries/disclaimer section present: `false`
- Deterministic failure reasons:
  - `unclean_or_mid_sentence_ending`
  - `missing_final_section:claim_boundaries`
- Tail observation: ends mid-sentence at `Second Treasury approval rec`

The deterministic completeness addendum also corrected the blind score object's word count for this exported artifact: `ARTIFACT_002` was `1032`, not `820`.

## Solo Opus Attempt 2

- Run id: `d13_treasury_sanctions_payment_release_001_solo_opus_4_8_baseline_live_corrected_20260622T202300Z`
- Status: `HOLOBUILD_MINI_SCOUT_LIVE_GENERATION_COMPLETE`
- Final artifact hash: `148dc8882b463fb3767b422aab320f50b1c674eedc9002040c2fd828b0510f4b`
- Provider calls: `6`
- Input tokens: `53825`
- Output tokens: `21324`
- Corrected baseline eligibility: `false`

Corrected deterministic check for attempt 2:

- Word count: `972`
- Deterministic gate status: `pass`
- Final word band: `pass`
- Final artifact completeness: `fail`
- Clean ending: `false`
- Claim boundaries/disclaimer section present: `false`
- Deterministic failure reasons:
  - `unclean_or_mid_sentence_ending`
  - `missing_final_section:claim_boundaries`
- Tail observation: ends after an unfinished stop condition: `STOP: any gate open at cutoff -> no release; hold queue persists;`

Attempt 2 therefore preserved another failed baseline attempt. It did not produce a baseline-eligible solo artifact.

## Blind Export And Held-Out Judging

Blind export id: `d13_two_artifact_blind_comparison_20260622T201000Z`

The blind export was authentic: the deterministic addendum records that `ARTIFACT_001` and `ARTIFACT_002` exported text hashes each matched one committed source final artifact hash. However, the export is non-score-valid because `ARTIFACT_002` was a truncated/incomplete solo artifact.

Held-out judging remains non-score-valid:

- Score lock addendum id: `d13_two_artifact_blind_comparison_20260622T201000Z_score_lock_addendum_001`
- Judge calls: `6`
- Repair calls: `3`
- Parse success count: `0`
- Parse failure count: `3`
- Accepted score paths: `[]`
- `ARTIFACT_001` judge count scored: `0`
- `ARTIFACT_002` judge count scored: `0`
- Contamination scan: `PASS`
- Anonymization map remained sealed: `true`

Final parse/validation failures:

- xAI held-out judge: `ARTIFACT_001:claim_ledger_too_short`, `ARTIFACT_001:argument_power_score_math_wrong`, `ARTIFACT_001:argument_power_above_90_without_three_insight_findings`, `ARTIFACT_002:claim_ledger_too_short`; repair also failed validation.
- MiniMax held-out judge: invalid claim types for both artifacts and `ARTIFACT_002:argument_power_score_math_wrong`; repair also failed validation.
- Google held-out judge: initial JSON decode failure; repair failed validation for score math, short claim ledger, invalid severity, and raw composite math.

Because all held-out judge outputs failed strict parsing/validation, no official numeric Holo-vs-Opus score exists for D13. The repo has no score-valid locked comparison result for this pair. The pasted/native score payload was also rejected by strict validation and was not accepted as a locked score.

## Clean Takeaway

D13 currently supports a trace-based baseline failure finding, not a scored flagship proof.

The Holo run completed and passed the proof-clean architecture and deterministic gates. Both solo Opus baseline attempts failed corrected deterministic baseline eligibility despite passing the simple word-band gate. In both solo attempts, the final artifact ended uncleanly and omitted the required claim-boundaries section. The original blind packet is authentic but non-score-valid because it included the incomplete attempt-1 solo artifact and held-out judging produced zero parse-valid score objects.

## Recommendation

Preserve D13 as baseline-failure evidence. Do not present it as a numeric scored Holo-vs-Opus flagship proof unless a future baseline-eligible solo artifact is generated under the corrected deterministic gate and a fresh blind comparison is judged with a valid locked score.
