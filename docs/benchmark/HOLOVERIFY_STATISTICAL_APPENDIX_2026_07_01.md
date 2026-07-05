# HoloVerify Statistical Appendix

Classification: `HOLOVERIFY_STATISTICAL_APPENDIX_NO_PROVIDER_2026_07_01`
Root signature: `6ae112ed1043af2f0182e8f6bf6e5e0d7e6246f7dcd2d1cb446eb0c3ffddc8f8`

This appendix packages the current clean benchmark-grade HoloVerify action-boundary denominator.
It was generated without provider calls and excludes canaries, precursors, and missing-evidence rows.

## Current Denominator

- Packets: `614`
- Correct packets: `614`
- Observed errors: `0`
- Sibling pairs: `307`
- ALLOW truths: `307`
- ESCALATE truths: `307`

## Confusion Matrix

Positive class: `ESCALATE`. Negative class: `ALLOW`.

| Metric | Count |
| --- | ---: |
| TP | 307 |
| TN | 307 |
| FP | 0 |
| FN | 0 |

| Rate | Observed |
| --- | ---: |
| Sensitivity / TPR | 100.00% |
| Specificity / TNR | 100.00% |
| FPR | 0.00% |
| FNR | 0.00% |
| PPV | 100.00% |
| NPV | 100.00% |

## 95% Upper Bounds

| Metric | Errors | n | Exact one-sided 95% upper | Wilson 95% upper | Rule of three |
| --- | ---: | ---: | ---: | ---: | ---: |
| Overall packet error | 0 | 614 | 0.487% | 0.622% | 0.489% |
| False positive rate | 0 | 307 | 0.971% | 1.236% | 0.977% |
| False negative rate | 0 | 307 | 0.971% | 1.236% | 0.977% |

## Included Evidence Families

| Evidence family | Packets | Pairs | Correct | Source |
| --- | ---: | ---: | ---: | --- |
| `Agentic Commerce / Order Execution Replication` | 40 | 20 | 40 | `domain_consolidation_ledger` |
| `Clinical Activation Boundary Controls / Kit C` | 40 | 20 | 40 | `domain_consolidation_ledger` |
| `IT Access / Permission Change Replication` | 40 | 20 | 40 | `domain_consolidation_ledger` |
| `Vendor-Master Payment Controls / AP Replication` | 40 | 20 | 40 | `domain_consolidation_ledger` |
| `Wave2+Wave3+Wave4 / HR-Privacy-Finance-Government-Benefits-Banking-Defense-Insurance-Utilities` | 174 | 87 | 174 | `wave2_wave3_wave4_combined_evidence` |
| `Wave5 Completed 7-Domain Expansion / Medical-Treasury-Legal-Cloud-Security-PublicSector-OT` | 280 | 140 | 280 | `wave5_completed_batch_evidence` |

## Excluded From Clean Denominator

| Evidence family | Packets | Reason |
| --- | ---: | --- |
| `Agentic Commerce / All-Six Collapse Canary` | 6 | lock-rooted canary, useful but not benchmark-grade denominator |
| `D11-Lock HoloBuild Mini-Suite` | 5 | HoloBuild quality suite, not HoloVerify action-boundary denominator and missing repo evidence |
| `Hard ALLOW FP 5-Pair Precursor` | 10 | precursor frozen pending judge, not included in clean denominator |
| `Wave 2 / HR-Data Privacy-Finance Targeted Holo Runs` | 74 | superseded here by Wave2+Wave3+Wave4 combined evidence |

## Sample Size Planning

| Target upper bound | n needed with zero errors | More packets for overall | More balanced pairs for both FP/FN | More balanced packets for both FP/FN |
| ---: | ---: | ---: | ---: | ---: |
| < 1.0% | 299 | 0 | 0 | 0 |
| < 0.5% | 598 | 0 | 291 | 582 |
| < 0.25% | 1197 | 583 | 890 | 1780 |
| < 0.1% | 2995 | 2381 | 2688 | 5376 |

## Why Zero Errors Does Not Mean Zero Risk

Zero observed errors means no failures appeared in this locked sample. It does not prove the true error rate is zero; it means the plausible upper risk is bounded by the confidence interval.

The current honest packet-level statement is:

> Across 614 clean benchmark-grade HoloVerify action-boundary packets, the architecture observed 0 errors. The exact one-sided 95% upper bound on packet-level error is 0.487%, with a Wilson upper band of 0.622%.

The current honest FP/FN statement is:

> With 307 ALLOW and 307 ESCALATE truths, observed FPR and FNR are 0%. The exact one-sided 95% upper bound per side is 0.971%, with a Wilson upper band of 1.236%.

## Assertions

| Assertion | Status |
| --- | --- |
| `packets_614` | `PASS` |
| `pairs_307` | `PASS` |
| `allow_truths_307` | `PASS` |
| `escalate_truths_307` | `PASS` |
| `observed_errors_zero` | `PASS` |
| `tp_307` | `PASS` |
| `tn_307` | `PASS` |
| `fp_zero` | `PASS` |
| `fn_zero` | `PASS` |
| `no_provider_calls` | `PASS` |
| `canaries_and_precursors_excluded` | `PASS` |
