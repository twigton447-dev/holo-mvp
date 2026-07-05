# HoloVerify Atlas 5-Failure 3-Model Majority Ensemble Ablation Lock

Status: `PREREGISTERED_NO_PROVIDERS`

Date: `2026-07-03`

## Purpose

This locks the canonical non-Holo orchestration comparator for the Atlas five-failure target set.

The comparator is not another worker chain. It is the common external ensemble pattern:

> Send the same packet independently to multiple models, then take the majority verdict.

This is the clean test of whether Full Holo is doing more than ordinary multi-model voting.

## Lane

`HOLOVERIFY_ATLAS_5FAIL_3MODEL_MAJORITY_ENSEMBLE_ABLATION_V0`

## Target Set

Use the five primary solo-failure pairs established in:

`docs/benchmark/HOLOVERIFY_ATLAS_5_SOLO_FAILURES_ESTABLISHED_2026_07_03.json`

Each pair includes both siblings, for `10` packets total:

| Pair | A sibling | B sibling |
| --- | --- | --- |
| `HV-ATLAS-DISC-020` | `ATLASRESCUE-4D29A82BECA21E67C3C8` | `ATLASRESCUE-5F4D2BECC8894EA1B843` |
| `HV-ATLAS-DISC-023` | `ATLASRESCUE-F9088C560DD2A436259C` | `ATLASRESCUE-A99C97DE339525880895` |
| `HV-ATLAS-DISC-025` | `ATLASRESCUE-E01246E499290B3163AD` | `ATLASRESCUE-AEA4A946BF50E7131481` |
| `HV-ATLAS-DISC-033` | `ATLASRESCUE-9D8631D7FB8017C6E397` | `ATLASRESCUE-93D992FE116415AEA6EE` |
| `HV-ATLAS-DISC-035` | `ATLASRESCUE-C3FCACEB77CC0CCEBF77` | `ATLASRESCUE-9917935F9BA192D89299` |

Frozen packet bank:

- Freeze root: `d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da`
- Runtime manifest: `docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/holoverify_atlas_holo_rescue_runtime_manifest_2026_07_03.json`
- Runtime manifest hash: `0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7`
- Scoring map hash, post-freeze only: `70ddcbcf5a32e4c1a75ebef563dd60c0514e3cc40eda90f5653ef80974661e19`

## Model Roster

Same three model families used in the Holo lane:

| Vote | Model |
| --- | --- |
| `M1` | `xai/grok-3-mini` |
| `M2` | `openai/gpt-5.4-mini` |
| `M3` | `minimax/MiniMax-M2.5-highspeed` |

Expected live calls:

- Packets: `10`
- Calls per packet: `3`
- Total provider calls: `30`

## Orchestration Rule

Each model receives the same model-visible packet independently.

Forbidden:

- no prior-turn summaries
- no continuity
- no state brief
- no Gov
- no Gov baton
- no routing lens
- no deterministic gate feedback before another model answers
- no artifact registry
- no best-artifact preservation
- no final selector other than the declared majority rule
- no judges
- no substitutions
- no scoring map before trace freeze

## Majority Rule

For each packet:

1. Run all three model calls independently.
2. Validate each output locally for parse/admissibility.
3. Valid votes are admissible `ALLOW` or `ESCALATE` verdicts.
4. Final ensemble verdict is the majority of valid votes.
5. If fewer than two valid votes agree, final ensemble result is `NO_ADMISSIBLE_MAJORITY`.
6. Model parse/admissibility failures remain model failures even if the packet-level ensemble verdict is correct.

Scoring is post-freeze only:

- First freeze raw prompts, raw provider outputs, trace rows, token accounting, and ensemble-vote ledger.
- Then load the scoring map.
- Then score packet correctness and pair correctness.

## Why This Is the Canonical Ablation

This is the real non-Holo orchestration comparator.

It answers:

> If we simply ask the same three models independently and let the majority win, does that recover the five solo-failure seams?

The earlier workers-only chain remains useful as a diagnostic, but it is not the main outside-world comparator because it added sequential continuity. Most existing multi-model voting systems do not preserve Holo-style state, baton, gates, or artifacts.

## Existing Comparison Anchors

Solo side:

- `docs/benchmark/HOLOVERIFY_ATLAS_5_SOLO_FAILURES_ESTABLISHED_2026_07_03.json`
- Requirement already met: at least one solo wrong-verdict failure per primary target.

Full Holo side:

- `docs/benchmark/HOLOVERIFY_ATLAS_SELECTOR_W3_PATCH_VALIDATION_RESULT_2026_07_03.json`
- Existing Full Holo result: `12/12` on the same-six packet set, including these five primary pairs plus spare `HV-ATLAS-DISC-036`.

Auxiliary workers-only side:

- `docs/benchmark/HOLOVERIFY_ATLAS_5FAIL_WORKERS_ONLY_ABLATION_RESULT_2026_07_03.json`
- Result: `7/10` packets, `2/5` pairs.
- This is diagnostic, not the canonical existing-orchestration comparator.

## Success Interpretation

If majority ensemble clears:

> The five seams do not separate Full Holo from ordinary three-model majority voting. We need harder seams or a different target set.

If majority ensemble fails where Full Holo passed:

> The five seams separate Full Holo from ordinary independent multi-model voting. Holo's lift is not explained by majority voting alone.

## Claim Boundary

Allowed internal language after a clean run:

> The Atlas five-failure target was tested against a locked three-model independent majority ensemble using the same models as Full Holo.

Forbidden until after execution and post-freeze scoring:

- claim that majority ensemble failed
- claim that Holo beats majority ensemble on this set
- public benchmark rate
- confidence interval claim
- universal Holo superiority claim
- claim that Gov alone explains lift

