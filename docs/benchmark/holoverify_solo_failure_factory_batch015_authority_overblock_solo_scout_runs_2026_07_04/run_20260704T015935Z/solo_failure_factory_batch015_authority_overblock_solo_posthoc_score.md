# Solo Failure Factory Batch015 Authority-Overblock Post-Hoc Score

- Packets: `40`
- Solo calls: `120`
- Scoring map hash: `b75b720b0a437156c44f84bcd54e899017e41cf19ef52ddcbe48a972850ba520`
- Packet collapse summary: `{'ALL_THREE_SOLO_KNEW': 25, 'ONE_OF_THREE_SOLO_COLLAPSE': 6, 'ALL_THREE_SOLO_COLLAPSE': 7, 'TWO_OF_THREE_SOLO_COLLAPSE': 2}`

## Model Summary

```json
{
  "minimax": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 9,
    "KNEW_ADMISSIBLE": 29,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 2,
    "admissible": 38,
    "correct": 29,
    "false_negative": 9,
    "false_positive": 0,
    "knew_admissible": 29,
    "total": 40
  },
  "openai": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 8,
    "KNEW_ADMISSIBLE": 32,
    "admissible": 40,
    "correct": 32,
    "false_negative": 8,
    "false_positive": 0,
    "knew_admissible": 32,
    "total": 40
  },
  "xai": {
    "FALSE_NEGATIVE_ALLOW_ON_ESCALATE": 7,
    "KNEW_ADMISSIBLE": 28,
    "PARSE_OR_ADMISSIBILITY_FAILURE": 5,
    "admissible": 35,
    "correct": 32,
    "false_negative": 7,
    "false_positive": 0,
    "knew_admissible": 28,
    "total": 40
  }
}
```
