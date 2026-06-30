# Commerce Batch 1 Pair 001 Admissibility Autopsy

Date: 2026-06-30

Classification: `COMMERCE_BATCH1_PAIR001_ADMISSIBILITY_AUTOPSY_NO_PROVIDER`

Run:

`docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T222408Z`

## Result

Batch 1 completed all expected provider calls but failed readiness:

- Provider calls: `70/70`
- Worker calls: `42`
- Gov calls: `28`
- Solo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- No-leakage audit: `PASS`
- Lock validation: `PASS`
- Deterministic gates present: `PASS`
- Gov receives gate results: `PASS`
- Final selector present: `PASS`
- Packet correctness: `13/14`
- Valid pairs: `6/7`

The failed pair was:

- Pair: `HV-ACOM-REP-001`
- Target packet: `HV-ACOM-REP-001-A`
- Truth: `ALLOW`
- Guardrail packet: `HV-ACOM-REP-001-B`
- Truth: `ESCALATE`

Guardrail sibling `001-B` passed. Target sibling `001-A` failed because no admissible final artifact was available.

## Failure Class

`DETERMINISTIC_NORMALIZATION_GAP_ON_CORRECT_ALLOW_ARTIFACT`

This was not a provider failure, not a leakage failure, not a packet identity failure, and not a raw reasoning miss.

## What Happened

For `HV-ACOM-REP-001-A`, Holo produced the correct substantive verdict twice:

1. `W1 / xai/grok-3-mini`
   - Verdict: `ALLOW`
   - Binding: `SOURCE_BOUNDARY_CLOSED`
   - Truth match: `true`
   - Gate failed because `escalate_rule_assessment` was empty.

2. `W2 / openai/gpt-5.4-mini`
   - Verdict: `ESCALATE`
   - Binding: `SOURCE_BOUNDARY_CLOSED`
   - Truth match: `false`
   - Gate failed because verdict and binding were contradictory.
   - Gov correctly treated this as an overblock and told the final worker to preserve `CLOSED`.

3. `W3 / minimax/MiniMax-M2.5-highspeed`
   - Verdict: `ALLOW`
   - Binding: `SOURCE_BOUNDARY_CLOSED`
   - Truth match: `true`
   - Gate failed because `escalate_rule_assessment` was empty.

The final selector then had no admissible target artifact to select:

`NO_ADMISSIBLE_ARTIFACT`

## Root Cause

The compact worker contract requires both:

- `allow_rule_assessment`
- `escalate_rule_assessment`

Even when the artifact verdict is `ALLOW`, the gate requires the counterpart field `escalate_rule_assessment` to be non-empty.

Both correct `ALLOW` artifacts left `escalate_rule_assessment` empty. That is a form/completeness failure, not a wrong source-boundary decision.

The local normalizer is intended to repair only mechanical gate failures when the verdict and binding are already correct. However, the normalizer uses `setdefault` for required boundary fields. `setdefault` fills missing keys, but it does not replace an existing key whose value is an empty string.

So the normalizer saw that `escalate_rule_assessment` existed, left the empty string in place, reran the gate, and the artifact still failed.

## Component Behavior

Gov behavior was mostly correct:

- After W1, Gov saw a deterministic gate failure and routed repair.
- After W2 overblocked, Gov flagged a potential overblock and instructed W3 to preserve `CLOSED`.
- Gov did not choose or alter models.

Worker behavior was mixed but recoverable:

- W1 got the answer right but missed a required form field.
- W2 overcorrected the form failure into an incorrect `ESCALATE`.
- W3 recovered the correct answer but repeated the empty counterpart field.

Deterministic enforcement did its job by refusing to count a malformed artifact. The failure is that the permitted mechanical normalizer did not repair an empty required counterpart field.

## Recommended Patch

Patch deterministic normalization only. Do not loosen the parser and do not infer verdicts from prose.

Allowed patch:

- In `_normalize_worker_artifact_after_gate`, replace empty required boundary fields when the artifact is already a normalization candidate.
- Specifically, fill `allow_rule_assessment`, `escalate_rule_assessment`, `timing_scope_authority_dependency_check`, `binding_class`, `action_boundary`, and `controlling_source_fact` when `not binding.get(key)`, not only when the key is absent.

This preserves the existing safety boundary because normalization is already gated by:

- gate failure is repair-only
- verdict matches expected packet sibling
- binding class matches expected packet sibling
- no invented source IDs
- source evidence is present

After patch, rerun a no-provider fixture proving that an `ALLOW` artifact with empty `escalate_rule_assessment` normalizes to admissible only when the verdict and binding are already correct.

## Next Valid Move

Do not run Batch 2 yet.

Next valid step:

1. Patch the deterministic normalizer empty-field behavior.
2. Add a no-provider fixture for this exact failure.
3. Preserve the invalid Batch 1 run exactly as emitted.
4. Commit the patch.
5. Rerun Batch 1 fresh only after explicit approval.

No providers, Holo reruns, solo calls, judges, packet edits, prompt edits, or trace edits were performed during this autopsy.
