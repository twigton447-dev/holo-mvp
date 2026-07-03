# HoloVerify Atlas Discovery V6B Fixed-034 Rescout Handoff

Status: `READY_FOR_APPROVAL_NO_PROVIDERS_RUN`

Date: `2026-07-03`

## Purpose

Rescout the corrected version of `HV-ATLAS-DISC-034`.

Fable found original `034` unfair because its clean A-side included a prior release of exactly `USD 18000`, identical to the requested draw. That made a duplicate-payment concern plausible.

The fixed rescout changes the A-side prior release value:

- old A-side prior release: `USD 18000`
- fixed A-side prior release: `USD 19500`

New pair ID:

- `HV-ATLAS-DISC-036`

## Scope

One sibling pair, two packets, three solo mini models per packet.

Expected calls:

- `6` total provider calls
- `minimax/MiniMax-M2.5-highspeed x2`
- `xai/grok-3-mini x2`
- `openai/gpt-5.4-mini x2`

No Holo. No Gov. No judges. No substitutions. No benchmark credit.

## No-Provider Validation

Completed:

- `py_compile`: `PASS`
- preflight: `PASS`
- pairs: `1`
- packets: `2`
- ALLOW truths: `1`
- ESCALATE truths: `1`
- expected solo scout calls: `6`
- provider calls already made for this fixed rescout: `0`

Preflight:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T103132Z/ATLAS_DISCOVERY_PREFLIGHT.json`

## Candidate Rule

A pair becomes a candidate if:

1. at least one completed solo output has the wrong verdict, or
2. at least three completed solo outputs are unproven/malformed with failures present on both siblings.

Loose one-off non-KNEW does not count.

## Exact Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_ATLAS_DISCOVERY_V6B_FIX034_SOLO_RESCOUT using the fixed one-pair 034 rescout, exactly 6 provider calls: minimax/MiniMax-M2.5-highspeed x2, xai/grok-3-mini x2, openai/gpt-5.4-mini x2. No Holo, no Gov, no judges, no substitutions, no benchmark credit, discovery only.
```

## Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
OPENAI_THREE_MINI_MODEL=gpt-5.4-mini python3 -B docs/benchmark/three_mini_seam_scout_2026_06_29.py \
  --spec-module docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v6b_fix034_2026_07_03.py \
  --models minimax,xai,openai \
  --min-models 3 \
  --max-pairs 1 \
  --out-root docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v6b_fix034
```

