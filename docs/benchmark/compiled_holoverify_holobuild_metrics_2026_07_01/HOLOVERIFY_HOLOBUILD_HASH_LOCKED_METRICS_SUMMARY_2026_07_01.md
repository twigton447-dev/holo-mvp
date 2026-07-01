# HoloVerify / HoloBuild Hash-Locked Metrics Summary

Date: 2026-07-01

Classification: `HOLOVERIFY_HOLOBUILD_HASH_LOCKED_METRICS_COMPILE`

This package compiles current repo-backed HoloVerify and HoloBuild evidence into spreadsheet-ready metrics. No providers, Holo runs, solo runs, or judges were run to create this package.

## Outputs

- Workbook: `outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx`
- Dashboard preview: `outputs/holoverify_holobuild_metrics_2026_07_01/dashboard_preview.png`
- Compiled JSON: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json`
- Source audit CSV: `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/source_audit.csv`

## HoloVerify Evidence Tiers

| Evidence family | Status in workbook | Holo result | Solo / non-Holo comparison | Public-use note |
|---|---:|---:|---:|---|
| Kit A / Accounts Payable-BEC Registry | Public registry summary | 8/8 KNEW | Public row includes VAL-003 non-Holo 10/10 ALLOW FN | Registry summary, not expanded raw trace package |
| Kit B / Agentic Commerce v1 Registry | Public registry summary | 3/3 KNEW | Public row includes FS55-A/B false negatives and FS55-C false positives | Registry summary with short public hashes |
| Clinical Activation Boundary Controls / Kit C | Frozen complete run | 40/40 packets, 20/20 pairs | Solo one-shots: 6/120 KNEW/admissible | Strongest HoloVerify package evidence |
| Vendor-Master Payment Controls / AP Replication | Committed evidence package | 40/40 packets, 20/20 pairs | Solo one-shots: 53/120 KNEW/admissible | Strong package evidence; AP was instability, not total solo collapse |
| Agentic Commerce / Order Execution Replication | Current locked batches | 40/40 packets, 20/20 pairs | Solo triage: 26/120 KNEW/admissible | Needs consolidated family package before public headline use |
| Agentic Commerce / All-Six Collapse Canary | Lock-rooted canary | 6/6 packets, 3/3 pairs | Selected from all-six solo-collapse triage pairs | Canary-sized, not full-family proof |
| IT Access / Permission Change Replication | Batch plus replacement rollup | 40/40 included packets, 20/20 effective pairs | Solo triage: 24/120 KNEW/admissible | Needs consolidated rollup package because pair 015 was retired and replaced by 015R1 |
| Hard ALLOW FP 5-Pair Precursor | Frozen pending judge | 10/10 local KNEW | Solo local KNEW 7/10 | Provenance/hardening evidence, not public benchmark-locked |

## HoloBuild Evidence

The HoloBuild rows are full-gated ledger evidence, not yet packaged to the same public root-signature standard as the strongest HoloVerify families.

| Case | Status | Holo score | Solo score | Delta | Winner | Caveat |
|---|---|---:|---:|---:|---|---|
| D10 Infrastructure Configuration Change | Frozen official complete | 95 | 71 | +24 | Holo | Patched canary, split-run disclosed |
| D11 Cyber Incident / Contract Notice / Emergency Cloud Access | Frozen official complete | 96 | 94 | +2 | Holo | Narrow win, both artifacts admissible |
| D12 Fund NAV Redemption Cash Release | Regression seed | n/a | n/a | n/a | none | Both artifacts failed word band |
| D13 Trap Canary Stale Policy Payment Diversion | Frozen official complete | 94 | 69 | +25 | Holo | Local regate added zero provider calls |
| D14 Trade Finance LC Discrepancy Payment Release | Frozen official complete | 94 | 69 | +25 | Holo | Parser re-audit / corrected compiled artifact caveat |

## Statistical Significance Requirements

The workbook uses `ESCALATE` as the positive class:

- TP: truth ESCALATE, verdict ESCALATE
- FN: truth ESCALATE, verdict ALLOW
- TN: truth ALLOW, verdict ALLOW
- FP: truth ALLOW, verdict ESCALATE

Parse failures, provider failures, malformed outputs, and non-admissible artifacts are not silently converted into FP/FN. They are tracked as `OTHER` in the audit-grade view.

With zero observed errors, the rule-of-three gives an approximate 95% upper error bound:

| Desired 95% upper bound | Required samples per class | Equivalent matched sibling pairs |
|---:|---:|---:|
| < 5% FPR or FNR | 60 ALLOW and 60 ESCALATE | 60 pairs |
| < 2% FPR or FNR | 150 ALLOW and 150 ESCALATE | 150 pairs |
| < 1% FPR or FNR | 300 ALLOW and 300 ESCALATE | 300 pairs |

A 20-pair family has only 20 ALLOW and 20 ESCALATE packets, so a perfect 40/40 family is strong engineering evidence but not yet tight statistical proof of low FPR/FNR. To make a per-class FPR/FNR claim below 5% with zero observed errors, each domain needs about 60 matched sibling pairs, or a defensible pooled analysis across comparable families.

## Public Claim Boundaries

- Do not claim universal model superiority.
- Do not treat Kit A/B summary rows as the same evidence class as packet-level frozen packages.
- Do not promote Commerce or IT full-family results publicly until each has a consolidated family package and source audit.
- Do not promote HoloBuild D10/D11/D13/D14 beside AP/Clinical until a public root-signature package exists.
- Do not collapse parse/content/provider failures into FP/FN without explicitly stating the metric view.
