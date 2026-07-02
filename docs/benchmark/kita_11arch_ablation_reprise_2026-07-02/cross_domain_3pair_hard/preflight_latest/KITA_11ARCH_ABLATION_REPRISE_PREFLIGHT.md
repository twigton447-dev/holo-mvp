# Kit A 11-Architecture Ablation Reprise Preflight

Status: `PASS`

No provider calls, Gov calls, Holo calls, solo reruns, judges, packet edits, or prompt edits were made.

## Scope

- Label: `cross_domain_3pair_hard`
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- Selected pairs: `HV-AP-REP-011, HV-ACOM-REP-020, HV-ITAC-REP-018`
- Selected packets: `6`
- Expected provider calls if later approved: `144`
- Expected Gov calls: `0`
- Approval packet SHA-256: `5d1f1edd100e9c7ca816b765910d3212f0e929d9bee8656b8ac176a06bde96fd`

## Fairness Frame

- Provider-balanced no-Gov ablation fairness.
- Calls per packet per architecture: `6`
- Turns per model per packet per architecture: `2`
- Holo's original governed path used 5 calls per packet; this 6-call reprise slightly favors the ablations.

## Architectures

- `provider_balanced_reconsider_no_gov_6call`
- `provider_balanced_vote_no_gov_6call`
- `provider_balanced_council_no_gov_6call`
- `provider_balanced_debate_no_gov_6call`

## Model Roster

- `xai/grok-3-mini` (xai)
- `openai/gpt-5.4-mini` (openai)
- `minimax/MiniMax-M2.5-highspeed` (minimax)

## Checks

- `freeze_root_matches`: `PASS`
- `packet_hashes_match`: `PASS`
- `prompt_hashes_match`: `PASS`
- `model_visible_payload_hashes_match`: `PASS`
- `selected_pairs_have_two_siblings`: `PASS`
- `provider_balanced_two_turns_each_model`: `PASS`
- `no_prompt_leakage`: `PASS`
- `no_gov_context_in_call_plan`: `PASS`
- `no_holo_state_in_call_plan`: `PASS`
- `no_artifact_registry_in_call_plan`: `PASS`
- `no_final_selector_in_call_plan`: `PASS`
- `provider_calls_made`: `PASS`
- `judge_calls_made`: `PASS`

## Selected Packets

- `HV-ACOM-REP-020-A` / `ALLOW` / `Agentic commerce / order execution controls` / `HV-ACOM-REP-020`
- `HV-ACOM-REP-020-B` / `ESCALATE` / `Agentic commerce / order execution controls` / `HV-ACOM-REP-020`
- `HV-AP-REP-011-A` / `ALLOW` / `AP / procurement / vendor-master controls` / `HV-AP-REP-011`
- `HV-AP-REP-011-B` / `ESCALATE` / `AP / procurement / vendor-master controls` / `HV-AP-REP-011`
- `HV-ITAC-REP-018-A` / `ALLOW` / `IT access / permission change controls` / `HV-ITAC-REP-018`
- `HV-ITAC-REP-018-B` / `ESCALATE` / `IT access / permission change controls` / `HV-ITAC-REP-018`

## Boundaries

- This is a no-Gov diagnostic plan.
- No-Gov architectures must not receive Gov baton, Holo state, Blindspot Atlas, artifact registry, or final selector.
- Existing one-shot solo results should be carried forward where already frozen instead of rerun.
- Deterministic policy gate, if tested later, must be reported separately from model architectures.
