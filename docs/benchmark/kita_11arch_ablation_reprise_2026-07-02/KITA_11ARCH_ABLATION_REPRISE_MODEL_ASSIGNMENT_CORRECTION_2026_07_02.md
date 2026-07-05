# Kit A Ablation Reprise Model Assignment Correction

Classification: `KITA_11ARCH_ABLATION_REPRISE_MODEL_ASSIGNMENT_CORRECTION`

This note restores the canonical interpretation of the Kit A 11-architecture ablation reprise to the provider-balanced model assignment from commit `a33c196d3`.

## Canonical Baseline-Matched Run

- Commit being matched: `a33c196d3`
- Run: `run_20260702T184308Z`
- Path: `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/cross_domain_3pair_hard/live_runs/run_20260702T184308Z`
- Evidence status: `CANONICAL_PROVIDER_BALANCED_BASELINE_MATCH`

Required model mix:

- `grok-3-mini`: `48`
- `gpt-5.4-mini`: `48`
- `MiniMax-M2.5-highspeed`: `48`
- Total provider calls: `144`

Other invariants:

- Same frozen packet set: `HV-AP-REP-011`, `HV-ACOM-REP-020`, `HV-ITAC-REP-018`
- Selected packets: `6`
- Architectures: reconsider, vote, council, debate
- Packet-architecture units: `24`
- Calls per packet-architecture unit: `6`
- Gov calls: `0`
- Holo calls: `0`
- Judge calls: `0`
- No Gov baton, Holo state, artifact registry, or final selector in prompts
- Same runner, JSON output contract, and deterministic local adjudication harness

## Diagnostic Run Boundary

The homogeneous OpenAI-5.4 run committed at `b43eb7628` is preserved as diagnostic evidence only:

- Run: `run_20260702T193334Z`
- Path: `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/openai54_homogeneous_6call_same_arch_family/live_runs/run_20260702T193334Z`
- Evidence status: `DIAGNOSTIC_ONLY_NOT_BASELINE_MATCHED`

Reason: all `144` calls use `openai/gpt-5.4-mini`, so that run does not preserve the `a33c196d3` provider-balanced `48/48/48` model assignment.

Required verification line before commit:

`Model mix verified: grok-3-mini=48, gpt-5.4-mini=48, MiniMax-M2.5-highspeed=48`
