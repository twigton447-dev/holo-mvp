# HoloVerify Stress Matrix Wave 1 Solo Scout Rollup

Status: `SOLO_SCOUT_SCORED_POSTHOC`

- Run dir: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_stress_matrix_expansion_wave1_solo_scout_runs_2026_07_05/run_20260705T215904Z`
- Packets: `40`
- Solo calls: `120`
- Trace hash: `f639b4b62aed7c1eb51e6ecab050f495eb15fdf931d7f8ace51c5f71ca22158f`
- Scoring map hash: `854695052774477c3fbb23c834b40cb6cdd33891f4b47c60512ac829b49365a5`

## Aggregate

```json
{
  "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 23,
  "KNEW_ADMISSIBLE": 90,
  "PARSE_OR_ADMISSIBILITY_FAILURE": 7,
  "admissible": 113,
  "correct": 91,
  "false_negative": 0,
  "false_positive": 23,
  "knew_admissible": 90,
  "parse_or_admissibility_failure": 7,
  "solo_calls": 120
}
```

## Pair Summary

```json
{
  "pairs": [
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "openai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W1-001-A",
        "HVSM-W1-001-E"
      ],
      "pair_id": "HVSM-W1-001",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 4,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "openai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W1-002-A",
        "HVSM-W1-002-E"
      ],
      "pair_id": "HVSM-W1-002",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "openai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W1-003-A",
        "HVSM-W1-003-E"
      ],
      "pair_id": "HVSM-W1-003",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "KNEW_ADMISSIBLE": 5,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "openai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-004-A",
        "HVSM-W1-004-E"
      ],
      "pair_id": "HVSM-W1-004",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
        "KNEW_ADMISSIBLE": 3
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 3,
      "legacy_packets": [
        "HVSM-W1-005-A",
        "HVSM-W1-005-E"
      ],
      "pair_id": "HVSM-W1-005",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "KNEW_ADMISSIBLE": 5,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax"
      ],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-006-A",
        "HVSM-W1-006-E"
      ],
      "pair_id": "HVSM-W1-006",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Public Sector, Benefits & Grants",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
        "KNEW_ADMISSIBLE": 3,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 2,
      "legacy_packets": [
        "HVSM-W1-007-A",
        "HVSM-W1-007-E"
      ],
      "pair_id": "HVSM-W1-007",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": "Legal, Privacy & Regulatory",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "openai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W1-008-A",
        "HVSM-W1-008-E"
      ],
      "pair_id": "HVSM-W1-008",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Legal, Privacy & Regulatory",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
        "KNEW_ADMISSIBLE": 4
      },
      "failing_models": [
        "minimax",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 2,
      "legacy_packets": [
        "HVSM-W1-009-A",
        "HVSM-W1-009-E"
      ],
      "pair_id": "HVSM-W1-009",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 2
    },
    {
      "domain": "Legal, Privacy & Regulatory",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-010-A",
        "HVSM-W1-010-E"
      ],
      "pair_id": "HVSM-W1-010",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Legal, Privacy & Regulatory",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
        "KNEW_ADMISSIBLE": 3
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 3,
      "legacy_packets": [
        "HVSM-W1-011-A",
        "HVSM-W1-011-E"
      ],
      "pair_id": "HVSM-W1-011",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": "Legal, Privacy & Regulatory",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "minimax"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W1-012-A",
        "HVSM-W1-012-E"
      ],
      "pair_id": "HVSM-W1-012",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Operations, Insurance & Industrial",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
        "KNEW_ADMISSIBLE": 3,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 2,
      "legacy_packets": [
        "HVSM-W1-013-A",
        "HVSM-W1-013-E"
      ],
      "pair_id": "HVSM-W1-013",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": "Operations, Insurance & Industrial",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
        "KNEW_ADMISSIBLE": 3,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 2,
      "legacy_packets": [
        "HVSM-W1-014-A",
        "HVSM-W1-014-E"
      ],
      "pair_id": "HVSM-W1-014",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": "Operations, Insurance & Industrial",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-015-A",
        "HVSM-W1-015-E"
      ],
      "pair_id": "HVSM-W1-015",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Operations, Insurance & Industrial",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-016-A",
        "HVSM-W1-016-E"
      ],
      "pair_id": "HVSM-W1-016",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Banking, KYC & Risk",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-017-A",
        "HVSM-W1-017-E"
      ],
      "pair_id": "HVSM-W1-017",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Banking, KYC & Risk",
      "error_classes": {
        "KNEW_ADMISSIBLE": 5,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax"
      ],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W1-018-A",
        "HVSM-W1-018-E"
      ],
      "pair_id": "HVSM-W1-018",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Banking, KYC & Risk",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
        "KNEW_ADMISSIBLE": 3
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 3,
      "legacy_packets": [
        "HVSM-W1-019-A",
        "HVSM-W1-019-E"
      ],
      "pair_id": "HVSM-W1-019",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": "Clinical & Regulated Activation",
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "openai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W1-020-A",
        "HVSM-W1-020-E"
      ],
      "pair_id": "HVSM-W1-020",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    }
  ],
  "summary": {
    "pair_count": 20,
    "pairs_parse_only": 3,
    "pairs_with_any_solo_failure": 16,
    "pairs_with_false_positive": 13,
    "pairs_with_wrong_verdict": 13
  }
}
```

## Claim Boundary

Solo stress-matrix discovery only. No Holo, no Gov, no judges, and no public benchmark claim.
