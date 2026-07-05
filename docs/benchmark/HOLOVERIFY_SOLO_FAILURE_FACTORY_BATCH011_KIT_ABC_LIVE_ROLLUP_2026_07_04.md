# HoloVerify Solo Failure Factory Batch011 Kit A/B/C Live Rollup

Status: `TRACE_FROZEN_AND_POSTHOC_SCORED`

Claim limit: Internal export-safe solo seam scout only. No Holo run, no Gov run, no judge, no public benchmark claim.

Run dir: `docs/benchmark/holoverify_solo_failure_factory_batch011_kit_abc_solo_scout_runs_2026_07_03/run_20260704T000221Z`
Freeze root: `410d96251d9d25b8cf7889123bb95145d0fcce25779a82e8c1187e8a0b12f76b`
Runtime manifest hash: `b02dc9c519b8d051edae5c7c83b52811dbc3aa8853a53d7c5534c558e937cb00`

## Runtime Validation

- Passed runtime: `True`
- Provider calls: `120 / 120`
- Provider failures: `[]`
- Packets scored: `40`
- Solo calls scored: `120`
- Raw outputs: `120`
- Prompts: `120`
- Scoring loaded after trace hash binding: `True`

## Model Summary

```json
{
  "minimax": {
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
    "KNEW_ADMISSIBLE": 39,
    "admissible": 40,
    "correct": 39,
    "false_negative": 0,
    "false_positive": 1,
    "knew_admissible": 39,
    "total": 40
  },
  "openai": {
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
    "KNEW_ADMISSIBLE": 38,
    "admissible": 40,
    "correct": 38,
    "false_negative": 0,
    "false_positive": 2,
    "knew_admissible": 38,
    "total": 40
  },
  "xai": {
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
    "KNEW_ADMISSIBLE": 35,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "admissible": 38,
    "correct": 37,
    "false_negative": 0,
    "false_positive": 3,
    "knew_admissible": 35,
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

## Failure Summary

```json
{
  "error_counts": {
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 6,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 2
  },
  "model_error_counts": {
    "minimax|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
    "openai|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
    "xai|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
    "xai|PARSE_OR_ADMISSIBILITY_FAILURE": 2
  },
  "pairs_with_any_failure": 6,
  "pairs_with_wrong_verdict_failure": 5,
  "parse_or_admissibility_failure_count": 2,
  "solo_failure_count": 8,
  "truth_error_counts": {
    "ALLOW|FALSE_POSITIVE_ESCALATE_ON_ALLOW": 6,
    "ALLOW|PARSE_OR_ADMISSIBILITY_FAILURE": 2
  },
  "wrong_verdict_count": 6
}
```

## Useful Pair Failures

| Pair | Domain | Failures | Wrong verdicts | Parse/admissibility | Failure details |
| --- | --- | ---: | ---: | ---: | --- |
| `HVSF-FACTORY11K-003` | Synthetic grant-funded AP controls | `1` | `0` | `1` | `HVSF-FACTORY11K-003-A` `xai` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ALLOW` gate=short_final_answer |
| `HVSF-FACTORY11K-005` | Synthetic split-invoice duplicate controls | `1` | `1` | `0` | `HVSF-FACTORY11K-005-A` `xai` `FALSE_POSITIVE_ESCALATE_ON_ALLOW` truth=`ALLOW` solo=`ESCALATE` |
| `HVSF-FACTORY11K-007` | Synthetic tax-withholding payment controls | `1` | `1` | `0` | `HVSF-FACTORY11K-007-A` `openai` `FALSE_POSITIVE_ESCALATE_ON_ALLOW` truth=`ALLOW` solo=`ESCALATE` |
| `HVSF-FACTORY11K-009` | Synthetic subscription cart controls | `2` | `1` | `1` | `HVSF-FACTORY11K-009-A` `xai` `PARSE_OR_ADMISSIBILITY_FAILURE` truth=`ALLOW` solo=`ALLOW` gate=short_final_answer<br>`HVSF-FACTORY11K-009-A` `openai` `FALSE_POSITIVE_ESCALATE_ON_ALLOW` truth=`ALLOW` solo=`ESCALATE` |
| `HVSF-FACTORY11K-012` | Synthetic agent purchase-cap controls | `2` | `2` | `0` | `HVSF-FACTORY11K-012-A` `xai` `FALSE_POSITIVE_ESCALATE_ON_ALLOW` truth=`ALLOW` solo=`ESCALATE`<br>`HVSF-FACTORY11K-012-A` `minimax` `FALSE_POSITIVE_ESCALATE_ON_ALLOW` truth=`ALLOW` solo=`ESCALATE` |
| `HVSF-FACTORY11K-014` | Synthetic IAM read-only access controls | `1` | `1` | `0` | `HVSF-FACTORY11K-014-A` `xai` `FALSE_POSITIVE_ESCALATE_ON_ALLOW` truth=`ALLOW` solo=`ESCALATE` |

## Transport Anomaly

- Failed partial run preserved: `docs/benchmark/holoverify_solo_failure_factory_batch011_kit_abc_solo_scout_runs_2026_07_03/run_20260703T235608Z`
- Observed provider calls: `51 / 120`
- Failure: `{"attempt": 1, "error": "<urlopen error [Errno 8] nodename nor servname provided, or not known>", "error_type": "URLError", "model": "MiniMax-M2.5-highspeed", "provider": "minimax", "retryable": false, "transport_retry_failures": []}`
- Status: `PRESERVED_FAILED_PARTIAL_TRACE_NOT_SCORED_AS_CLEAN_RUN`
- Repair: Transport retry classifier was updated for DNS nodename/service failures before the clean rerun.

## Trace Binding

```json
{
  "live_summary_sha256": "c0d742afbdfb4051f2eb3a3147f0fb1bf97bce7f1c19dfee6805f6172fa3dd66",
  "runtime_results_sha256": "d341292428562abeac55ccec69ee6b040762046138440eddb154e0d1a690cb04",
  "scoring_map_sha256": "02194e68175a592f7c8d78f5c012341afd5ce02b5ef3a511a261b3144329c974",
  "trace_provider_calls_sha256": "e1c901e868a14726dc967f2b0816dd6fda3065d318f8272ec14efacaa9343ce2"
}
```

## Token Totals

```json
{
  "token_totals": {
    "input_tokens": 70809,
    "output_tokens": 38368,
    "total_tokens": 130071
  },
  "token_totals_by_model": {
    "minimax": {
      "input_tokens": 22448,
      "output_tokens": 28280,
      "total_tokens": 50728
    },
    "openai": {
      "input_tokens": 21954,
      "output_tokens": 5821,
      "total_tokens": 27775
    },
    "xai": {
      "input_tokens": 26407,
      "output_tokens": 4267,
      "total_tokens": 51568
    }
  }
}
```
