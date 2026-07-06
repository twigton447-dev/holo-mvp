# HoloVerify Stress Matrix Wave 2 Solo Scout Rollup

Status: `SOLO_SCOUT_SCORED_POSTHOC`

- Run dir: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_stress_matrix_expansion_wave2_solo_scout_runs_2026_07_06/run_20260706T202901Z`
- Packets: `60`
- Solo calls: `180`
- Trace hash: `350073a2e96089d9b33b1ae32d3f1ca631dd2f868845e27bdbeb8ed64a57a247`
- Scoring map hash: `edea242aed13d949b977779f19fbbeb91ec89d08103be8e5be8d2df1b781289a`

## Aggregate

```json
{
  "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 42,
  "KNEW_ADMISSIBLE": 124,
  "PARSE_OR_ADMISSIBILITY_FAILURE": 14,
  "admissible": 166,
  "correct": 125,
  "false_negative": 0,
  "false_positive": 42,
  "knew_admissible": 124,
  "parse_or_admissibility_failure": 14,
  "solo_calls": 180
}
```

## Pair Summary

```json
{
  "pairs": [
    {
      "domain": null,
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W2-001-A",
        "HVSM-W2-001-E"
      ],
      "pair_id": "HVSM-W2-001",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W2-002-A",
        "HVSM-W2-002-E"
      ],
      "pair_id": "HVSM-W2-002",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W2-003-A",
        "HVSM-W2-003-E"
      ],
      "pair_id": "HVSM-W2-003",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
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
        "HVSM-W2-004-A",
        "HVSM-W2-004-E"
      ],
      "pair_id": "HVSM-W2-004",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
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
        "HVSM-W2-005-A",
        "HVSM-W2-005-E"
      ],
      "pair_id": "HVSM-W2-005",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W2-006-A",
        "HVSM-W2-006-E"
      ],
      "pair_id": "HVSM-W2-006",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
      "error_classes": {
        "KNEW_ADMISSIBLE": 4,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 2
      },
      "failing_models": [
        "minimax"
      ],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W2-007-A",
        "HVSM-W2-007-E"
      ],
      "pair_id": "HVSM-W2-007",
      "parse_or_admissibility_count": 2,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 3,
        "KNEW_ADMISSIBLE": 2,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 3,
      "legacy_packets": [
        "HVSM-W2-008-A",
        "HVSM-W2-008-E"
      ],
      "pair_id": "HVSM-W2-008",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 4,
      "wrong_verdict_count": 3
    },
    {
      "domain": null,
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
        "HVSM-W2-009-A",
        "HVSM-W2-009-E"
      ],
      "pair_id": "HVSM-W2-009",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": null,
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
        "HVSM-W2-010-A",
        "HVSM-W2-010-E"
      ],
      "pair_id": "HVSM-W2-010",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": null,
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W2-011-A",
        "HVSM-W2-011-E"
      ],
      "pair_id": "HVSM-W2-011",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
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
        "HVSM-W2-012-A",
        "HVSM-W2-012-E"
      ],
      "pair_id": "HVSM-W2-012",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-013-A",
        "HVSM-W2-013-E"
      ],
      "pair_id": "HVSM-W2-013",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-014-A",
        "HVSM-W2-014-E"
      ],
      "pair_id": "HVSM-W2-014",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W2-015-A",
        "HVSM-W2-015-E"
      ],
      "pair_id": "HVSM-W2-015",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "HVSM-W2-016-A",
        "HVSM-W2-016-E"
      ],
      "pair_id": "HVSM-W2-016",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 4,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W2-017-A",
        "HVSM-W2-017-E"
      ],
      "pair_id": "HVSM-W2-017",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 1,
      "legacy_packets": [
        "HVSM-W2-018-A",
        "HVSM-W2-018-E"
      ],
      "pair_id": "HVSM-W2-018",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
        "KNEW_ADMISSIBLE": 4
      },
      "failing_models": [
        "openai",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 2,
      "legacy_packets": [
        "HVSM-W2-019-A",
        "HVSM-W2-019-E"
      ],
      "pair_id": "HVSM-W2-019",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-020-A",
        "HVSM-W2-020-E"
      ],
      "pair_id": "HVSM-W2-020",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": null,
      "error_classes": {
        "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
        "KNEW_ADMISSIBLE": 3,
        "PARSE_OR_ADMISSIBILITY_FAILURE": 1
      },
      "failing_models": [
        "minimax",
        "xai"
      ],
      "false_negative_count": 0,
      "false_positive_count": 2,
      "legacy_packets": [
        "HVSM-W2-021-A",
        "HVSM-W2-021-E"
      ],
      "pair_id": "HVSM-W2-021",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-022-A",
        "HVSM-W2-022-E"
      ],
      "pair_id": "HVSM-W2-022",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-023-A",
        "HVSM-W2-023-E"
      ],
      "pair_id": "HVSM-W2-023",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 2,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
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
        "HVSM-W2-024-A",
        "HVSM-W2-024-E"
      ],
      "pair_id": "HVSM-W2-024",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-025-A",
        "HVSM-W2-025-E"
      ],
      "pair_id": "HVSM-W2-025",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 2
    },
    {
      "domain": null,
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
        "HVSM-W2-026-A",
        "HVSM-W2-026-E"
      ],
      "pair_id": "HVSM-W2-026",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
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
        "HVSM-W2-027-A",
        "HVSM-W2-027-E"
      ],
      "pair_id": "HVSM-W2-027",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    },
    {
      "domain": null,
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
        "HVSM-W2-028-A",
        "HVSM-W2-028-E"
      ],
      "pair_id": "HVSM-W2-028",
      "parse_or_admissibility_count": 1,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 0
    },
    {
      "domain": null,
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
        "HVSM-W2-029-A",
        "HVSM-W2-029-E"
      ],
      "pair_id": "HVSM-W2-029",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": null,
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
        "HVSM-W2-030-A",
        "HVSM-W2-030-E"
      ],
      "pair_id": "HVSM-W2-030",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 3,
      "wrong_verdict_count": 3
    }
  ],
  "summary": {
    "pair_count": 30,
    "pairs_parse_only": 4,
    "pairs_with_any_solo_failure": 26,
    "pairs_with_false_positive": 22,
    "pairs_with_wrong_verdict": 22
  }
}
```

## Claim Boundary

Solo stress-matrix discovery only. No Holo, no Gov, no judges, and no public benchmark claim.
