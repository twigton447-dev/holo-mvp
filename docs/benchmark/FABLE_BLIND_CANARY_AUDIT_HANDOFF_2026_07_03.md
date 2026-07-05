# Fable Blind Canary Audit Handoff

Status: `READY_FOR_READ_ONLY_FABLE_AUDIT`

Created: `2026-07-03T00:57:21Z`

Provider calls made by this handoff: `0`

Judge calls made by this handoff: `0`

## Plain-English Mission

Please audit the repaired blind canary rollup. The question is not "did Holo
prove a public error rate?" It did not. The question is narrower:

> Does the file-backed evidence support the claim that the repaired blind
> runtime firewall completed 20 opaque packets, kept the scoring map out of the
> live runtime path, froze traces first, and only then scored 20/20 final
> verdicts against the hidden map?

If yes, say exactly that and no more. If no, identify the confound, leak,
survivorship issue, or missing artifact.

## Files To Review First

1. `docs/benchmark/HOLOVERIFY_BLIND_CANARY_20PKT_ROLLUP_2026_07_03.md`
2. `docs/benchmark/HOLOVERIFY_BLIND_CANARY_20PKT_ROLLUP_2026_07_03.json`
3. `docs/benchmark/FABLE_CANARY_GATE_RECORD_2026_07_02.md`
4. `docs/benchmark/HOLOVERIFY_BLIND_CANARY_LIVE_PROVIDER_SCOPE_2026_07_02.md`
5. `docs/benchmark/BLIND_CANARY_W3_FINAL_COMPILER_CONTRACT_PATCH_2026_07_03.md`

Then inspect the run folders named in the rollup:

`docs/benchmark/holoverify_blind_canary_live_runs_2026_07_02/`

## Critical Review Questions

Please answer these directly:

1. Does the rollup correctly distinguish canonical passing traces from preserved
   invalid attempts?
2. Do the canonical passing traces really cover 20 unique opaque packets and
   exactly 100 provider calls?
3. Is there any evidence the scoring map was loaded before trace freeze in the
   canonical passing traces?
4. Are any legacy packet IDs, truth labels, sibling suffixes, `knew_terms`,
   `allow_rule`, or `esc_rule` visible in runtime prompts or payloads?
5. Did the W3 final compiler patch fix the specific failure seen in
   `run_20260703T004112Z`, or did it merely route around it?
6. Does the rollup accidentally overclaim by implying an error-rate, FP/FN,
   Wilson, or architecture-advantage result?
7. Are the token totals, provider counts, run IDs, and packet rows reproducible
   from disk?
8. Is there any remaining ordering, manifest, file-access, import-closure, or
   payload-shape channel that could leak the answer?

## Expected Audit Style

Please be adversarial and file-backed. Do not accept the rollup's own
assertions without recomputing them. Prefer hard classifications:

- `PASS_RUNTIME_FIREWALL_ROLLUP`
- `PASS_WITH_LIMITATIONS`
- `BLOCK_PUBLIC_LANGUAGE_ONLY`
- `BLOCK_ROLLUP_CONFIRMED_DEFECT`
- `BLOCK_NEEDS_TRACE_REBUILD`

## Non-Negotiable Claim Boundary

Even if the audit passes, this canary licenses only:

> No detected answer-key channel in the repaired 20-packet blind runtime
> firewall path, with post-hoc scoring after trace freeze showing 20/20 final
> verdicts matched the hidden map.

It does not license:

- a public benchmark rate
- a confidence interval
- a false-positive or false-negative rate
- a claim that Holo beats solo
- a claim that the old 614-packet result is restored
- a claim that the architecture is generally validated

## Evidence Lineage To Preserve

The invalid attempts are part of the story, not clutter:

- `run_20260702T233202Z`: full 20-packet attempt invalidated by broad worker/Gov
  contract failure after successful transport.
- `run_20260703T000229Z`: packet 2 invalidated by W3 truncation plus retry
  boundary bug.
- `run_20260703T000924Z`: packet 3 invalidated by MiniMax G2 hidden-thinking
  length failure and empty filtered baton.
- `run_20260703T004112Z`: packets 19-20 invalidated by MiniMax W3
  hidden-thinking length failure and empty filtered final compiler output.

Please verify that these are not counted as pass rows, FP/FN rows, or public
benchmark datapoints.

## Suggested Output

Return:

1. Verdict.
2. Findings, ordered by severity.
3. Recomputed counts.
4. Claim-language corrections.
5. Whether the next move should be:
   - larger blind packet bank,
   - more firewall tests,
   - solo/ablation redesign,
   - or another code hardening pass.

