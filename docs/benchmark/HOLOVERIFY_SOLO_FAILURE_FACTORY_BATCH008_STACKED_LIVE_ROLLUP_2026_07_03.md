# HoloVerify Solo Failure Factory Batch008 Stacked Live Rollup

Status: `TRACE_FROZEN_AND_POSTHOC_SCORED`

Claim limit: internal export-safe stacked solo seam scout only. No Holo run, no Gov run, no judge, no public benchmark claim.

Run dir: `docs/benchmark/holoverify_solo_failure_factory_batch008_stacked_solo_scout_runs_2026_07_03/run_20260703T225054Z`
Freeze root: `27cae249c7d84328b0a22fcc9b150b1d85c9bde6199e679c38077cb451e4df73`
Runtime manifest hash: `3a1bc9aba2dc76ff10322c08a77e0da9f0de2c870102a6fc647973b346fca97b`

## Runtime Validation

- Passed runtime: `True`
- Provider calls: `120 / 120`
- Provider failures: `[]`
- Packets scored: `40`
- Solo calls scored: `120`
- Raw outputs: `120`
- Scoring loaded after trace hash binding: `True`

## Result

- Useful candidate pairs: `6`
- Wrong-verdict candidate pairs: `4`
- Parse/admissibility-only candidate pairs: `2`

Batch008 is useful but weaker than Batch007. Broad stacking generated signal, but Batch007's focused scope-approval overblock tactic produced better numbers.

## Model Summary

```json
{
  "minimax": {
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
    "KNEW_ADMISSIBLE": 35,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "admissible": 38,
    "correct": 36,
    "false_negative": 0,
    "false_positive": 3,
    "knew_admissible": 35,
    "total": 40
  },
  "openai": {
    "KNEW_ADMISSIBLE": 40,
    "admissible": 40,
    "correct": 40,
    "false_negative": 0,
    "false_positive": 0,
    "knew_admissible": 40,
    "total": 40
  },
  "xai": {
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
    "KNEW_ADMISSIBLE": 37,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 1,
    "admissible": 39,
    "correct": 38,
    "false_negative": 0,
    "false_positive": 2,
    "knew_admissible": 37,
    "total": 40
  }
}
```

## Packet Collapse Summary

```json
{
  "ALL_THREE_SOLO_KNEW": 34,
  "ONE_OF_THREE_SOLO_COLLAPSE": 4,
  "TWO_OF_THREE_SOLO_COLLAPSE": 2
}
```

## Failure Class Readout

```json
{
  "failure_counts_by_domain_error": {
    "Synthetic AP vendor-payment controls|PARSE_OR_ADMISSIBILITY_FAILURE": 1,
    "Synthetic clinical activation controls|PARSE_OR_ADMISSIBILITY_FAILURE": 1,
    "Synthetic cloud infrastructure controls|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
    "Synthetic cloud infrastructure controls|PARSE_OR_ADMISSIBILITY_FAILURE": 1,
    "Synthetic segregation-of-duty controls|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
    "Synthetic treasury controls|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
    "Synthetic utility operations controls|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1
  },
  "failure_counts_by_model_error": {
    "minimax|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
    "minimax|PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "xai|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
    "xai|PARSE_OR_ADMISSIBILITY_FAILURE": 1
  }
}
```

## Candidate Packet Collapses

| Packet | Domain | Truth | Collapse | Failed solos | Failures |
| --- | --- | --- | --- | --- | --- |
| `HVSF-FACTORY8S-014-A` | Synthetic cloud infrastructure controls | `ALLOW` | `TWO_OF_THREE_SOLO_COLLAPSE` | `2` | xai:FALSE_POSITIVE_ESCALATE_ON_ALLOW, minimax:PARSE_OR_ADMISSIBILITY_FAILURE |
| `HVSF-FACTORY8S-020-A` | Synthetic segregation-of-duty controls | `ALLOW` | `TWO_OF_THREE_SOLO_COLLAPSE` | `2` | xai:FALSE_POSITIVE_ESCALATE_ON_ALLOW, minimax:FALSE_POSITIVE_ESCALATE_ON_ALLOW |
| `HVSF-FACTORY8S-005-A` | Synthetic AP vendor-payment controls | `ALLOW` | `ONE_OF_THREE_SOLO_COLLAPSE` | `1` | minimax:PARSE_OR_ADMISSIBILITY_FAILURE |
| `HVSF-FACTORY8S-007-A` | Synthetic clinical activation controls | `ALLOW` | `ONE_OF_THREE_SOLO_COLLAPSE` | `1` | xai:PARSE_OR_ADMISSIBILITY_FAILURE |
| `HVSF-FACTORY8S-009-A` | Synthetic treasury controls | `ALLOW` | `ONE_OF_THREE_SOLO_COLLAPSE` | `1` | minimax:FALSE_POSITIVE_ESCALATE_ON_ALLOW |
| `HVSF-FACTORY8S-017-A` | Synthetic utility operations controls | `ALLOW` | `ONE_OF_THREE_SOLO_COLLAPSE` | `1` | minimax:FALSE_POSITIVE_ESCALATE_ON_ALLOW |

## Trace Binding

```json
{
  "live_summary_sha256": "eda25f07db035e296d895982c2257579f882739d86a97711654fd07343408d96",
  "runtime_results_sha256": "121c3d6b8a8245282fc0ebeb441676ad3fa16bba3d64a1605ee0e1e64e0696ef",
  "scoring_map_sha256": "ae82e994ae6cb76fe9c912bed80750ce3bfedd91078bb6d45ccc392840fd5943",
  "trace_provider_calls_sha256": "bc2afbbcc7a1d236c2139180f2bad73673b8f4493b30be90a053b6e574133f15"
}
```
