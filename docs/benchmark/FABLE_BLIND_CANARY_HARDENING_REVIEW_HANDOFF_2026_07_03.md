# Fable Blind Canary Hardening Review Handoff

Status: `READY_FOR_READ_ONLY_REVIEW`

Created: `2026-07-03T00:57:21Z`

Provider calls made by this handoff: `0`

Judge calls made by this handoff: `0`

## Mission

Please review the no-provider hardening patch that follows your
`PASS_WITH_LIMITATIONS` rollup audit.

This is not a request to approve public claims. It is a request to verify that
the next blind run will have cleaner proof mechanics before we build/freeze the
120-packet bank.

## Files To Review First

1. `docs/benchmark/BLIND_CANARY_ROLLUP_HARDENING_PATCH_2026_07_03.md`
2. `docs/benchmark/BLIND_CANARY_ROLLUP_HARDENING_PATCH_2026_07_03.json`
3. `docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py`
4. `docs/benchmark/score_holoverify_blind_canary_posthoc_2026_07_03.py`
5. `tests/test_holoverify_blind_canary_live_wrapper.py`
6. `docs/benchmark/HOLOVERIFY_BLIND_CANARY_20PKT_ROLLUP_2026_07_03.md`
7. `docs/benchmark/HOLOVERIFY_BLIND_CANARY_20PKT_ROLLUP_2026_07_03.json`

## What Changed

The patch attempts to close your L2/L4/L5 proof-quality issues:

- live wrapper freezes traces only;
- post-hoc scoring moved to a separate script;
- score artifact binds itself to frozen trace hashes;
- live preflight no longer reads scoring-map bytes;
- live wrapper no longer has a `SCORING_MAP` file path;
- attempt budget is declared before the next run;
- wrapper tests now cover the scoring split and wrapper import closure;
- rollup language now discloses two contract versions and four preserved invalid
  attempts totaling 119 provider calls.

## Please Verify

Answer these directly:

1. Does the live wrapper truly avoid loading or reading the scoring map?
2. Does the post-hoc scorer bind its output to the exact frozen trace hashes?
3. Does the live summary now make clear that scoring is a separate post-freeze
   step?
4. Is the attempt budget enforceable and clear enough for the 120-packet run?
5. Does the wrapper static/import-closure test actually cover the relevant live
   path, or is there still an unscanned truth channel?
6. Does the rollup language now carry your limitations without accidentally
   making a rate claim?
7. Is anything in this patch merely moving the problem rather than closing it?

## Required Verdict Shape

Return one of:

- `PASS_TO_BUILD_FREEZE_120_PACKET_BLIND_BANK`
- `PASS_WITH_MINOR_DOC_FIXES`
- `BLOCK_NEEDS_CODE_FIX`
- `BLOCK_NEEDS_TEST_FIX`
- `BLOCK_CLAIM_LANGUAGE_ONLY`

Then provide:

1. Findings ordered by severity.
2. Recomputed no-provider test result if you run tests.
3. Whether the next step may be building/freezing the 120-packet blind bank.
4. Any exact claim-language correction.

## Claim Boundary

Even if this passes, it licenses only the next prep step:

> build/freeze a 120-packet blinded runtime bank under the hardened proof
> discipline.

It does not license:

- provider execution;
- public benchmark claims;
- FP/FN rates;
- Wilson or exact intervals;
- solo comparison claims;
- architecture superiority claims.

