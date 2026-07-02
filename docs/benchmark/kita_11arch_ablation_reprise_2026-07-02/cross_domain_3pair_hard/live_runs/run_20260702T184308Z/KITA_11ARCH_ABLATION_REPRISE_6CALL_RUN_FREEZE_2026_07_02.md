# Kit A Ablation Reprise 6-Call Run Freeze

Status: `FROZEN_COMPLETE_NO_GOV_ABLATION_REPRISE`

Run: `run_20260702T184308Z`
Evidence root SHA-256: `215476b55ce00b11ff34240febc85504ed143c8c9bf5880ab0de254e6b2b8439`
Packet freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Approval packet SHA-256: `5d1f1edd100e9c7ca816b765910d3212f0e929d9bee8656b8ac176a06bde96fd`

## Scope

- Pairs: `HV-AP-REP-011, HV-ACOM-REP-020, HV-ITAC-REP-018`
- Packets: `6`
- Architectures: `provider_balanced_reconsider_no_gov_6call, provider_balanced_vote_no_gov_6call, provider_balanced_council_no_gov_6call, provider_balanced_debate_no_gov_6call`
- Fairness frame: provider-balanced no-Gov ablation, 6 calls per packet per architecture, 2 turns per model.
- Holo/Gov/judge calls: `0`

## Assertions

- `provider_calls_complete`: `PASS`
- `provider_failures_zero`: `PASS`
- `gov_calls_zero`: `PASS`
- `holo_calls_zero`: `PASS`
- `judge_calls_zero`: `PASS`
- `selected_packet_count_six`: `PASS`
- `architecture_result_units_24`: `PASS`
- `provider_balanced_two_turns_each_model`: `PASS`
- `no_prompt_leakage`: `PASS`
- `no_holo_controls_in_prompts`: `PASS`

## Trace Summary

- Provider calls: `144 / 144`
- Provider failures: `0`
- Parse failures: `4`
- Admissible trace rows: `36 / 144`
- Tokens: `153015` input / `54284` output / `235287` total
- Prompt files hashed: `144`

## Selected Packet One-Shot Solo Baseline

- Strict admissible/KNEW: `0 / 18`
- Label correct: `3 / 18`
- Parse failures: `11`
- Provider failures: `0`
- Caveat: frozen solo triage used `openai/gpt-4o-mini` as the weak OpenAI solo slot; the 6-call ablation reprise used `openai/gpt-5.4-mini`.

## Self-reference note

The evidence root hashes primary evidence files and prompt files, excluding derived freeze/autopsy files to avoid recursive self-hashing.
