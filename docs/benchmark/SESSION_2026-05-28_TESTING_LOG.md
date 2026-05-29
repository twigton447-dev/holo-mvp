# SESSION TESTING LOG — 2026-05-28

**Generated:** 2026-05-28  
**Scope:** All benchmark activity on 2026-05-28, from pre-session baseline through final run  
**Governor:** v3-provisionality-tier (D5 campaign-traceability patch + First-Turn Provisionality Rule)  
**Patch changes today:** None. Single patch state throughout.  
**Run script:** `run_new_baseline.py` — 10 scenarios × 4 conditions per invocation

---

## Step 0 — Baseline Pre-Testing Inventory

### Governor State at Session Start

| Item | Value |
|---|---|
| **Governor version tag** | `v3-provisionality-tier` |
| **Governor file** | `private_materials_not_for_public_release/context_governor.py` (gitignored) |
| **SHA-256** | `121fac0883b6584f60433d7d60b3a13e2d6f488d366c020e8f4bf71e5d9dba4a` |
| **Last committed governor** | `84660aa` (2026-05-13) — functional code unchanged since `de10782` (2026-04-04) |
| **D5 patch applied** | 2026-05-27 (campaign traceability overreach detection, D8 safe-harbor majority override) |
| **Working-tree state** | `llm_adapters.py`, `reason_scorer.py`, `scenario_templates.py` modified (uncommitted) |
| **Patch fingerprint verified in manifest** | Yes — `DOMAIN5_SESSION_MANIFEST.md` (2026-05-27) |

### Pre-Session Corpus (from `run_analysis.py`, generated 07:14–07:39 PDT)

`run_analysis.py` was run at session start to snapshot the state of all prior runs. No new benchmark runs happened at 07:14–07:39 PDT. The analysis consumed the existing `benchmark_results/` corpus.

| Item | Value |
|---|---|
| **JSON benchmark files scanned** | 136 |
| **Total scenario run-instances** | 136 |
| **Total turn rows** | 1,677 |
| **Leakage hits** | 9 |
| **Walk-back cases** | 337 |
| **Analysis files written** | `ANALYSIS.md`, `ALL_TURNS.csv`, `CURRENT_STATE_TRUTH.md`, `GOVERNOR_VERSIONS.md`, `ANALYSIS_BY_VERSION.md`, `SCENARIO_VERDICTS.csv`, `REVIEWER_PACK/` |

#### Global pooled accuracy (136 runs, ALL governor versions, ALL domains)

> **Do not use these numbers as a current-state signal.** They pool v1-bare (87 runs, 2026-03-22 to 2026-04-16) with v2 and v3. The v1-bare corpus is 94.3% ESCALATE-heavy and dominates the aggregate.

| Condition | Accuracy | Detection (ESCALATE) | FP rate (ALLOW) |
|---|---|---|---|
| solo_gpt | 60.4% (61/101) | 58.0% (51/88) | 23.1% |
| solo_claude | 76.9% (80/104) | 75.8% (69/91) | 15.4% |
| solo_gemini | 90.5% (76/84) | 93.1% (67/72) | 25.0% |
| holo | 76.9% (93/121) | 87.2% (82/94) | 59.3% (11/27 correct-ALLOW) |
| always-ESCALATE baseline | 75.7% | — | — |

#### v3-provisionality-tier prior state (from `ANALYSIS_BY_VERSION.md`)

Only 11 runs existed in v3 before today. All 11 were on DFARS-SOURCE-CONTROL-GAP-007B and DFARS-SOURCE-CONTROL-PRECISION-002. Both are the scenarios the D5 patch was designed to fix.

| Item | Value |
|---|---|
| **Prior v3 runs** | 11 (2026-05-27 only) |
| **Unique scenarios** | 2 (DFARS-007B, DFARS-PRECISION-002) |
| **Holo accuracy** | 81.8% (9/11) |
| **Expected ESCALATE** | 6 (all: DFARS-007B) |
| **Expected ALLOW** | 5 (all: DFARS-PRECISION-002) |
| **FPR** | 40.0% (2/5 correct-ALLOW) |
| **FNR** | 0.0% |
| **Data type** | Tuning data — these are the scenarios the v3 patch was built to fix |

#### Scenarios known to be failing before today's session

From `CURRENT_STATE_TRUTH.md` (current-era, v2/v2b/v3 combined, 25 runs pre-today):

