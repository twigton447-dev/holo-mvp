# HoloVerify Atlas W3 Artifact-First Contract Patch

Status: `PATCHED_NO_PROVIDER_READY_FOR_EXACT_RERUN_APPROVAL`

This patch follows the no-provider autopsy:

`HOLOVERIFY_ATLAS_W3_EMPTY_TEXT_AUTOPSY_2026_07_03`

No providers, judges, solo calls, scoring, or reruns were performed by this patch.

## Root Failure Being Patched

Invalid run:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z`

Failure:

`W3_EMPTY_TEXT_AFTER_HIDDEN_THINKING_FILTER_AND_LENGTH_FINISH`

Autopsy root cause:

`MINIMAX_W3_HIDDEN_THINKING_RUNAWAY_ON_AMBIGUOUS_SOURCE_SEAM`

The final W3 call consumed `2048/2048` output tokens in hidden thinking and never emitted `worker_role=W3`. The validator correctly failed closed and no post-hoc scoring was run.

## Patch

Patched shared runner:

`holoverify_blind_runner_v0.py`

New worker contract version:

`WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03`

Worker contract hash:

`d5fdea3133f2bcdea0a9c16f1261081a8fe5ca8264f2a2f0a7e43d41c69a0320`

W3 artifact-first guard:

- `W3 ARTIFACT-FIRST CONTRACT V2.`
- `Start immediately with worker_role=W3 before any reasoning.`
- `Never output <think>, hidden reasoning, analysis, or deliberation.`
- `If the source seam is ambiguous, encode that only in verification_verdict, binding_class, open_blockers, and final_answer.`
- `Do not debate competing interpretations outside the key=value fields.`
- `Emit exactly the required key=value artifact lines, then stop.`

The user-side W3 prompt now also states:

- first visible output line must be `worker_role=W3`
- if uncertain, still emit the compact artifact immediately
- ambiguity must be represented only inside compact fields
- no explanatory analysis before or after the artifact

## What Did Not Change

- No packet text changed.
- No scoring map changed.
- No truth map changed.
- No selector policy changed.
- No parser permissiveness was added.
- Empty stripped text remains invalid.
- `finish_reason=length` remains invalid.
- Hidden-thinking-only output remains invalid.
- Content failures remain non-retryable.

## Summary Stamping

The live wrapper now stamps:

- `selector_policy`
- `worker_contract`
- `attempt_budget_policy`

into preflight and live summaries.

The Atlas approval sentence now binds both:

- selector version/hash
- W3 worker contract version/hash

so an old selector-only approval sentence cannot silently authorize the new contract.

## Fixtures Added

Updated:

`tests/test_holoverify_blind_canary_live_wrapper.py`

Fixtures:

- W3 hidden-thinking-only output strips to empty and fails closed.
- W3 hidden-thinking plus valid compact artifact passes after stripping.
- W3 prompt contains the artifact-first guard and ambiguity-field instruction.
- Canary preflight stamps worker contract version/hash.

Updated:

`tests/test_holoverify_blind_120_live_wrapper.py`

Fixture:

- 120 preflight stamps worker contract version/hash.

Updated:

`tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py`

Fixtures:

- Atlas approval sentence binds worker contract version/hash.
- Atlas preflight stamps worker contract version/hash.

Updated:

`tests/test_holoverify_blind_selector_repair_regression.py`

Fixture:

- Runtime fixture result stamps worker contract version/hash.

## No-Provider Validation

Commands run:

```bash
python3 -m py_compile holoverify_blind_runner_v0.py docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_selector_repair_regression.py tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py
python3 -m pytest tests/test_holoverify_blind_canary_live_wrapper.py::test_w3_hidden_thinking_only_strips_to_empty_and_fails_closed tests/test_holoverify_blind_canary_live_wrapper.py::test_w3_hidden_thinking_plus_valid_artifact_passes_after_strip tests/test_holoverify_blind_canary_live_wrapper.py::test_w3_prompt_uses_final_compiler_output_firewall tests/test_holoverify_blind_selector_repair_regression.py::test_runtime_result_stamps_selector_version_and_hash -q
python3 -m pytest tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py tests/test_holoverify_blind_selector_repair_regression.py -q
zsh -lc 'set -a; source .env; set +a; python3 -B docs/benchmark/run_holoverify_atlas_holo_rescue_live_2026_07_03.py --preflight'
```

Results:

- py_compile: `PASS`
- focused W3 fixtures: `4 passed`
- wrapper / selector / Atlas gate suite: `43 passed`
- fresh Atlas preflight: `PASS`
- provider calls: `0`
- judge calls: `0`

## Next Valid Move

A new exact rerun approval may be requested using the updated approval sentence below.

This rerun remains:

`PATCH VALIDATION ONLY`

It is not fresh benchmark evidence.

## Updated Exact Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_ATLAS_HOLO_RESCUE_6PAIR_RUNTIME_FIREWALL_V0 using freeze root d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da, runtime manifest 0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7, opaque packet indices 1-12 only, and exactly 60 provider calls: W1 xai/grok-3-mini x12, G1 minimax/MiniMax-M2.5-highspeed x12, W2 openai/gpt-5.4-mini x12, G2 minimax/MiniMax-M2.5-highspeed x12, W3 minimax/MiniMax-M2.5-highspeed x12. Selector policy SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03 hash 32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6. Worker contract WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03 hash d5fdea3133f2bcdea0a9c16f1261081a8fe5ca8264f2a2f0a7e43d41c69a0320. PATCH VALIDATION ONLY for SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03; not fresh benchmark evidence. No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims.
```
