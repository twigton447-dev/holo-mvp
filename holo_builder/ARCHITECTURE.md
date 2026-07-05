# HoloBuild Architecture Contract

This file defines architecture-level invariants for HoloBuild-style runs. Project
fixtures may add stricter limits, but they must not weaken these defaults.

## Canonical Thread

HoloBuild is lossless across build turns. Each subsequent LLM call must receive
the complete canonical thread before it, including prior prompts, prior model
outputs, critiques, governor briefs, source records, rejected options, accepted
repairs, missing-evidence notes, claim-boundary warnings, and the current
candidate artifact.

A navigation index or section labels may be added for readability, but prior
canonical content must remain available verbatim. If the full canonical thread
cannot fit in the target model context, the run must stop and mark itself
blocked rather than silently summarizing, truncating, or dropping earlier turns.

## Live Research Budget

Live web research is permitted only under an explicit per-turn budget.

Default budget:

- Maximum 20 seconds of web research per turn.
- Maximum 120 seconds of total web research per lane unless a stricter project
  budget is declared.
- Maximum 8 search queries per lane unless a stricter project budget is
  declared.
- Maximum 12 opened pages per lane unless a stricter project budget is declared.

The runner must stop web research immediately when a turn reaches the 20-second
cap. If evidence is still missing, the model must proceed from the existing
packet and record the gap as missing evidence.

## Source Handling

Every live web finding used in an artifact must first be stored as a source
record with URL, title, source type, brand or publisher, accessed timestamp,
evidence snippet, confidence, reliability score or tier, evidence level, and
intended use.

Missing evidence must remain visible. HoloBuild must not launder missing source
coverage into a confident convention, claim, or recommendation.

## Trace Artifacts

The runner must persist enough trace material to audit the build:

- `canonical_thread.jsonl`
- `turn_inputs.jsonl`
- `turn_outputs.jsonl`
- `live_source_records.jsonl`
- final candidate artifact

These trace files are part of the HoloBuild architecture, not optional project
notes.
