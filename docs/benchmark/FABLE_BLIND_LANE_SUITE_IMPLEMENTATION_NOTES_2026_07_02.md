# Fable Blind-Lane Suite Implementation Notes

Status: IMPLEMENTED_NO_PROVIDER
Date: 2026-07-02
Spec: `docs/benchmark/FABLE_BLIND_LANE_DISCONFIRMATION_BATTERY_2026_07_02.md`

Boundaries held: no providers, no judges, no frozen evidence edited, no packet truths changed, no public claims. All new code is tests, fixture builders, lint, and a suite package. Fixture output goes to pytest temp dirs only.

## Layout

```
blind_lane_suite/                 suite package (importable; pyproject already sets pythonpath=["."])
  __init__.py                     paths, BLIND_RUNNER_MODULE env contract, canary ceiling
  runner_contract.py              blind-runner interface (documented in module docstring)
  id_channel.py                   T1 scanner
  static_guards.py                T2/T3 AST truth-reachability scanner
  fixtures.py                     synthetic pair spec, poisoned variants, mock transcripts,
                                  selector sweep cases, FailingTransport
  hash_chain.py                   T3 verifier
  claim_lint.py                   T7 lint
  canary_skew.py                  T5 difficulty proxy + skew check
  budget_audit.py                 T6 envelope extraction + retry checks
tests/
  test_blind_lane_t1_id_channel.py       … t2 … t3 … t4 … t5 … t6 … t7
```

Contract: a future blind runner (Codex-built) registers via `BLIND_RUNNER_MODULE`
env var and must expose `run_blind_fixture`, `select_final`, `apply_criteria`,
`SELECTOR_CRITERIA`, `BUDGET_LIMITS` (full signatures in `runner_contract.py`).
Unregistered ⇒ contract tests **skip with an explicit "skip is not a pass"
message**. Registered-but-incomplete ⇒ **fail** (contract violation).

## Current run state

```
28 passed, 0 skipped, 0 failed
```

- All four detector-validation tests pass: T1 catches the known governed-lane
  suffix leak; T2's AST scan catches the known-leaky governed runner; T3's
  verifier flags a synthetic mutation; T7's lint flags a planted violation.
- Codex follow-up cleared the intentional red by updating
  `HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.md/json` with an explicit
  `## Stopping Rule` section and a pre-registered first blind full-run size of
  120 packets. The test was not weakened.
- Codex also patched the T1 test file for Python 3.9 annotation compatibility.
- Codex added `holoverify_blind_runner_v0.py`, generated no-provider blind
  prompt fixtures, and created a seeded 20-packet blind canary manifest.
- After Fable's `BLOCK_CANARY` review, Codex hardened the package: seed now
  derives from the frozen bank hash, prompt fixtures cover the full 20-packet
  canary set, runtime/scoring manifests are split, T1 detector validation uses
  a synthetic dirty prompt, T5 uses a one-sided exact binomial skew check, and
  runner budget/selector checks were tightened.
- After Fable's second `BLOCK_CANARY` review, Codex hardened the package again:
  the first-turn bank is frozen to disk, runtime manifest order is hash-sorted
  by opaque ID, runtime metadata no longer carries bank hash or seed material,
  opaque IDs are salted by a private scoring-map-only salt, and T5 now checks
  ordering parity, sibling adjacency, runtime metadata leakage, and bank pinning.
- The registered runner was tested with
  `BLIND_RUNNER_MODULE=holoverify_blind_runner_v0` and
  `BLIND_LANE_PROMPTS_DIR=docs/benchmark/blind_lane_fixture_prompts_2026_07_02/prompts`.
- Notable byproduct: the T5 baseline computed **bank first-turn correctness
  = 577/638 ≈ 90.4%** from frozen artifacts. Workers were right on turn 1,
  pre-repair, for ~90% of packets — a first magnitude bound on oracle
  steering exposure (~10% of packets had a wrong first verdict that the
  answer-aware loop could have corrected). Internal note only; not claim language.

## Per-test detail

