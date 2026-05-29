# SESSION MATRIX — Governor Version × Scenario
## Addendum to SESSION_2026-05-28_TESTING_LOG.md

**Generated:** 2026-05-28  
**Scope:** All Holo runs across all governor versions, current-era scenarios only (10 scenarios)  
**Data completeness:** Both `benchmark_results/` and `private_materials_not_for_public_release/benchmark_results/` scanned. No missing runs found.

---

## Is This Everything?

Yes. Both directories scanned. 2 private runs exist for BEC-EXPLAINED-ANOMALY-001 (v2-briefs-threat) — both already included in the totals below. No other current-era scenarios have runs in private directories that are missing from the public results.

---

## The 90% / 17% Numbers

These came from **Batch 2** of today's runs: 18:18–18:58 UTC (11:18–11:58 PDT).

`run_new_baseline.py` overwrites `artifacts/NEW_BASELINE_TRUTH.md` on every invocation. Batch 2 wrote 9/10 = 90% accuracy, FPR = 1/6 = 17% to that file. Subsequent batches wrote over it. The file you saw at 90%/17% no longer exists on disk — it was overwritten by Batch 3 (70%, FPR=50%), then Batch 4, Batch 5, and finally Batch 6 (80%, FPR=33%).

**Batch 2 was not a fluke — it was a real run.** But it was also the single best-performing batch out of six today, all on the same governor with no code changes. The range was 50%–90% accuracy, 17%–83% FPR. No one batch is "the" result.

| Batch | UTC | Holo Accuracy | FPR | Note |
|---|---|---|---|---|
| Batch 1 | 17:03–17:42 | 5/10 = **50%** | 5/6 = 83% | |
| **Batch 2** | **18:18–18:58** | **9/10 = 90%** | **1/6 = 17%** | **You saw this — was overwritten** |
| Batch 3 | 19:21–20:06 | 7/10 = 70% | 3/6 = 50% | |
| Batch 4 | 20:12–20:53 | ~8/9 = 89% | ~1/5 = 20% | boundary ambiguous (see testing log) |
| Batch 5 | 20:52–21:50 | ~8/11 = 73% | ~2/7 = 29% | includes duplicate IAM run |
| Batch 6 | 21:55–22:40 | 8/10 = **80%** | 2/6 = 33% | **Final — what NEW_BASELINE_TRUTH.md shows now** |

The 90%/17% was Batch 2. The current NEW_BASELINE_TRUTH.md shows 80%/33% from Batch 6.

---

## Full Matrix: Pass Rate by Governor Version × Scenario

Format: `correct / total = pass_rate`  
`—` = not run under this governor  
ALLOW scenarios: pass = TN. ESCALATE scenarios: pass = TP.

| Scenario | Exp | v2-briefs-threat | v2b-shadow-briefs | v3-provisionality-tier |
|---|---|---|---|---|
| **ESCALATE scenarios** | | | | |
| BEC-EXPLAINED-ANOMALY-001 | ESC | 2/2 = 100% | — | 6/6 = 100% |
| RX-OBJECTIVE-OVERRIDE-001 | ESC | 1/1 = 100% | — | 6/6 = 100% |
| SR-OBJECTIVE-OVERRIDE-001 | ESC | 1/1 = 100% | — | 6/6 = 100% |
| DFARS-SOURCE-CONTROL-GAP-007B | ESC | — | 2/2 = 100% | 12/12 = 100% |
| **ALLOW scenarios (FP pressure)** | | | | |
| AP-FP-DUP-INV-001 | ALLOW | 1/3 = **33%** | — | 4/6 = **67%** |
| IAM-FP-GEO-JUMP-001 | ALLOW | 1/3 = **33%** | — | 4/7 = **57%** |
| BEC-FP-SPINOFF-001 | ALLOW | 1/4 = **25%** | — | 3/6 = **50%** |
| AP-PRECISION-TRUEUP-001 | ALLOW | — | 1/2 = **50%** | 4/6 = **67%** |
| PE-CONSOLIDATION-PRECISION-FP-001 | ALLOW | — | 2/5 = **40%** | 2/6 = **33%** |
| DFARS-SOURCE-CONTROL-PRECISION-002 | ALLOW | — | — | 9/11 = **82%** † |

† Tuning data. D5 patch was built to fix this scenario.

**v1-bare excluded from this table.** v1-bare runs (87 total, 2026-03-22 to 2026-04-16) do not cover any of these 10 scenarios. They are a different, predominantly ESCALATE-heavy scenario set and cannot be compared.

---

## Aggregated Stats by Governor Version

### One patch state = one block. Do not pool across blocks.

#### v2-briefs-threat (14 runs across 6 scenarios)

| Metric | Value |
|---|---|
| ESCALATE scenarios tested | 3 (BEC-EXPLAINED-ANOMALY, RX, SR) |
| ALLOW scenarios tested | 3 (AP-FP-DUP, IAM, BEC-FP-SPINOFF) |
| ESCALATE runs | 4 |
| ALLOW runs | 10 |
| TP | 4 |
| TN | 3 |
| FP | 7 |
| FN | 0 |
| **Accuracy** | 7/14 = **50.0%** |
| **FPR** | 7/10 = **70.0%** |
| **FNR** | 0/4 = **0%** |

---

#### v2b-shadow-briefs (9 runs across 3 scenarios)

