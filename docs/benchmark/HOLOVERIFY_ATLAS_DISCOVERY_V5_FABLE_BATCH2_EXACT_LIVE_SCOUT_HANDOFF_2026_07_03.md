# HoloVerify Atlas Discovery V5 Exact Fable Batch-2 Scout Handoff

Status: `READY_FOR_APPROVAL_NO_PROVIDERS_RUN`

Date: `2026-07-03`

## Purpose

Run the exact Fable Batch-2 first scout after reconciling the provisional V4 mapping.

This is discovery only:

- no Holo
- no Gov
- no judges
- no substitutions
- no benchmark credit
- no public claim

## Scope

Five sibling pairs, ten packets, three solo mini models per packet.

Expected calls:

- `30` total provider calls
- `minimax/MiniMax-M2.5-highspeed x10`
- `xai/grok-3-mini x10`
- `openai/gpt-5.4-mini x10`

## Exact Scout Pairs

| Fable ID | Local Pair | Truth shape | Purpose |
| --- | --- | --- | --- |
| `NFP-2` | `HV-ATLAS-DISC-026` | ALLOW sibling + ESCALATE sibling | Duplicate-payment system alert on legitimate installment billing |
| `NFP-9` | `HV-ATLAS-DISC-027` | ALLOW sibling + ESCALATE sibling | After-hours flag on scheduled batch |
| `NFN-1` | `HV-ATLAS-DISC-028` | ALLOW sibling + ESCALATE sibling | EUR vs USD with identical numerals |
| `NFN-2` | `HV-ATLAS-DISC-029` | ALLOW sibling + ESCALATE sibling | Timezone conversion across approval window |
| `NFN-8` | `HV-ATLAS-DISC-030` | ALLOW sibling + ESCALATE sibling | Refund exceeding remaining balance |

## No-Provider Validation

Completed:

- `py_compile`: `PASS`
- preflight: `PASS`
- pairs: `5`
- packets: `10`
- ALLOW truths: `5`
- ESCALATE truths: `5`
- expected solo scout calls: `30`
- forbidden model-visible terms: `0`
- provider calls already made for V5: `0`

Preflight:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T062818Z/ATLAS_DISCOVERY_PREFLIGHT.json`

## Candidate Rule

A pair becomes a strict scout candidate only after at least three completed mini-model probes and either:

1. at least one completed mini output has the wrong verdict, or
2. at least three completed mini outputs are unproven/malformed with failures present on both siblings.

Loose one-off non-KNEW does not promote a pair.

## Exact Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_ATLAS_DISCOVERY_V5_FABLE_BATCH2_EXACT_SOLO_SCOUT using the exact 5-pair Fable Batch-2 scout, exactly 30 provider calls: minimax/MiniMax-M2.5-highspeed x10, xai/grok-3-mini x10, openai/gpt-5.4-mini x10. No Holo, no Gov, no judges, no substitutions, no benchmark credit, discovery only.
```

## Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
OPENAI_THREE_MINI_MODEL=gpt-5.4-mini python3 -B docs/benchmark/three_mini_seam_scout_2026_06_29.py \
  --spec-module docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v5_fable_batch2_exact_2026_07_03.py \
  --models minimax,xai,openai \
  --min-models 3 \
  --max-pairs 5 \
  --out-root docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v5_fable_batch2_exact
```

## Stop Rules

Stop and report invalid if:

- any provider call fails
- any model substitution is needed
- provider call count is not exactly `30`
- any Holo/Gov/judge call occurs
- output folder is not the V5 output folder
- candidate rule reverts to loose non-KNEW

