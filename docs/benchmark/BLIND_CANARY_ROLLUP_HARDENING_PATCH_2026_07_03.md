# Blind Canary Rollup Hardening Patch

Status: `NO_PROVIDER_PATCH`

Created: `2026-07-03T00:57:21Z`

Provider calls made by this patch: `0`

Judge calls made by this patch: `0`

## Why This Patch Exists

Fable passed the 20-packet blind canary rollup with limitations. The limitations
were not detected answer-key channels, but they were proof-quality gaps before a
larger blind run:

- the old score artifact did not bind itself to the exact trace hash it scored;
- the old live wrapper contained both live execution and post-hoc scoring;
- the wrapper itself was not covered by the static/shim discipline;
- the canary history used manual reruns after content-contract failures, so a
  future run needs a pre-declared attempt budget.

## Patch Summary

1. Split post-hoc scoring out of the live wrapper.

   New scorer:

   `docs/benchmark/score_holoverify_blind_canary_posthoc_2026_07_03.py`

   The live wrapper now freezes runtime traces only. It reports the exact
   post-hoc scoring command instead of loading the scoring map.

2. Add trace-hash binding to the post-hoc score artifact.

   The new scorer writes:

   - `trace_calls_sha256`
   - `trace_provider_calls_sha256`
   - `runtime_results_sha256`
   - `live_summary_sha256`
   - `scoring_map_sha256`

3. Remove the scoring-map path from the live wrapper.

   The live wrapper still carries the expected scoring-map hash for audit
   reference, but it no longer has a `SCORING_MAP` file path or score function.

4. Declare the attempt budget.

   Future blind runtime runs now emit:

   - `ATTEMPT_BUDGET_POLICY_VERSION=BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`
   - `max_content_contract_attempts_per_packet=1`
   - `max_live_run_attempts_per_packet=1`
   - transport retries remain bounded separately
   - content failures are not retried
   - manual rerun requires new approval and preserved invalid trace

5. Expand no-provider tests.

   Added tests verify:

   - live preflight does not read scoring-map bytes;
   - live wrapper does not keep a scoring-map path or post-hoc scorer;
   - post-hoc score binds itself to frozen trace hashes;
   - wrapper import-closure scan has only detector literals;
   - attempt-budget fields are present in preflight.

6. Apply Fable's minor hardening-review followups.

   After Fable returned `PASS_TO_BUILD_FREEZE_120_PACKET_BLIND_BANK`, the
   wrapper artifact fields were changed from bare assurance literals to
   test-backed access-control fields, git preflight failure now reports a clear
   `git_head_unavailable` blocker, future rollups are required to recompute
   score-artifact trace hashes, and the 120 sequence lock now requires any
   ablation deferral to be file-backed with a reason.

## Claim Boundary

This patch does not convert the 20-packet canary into an error-rate claim.

It makes the next blind run cleaner: runtime first, trace freeze, separate
post-hoc score, hash-bound score artifact.
