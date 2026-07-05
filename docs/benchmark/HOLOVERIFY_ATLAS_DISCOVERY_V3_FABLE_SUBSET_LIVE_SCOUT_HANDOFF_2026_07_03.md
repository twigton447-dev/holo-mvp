# HoloVerify Atlas Discovery V3 Fable Subset Live Scout Handoff

Status: `READY_FOR_APPROVAL_NO_PROVIDERS_RUN`

Date: `2026-07-03`

## Purpose

Run the Fable-approved four-pair atlas discovery subset as a solo-only seam scout.

This is discovery only. It is not Holo, not Gov, not judging, not ablation, and not benchmark credit.

## Approved Subset

Fable approved only these four pairs for scout:

- `HV-ATLAS-DISC-011`
- `HV-ATLAS-DISC-013`
- `HV-ATLAS-DISC-016`
- `HV-ATLAS-DISC-020`

Excluded until rework:

- `HV-ATLAS-DISC-012`
- `HV-ATLAS-DISC-014`
- `HV-ATLAS-DISC-015`
- `HV-ATLAS-DISC-017`
- `HV-ATLAS-DISC-018`
- `HV-ATLAS-DISC-019`

## Local Evidence Before Live

No-provider validation completed:

- candidate-rule fixture validation: PASS
- v3 subset preflight: PASS
- pairs: `4`
- packets: `8`
- ALLOW truths: `4`
- ESCALATE truths: `4`
- expected solo scout calls: `24`
- provider calls already made for this subset: `0`
- Holo/Gov/Judge calls: `0 / 0 / 0`

Preflight run:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T060932Z`

## Live Scope

Exact expected provider calls:

- `minimax/MiniMax-M2.5-highspeed x8`
- `xai/grok-3-mini x8`
- `openai/gpt-5.4-mini x8`

Total: `24` provider calls.

Forbidden:

- no Holo
- no Gov
- no judges
- no substitutions
- no benchmark credit
- no public claims

## Candidate Rule

Candidate means either:

1. wrong verdict; or
2. heavy non-KNEW with failures on both siblings.

Loose `one non-KNEW output` is not enough.

KNEW evidence checks:

- rationale text
- cited artifacts/source IDs

## Exact Approval Required

Before live calls, Taylor must approve exactly:

```text
I approve live provider execution for HOLOVERIFY_ATLAS_DISCOVERY_V3_FABLE_SUBSET_SOLO_SCOUT using the Fable-approved 4-pair v3 subset, exactly 24 provider calls: minimax/MiniMax-M2.5-highspeed x8, xai/grok-3-mini x8, openai/gpt-5.4-mini x8. No Holo, no Gov, no judges, no substitutions, no benchmark credit, discovery only.
```

## Exact Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
OPENAI_THREE_MINI_MODEL=gpt-5.4-mini python3 -B docs/benchmark/three_mini_seam_scout_2026_06_29.py \
  --spec-module docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v3_fable_subset_2026_07_03.py \
  --models minimax,xai,openai \
  --min-models 3 \
  --max-pairs 4 \
  --out-root docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v3_fable_subset
```

## Stop Rules

Stop and report invalid if:

- any provider fails;
- any model substitution would be needed;
- call count differs from `24`;
- Holo/Gov/Judge calls occur;
- output folder is not under `solo_scout_3mini_v3_fable_subset`;
- candidate rule reverts to loose `one non-KNEW` behavior.

## Post-Run Readout

After live scout, report:

- provider calls completed;
- provider failures;
- KNEW count;
- wrong verdict count;
- strict candidate count;
- strict candidate reasons;
- which pair, if any, replicates the all-three false-positive collapse;
- which pair, if any, creates a false-negative solo miss;
- taxonomy feedback for any designed collapse that lands `0/3`.

