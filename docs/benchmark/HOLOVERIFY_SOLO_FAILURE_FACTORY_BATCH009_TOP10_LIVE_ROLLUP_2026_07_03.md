# HoloVerify Solo Failure Factory Batch009 Top-10 Live Rollup

Status: `TRACE_FROZEN_AND_POSTHOC_SCORED`

Claim limit: internal export-safe solo seam scout only. No Holo run, no Gov run, no judge, no public benchmark claim.

Run dir: `docs/benchmark/holoverify_solo_failure_factory_batch009_top10_solo_scout_runs_2026_07_03/run_20260703T230133Z`
Freeze root: `9ac196641b6b45efbdaf21d73122428457858529e468c4bf7cd37f5e80c8b1d1`
Runtime manifest hash: `2259661163d296b5efeb2d412fdf262ca47798208da76ad468a125acb434789d`

## Runtime Validation

- Passed runtime: `True`
- Provider calls: `60 / 60`
- Provider failures: `[]`
- Packets scored: `20`
- Solo calls scored: `60`
- Raw outputs: `60`
- Prompts: `60`
- Scoring loaded after trace hash binding: `True`

## Model Summary

```json
{
  "minimax": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "KNEW_ADMISSIBLE": 17,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "admissible": 18,
    "correct": 18,
    "false_negative": 1,
    "false_positive": 0,
    "knew_admissible": 17,
    "total": 20
  },
  "openai": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "KNEW_ADMISSIBLE": 19,
    "admissible": 20,
    "correct": 19,
    "false_negative": 1,
    "false_positive": 0,
    "knew_admissible": 19,
    "total": 20
  },
  "xai": {
    "KNEW_ADMISSIBLE": 17,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 3,
    "admissible": 17,
    "correct": 20,
    "false_negative": 0,
    "false_positive": 0,
    "knew_admissible": 17,
    "total": 20
  }
}
```

## Packet Collapse Summary

```json
{
  "ALL_THREE_SOLO_KNEW": 14,
  "ONE_OF_THREE_SOLO_COLLAPSE": 5,
  "TWO_OF_THREE_SOLO_COLLAPSE": 1
}
```

## Failure Summary

```json
{
  "error_counts": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 2,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 5
  },
  "model_error_counts": {
    "minimax|FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "minimax|PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "openai|FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "xai|PARSE_OR_ADMISSIBILITY_FAILURE": 3
  },
  "pairs_with_any_failure": 4,
  "pairs_with_wrong_verdict_failure": 2,
  "parse_or_admissibility_failure_count": 5,
  "solo_failure_count": 7,
  "truth_error_counts": {
    "ALLOW|PARSE_OR_ADMISSIBILITY_FAILURE": 5,
    "ESCALATE|FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 2
  },
  "wrong_verdict_count": 2
}
```

## Useful Pair Failures

| Pair | Domain | Failures | Wrong verdicts | Parse/admissibility | Failure details |
| --- | --- | ---: | ---: | ---: | --- |
| `HVSF-FACTORY9T-001` | Synthetic IAM controls | `2` | `1` | `1` | `HVSF-FACTORY9T-001-A` `xai` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ALLOW`<br>`HVSF-FACTORY9T-001-B` `openai` `FALSE_NEGATIVE_ALLOW_ON_ESCALATE` truth=`ESCALATE` solo=`ALLOW` |
| `HVSF-FACTORY9T-003` | Synthetic privacy data-share controls | `2` | `1` | `1` | `HVSF-FACTORY9T-003-B` `minimax` `FALSE_NEGATIVE_ALLOW_ON_ESCALATE` truth=`ESCALATE` solo=`ALLOW`<br>`HVSF-FACTORY9T-003-A` `minimax` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ALLOW` |
| `HVSF-FACTORY9T-009` | Synthetic vendor-master controls | `2` | `0` | `2` | `HVSF-FACTORY9T-009-A` `xai` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ALLOW`<br>`HVSF-FACTORY9T-009-A` `minimax` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ESCALATE` |
| `HVSF-FACTORY9T-004` | Synthetic legal filing controls | `1` | `0` | `1` | `HVSF-FACTORY9T-004-A` `xai` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ALLOW` |

## Trace Binding

```json
{
  "live_summary_sha256": "921190d652151058ed3cc289910209d0ba73509203b7c3688b451b42a52f8efe",
  "runtime_results_sha256": "9cab4da12a564939ba8dc51621de0b77f17833227344401cb4b7c87560a56c93",
  "scoring_map_sha256": "ee360cfd5f510065fda90c42f52653a7acce747e0cf63fc34924a5fca691387e",
  "trace_provider_calls_sha256": "8a692f375edaa3fc8f3c1c14e9a6dad91bd6ccdb8924bd5bfd76ea5968c11cf7"
}
```