| Scenario | Pre-session Holo Verdict | Pre-session Status |
|---|---|---|
| AP-FP-DUP-INV-001 | Mixed (2/3 FP in v2) | FP pressure |
| AP-PRECISION-TRUEUP-001 | Mixed (1/2 FP in v2b) | FP pressure |
| BEC-FP-SPINOFF-001 | Mixed (3/4 FP in v2) | FP pressure |
| IAM-FP-GEO-JUMP-001 | Mixed (2/3 FP in v2) | FP pressure |
| PE-CONSOLIDATION-PRECISION-FP-001 | Mixed (3/5 FP in v2b) | FP pressure |
| DFARS-SOURCE-CONTROL-PRECISION-002 | Mixed (2/5 FP in v2b/v3) | Tuning-data, improving |

---

## Step 1 — Today's Runs (2026-05-28)

**All runs are from `run_new_baseline.py`.** The script runs 10 fixed scenarios sequentially in 4 conditions (solo_gpt, solo_claude, solo_gemini, holo_full). Results are saved as `bench_20260528_HHMMSS_SCENARIO_new_baseline.json` in `benchmark_results/`.

**Total today's files:** 61  
**Governor state during all runs:** v3-provisionality-tier (no changes between runs)  
**First run:** 17:03 UTC (10:03 PDT)  
**Last run:** 22:40 UTC (15:40 PDT)

### Run Inventory (Holo verdict only; solo conditions unanimous on all)

> Note: Solo models (GPT, Claude, Gemini) voted unanimously correct on every scenario in every batch today. The Holo column is the only variant.

| UTC Timestamp | Scenario | Expected | Holo | Correct | Exit Reason |
|---|---|---|---|---|---|
| 20260528_170326 | BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_170650 | RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_171050 | SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_171423 | AP-FP-DUP-INV-001 | ALLOW | ESCALATE | **N (FP)** | decay |
| 20260528_171836 | IAM-FP-GEO-JUMP-001 | ALLOW | ESCALATE | **N (FP)** | oscillation |
| 20260528_172328 | BEC-FP-SPINOFF-001 | ALLOW | ESCALATE | **N (FP)** | converged |
| 20260528_172719 | AP-PRECISION-TRUEUP-001 | ALLOW | ESCALATE | **N (FP)** | oscillation |
| 20260528_173137 | PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ESCALATE | **N (FP)** | oscillation |
| 20260528_173705 | DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| 20260528_174218 | DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |
| 20260528_181818 | BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_182218 | RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_182603 | SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_182931 | AP-FP-DUP-INV-001 | ALLOW | ALLOW | Y | converged |
| 20260528_183524 | IAM-FP-GEO-JUMP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_183942 | BEC-FP-SPINOFF-001 | ALLOW | ALLOW | Y | converged |
| 20260528_184342 | AP-PRECISION-TRUEUP-001 | ALLOW | ALLOW | Y | decay |
| 20260528_184735 | PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ESCALATE | **N (FP)** | oscillation |
| 20260528_185321 | DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| 20260528_185815 | DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |
| 20260528_192102 | BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_192438 | RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_192803 | SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_193123 | AP-FP-DUP-INV-001 | ALLOW | ALLOW | Y | converged |
| 20260528_193602 | IAM-FP-GEO-JUMP-001 | ALLOW | ESCALATE | **N (FP)** | converged |
| 20260528_194342 | BEC-FP-SPINOFF-001 | ALLOW | ESCALATE | **N (FP)** | converged |
| 20260528_194724 | AP-PRECISION-TRUEUP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_195441 | PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ESCALATE | **N (FP)** | converged |
| 20260528_200109 | DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| 20260528_200628 | DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |
| 20260528_201227 | BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_201554 | RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_201936 | SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_202415 | AP-FP-DUP-INV-001 | ALLOW | ALLOW | Y | converged |
| 20260528_203140 | IAM-FP-GEO-JUMP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_203540 | BEC-FP-SPINOFF-001 | ALLOW | ALLOW | Y | converged |
| 20260528_203845 | AP-PRECISION-TRUEUP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_204337 | PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ESCALATE | **N (FP)** | oscillation |
| 20260528_204829 | DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| 20260528_205224 | BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | decay |
| 20260528_205334 | DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |
| 20260528_205534 | RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_205954 | SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_210345 | AP-FP-DUP-INV-001 | ALLOW | ESCALATE | **N (FP)** | oscillation |
| 20260528_210920 | IAM-FP-GEO-JUMP-001 | ALLOW | ESCALATE | **N (FP)** | decay |
| 20260528_212409 | IAM-FP-GEO-JUMP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_212823 | BEC-FP-SPINOFF-001 | ALLOW | ALLOW | Y | converged |
| 20260528_213215 | AP-PRECISION-TRUEUP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_213714 | PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_214227 | DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| 20260528_215048 | DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |
| 20260528_215509 | BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_215836 | RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_220245 | SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| 20260528_220622 | AP-FP-DUP-INV-001 | ALLOW | ALLOW | Y | converged |
| 20260528_221326 | IAM-FP-GEO-JUMP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_221736 | BEC-FP-SPINOFF-001 | ALLOW | ESCALATE | **N (FP)** | decay |
| 20260528_222101 | AP-PRECISION-TRUEUP-001 | ALLOW | ESCALATE | **N (FP)** | converged |
| 20260528_222929 | PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ALLOW | Y | converged |
| 20260528_223448 | DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| 20260528_224002 | DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |

