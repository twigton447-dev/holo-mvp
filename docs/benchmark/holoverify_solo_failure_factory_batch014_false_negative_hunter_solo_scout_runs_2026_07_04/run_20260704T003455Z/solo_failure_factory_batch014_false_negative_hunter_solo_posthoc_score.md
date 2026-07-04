# Solo Failure Factory Batch014 False-Negative-Hunter Post-Hoc Score

- Packets: `40`
- Solo calls: `120`
- Scoring map hash: `0ef003fe9b4e4d25e99513546b9a330ff676d86006d870af2ff932ec6a9926e5`
- Packet collapse summary: `{'ONE_OF_THREE_SOLO_COLLAPSE': 7, 'ALL_THREE_SOLO_KNEW': 25, 'ALL_THREE_SOLO_COLLAPSE': 3, 'TWO_OF_THREE_SOLO_COLLAPSE': 5}`

## Model Summary

```json
{
  "minimax": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 2,
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 7,
    "KNEW_ADMISSIBLE": 31,
    "admissible": 40,
    "correct": 31,
    "false_negative": 2,
    "false_positive": 7,
    "knew_admissible": 31,
    "total": 40
  },
  "openai": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 3,
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 2,
    "KNEW_ADMISSIBLE": 35,
    "admissible": 40,
    "correct": 35,
    "false_negative": 3,
    "false_positive": 2,
    "knew_admissible": 35,
    "total": 40
  },
  "xai": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 1,
    "FALSE_POSITIVE_ESCALATE_ON_ALLOW": 8,
    "KNEW_ADMISSIBLE": 28,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 3,
    "admissible": 37,
    "correct": 30,
    "false_negative": 1,
    "false_positive": 8,
    "knew_admissible": 28,
    "total": 40
  }
}
```
