# Ten-Domain HoloBuild Benchmark Runbook

This runbook is the tomorrow-ready operating path for the frozen D1-D10 HoloBuild action-boundary packet suite.

Safety state at creation: no providers, no live artifacts, no scoring, no judging, no unblinding, no push.

## A. No-Provider Readiness

```bash
cd /Users/taylorwigton/Desktop/holo-mvp
python3 -B artifact_benchmarks/holo_factory/validate_holobuild_ten_domain_suite.py
```

Expected status: `HOLOBUILD_TEN_DOMAIN_SUITE_READY_NO_PROVIDER`.

## B. No-Provider Runner Smoke

```bash
cd /Users/taylorwigton/Desktop/holo-mvp
python3 -B artifact_benchmarks/holo_factory/run_holobuild_mini_scout.py   --packet-dir artifact_benchmarks/holo_factory/mini_scouts/d1_capital_markets_execution_risk_001   --condition holo_build_arch   --holo-mode patent_aligned_v4   --run-id SMOKE_D1_HOLO   --dry-run
```

Dry-run writes only a generic runner dry-run manifest. It does not call providers or create live artifacts.

## C. Live Holo Generation Example

Use only after explicit approval for live generation.

```bash
cd /Users/taylorwigton/Desktop/holo-mvp
export HOLO_ALLOW_LIVE=1
python3 -B artifact_benchmarks/holo_factory/run_holobuild_mini_scout.py   --packet-dir artifact_benchmarks/holo_factory/mini_scouts/d1_capital_markets_execution_risk_001   --condition holo_build_arch   --holo-mode patent_aligned_v4   --run-id <RUN_ID>   --live
unset HOLO_ALLOW_LIVE
```

`patent_aligned_v4` is the only proof-eligible HoloBuild mode. Legacy modes require `--diagnostic-legacy-holo-mode` and remain diagnostic-only.

## D. Live Solo Generation Example

Use the same frozen packet and the same run id as the matching Holo run when building a comparison.

```bash
cd /Users/taylorwigton/Desktop/holo-mvp
export HOLO_ALLOW_LIVE=1
python3 -B artifact_benchmarks/holo_factory/run_holobuild_mini_scout.py   --packet-dir artifact_benchmarks/holo_factory/mini_scouts/d1_capital_markets_execution_risk_001   --condition solo_openai_gpt_5_5   --run-id <RUN_ID>   --live
unset HOLO_ALLOW_LIVE
```

## E. Post-Generation Sequence

1. Verify artifact hashes and run manifest.
2. Verify Layer 1 deterministic gate for each artifact.
3. For Holo runs, verify architecture evidence and `architecture_evidence_visible_to_judges=false`.
4. Create or inspect blind export.
5. Run contamination scan on judge-visible packets.
6. Do not judge until artifacts pass deterministic gate.
7. Do not score until blind export is clean.
8. Do not unblind until scores are locked.

## F. Safety Rules

- No unblinding during generation.
- No judging during generation.
- No scoring during generation.
- No packet edits after freeze.
- No scoring-rubric edits after artifacts are generated.
- No provider calls unless `--live` and `HOLO_ALLOW_LIVE=1` are both present.
- No push unless explicitly approved.
- Scoring protocol lives separately under `artifact_benchmarks/holo_factory/scoring_policies/`; packets carry deterministic admission gates only.
- Active scoring lock for all tests: `artifact_benchmarks/holo_factory/scoring_policies/ACTIVE_SCORING_PROTOCOL.lock.json`.
- Current active protocol: `unified_artifact_scoring_protocol_v6_structural_epistemic`.
- Do not score new benchmark outputs with older v4/v5/v5.1/v5.2 protocols unless the run is explicitly labeled historical/regression/autopsy.
