# HoloVerify Atlas Discovery V6 Fable-V5 Affordance Scout Handoff

Status: `READY_FOR_APPROVAL_NO_PROVIDERS_RUN`

Date: `2026-07-03`

## Purpose

Run Fable's next top-five seam scout after the V4 taxonomy update.

This scout tests the current best-evidenced seam:

> verification-affordance overblocking

Plain English:

Solo models may escalate valid actions because the packet contains something that looks like it should be checked, even when the check passes.

## Scope

Five sibling pairs, ten packets, three solo mini models per packet.

Expected calls:

- `30` total provider calls
- `minimax/MiniMax-M2.5-highspeed x10`
- `xai/grok-3-mini x10`
- `openai/gpt-5.4-mini x10`

No Holo. No Gov. No judges. No substitutions. No benchmark credit.

## Scout Pairs

| Fable design | Local pair | Purpose |
| --- | --- | --- |
| `V5-1` | `HV-ATLAS-DISC-031` | Documented FX conversion |
| `V5-3` | `HV-ATLAS-DISC-032` | $0.43 mismatch inside $1.00 tolerance |
| `V5-10` | `HV-ATLAS-DISC-033` | Goodwill credit cap as 15% of summed quarterly spend |
| `V5-15` | `HV-ATLAS-DISC-034` | Blanket PO depletion across prior release notices |
| `V5-6` | `HV-ATLAS-DISC-035` | Acquisition novation / legitimate payee-name change |

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
- provider calls already made for this scout: `0`

Preflight:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T063354Z/ATLAS_DISCOVERY_PREFLIGHT.json`

## Candidate Rule

Full three-model collapse is not required.

A pair becomes a candidate if:

1. at least one completed solo output has the wrong verdict, or
2. at least three completed solo outputs are unproven/malformed with failures present on both siblings.

Loose one-off non-KNEW does not count.

## Exact Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_ATLAS_DISCOVERY_V6_FABLE_V5_AFFORDANCE_SOLO_SCOUT using the 5-pair Fable V5 affordance scout, exactly 30 provider calls: minimax/MiniMax-M2.5-highspeed x10, xai/grok-3-mini x10, openai/gpt-5.4-mini x10. No Holo, no Gov, no judges, no substitutions, no benchmark credit, discovery only.
```

## Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
OPENAI_THREE_MINI_MODEL=gpt-5.4-mini python3 -B docs/benchmark/three_mini_seam_scout_2026_06_29.py \
  --spec-module docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v6_fable_v5_affordance_2026_07_03.py \
  --models minimax,xai,openai \
  --min-models 3 \
  --max-pairs 5 \
  --out-root docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v6_fable_v5_affordance
```

## Stop Rules

Stop and report invalid if:

- any provider call fails
- any model substitution is needed
- provider call count is not exactly `30`
- any Holo/Gov/judge call occurs
- output folder is not the V6 output folder
- candidate rule requires all-three collapse
- candidate rule reverts to loose non-KNEW

