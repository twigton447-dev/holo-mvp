# HoloVerify / HoloBuild Compiled Metrics Summary

Date: 2026-07-01

Classification: `HOLOVERIFY_HOLOBUILD_HASH_LOCKED_METRICS_COMPILE`

Provider calls during this compile: `0`

Judge calls during this compile: `0`

## Outputs

- Workbook: `outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx`
- Source package: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json`
- Packet rows CSV: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_packet_rows.csv`
- Metrics CSV: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/holoverify_metric_summary.csv`
- Source audit CSV: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/source_audit.csv`
- Lock inventory CSV: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/lock_inventory.csv`

## HoloVerify Headline Rows

ESCALATE is treated as the positive class.

| Family | Evidence tier | Holo audit-grade result | FPR | FNR | Caveat |
|---|---|---:|---:|---:|---|
| Kit A / Accounts Payable-BEC Registry | public registry summary | 8/8 | 0% | 0% | Public registry summary; packet-level traces are not expanded in this compile. |
| Kit B / Agentic Commerce v1 Registry | public registry summary | 3/3 | 0% | 0% | Public registry summary; Kit B hash snippets are in `frontend/benchmark.html`. |
| Clinical Activation Boundary Controls / Kit C | frozen complete run | 40/40 | 0% | 0% | Strongest public-package HoloVerify evidence. |
| Vendor-Master Payment Controls / AP Replication | committed evidence package | 40/40 | 0% | 0% | Full AP family. |
| Agentic Commerce / Order Execution Replication | consolidated public package created | 40/40 | 0% | 0% | Complete via locked batches; consolidated package root `74a5729fdd01834b9c0e2212d10a37e24a9b81e17bf7169affea60a02b917b21`. |
| Agentic Commerce / All-Six Collapse Canary | lock-rooted canary | 6/6 | 0% | 0% | Canary-sized, not full-family proof. |
| IT Access / Permission Change Replication | replacement rollup package created | 40/40 | 0% | 0% | Retired ambiguous `HV-ITAC-REP-015`; replacement `HV-ITAC-REP-015R1` is included. Rollup root `b09d4edc97eda5f9f90c73996e1675dc41d902a3b92c8f24ce7fe65fa6ddb6d3`. |
| Hard ALLOW FP 5-Pair Precursor | frozen pending judge | 10/10 | 0% | 0% | Provenance/hardening evidence, not public benchmark-locked proof. |

## Solo / Non-Holo KNEW-Admissible Rows

| Family | Solo/non-Holo evidence tier | KNEW/admissible success | Notes |
|---|---|---:|---|
| Clinical Activation Boundary Controls / Kit C | final evidence package | 6/120 | Roster-matched one-shot baseline: solo used the same three model families used inside Holo, `xai/grok-3-mini`, `google/gemini-2.5-flash-lite`, and `minimax/MiniMax-M2.5-highspeed`. |
| Vendor-Master Payment Controls / AP Replication | roster-matched solo baseline | 53/120 | Exact same three models as AP Holo: `xai/grok-3-mini`, `openai/gpt-5.4-mini`, and `minimax/MiniMax-M2.5-highspeed`. |
| Agentic Commerce / Order Execution Replication | solo triage | 26/120 | Same packet bank seam triage, not exact roster-matched proof: xAI and MiniMax match Holo, but solo used `openai/gpt-4o-mini` while Holo W2 used `openai/gpt-5.4-mini`. |
| IT Access / Permission Change Replication | solo triage | 24/120 | Same packet bank seam triage run before retiring ambiguous `HV-ITAC-REP-015`; not exact roster-matched proof because solo used `openai/gpt-4o-mini` while Holo W2 used `openai/gpt-5.4-mini`. |
| Hard ALLOW FP 5-Pair Precursor | local KNEW benchmark | 7/10 | Pending judge / not benchmark-locked. |

## Model Roster Notes

- Exact roster-matched means the solo one-shot baseline used the same three models that appeared inside the corresponding Holo run.
- Clinical / Kit C exact roster: `xai/grok-3-mini`, `google/gemini-2.5-flash-lite`, `minimax/MiniMax-M2.5-highspeed`.
- AP exact roster: `xai/grok-3-mini`, `openai/gpt-5.4-mini`, `minimax/MiniMax-M2.5-highspeed`.
- Commerce and IT Holo roster: W1 `xai/grok-3-mini`, G1 `minimax/MiniMax-M2.5-highspeed`, W2 `openai/gpt-5.4-mini`, G2 `minimax/MiniMax-M2.5-highspeed`, W3 `minimax/MiniMax-M2.5-highspeed`.
- Commerce and IT solo triage roster: `xai/grok-3-mini`, `openai/gpt-4o-mini`, `minimax/MiniMax-M2.5-highspeed`. Those triage rows are useful seam evidence, but should not be described as exact same-three-model comparisons.

## HoloBuild Rows

The HoloBuild D11-lock sheet is a separate evidence class. It is full-gated 100-point ledger evidence, but it should be public-packaged with a root signature before being placed beside AP or Clinical as hash-package proof.

| Case | Holo | Solo | Delta | Status |
|---|---:|---:|---:|---|
| D10 Infrastructure Configuration Change | 95 | 71 | +24 | Official full-gated Holo win; patched canary caveat. |
| D11 Cyber Incident / Contract Notice / Emergency Cloud Access | 96 | 94 | +2 | Official full-gated Holo win; narrow, both admissible. |
| D13 Trap Canary / Stale Policy Payment Diversion | 94 | 69 | +25 | Official full-gated Holo win. |
| D14 Trade Finance / LC Discrepancy Payment Release | 94 | 69 | +25 | Official full-gated Holo win after parser re-audit. |
| D12 Fund NAV Redemption Cash Release | n/a | n/a | n/a | Regression seed; both artifacts failed deterministic word band. |

## Statistical Significance Planner

The workbook includes two significance views:

- Observed Wilson 95% confidence bands for FPR, FNR, overall binary error, and operational non-success.
- Future replication planning rows for detecting error-rate drops at alpha `0.05` and power `0.80`.

Rule-of-three quick read:

- With zero observed errors, about `60` samples per class are needed for a 95% upper error bound below `5%`.
- About `150` samples per class are needed for a 95% upper error bound below `2%`.
- About `300` samples per class are needed for a 95% upper error bound below `1%`.

## Claim Boundaries

- This compile does not claim universal model superiority.
- This compile does not treat parse/content/provider failures as false positives or false negatives unless a binary verdict exists.
- Kit A/B public registry rows are summary-level rows, not expanded packet-level traces.
- Commerce full-family evidence is current file-backed batched evidence with a consolidated public package now created.
- IT is a row-level rollup with replacement pair `HV-ITAC-REP-015R1` and a replacement rollup package now created.
- HoloBuild is ledger evidence and should be root-packaged before public promotion.

## Lock Inventory

The workbook includes a `Lock Inventory` sheet that enumerates every discovered `LOCK_VALIDATION.json`, `LOCK_MANIFEST.json`, `RUN_LOCK_VALIDATION.json`, `AUTOPSY_LOCK_VALIDATION.json`, `FINAL_EVIDENCE_PACKAGE_LOCK_VALIDATION.json`, `PUBLIC_FREEZE_PACKAGE_LOCK_VALIDATION.json`, and `FREEZE_MANIFEST.json` under `docs/benchmark`.

That sheet is deliberately broader than the metric rows. It includes valid proof runs, invalid preserved runs, solo lock files, public/final package locks, and packet-only freezes. The metric sheets count only rows whose evidence tier is appropriate for scoring or comparison.
