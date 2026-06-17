# HoloBuild Frontier Model Policy Audit

**Date:** 2026-06-17  
**Repo:** `/Users/taylorwigton/CascadeProjects/holo-mvp`  
**Branch:** `holo-builder-freeze-manifest-gate-001`  
**Observed HEAD:** `56c5522 freeze: lock HBB-BEC-002 hard callback pair`  
**Status:** CLEAN_REPORT_ONLY

## Scope

This audit separates HoloBuild from the mini 4DNA benchmark lane:

- **HoloBuild:** builder, artifact generation, packet refinement, QA attacker surfaces.
- **Mini benchmark lane:** `ablation_cohort_mini.json`, `holo_builder/frozen_4dna_runner.py`, 4DNA mini tests, dry-run/live trace infrastructure, and committed trace/report artifacts.

No live calls, traces, Judge, QA, ablation, freeze, packet edits, frozen edits, or push were performed.

## Answers

1. **Does HoloBuild currently have any mini model configured as builder/generator/refiner/default?**  
   No. No active HoloBuild path was found using `gpt-4o-mini`, `claude-haiku-4-5-20251001`, `gemini-2.5-flash-lite`, `grok-3-mini`, or `MiniMax-Text-01` as a builder/generator/refiner/default.

2. **Are mini models isolated to the 4DNA benchmark lane?**  
   Yes for committed defaults and current code paths. Mini models appear in the explicit mini cohort, frozen 4DNA runner, related tests, and existing committed trace/report artifacts.

3. **Are HoloBuild defaults explicitly frontier-only?**  
   Yes for the active HoloBuild adapter defaults. `holo_builder/loop.py` and `holo_builder/qa_attacker.py` construct `OpenAIAdapter`, `AnthropicAdapter`, and `GoogleAdapter` directly. Their defaults in `llm_adapters.py` are `gpt-5.4`, `claude-sonnet-4-6`, and `gemini-2.5-pro`.

4. **Any ambiguous shared config that could let mini models leak into HoloBuild?**  
   No active leak was found. The shared `llm_adapters.py` file does contain bench/fast registries with mini or low-cost models, but HoloBuild does not call `load_adapters` or `load_fast_adapters`. Operational caveat: `OPENAI_MODEL`, `ANTHROPIC_MODEL`, and `GOOGLE_MODEL` can override direct adapter defaults at runtime, so frontier-only is a committed default policy, not a runtime allowlist.

5. **Are tests/docs aligned?**  
   Mostly. The mini lane has static fail-closed tests. The default frontier cohort exists. No docs or tests were found that make mini models the HoloBuild builder default.

6. **What files contain model names?**  
   Relevant model strings were found in:

   - `ablation_cohort_default.json`
   - `ablation_cohort_mini.json`
   - `holo_builder/frozen_4dna_runner.py`
   - `llm_adapters.py`
   - `config.py`
   - `bot.py`
   - `native_solo_probe.py`
   - `d5_native_solo_probe.py`
   - `test_ablation_cohort_mini_static.py`
   - `test_holo_builder_frozen_4dna_runner.py`
   - `test_lifecycle.py`
   - `BENCHMARK_README.md`
   - `docs/benchmark/FP_TRACES_2026-05-28.md`
   - `docs/benchmark/TRACE_REPORT_2026-05-28.md`
   - `ledger/hargrove_bec_allow_001_freeze_record.json`
   - `reports/HBB_BEC_001_pair_4dna_seed447_judge_summary.json`
   - `reports/HBB_BEC_001_pair_4dna_seed447_judge_summary.md`
   - `traces/HBB-BEC-001_pair_4dna_seed447/HBB-BEC-001_8181d83c_4dna_trace.json`
   - `traces/HBB-BEC-001_pair_4dna_seed447/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc_4dna_trace.json`

7. **What changes are required?**  
   No required code/config changes. Optional future hardening would add a HoloBuild-only frontier allowlist around env overrides.

## Key Evidence

- `holo_builder/loop.py` constructs only `OpenAIAdapter`, `AnthropicAdapter`, and `GoogleAdapter` for `run_builder`.
- `holo_builder/qa_attacker.py` constructs only `OpenAIAdapter`, `AnthropicAdapter`, and `GoogleAdapter` for QA attack execution.
- `llm_adapters.py` direct adapter defaults are:
  - `OPENAI_MODEL` fallback: `gpt-5.4`
  - `ANTHROPIC_MODEL` fallback: `claude-sonnet-4-6`
  - `GOOGLE_MODEL` fallback: `gemini-2.5-pro`
- `ablation_cohort_default.json` uses the same frontier trio.
- `ablation_cohort_mini.json` and `holo_builder/frozen_4dna_runner.py` define the approved five-mini lane separately.

## Conclusion

HoloBuild is clean under committed defaults. Mini models are isolated to the 4DNA benchmark lane and historical trace/report artifacts. No patch was required.