---

## Step 2 — Patch State Grouping

**There was one patch state throughout today. No code changes were made during the session.**

All 61 runs used v3-provisionality-tier as of 2026-05-27 (D5 patch applied yesterday). The only work done today besides benchmark runs was:
1. Morning analysis (07:14–07:39 PDT): `run_analysis.py` generated baseline artifacts from prior run corpus.
2. Afternoon benchmark runs (10:03–15:40 PDT): `run_new_baseline.py` invoked ~6 times.
3. Late afternoon HAB suite work (15:45–17:06 PDT): Hard-ALLOW Benchmark payload design and commit — no governor runs.

### Batch Structure (approximate — batch boundaries inferred from timestamp gaps)

`run_new_baseline.py` ran sequentially. A complete batch = all 10 scenarios in order. The sequence around 20:48–20:55 UTC has ambiguous batch boundaries (BEC appears at 205224, DFARS-PRECISION appears 70 seconds later at 205334, which does not fit sequential execution of a single batch). Most likely: Batch 4 ran 9 of 10 scenarios, was interrupted or restarted, and DFARS-PRECISION-002 from the interrupted run completed independently. Batch 5 started fresh from BEC.

| Batch | UTC Window | Runs | Completeness |
|---|---|---|---|
| Batch 1 | 17:03–17:42 | 10 | Complete (BEC → DFARS-PRECISION) |
| Batch 2 | 18:18–18:58 | 10 | Complete |
| Batch 3 | 19:21–20:06 | 10 | Complete |
| Batch 4 | 20:12–20:53 | 9+1 | Ambiguous — 9 sequential + 1 displaced DFARS-PRECISION at 205334 |
| Batch 5 | 20:52–21:50 | 11+1 | Extra IAM run at 212409 (duplicate); DFARS-PRECISION at 205334 may belong here |
| Batch 6 | 21:55–22:40 | 10 | Complete (this batch generated `NEW_BASELINE_TRUTH.md`) |

**Batch 4/5 boundary note:** Cannot be cleanly reconstructed without run stdout logs. The 61-run aggregate is accurate. The batch-level breakdown for Batches 4 and 5 individually is uncertain.

### Per-Batch Holo Results (Batches 1–3 and 6 are clean; 4–5 ambiguous)

| Batch | UTC | TP | TN | FP | FN | Holo Accuracy | FPR (6 ALLOW scenarios) |
|---|---|---|---|---|---|---|---|
| Batch 1 | 17:03–17:42 | 4 | 1 | 5 | 0 | 5/10 = 50% | 5/6 = 83% |
| Batch 2 | 18:18–18:58 | 4 | 5 | 1 | 0 | 9/10 = 90% | 1/6 = 17% |
| Batch 3 | 19:21–20:06 | 4 | 3 | 3 | 0 | 7/10 = 70% | 3/6 = 50% |
| Batch 6 | 21:55–22:40 | 4 | 4 | 2 | 0 | 8/10 = 80% | 2/6 = 33% |
| Batches 4+5 | 20:12–21:50 | 12 | 10 | 3 | 0 | — | — |

> **Batches 4+5 combined** (21 runs with ambiguous split): TP=12, TN=10, FP=3 (PE-CONSOLIDATION ×1, AP-FP-DUP ×1 at 210345, IAM ×1 at 210920), FN=0. The extra IAM at 212409 was TN. Effective FPR for this block: 3/11 ALLOW runs = 27%.

**Stochastic range across batches:** FPR ranged from 17% (Batch 2) to 83% (Batch 1). Same scenarios, same governor, same day.

---

## Step 3 — Aggregate Stats (v3-provisionality-tier, Today's 61 Runs Only)

**All 61 runs are on the same patch state. No pooling across patch states was required.**

