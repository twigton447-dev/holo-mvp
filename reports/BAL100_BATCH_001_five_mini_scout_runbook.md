# BAL100 Batch 001 Five-Mini Solo Scout Runbook

Status: draft-scout runbook  
Batch: BAL100-BATCH-001  
Scope: BEC callback provenance draft packets, BEC-PAIR-003 through BEC-PAIR-010  
Benchmark credit: false

## Purpose

This scout is a prefreeze diagnostic only. It is meant to find collapse, model disagreement, too-easy packets, and the best candidates to repair, discard, or promote into prefreeze review.

It is not Judge truth, not proof credit, not an official benchmark trace, and not an ablation.

## Draft Inputs

```text
holo_builder/outputs/builder/BAL100_BEC_PAIR_003_ALLOW_draft_v0_1.json
holo_builder/outputs/builder/BAL100_BEC_PAIR_003_ESCALATE_draft_v0_1.json
...
holo_builder/outputs/builder/BAL100_BEC_PAIR_010_ALLOW_draft_v0_1.json
holo_builder/outputs/builder/BAL100_BEC_PAIR_010_ESCALATE_draft_v0_1.json
```

Expected count:

```text
8 ALLOW
8 ESCALATE
16 total draft packets
```

## Scout Models

```text
OpenAI gpt-4o-mini
Anthropic claude-haiku-4-5-20251001
Google gemini-2.5-flash-lite
xAI grok-3-mini
MiniMax MiniMax-Text-01
```

No HoloGov. No Judge. No QA Attacker. No ablation.

## Hard Boundary

Do not run provider calls from Co. If this scout is run, Taylor should run it manually in a local Mac Terminal session after explicitly approving provider transmission for these 16 draft payloads.

Scout output, if generated, belongs only under:

```text
scout_runs/BAL100-BATCH-001_five_mini_solo_scout/
```

## Local Preparation Commands

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp
pwd
git branch --show-current
git status --short
cat docs/HOLO_ACTIVE_MANDATE.md
python3 -m py_compile benchmark_factory/batches/run_BAL100_BATCH_001_five_mini_scout.py
python3 benchmark_factory/batches/run_BAL100_BATCH_001_five_mini_scout.py
```

The script above prepares payload-only prompt cards and a non-benchmark scout plan. It does not call providers.

## Manual Scout Result Schema

Each packet/model result should be recorded with:

```json
{
  "batch_id": "BAL100-BATCH-001",
  "benchmark_credit": false,
  "packet_id": "BAL100-BEC-PAIR-003-ALLOW",
  "builder_hypothesis": "ALLOW",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "model_verdict": "ALLOW",
  "rationale": "Short artifact-cited rationale",
  "called_at": "manual timestamp"
}
```

## Summary Fields

After all manual scout calls, summarize:

```text
packet_id
builder_hypothesis
model verdicts
wrong_allow_count
wrong_escalate_count
collapse_count
model_disagreement
too_easy_packets
best_promote_candidates
repair_candidates
discard_candidates
benchmark_credit: false
```

## Interpretation Rules

Packets with unanimous correct mini verdicts may be too easy and should be inspected before prefreeze.

Packets with model disagreement and crisp artifact-grounded rationales are stronger promotion candidates.

Any ESCALATE sibling missed by multiple models should be autopsied for callback-source provenance salience before prefreeze.

Any ALLOW sibling falsely escalated by multiple models should be inspected for accidental second blockers or overly scary trigger language.
