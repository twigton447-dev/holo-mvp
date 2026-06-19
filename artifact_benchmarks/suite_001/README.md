# Artifact Suite 001

Suite 001 is the planned multi-domain version of the artifact benchmark.

The suite asks whether Holo's Governor-orchestrated adversarial loop creates measurable artifact-quality lift over solo recursive runs under the same source context, turn budget, role sequence, word band, and blinded judging process.

## Lanes

- `frontier_3_model_main`: GPT + Opus + Gemini Holo versus the same three solo baselines.
- `frontier_2_model_ablation`: GPT + Opus Holo versus GPT solo and Opus solo.
- `mini_3_model_cost_lane`: three mini models as Holo versus the same three mini solo baselines.

## Domains

- Finance: adaptive algorithmic execution governor.
- Healthcare: clinical operations and AI triage governance.
- Cybersecurity: incident response under partial observability.
- Legal/regulatory: AI vendor risk and contract controls.
- Energy/infrastructure: AI data-center power and grid-risk strategy.

## Current Status

Finance has a built and hash-locked frontier-3 packet.

The other four domains are scenario skeletons only. Do not freeze them until the finance run and autopsy prove the harness end to end.

## What Counts As Evidence

Evidence requires:

- hash lock
- run manifest
- complete traces
- validity gates
- blinded judge packets
- judge score files
- score/verdict consistency checks
- full autopsy
- clear distinction between all-judge and clean-only scoring

Default status remains `benchmark_credit=false` and `public_claim=false`.