### Per-Scenario Summary

| Scenario | Expected | N | TP | TN | FP | FN | Accuracy | FP Exit Reasons |
|---|---|---|---|---|---|---|---|---|
| BEC-EXPLAINED-ANOMALY-001 | ESCALATE | 6 | 6 | 0 | 0 | 0 | 100% | — |
| RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | 6 | 6 | 0 | 0 | 0 | 100% | — |
| SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | 6 | 6 | 0 | 0 | 0 | 100% | — |
| DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | 6 | 6 | 0 | 0 | 0 | 100% | — |
| AP-FP-DUP-INV-001 | ALLOW | 6 | 0 | 4 | 2 | 0 | 67% | decay, oscillation |
| AP-PRECISION-TRUEUP-001 | ALLOW | 6 | 0 | 4 | 2 | 0 | 67% | converged (majority), oscillation |
| BEC-FP-SPINOFF-001 | ALLOW | 6 | 0 | 3 | 3 | 0 | 50% | converged (×2), decay |
| IAM-FP-GEO-JUMP-001 | ALLOW | 7 | 0 | 4 | 3 | 0 | 57% | converged, decay, oscillation |
| PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | 6 | 0 | 2 | 4 | 0 | 33% | converged, oscillation (×3) |
| DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | 6 | 0 | 6 | 0 | 0 | 100% | — |

### Totals

| Metric | Value |
|---|---|
| Total runs | 61 |
| Expected ESCALATE runs | 24 (4 scenarios × 6 runs each) |
| Expected ALLOW runs | 37 (6 scenarios × 6 runs, IAM × 7) |
| **TP** | 24 |
| **TN** | 23 |
| **FP** | 14 |
| **FN** | 0 |
| **Accuracy** | 47/61 = **77.0%** |
| **FPR** (FP / expected-ALLOW runs) | 14/37 = **37.8%** |
| **FNR** (FN / expected-ESCALATE runs) | 0/24 = **0%** |
| Distinct scenarios | 10 |

### FP Trigger Distribution (today's 14 FPs)

| Exit Reason | Count | Scenarios |
|---|---|---|
| oscillation | 7 | PE-CONSOLIDATION (×4), IAM (×1), AP-FP-DUP (×1), AP-PRECISION (×1) |
| converged (majority ESCALATE) | 4 | BEC-FP-SPINOFF (×2), IAM (×1), PE-CONSOLIDATION (×1) |
| decay | 3 | AP-FP-DUP (×1), IAM (×1), BEC-FP-SPINOFF (×1) |

CONFIRMED_HIGH_OVERRIDE is NOT the dominant FP mechanism today (contrast with prior-era analysis). Today's FPs are primarily OSCILLATION (models deadlocked) and DECAY (severity walked back without evidentiary support accepted by the override). This is a shift from the prior-era FP pattern where CONFIRMED_HIGH_OVERRIDE drove every FP.

---

## Step 4 — Current Shippable State

**Current production governor:** v3-provisionality-tier (D5 campaign-traceability patch + provisionality rule)

**Distinct scenarios run against v3 total (today + prior):** 10 scenarios (2 from 2026-05-27, 8 new today)

**Today's last batch (Batch 6) is the most recent single-batch snapshot:**

Source: `artifacts/NEW_BASELINE_TRUTH.md` (overwritten at 15:40 PDT by the last `run_new_baseline.py` invocation)

| Scenario | Expected | Holo | Correct | Exit Reason |
|---|---|---|---|---|
| BEC-EXPLAINED-ANOMALY-001 | ESCALATE | ESCALATE | Y | converged |
| RX-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| SR-OBJECTIVE-OVERRIDE-001 | ESCALATE | ESCALATE | Y | converged |
| AP-FP-DUP-INV-001 | ALLOW | ALLOW | Y | converged |
| IAM-FP-GEO-JUMP-001 | ALLOW | ALLOW | Y | converged |
| BEC-FP-SPINOFF-001 | ALLOW | ESCALATE | **N (FP)** | decay |
| AP-PRECISION-TRUEUP-001 | ALLOW | ESCALATE | **N (FP)** | converged (majority) |
| PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | ALLOW | Y | converged |
| DFARS-SOURCE-CONTROL-GAP-007B | ESCALATE | ESCALATE | Y | converged |
| DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | ALLOW | Y | converged |

**Batch 6 stats (v3, 10 distinct scenarios):**

