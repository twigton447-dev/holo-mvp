# HoloVerify Provider-Enabled Execution Handoff

Created: 2026-07-06

Status: no-provider handoff only. This document does not create a live result.

## Purpose

This handoff gives Taylor one safe checklist for running provider-backed lanes from an approved provider-enabled environment. The current Codex environment blocked both live attempts before any external provider call, so these lanes remain ready but unexecuted here.

Run one lane at a time. Preserve the first run before starting the second.

## General Execution Rules

- Do not edit runtime manifests or runtime payloads.
- Do not run both lanes in the same terminal session without preserving the first result.
- Do not rerun failed content attempts into a clean result.
- Preserve invalid, blocked, transport-failure, or partial traces separately.
- Score only after trace freeze.
- Do not load scoring maps before trace freeze.
- Do not use substitutions.
- Do not make public claims from these runs.
- Send back the run folder path, live summary, TRACE_PROVIDER_CALLS hash, raw output count, and post-hoc score JSON/MD.

## Lane 1: V7 Tiny Patch Validation

Lane name: `HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_V0`

Status:

- Preflight committed.
- Live attempt blocked before calls in the Codex environment.
- No live result exists.

Runtime manifest:

- Path: `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- SHA-256: `f1f55f0c5b69f8bffa9c9a770f1b21a845e51e7bab5b810156f799175e213db8`

Selector:

- Version: `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05`
- SHA-256: `f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d`

Worker contract:

- Version: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`

Expected provider calls:

- Total: `30`
- `W1 xai/grok-3-mini x6`
- `G1 minimax/MiniMax-M2.5-highspeed x6`
- `W2 openai/gpt-5.4-mini x6`
- `G2 minimax/MiniMax-M2.5-highspeed x6`
- `W3 minimax/MiniMax-M2.5-highspeed x6`

Exact approval sentence:

```text
I approve live provider execution for HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 f1f55f0c5b69f8bffa9c9a770f1b21a845e51e7bab5b810156f799175e213db8, selector SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05 hash f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 30 provider calls: W1 xai/grok-3-mini x6, G1 minimax/MiniMax-M2.5-highspeed x6, W2 openai/gpt-5.4-mini x6, G2 minimax/MiniMax-M2.5-highspeed x6, W3 minimax/MiniMax-M2.5-highspeed x6. TINY PATCH VALIDATION ONLY for V7 false-blocker suppression and affirmative closure behavior across three Wave 1 failed ALLOW fixtures plus their matching ESCALATE negative controls; not public benchmark evidence, not a Holo win, not a global FPR/FNR claim, not FP precision evidence, and not production safety certification. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```

Live wrapper:

- Path: `docs/benchmark/run_holoverify_v7_false_blocker_suppression_tiny_patch_validation_live_2026_07_05.py`
- Command:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
APPROVAL='I approve live provider execution for HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 f1f55f0c5b69f8bffa9c9a770f1b21a845e51e7bab5b810156f799175e213db8, selector SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05 hash f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 30 provider calls: W1 xai/grok-3-mini x6, G1 minimax/MiniMax-M2.5-highspeed x6, W2 openai/gpt-5.4-mini x6, G2 minimax/MiniMax-M2.5-highspeed x6, W3 minimax/MiniMax-M2.5-highspeed x6. TINY PATCH VALIDATION ONLY for V7 false-blocker suppression and affirmative closure behavior across three Wave 1 failed ALLOW fixtures plus their matching ESCALATE negative controls; not public benchmark evidence, not a Holo win, not a global FPR/FNR claim, not FP precision evidence, and not production safety certification. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.'
python3 docs/benchmark/run_holoverify_v7_false_blocker_suppression_tiny_patch_validation_live_2026_07_05.py --run-live --approval-statement "$APPROVAL"
```

Post-hoc scorer:

- Path: `docs/benchmark/score_holoverify_v7_false_blocker_suppression_tiny_patch_validation_posthoc_2026_07_05.py`
- Command after trace freeze:

```bash
python3 docs/benchmark/score_holoverify_v7_false_blocker_suppression_tiny_patch_validation_posthoc_2026_07_05.py --run-dir <RUN_DIR>
```

Expected output folder:

- Pattern: `docs/benchmark/holoverify_v7_false_blocker_suppression_tiny_patch_validation_2026_07_05/live_runs/run_<UTCSTAMP>/`

Post-run artifacts to send back:

- Run folder path.
- `blind_canary_live_summary.json`
- `v7_false_blocker_suppression_tiny_patch_validation_live_summary.json`
- `TRACE_CALLS.jsonl`
- `TRACE_PROVIDER_CALLS.jsonl`
- `raw_provider_outputs/`
- `blind_canary_runtime_results.json`
- `v7_false_blocker_suppression_tiny_patch_validation_posthoc_score_trace_bound_v0.json`
- Any generated post-hoc Markdown report, if present.

Claim boundary:

- Tiny patch validation only.
- Not public benchmark evidence.
- Not a Holo win.
- Not a global FPR/FNR claim.
- Not FP precision evidence.
- Not production safety certification.

## Lane 2: Wave 2 Solo Scout

Lane name: `HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_SOLO_SCOUT_V0`

Status:

- Design and freeze committed.
- Live attempt blocked before calls in the Codex environment.
- No Wave 2 solo result exists.

Runtime manifest:

- Path: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json`
- SHA-256: `428bdd3e1e24e2538bfc6e37989ff741e3efa2749da7dc3b86c863ead90fb39c`