| Metric | Value |
|---|---|
| ESCALATE scenarios tested | 1 (DFARS-007B) |
| ALLOW scenarios tested | 2 (AP-PRECISION, PE-CONSOLIDATION) |
| ESCALATE runs | 2 |
| ALLOW runs | 7 |
| TP | 2 |
| TN | 3 |
| FP | 4 |
| FN | 0 |
| **Accuracy** | 5/9 = **55.6%** |
| **FPR** | 4/7 = **57.1%** |
| **FNR** | 0/2 = **0%** |

---

#### v3-provisionality-tier (72 runs across 10 scenarios — includes 11 from 2026-05-27 + 61 from today)

| Metric | Value |
|---|---|
| ESCALATE scenarios tested | 4 (BEC-EXPLAINED-ANOMALY, RX, SR, DFARS-007B) |
| ALLOW scenarios tested | 6 (AP-FP-DUP, IAM, BEC-FP-SPINOFF, AP-PRECISION, PE-CONSOLIDATION, DFARS-PRECISION) |
| ESCALATE runs | 30 |
| ALLOW runs | 42 |
| TP | 30 |
| TN | 26 |
| FP | 16 |
| FN | 0 |
| **Accuracy** | 56/72 = **77.8%** |
| **FPR** | 16/42 = **38.1%** |
| **FNR** | 0/30 = **0%** |

**Stochastic range across today's 6 batches:** FPR = 17% (best) to 83% (worst), same governor, same day.

---

## Have We Improved? Valid Before/After Comparison

**Rule:** Only compare scenarios that appear in both versions. Different scenario sets cannot be compared directly.

### v2 → v3: 3 overlapping ALLOW scenarios (AP-FP-DUP, IAM, BEC-FP-SPINOFF)

| Scenario | v2 Pass Rate | v2 FPR | v3 Pass Rate | v3 FPR | Delta |
|---|---|---|---|---|---|
| AP-FP-DUP-INV-001 | 1/3 = 33% | 67% | 4/6 = 67% | 33% | **+33% IMPROVED** |
| IAM-FP-GEO-JUMP-001 | 1/3 = 33% | 67% | 4/7 = 57% | 43% | **+24% IMPROVED** |
| BEC-FP-SPINOFF-001 | 1/4 = 25% | 75% | 3/6 = 50% | 50% | **+25% IMPROVED** |
| **Combined (v2→v3)** | **3/10 = 30%** | **70%** | **11/19 = 58%** | **42%** | **+28% IMPROVED** |

v2 FPR on these 3 scenarios: **70%**. v3 FPR on same 3 scenarios: **42%**. Real improvement, same scenarios.

### v2b → v3: 2 overlapping ALLOW scenarios (AP-PRECISION, PE-CONSOLIDATION)

| Scenario | v2b Pass Rate | v2b FPR | v3 Pass Rate | v3 FPR | Delta |
|---|---|---|---|---|---|
| AP-PRECISION-TRUEUP-001 | 1/2 = 50% | 50% | 4/6 = 67% | 33% | **+17% IMPROVED** |
| PE-CONSOLIDATION-PRECISION-FP-001 | 2/5 = 40% | 60% | 2/6 = 33% | 67% | **-7% WORSE** |
| **Combined (v2b→v3)** | **3/7 = 43%** | **57%** | **6/12 = 50%** | **50%** | **+7% marginal** |

Mixed. AP-PRECISION improved. PE-CONSOLIDATION slightly worse (but sample sizes are tiny — 5 vs 6 runs).

### DFARS-PRECISION (new scenario in v3, tuning data)

No v2/v2b baseline exists for DFARS-PRECISION-002. v3 shows 9/11 = 82% pass rate, but this is the scenario the D5 patch was designed to fix. Cannot claim improvement against prior versions — there's no prior version data.

---

## Summary: What Is and Isn't Valid to Claim

| Claim | Valid? | Data |
|---|---|---|
| v3 FPR improved vs v2 on same ALLOW scenarios | **YES** | 70% → 42% on AP-FP-DUP, IAM, BEC-FP-SPINOFF |
| ESCALATE detection is perfect across all versions | **YES** | 0 FN in v2, v2b, or v3 |
| v3 accuracy is 80% or 90% | **NO** | That's one batch. Session range: 50–90%. Average: 77.8%. |
| v3 FPR is 17% | **NO** | That's Batch 2. Session average FPR: 38.1%. |
| PE-CONSOLIDATION improved in v3 | **NO** | v2b 40% pass, v3 33% pass — slight regression |
| DFARS-PRECISION improvement proves D5 patch works | **QUALIFIED** | 82% pass rate, but tuning data — no pre-patch baseline for comparison |
| v3 is overall better than v2 | **YES (narrowly)** | On the 3 scenarios with direct overlap, FPR dropped 70%→42% |

---

## Stochastic Warning

All FPR numbers carry ±20–30% stochastic uncertainty at these sample sizes (3–7 runs per scenario per version). The PE-CONSOLIDATION "regression" (-7%) is within noise. The AP-FP-DUP "improvement" (+33%) is real in direction but uncertain in magnitude. The only number with low variance is ESCALATE detection = 100% across all versions, which is stable at N=30+.

To make FPR claims defensible, each ALLOW scenario needs ≥15–20 runs per governor version. Current counts are 2–10 runs per scenario per version.