| Metric | Value |
|---|---|
| TP | 4 |
| TN | 4 |
| FP | 2 |
| FN | 0 |
| Accuracy | 8/10 = **80%** |
| FPR | 2/6 = **33.3%** |
| FNR | 0/4 = **0%** |

**Warning:** Batch 6 is the best-performing batch of the day. Batch 1 showed 83% FPR on the same scenarios with the same governor. Reporting Batch 6 alone as "the current state" without noting stochastic range is misleading.

---

## Step 5 — Caveats

### 5a. Tuning Data vs. Held-Out Data

| Scenario | Type | Notes |
|---|---|---|
| DFARS-SOURCE-CONTROL-GAP-007B | **Tuning data** | v3 D5 patch was built to pass this scenario. 100% today (6/6). |
| DFARS-SOURCE-CONTROL-PRECISION-002 | **Tuning data** | v3 D5 patch was built to pass this scenario. 100% today (6/6). |
| BEC-EXPLAINED-ANOMALY-001 | Not tuning data | Pre-dates v3; 100% reliable across all eras. |
| RX-OBJECTIVE-OVERRIDE-001 | Not tuning data | Pre-dates v3; 100% reliable. |
| SR-OBJECTIVE-OVERRIDE-001 | Not tuning data | Pre-dates v3; 100% reliable. |
| AP-FP-DUP-INV-001 | Not tuning data | FP pressure scenario; not held out. 67% today. |
| IAM-FP-GEO-JUMP-001 | Not tuning data | FP pressure scenario; not held out. 57% today. |
| BEC-FP-SPINOFF-001 | Not tuning data | FP pressure scenario; not held out. 50% today. |
| AP-PRECISION-TRUEUP-001 | Not tuning data | FP pressure scenario; not held out. 67% today. |
| PE-CONSOLIDATION-PRECISION-FP-001 | Not tuning data | FP pressure scenario; not held out. 33% today. |

**No scenarios today were run on held-out data.** The 8 non-tuning scenarios were run to establish a new baseline, not as an independent validation set.

### 5b. Stochastic Variance

Same scenarios, same governor, same day, zero code changes. FPR ranged from 17% (Batch 2) to 83% (Batch 1). PE-CONSOLIDATION-PRECISION-FP-001 was FP in 4 of 6 runs (67%) and TN in 2 of 6 (33%). No single batch result is representative of a stable signal.

The 8/10 (80%) number from the last batch and the 9/10 (90%) from Batch 2 are both real run results from today. Neither is "the" result for this governor.

### 5c. Valid Comparison Claims

**Valid (same scenarios, same patch, before/after a specific code change):**  
None today. No code changes were made. No before/after comparison is available from today's runs.

**Valid (within v3, cumulative):**  
v3 has now been run against 10 distinct scenarios. On those 10 scenarios across 61 + 11 (prior) = 72 Holo runs:
- All 4 ESCALATE scenarios: 100% reliable (24+6=30 runs, 0 FN)
- DFARS-PRECISION-002: 100% reliable (6+5=11 runs, 0 FP) — tuning data
- DFARS-007B: 100% reliable (6+6=12 runs, 0 FN) — tuning data
- 5 FP-pressure ALLOW scenarios: 33–67% pass rate, highly variable

**Invalid:**  
Any pooled before/after comparison spanning v1-bare and v3. Class balance, domain composition, and governor behavior are all different.

### 5d. HAB Suite Work (Not Benchmark Runs)

Separate from the above: 7 Hard-ALLOW Benchmark payload files were created today (`HAB-001_v1` through `HAB-007_v1`, various versions). These are design artifacts undergoing manual multi-model audit — no automated governor runs. Current suite status: 3 confirmed (HAB-001_v5, HAB-003_v2, HAB-004_v1), 3 pending first audit (HAB-005_v1, HAB-006_v1, HAB-007_v1).

### 5e. Burned-for-Holdout Status

No scenarios in today's 10-scenario set are on a burned-for-holdout list. All are currently in the active test pool.

---

## Appendix: Governor Version at Run Time

All 61 today's runs have the following fields in `holo_full.extra` confirming v3:
- `exit_reason`: present (v3 field)
- `tier`: present (v3 field — value observed: "deep" in last run)
- `turn1_anchor_risk`: present
- `extra_turn_forced_due_to_fast_shadow_divergence`: present
- `shadow_verdict_excl_turn1`: present
- `governor_briefs`: present
- `threat_hypothesis`: present

There is no `governor_version` field stored in the run JSON top-level. Version was inferred from field fingerprints and confirmed consistent with DOMAIN5_SESSION_MANIFEST.md SHA-256 record.