Expected provider calls:

- Total: `180`
- `xai/grok-3-mini x60`
- `openai/gpt-5.4-mini x60`
- `minimax/MiniMax-M2.5-highspeed x60`

Exact approval sentence:

```text
I approve live provider execution for HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_SOLO_SCOUT_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json with SHA-256 428bdd3e1e24e2538bfc6e37989ff741e3efa2749da7dc3b86c863ead90fb39c, and exactly 180 solo provider calls: xai/grok-3-mini x60, openai/gpt-5.4-mini x60, minimax/MiniMax-M2.5-highspeed x60. SOLO SCOUT ONLY for stress-matrix expansion Wave 2 across 30 sibling pairs / 60 packets; not Holo rescue, not public benchmark evidence, not a global FPR/FNR claim, and not natural production rate evidence. No Holo, no Gov, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```

Live runner status:

- Local support artifact path: `docs/benchmark/run_holoverify_stress_matrix_expansion_wave2_solo_scout_2026_07_06.py`
- Commit status: prepared but left uncommitted after the Codex policy block.
- Operator note: the design, freeze, runtime manifest, and blocked-attempt note are committed. This live runner must be supplied from the local working tree, recreated from the committed freeze package, or committed separately before use in another environment.

If the prepared local support runner is used, command:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
APPROVAL='I approve live provider execution for HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_SOLO_SCOUT_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json with SHA-256 428bdd3e1e24e2538bfc6e37989ff741e3efa2749da7dc3b86c863ead90fb39c, and exactly 180 solo provider calls: xai/grok-3-mini x60, openai/gpt-5.4-mini x60, minimax/MiniMax-M2.5-highspeed x60. SOLO SCOUT ONLY for stress-matrix expansion Wave 2 across 30 sibling pairs / 60 packets; not Holo rescue, not public benchmark evidence, not a global FPR/FNR claim, and not natural production rate evidence. No Holo, no Gov, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.'
python3 -B docs/benchmark/run_holoverify_stress_matrix_expansion_wave2_solo_scout_2026_07_06.py --run-live --approval-statement "$APPROVAL"
```

Post-hoc scorer status:

- Local support artifact path: `docs/benchmark/score_holoverify_stress_matrix_expansion_wave2_solo_scout_2026_07_06.py`
- Commit status: prepared but left uncommitted after the Codex policy block.

If the prepared local support scorer is used, command after trace freeze:

```bash
python3 -B docs/benchmark/score_holoverify_stress_matrix_expansion_wave2_solo_scout_2026_07_06.py --run-dir <RUN_DIR>
```

Expected output folder if the prepared support runner is used:

- Pattern: `docs/benchmark/holoverify_stress_matrix_expansion_wave2_solo_scout_runs_2026_07_06/run_<UTCSTAMP>/`

Post-run artifacts to send back:

- Run folder path.
- `solo_one_shot_live_summary.json`
- `solo_one_shot_live_summary.md`
- `solo_one_shot_runtime_results.json`
- `TRACE_PROVIDER_CALLS.jsonl`
- `raw_provider_outputs/`
- `prompts/`
- `stress_matrix_wave2_solo_posthoc_score.json`
- `stress_matrix_wave2_solo_posthoc_score.md`
- `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_SOLO_ROLLUP_2026_07_06.json`, if generated.
- `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE2_SOLO_ROLLUP_2026_07_06.md`, if generated.

Claim boundary:

- Solo scout only.
- Not Holo rescue.
- Not public benchmark evidence.
- Not a global FPR/FNR claim.
- Not natural production-rate evidence.
- No public claims.

## Return Checklist

For each executed lane, send HoloOps and HoloMiner:

- The exact lane name.
- The run folder path.
- The observed provider call count.
- Provider failures, if any.
- The SHA-256 of `TRACE_PROVIDER_CALLS.jsonl`.
- The raw provider output count.
- The live summary path and SHA-256.
- The post-hoc score JSON/MD paths and SHA-256 values.
- Any blocked, invalid, partial, transport-failure, or control-failure status.
- A statement confirming no scoring map was loaded before trace freeze.

