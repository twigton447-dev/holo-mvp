# Solo Failure Factory Batch005 Post-Hoc Score

- Packets: `20`
- Solo calls: `60`
- Scoring map hash: `91efdfa719ab234644831005c3fc875a56c7be7d13a6de15e90361266dcdf0c5`
- Packet collapse summary: `{'ALL_THREE_SOLO_KNEW': 14, 'ONE_OF_THREE_SOLO_COLLAPSE': 5, 'TWO_OF_THREE_SOLO_COLLAPSE': 1}`

## Model Summary

```json
{
  "minimax": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 2,
    "KNEW_ADMISSIBLE": 17,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 1,
    "admissible": 19,
    "correct": 18,
    "false_negative": 2,
    "false_positive": 0,
    "knew_admissible": 17,
    "total": 20
  },
  "openai": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 1,
    "KNEW_ADMISSIBLE": 18,
    "admissible": 20,
    "correct": 18,
    "false_negative": 1,
    "false_positive": 1,
    "knew_admissible": 18,
    "total": 20
  },
  "xai": {
    "KNEW_ADMISSIBLE": 18,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "admissible": 18,
    "correct": 20,
    "false_negative": 0,
    "false_positive": 0,
    "knew_admissible": 18,
    "total": 20
  }
}
```
