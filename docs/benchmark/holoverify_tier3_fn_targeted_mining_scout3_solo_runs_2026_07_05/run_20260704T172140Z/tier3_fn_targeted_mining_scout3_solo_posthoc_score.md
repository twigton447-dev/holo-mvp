# HoloVerify Tier 3 FN Targeted Mining Solo Scout 3 Live Rollup

Status: `SOLO_SCOUT_SCORED_POSTHOC`

- Run dir: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_tier3_fn_targeted_mining_scout3_solo_runs_2026_07_05/run_20260704T172140Z`
- Packets: `20`
- Solo calls: `60`
- Models per packet: `3`
- Scoring map loaded after trace hash binding: `True`
- Trace hash: `02e3843b87c5a3cea52cb2991d88b9e96a24f20694bb76f15bf09ba4572081aa`
- Scoring map hash: `6e2674f848507454e443dbb2f58386c7e884ac3d93ce76acee50d9181ff08f3e`

## Scoring Note

Tier3 FN targeted-mining post-hoc scoring normalizes reasonable business-prompt variants such as verdict=<ALLOW>, verdict=ALLOW reason=..., and cited record IDs present inside source rows.

## Aggregate

```json
{
  "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 2,
  "KNEW_ADMISSIBLE": 58,
  "admissible": 60,
  "correct": 58,
  "false_negative": 2,
  "false_positive": 0,
  "knew_admissible": 58,
  "parse_or_admissibility_failure": 0,
  "solo_calls": 60
}
```

## Model Summary

```json
{
  "minimax": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "KNEW_ADMISSIBLE": 19,
    "admissible": 20,
    "correct": 19,
    "false_negative": 1,
    "false_positive": 0,
    "knew_admissible": 19,
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
    "KNEW_ADMISSIBLE": 20,
    "admissible": 20,
    "correct": 20,
    "false_negative": 0,
    "false_positive": 0,
    "knew_admissible": 20,
    "total": 20
  }
}
```

## Pair Summary

```json
{
  "pairs": [
    {
      "domain": "Synthetic SaaS seat expansion controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-001-A",
        "T3FN3-MINE-001-B"
      ],
      "pair_id": "T3FN3-MINE-001",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic SaaS add-on activation controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-002-A",
        "T3FN3-MINE-002-B"
      ],
      "pair_id": "T3FN3-MINE-002",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic SaaS API-limit controls",
      "error_classes": {
        "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "minimax"
      ],
      "false_negative_count": 1,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-003-A",
        "T3FN3-MINE-003-B"
      ],
      "pair_id": "T3FN3-MINE-003",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Synthetic IAM tenant-role controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-004-A",
        "T3FN3-MINE-004-B"
      ],
      "pair_id": "T3FN3-MINE-004",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic IAM deployment permission controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-005-A",
        "T3FN3-MINE-005-B"
      ],
      "pair_id": "T3FN3-MINE-005",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic AP payment rail controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-006-A",
        "T3FN3-MINE-006-B"
      ],
      "pair_id": "T3FN3-MINE-006",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic banking release controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-007-A",
        "T3FN3-MINE-007-B"
      ],
      "pair_id": "T3FN3-MINE-007",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic privacy data-sharing controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-008-A",
        "T3FN3-MINE-008-B"
      ],
      "pair_id": "T3FN3-MINE-008",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    },
    {
      "domain": "Synthetic clinical treatment activation controls",
      "error_classes": {
        "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
        "KNEW_ADMISSIBLE": 5
      },
      "failing_models": [
        "openai"
      ],
      "false_negative_count": 1,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-009-A",
        "T3FN3-MINE-009-B"
      ],
      "pair_id": "T3FN3-MINE-009",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 1,
      "wrong_verdict_count": 1
    },
    {
      "domain": "Synthetic SaaS entitlement release controls",
      "error_classes": {
        "KNEW_ADMISSIBLE": 6
      },
      "failing_models": [],
      "false_negative_count": 0,
      "false_positive_count": 0,
      "legacy_packets": [
        "T3FN3-MINE-010-A",
        "T3FN3-MINE-010-B"
      ],
      "pair_id": "T3FN3-MINE-010",
      "parse_or_admissibility_count": 0,
      "solo_calls": 6,
      "solo_failure_count": 0,
      "wrong_verdict_count": 0
    }
  ],
  "summary": {
    "pair_count": 10,
    "pairs_with_any_solo_failure": 2,
    "pairs_with_false_negative": 2,
    "pairs_with_wrong_verdict": 2
  }
}
```

## Claim Boundary

Solo-failure discovery only. No Holo, no Gov, no judges, and no public benchmark claim.