### T1 — ID-channel scan
- **Files/functions:** `blind_lane_suite/id_channel.py` (`id_channel_report`, `scan_prompt_dir`, `deterministic_tokens`); `tests/test_blind_lane_t1_id_channel.py`.
- **Pass/fail:** fails on any `-A`/`-B`-suffixed ID token in model-visible messages, or any token appearing in ≥3 pairs that always co-occurs with one truth side. Blind-lane target dir supplied via `BLIND_LANE_PROMPTS_DIR`.
- **Fixtures:** none needed for the detector-validation (uses a frozen governed prompts dir read-only); blind-lane test consumes the runner's prompt output.
- **Does NOT prove:** payload *content* is truth-free (template wording may correlate with truth); nor that a re-keying scheme leaking via ordering below 3-pair support is caught.
- **False-confidence risk:** regexes bind to current ID grammar; a runner emitting lowercase or underscore IDs would evade both detectors. Mitigation in place: detector-validation test must keep passing against the governed leak; extend regexes when ID grammar changes.

### T2 — Poisoned-spec byte-invariance + static guard
- **Files/functions:** `fixtures.py` (`build_poisoned_variants`, `model_visible_payload`, `canonicalize_run_result`, `SENTINEL`); `static_guards.py` (`scan_source_for_truth_reachability`); `tests/test_blind_lane_t2_poisoned_spec.py`.
- **Pass/fail:** any byte difference in canonicalized run output across `as_written` / `truth_swapped` / `terms_sentinel` variants ⇒ fail; any sentinel string in runtime output ⇒ fail; any AST finding in registered runner source ⇒ fail.
- **Fixtures:** synthetic pair spec (`SYNTHETIC_PAIR_SPEC`) — deliberately not a frozen packet, so poisoning never touches real truths; deterministic mock transcripts.
- **Does NOT prove:** absence of truth channels through fields not in the forbidden set, or through modules the runner imports dynamically (AST scan covers the entry module's source only).
- **False-confidence risk (highest in suite):** `canonicalize_run_result` strips volatile keys (`run_id`, timestamps, paths); a runner hiding truth-conditioned content inside a stripped key would pass. Mitigation: keep VOLATILE minimal and review it in acceptance; extend the AST scan to the runner's import closure when the runner exists.

### T3 — Hash chain / no mutation
- **Files/functions:** `hash_chain.py` (`verify_hash_chain`, `sha256_text`); `tests/test_blind_lane_t3_hash_chain.py`.
- **Pass/fail:** any worker row whose recorded hash, stored `artifact_text`, or downstream-stage hash differs from the raw mock output ⇒ fail; normalizer functions reachable from runner source ⇒ fail.
- **Fixtures:** mock transcripts; synthetic mutated-run dict for detector validation.
- **Does NOT prove:** artifacts are correct or high quality — only untouched; prompt-side steering is out of scope (T2's job).
- **False-confidence risk:** the chain only covers stages the runner reports (`gate_input_sha256` etc. are checked *if present*). A runner that simply omits stage hashes weakens coverage while passing. Mitigation: acceptance review must require the stage hashes in the contract before counting T3 green.

### T4 — Selector truth-swap sweep
- **Files/functions:** `fixtures.py` (`selector_sweep_cases`); `tests/test_blind_lane_t4_selector_sweep.py` (invariance, declared-criteria recomputation, criteria-name screen).
- **Pass/fail:** pick changes across truth sweep ⇒ fail; `select_final` ≠ `apply_criteria` on any case ⇒ fail (undeclared criteria); any criterion name containing truth/knew/suffix terms ⇒ fail.
- **Fixtures:** artifact pairs where the truth-matching artifact is structurally weaker — the sweep is only informative because of this asymmetry.
- **Does NOT prove:** the criteria are wise; a truth-blind selector can still prefer verbose/conservative artifacts systematically.
- **False-confidence risk:** two cases is minimal coverage; a selector could special-case the fixture shape. Mitigation: cases are trivially extensible — add randomized artifact grids before relying on T4 for sign-off; criteria-name screen is string-based and can be evaded by renaming (the recomputation test is the real teeth).

### T5 — Canary skew check
- **Files/functions:** `canary_skew.py` (`first_turn_correctness`, `bank_stats`, `skew_check`, `find_canary_manifest`); `tests/test_blind_lane_t5_canary_skew.py`.
- **Pass/fail:** canary manifest packets' first-turn correctness rate > bank rate + 0.10 ⇒ fail; canary packets missing frozen evidence ⇒ fail; smoke test fails if <50 packets have first-turn evidence.
- **Fixtures:** none — runs read-only against frozen result artifacts, deduped by (packet_id, run_id).
- **Does NOT prove:** the bank generalizes (screened-for-solo-failure corpus, confound C4); nor seed reproducibility of the sampler (add when the sampler script exists).
- **False-confidence risk:** first-turn correctness is one difficulty proxy; a sample could be "easy" along other axes (domain mix, doc count). The dedupe keeps the *first* seen (packet, run) pair — if both an invalid and a complete run of the same run_id exist in different dirs, the proxy uses whichever globs first; acceptable for a rate estimate, not for per-packet adjudication.

### T6 — Budget parity replay
- **Files/functions:** `budget_audit.py` (`governed_envelope`, `check_runner_budget`, `check_retry_log`); `fixtures.py` (`FailingTransport`); `tests/test_blind_lane_t6_budget_parity.py`.
- **Pass/fail:** runner `BUDGET_LIMITS` exceeding the governed envelope (measured 5.0 calls/packet from 134 manifests, retry limit 1 per transport policy) ⇒ fail; forced-failure replay showing uncapped, unlogged, or content-triggered retries ⇒ fail.
- **Fixtures:** `FailingTransport` counting attempts.
- **Does NOT prove:** parity with solo baselines (that asymmetry is C5 and needs its own fix); nor that budgets are sufficient.
- **False-confidence risk:** worker-turn ceiling (3) and retry limit (1) are constants sourced from architecture docs, not parsed per-run; if a wave used different values the envelope is off. Mitigation: envelope report prints its sources; verify constants against `HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1` during acceptance.

### T7 — Claim-scope lint
- **Files/functions:** `claim_lint.py` (`lint_public_surfaces`, `lint_text`, `lint_canary_spec`); `tests/test_blind_lane_t7_claim_lint.py`.
- **Pass/fail:** canary-scale ratio (denominator ≤ 40) in the same sentence as a blind-lane keyword on a public surface ⇒ fail; window-proximity hits are warnings for human review; spec lacking a stopping-rule *section/definition* or pre-registered full-run size ⇒ fail.
- **Fixtures:** planted-violation strings (detector validation).
- **Does NOT prove:** anything about the architecture; it can only block premature claims. It also cannot catch prose claims without ratios ("the blind canary confirmed the result").
- **False-confidence risk — one already materialized and was fixed this session:** the stopping-rule check initially passed because the spec now contains a *table describing this very lint* ("canary lacks stopping rule…"). Meta-mentions satisfied the regex. The lint now requires a heading or `stopping rule:` definition line, and correctly fails. General lesson: text lints are satisfiable by text *about* the requirement; keep detector-validation tests adversarial.

## Standing false-confidence controls

1. Every scanner ships with a detector-validation test against a known-dirty target (governed prompts, governed runner, synthetic mutation, planted lint violation). If the known-dirty target ever scans clean, the suite fails loudly instead of going quietly green.
2. Contract tests never soft-pass: unregistered runner ⇒ loud skip with "skip is not a pass"; registered-but-incomplete ⇒ hard fail.
3. The former intentional red (`test_canary_spec_is_preregistered`) was cleared
   by adding real pre-registration text to the spec, not by weakening the test.
4. A 21/22 green board with the runner registered still licenses only: "no detected truth channel, as fixtured." The six residual rejection grounds in the battery document survive a clean sweep.

## Handoff to Codex

- The first no-provider blind runner now exists and passes the suite. Next
  acceptance step: adversarial review of the runner, prompt fixtures, canary
  manifest, and T1-T7 output.
- Extend the T2 AST scan to the runner's import closure once the runner's module graph exists.
- Add the sampler-reproducibility half of T5 when the canary sampler script lands.
- Maintain the explicit stopping rule and 120-packet first blind full-run
  pre-registration in the spec; do not let future public copy turn the
  20-packet canary into an error-rate claim.
