# Validate Pasted Native Browser JSON

This file is internal operator guidance and is not part of the judge-visible packet.

1. Save the returned judge JSON to a local file, for example `/private/tmp/v5_1_native_judge.json`.
2. Run:

```bash
python3 -B artifact_benchmarks/holo_factory/scoring_policies/validate_unified_v5_1_score.py --score-json /private/tmp/v5_1_native_judge.json
```

Expected pass status: `UNIFIED_V5_1_SCORE_VALID`.
