# HoloVerify Atlas Discovery V4 Fable Bank Live Scout Handoff

Status: `READY_FOR_APPROVAL_NO_PROVIDERS_RUN`

Date: `2026-07-03`

## Purpose

Run the first Fable seam-bank v4 scout.

This scout tests the updated seam-mining thesis:

1. False-positive vein: do solo models over-defer to non-human warning-shaped artifacts?
2. False-negative vein: do solo models miss unit, currency, timezone, or remaining-balance mismatches when the surface looks administratively complete?

This is discovery only. It is not Holo, not Gov, not judging, not ablation, and not benchmark credit.

## Scout Pairs

| Fable ID | Local Pair | Vein | Test |
| --- | --- | --- | --- |
| `NFP-2` | `HV-ATLAS-DISC-021` | Non-human alarm FP | After-hours system flag on legitimate scheduled batch. |
| `NFP-9` | `HV-ATLAS-DISC-022` | Non-human alarm FP | BEC/rebrand surface with executed change-control. |
| `NFN-1` | `HV-ATLAS-DISC-023` | Unit-blindness FN | EUR vs USD with identical numerals. |
| `NFN-2` | `HV-ATLAS-DISC-024` | Unit-blindness FN | Timezone math puts execution outside the approval window. |
| `NFN-8` | `HV-ATLAS-DISC-025` | Unit-blindness FN | Refund exceeds remaining balance after buried partial refund. |

## Local Evidence Before Live

No-provider validation completed:

- v4 spec py_compile: PASS
- v4 preflight: PASS
- pairs: `5`
- packets: `10`
- ALLOW truths: `5`
- ESCALATE truths: `5`
- expected solo scout calls: `30`
- provider calls already made for v4: `0`
- Holo/Gov/Judge calls: `0 / 0 / 0`

Preflight run:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T061635Z`

## Live Scope

Exact expected provider calls:

- `minimax/MiniMax-M2.5-highspeed x10`
- `xai/grok-3-mini x10`
- `openai/gpt-5.4-mini x10`

Total: `30` provider calls.

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

## Taxonomy Rule

If a designed collapse lands `0/3`, report that directly as taxonomy feedback.

Do not quietly drop it.

Do not loosen the candidate rule to make it look better.

## Exact Approval Required

Before live calls, Taylor must approve exactly:

```text
I approve live provider execution for HOLOVERIFY_ATLAS_DISCOVERY_V4_FABLE_BANK_SOLO_SCOUT using the 5-pair Fable seam-bank scout, exactly 30 provider calls: minimax/MiniMax-M2.5-highspeed x10, xai/grok-3-mini x10, openai/gpt-5.4-mini x10. No Holo, no Gov, no judges, no substitutions, no benchmark credit, discovery only.
```

## Exact Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
OPENAI_THREE_MINI_MODEL=gpt-5.4-mini python3 -B docs/benchmark/three_mini_seam_scout_2026_06_29.py \
  --spec-module docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v4_fable_bank_2026_07_03.py \
  --models minimax,xai,openai \
  --min-models 3 \
  --max-pairs 5 \
  --out-root docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v4_fable_bank
```

## Stop Rules

Stop and report invalid if:

- any provider fails;
- any model substitution would be needed;
- call count differs from `30`;
- Holo/Gov/Judge calls occur;
- output folder is not under `solo_scout_3mini_v4_fable_bank`;
- candidate rule reverts to loose `one non-KNEW` behavior.

## Post-Run Readout

After live scout, report:

- provider calls completed;
- provider failures;
- KNEW count;
- wrong verdict count;
- strict candidate count;
- strict candidate reasons;
- which NFP pairs, if any, produce false-positive over-escalation;
- which NFN pairs, if any, produce false-negative false-ALLOW;
- where the arithmetic/unit-blindness ladder stops;
- taxonomy feedback for any designed collapse that lands `0/3`.

