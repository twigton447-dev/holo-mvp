# BAL100 BEC-PAIR-005 Diagnostic Rescout Plan

Status: plan only. No scout run, provider call, Judge, QA, ablation, trace creation, packet edit, frozen artifact edit, or proof-credit change was performed.

## Scope

Prepare a narrow diagnostic rescout command for `BEC-PAIR-005` after the prompt/budget patch from commit `e08e75d`.

Target family:

- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`

## Current Runner Finding

Runner inspected:

`benchmark_factory/batches/run_BAL100_BATCH_001_five_mini_scout.py`

The current committed CLI does not support a BEC-PAIR-005-only live invocation. Its execution path loads all 16 draft packets from:

`holo_builder/outputs/builder/BAL100_BEC_PAIR_*_draft_v0_1.json`

and sends every packet to all five configured providers when `--execute-provider-calls` is used.

Therefore the narrowest currently supported live command is a full BAL100 Batch 001 scout, not a BEC-PAIR-005 diagnostic rescout. That command must not be used for this task.

## Exact Proposed Command

The exact proposed BEC-PAIR-005-only command is valid only after a minimal runner patch adds `--family-id` and `--out-dir` support:

```bash
BAL100_BATCH001_LOCAL_SCOUT_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION \
python3 -B benchmark_factory/batches/run_BAL100_BATCH_001_five_mini_scout.py \
  --execute-provider-calls \
  --operator Taylor \
  --i-am-taylor-local \
  --yes-send-draft-payloads-to-providers \
  --timeout 90 \
  --family-id BEC-PAIR-005 \
  --out-dir scout_runs/BAL100-BATCH-001_BEC-PAIR-005_diagnostic_rescout
```

Do not run this from Co/Codex. The active mandate says provider transmission should be prepared as a Taylor-local runbook unless explicitly approved otherwise.

## BEC-005-Only Confirmation

Confirmed BEC-005-only: no, not with the current committed runner.

Confirmed BEC-005-only after required minimal patch: yes, if `--family-id BEC-PAIR-005` filters loaded packets to these exact packet IDs before prompt-card creation and provider calls:

- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`

The patch must fail closed if the filtered set is not exactly two packets.

## Expected Output

Expected output directory after the required patch:

`scout_runs/BAL100-BATCH-001_BEC-PAIR-005_diagnostic_rescout/<timestamped_run_dir>/`

Expected files:

- `prompt_cards/BAL100-BEC-PAIR-005-ALLOW__openai__gpt-4o-mini.json`
- `prompt_cards/BAL100-BEC-PAIR-005-ALLOW__anthropic__claude-haiku-4-5-20251001.json`
- `prompt_cards/BAL100-BEC-PAIR-005-ALLOW__gemini__gemini-2.5-flash-lite.json`
- `prompt_cards/BAL100-BEC-PAIR-005-ALLOW__xai__grok-3-mini.json`
- `prompt_cards/BAL100-BEC-PAIR-005-ALLOW__minimax__MiniMax-Text-01.json`
- `prompt_cards/BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL__openai__gpt-4o-mini.json`
- `prompt_cards/BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL__anthropic__claude-haiku-4-5-20251001.json`
- `prompt_cards/BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL__gemini__gemini-2.5-flash-lite.json`
- `prompt_cards/BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL__xai__grok-3-mini.json`
- `prompt_cards/BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL__minimax__MiniMax-Text-01.json`
- `results.jsonl`
- `summary.json`

Expected record count: 10 result rows, representing 2 packets x 5 providers.

## Provider Roster

- `openai:gpt-4o-mini`
- `anthropic:claude-haiku-4-5-20251001`
- `gemini:gemini-2.5-flash-lite`
- `xai:grok-3-mini`
- `minimax:MiniMax-Text-01`

Provider subset selection is not supported by the current runner.

## Token Budget And Prompt Behavior

Current output token settings:

- Default providers: `DEFAULT_MAX_OUTPUT_TOKENS = 900`
- Anthropic: `ANTHROPIC_MAX_OUTPUT_TOKENS = 1200`

The prompt patch is already present. The system prompt now requires:

- compact JSON object only
- `verdict`, `rationale`, and `cited_artifacts`
- rationale of 1-3 concise sentences
- no markdown
- no numbered lists
- at most 5 cited artifact IDs
- no prose, code fences, or text outside JSON

Rationale suppression is not supported. The runner constrains rationale length but still asks for a rationale.

Dry-run or command-preview mode is not supported. The default non-execute path writes full-batch prompt cards and `scout_plan.json`, so it is not a BEC-005-only dry run.

## Old Failure Risk

This does not repeat the old 900-token Anthropic failure exactly after the patch, because Anthropic now receives `max_tokens = 1200` and the prompt asks for compact JSON with concise rationale. Residual risk remains if the model ignores the compact-response instruction, but the prior root cause is directly mitigated.

## Patch Recommendation Before Running

A code/config patch is required before a valid BEC-PAIR-005-only diagnostic rescout can be run from the committed runner.

Required minimal patch:

- add a family filter such as `--family-id BEC-PAIR-005`
- apply that filter before prompt-card creation and provider calls
- fail closed unless exactly the two BEC-PAIR-005 packet IDs are selected
- add an output directory override such as `--out-dir`
- preserve current fail-closed parser behavior
- preserve compact JSON prompt and Anthropic 1200-token cap

No packet patch, frozen artifact patch, parser broadening, proof-credit change, Judge, QA, ablation, or trace work is recommended before this diagnostic rescout.

## Stop Rules

Stop before running if:

- branch is not `holo-builder-freeze-manifest-gate-001`
- `git status --short` is not clean
- active mandate no longer allows this preparation path
- Taylor has not explicitly approved the diagnostic rescout
- the runner still lacks confirmed BEC-PAIR-005-only filtering
- the selected packet IDs are not exactly `BAL100-BEC-PAIR-005-ALLOW` and `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`
- the provider roster differs from the five configured mini providers unless Taylor explicitly scopes a provider subset
- required provider API keys are missing in Taylor-local environment
- output directory already exists and would overwrite prior artifacts
- any result is a provider operational failure or parser failure
- any output attempts to create traces, Judge artifacts, QA/ablation artifacts, packet edits, frozen artifact edits, or proof-credit changes

## Proof-Credit Impact

None. This plan does not change proof-credit accounting. `BEC-PAIR-009` and `BEC-PAIR-010` remain the only proof-credit-ready BAL100 Batch 001 families.
