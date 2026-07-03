# Randomized Corpus-Balanced Ablation Sample Lock

Status: `PASS`

This is a no-provider, no-judge sample lock. It selects sibling pairs from the clean 614-packet HoloVerify evidence denominator.

## Sample

- Seed: `HOLOVERIFY_RANDOM_BALANCED_ABLATION_V1_2026_07_02`
- Sample pairs: `3`
- Sample packets: `6`
- ALLOW packets: `3`
- ESCALATE packets: `3`
- Sample lock root: `903c9ed03384e41e66cb43561ae8961ebb3346670c910f9aaedeb67a854834fa`
- Approval packet SHA-256: `a580eacb11b6974c283c7cbb0096c4e7f1126909fcabec21169c0f7ab11e1afe`

## Why This Sample

- It is randomized from the whole scored denominator, not hand-picked from the hard packet set.
- It samples by sibling pair, so each selected unit carries one ALLOW and one ESCALATE packet.
- It is stratified across the early locked families, Wave2+3+4, and Wave5 so the random sample touches the full evidence stack.

## Selected Pairs

- `HV-ACOM-REP-015` / `domain_consolidated_early_locked` / `Agentic commerce / order execution controls` / packets: `HV-ACOM-REP-015-A=ALLOW`, `HV-ACOM-REP-015-B=ESCALATE`
- `HV-GOVP-REP-006` / `wave2_wave3_wave4_combined` / `Government procurement / grants controls` / packets: `HV-GOVP-REP-006-A=ALLOW`, `HV-GOVP-REP-006-B=ESCALATE`
- `HV-LREG-REP-014` / `wave5_completed` / `Legal / regulatory filing controls` / packets: `HV-LREG-REP-014-A=ALLOW`, `HV-LREG-REP-014-B=ESCALATE`

## Validation

- `generated_without_provider_calls`: `PASS`
- `generated_without_judge_calls`: `PASS`
- `clean_corpus_matches_614_denominator`: `PASS`
- `sample_pairs_requested`: `PASS`
- `sample_packets_are_pair_balanced`: `PASS`
- `sample_allow_equals_escalate`: `PASS`
- `sample_touches_all_three_source_tiers`: `PASS`
- `no_duplicate_sample_packets`: `PASS`
- `no_prompt_leakage_in_existing_prompt_refs`: `PASS`

## Live-Run Boundary

- Expected provider calls if approved: `144`
- Expected Gov calls: `0`
- Expected Holo calls: `0`
- Expected judge calls: `0`
- The next live runner must use no-Gov prompts only. Holo worker prompts are not permitted as packet prompts.
