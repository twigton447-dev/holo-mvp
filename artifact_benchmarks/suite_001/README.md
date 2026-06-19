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

## Expansion Backlog

- Medical diagnostic paradoxes: synthetic differential-diagnosis reasoning only, with no real patient data and no medical advice.
- Adversarial paradox reasoning: contradiction, impossibility, and tradeoff artifacts across domains.
- Experience-quality domains: food, hotel, travel, service, education, and student workflows where measured lift is easy to understand.

See `DOMAIN_EXPANSION_BACKLOG_20260619.md` and `domain_expansion_backlog.json`.

## Packet Taxonomy

Suite packets now split into three worlds:

- HoloBuild packets: build or improve artifacts.
- HoloVerify packets: verify facts, boundaries, authority, and action safety.
- Overlap packets: dissect trusted artifacts, find discrepancies, and repair them.

The working packet families are blank-slate build, best-existing-artifact improvement, discrepancy discovery, known-outcome retrospective, competition/court, medical diagnostic paradox, and experience quality.

See `PACKET_TAXONOMY_20260619.md` and `packet_taxonomy.json`.

## Packet Roadmap

The current packet queue starts with the finance blank-slate build packet, then moves to finance best-existing-artifact improvement and finance discrepancy discovery before opening new domains.

See `PACKET_ROADMAP_20260619.md` and `packet_roadmap.json`.

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
