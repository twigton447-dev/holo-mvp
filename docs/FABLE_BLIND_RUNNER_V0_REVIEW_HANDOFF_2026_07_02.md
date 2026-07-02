# Fable Blind Runner V0 Review Handoff

Status: READY_FOR_READ_ONLY_ADVERSARIAL_REREVIEW_AFTER_BLOCK_REPAIR

Date: 2026-07-02

## Mission

Review the repaired no-provider blind HoloVerify runner for remaining truth
channels, reward-hacking paths, selector loopholes, and claim-boundary risks.

Do not run providers. Do not run judges. Do not edit frozen evidence. Do not
interpret this as a live benchmark result.

## Files To Review

- Runner: `holoverify_blind_runner_v0.py`
- Prompt generator: `docs/benchmark/generate_blind_lane_fixture_prompts_2026_07_02.py`
- Canary sampler: `docs/benchmark/build_blind_canary_manifest_2026_07_02.py`
- Prompt fixtures: `docs/benchmark/blind_lane_fixture_prompts_2026_07_02/prompts/`
- Canary manifest: `docs/benchmark/holoverify_blind_canary_manifest_2026_07_02.json`
- Runtime manifest: `docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json`
- Post-hoc scoring map: `docs/benchmark/holoverify_blind_canary_scoring_map_2026_07_02.json`
- Blind-gate spec: `docs/benchmark/HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.md`
- Proof memo: `docs/benchmark/HOLOVERIFY_BLIND_RUNNER_V0_NO_PROVIDER_PROOF_2026_07_02.md`
- Third block repair report: `docs/benchmark/HOLOVERIFY_BLIND_RUNNER_V0_FABLE_THIRD_BLOCK_REPAIR_REPORT_2026_07_02.md`
- Suite implementation notes: `docs/benchmark/FABLE_BLIND_LANE_SUITE_IMPLEMENTATION_NOTES_2026_07_02.md`
- Tests: `tests/test_blind_lane_t1_id_channel.py` through `tests/test_blind_lane_t7_claim_lint.py`
- Suite package: `blind_lane_suite/`

## Current Local Result

```text
31 passed, 0 skipped, 0 failed
```

Command used:

```bash
BLIND_RUNNER_MODULE=holoverify_blind_runner_v0 \
BLIND_LANE_PROMPTS_DIR=docs/benchmark/blind_lane_fixture_prompts_2026_07_02/prompts \
python3 -B -m pytest -q -rs \
  tests/test_blind_lane_t1_id_channel.py \
  tests/test_blind_lane_t2_poisoned_spec.py \
  tests/test_blind_lane_t3_hash_chain.py \
  tests/test_blind_lane_t4_selector_sweep.py \
  tests/test_blind_lane_t5_canary_skew.py \
  tests/test_blind_lane_t6_budget_parity.py \
  tests/test_blind_lane_t7_claim_lint.py
```

## Specific Questions

1. Does `holoverify_blind_runner_v0.py` contain any runtime path that can infer
   packet truth, sibling side, target bucket, expected verdict, or answer-key
   terms?
2. Do the generated prompt fixtures expose legacy packet IDs, sibling suffixes,
   truth-correlated tokens, or hidden evaluator fields?
3. Does the selector actually choose by blind structural criteria only, or can
   the artifact shape leak correctness?
4. Does the canary manifest create any cherry-picking or post-hoc selection
   risk, despite being seeded and balanced?
5. Are T1-T7 too weak anywhere because they inspect only the entry module,
   strip volatile fields, trust optional hash fields, or use too-small fixture
   grids?
6. What must be fixed before any live 20-packet blind canary is allowed?

## Repair Context

Your first and second reviews returned `BLOCK_CANARY`. Codex patched the
no-provider package before any live calls:

- F1: seed now derives from the frozen bank hash; no author-selected seed and
  no redraw loop.
- F2: prompt fixtures now cover the full 20-packet canary set: 100 prompt files.
- F3: T1 detector validation now uses a synthetic dirty prompt instead of
  selecting only directories where the detector already fires.
- F4: T5 now uses a one-sided exact binomial skew check.
- F5: runtime and scoring artifacts are split. Runtime manifest/payloads omit
  legacy IDs and truth fields; the scoring map is post-hoc only.
- F6: canary is now 10 sibling pairs, both sides included.
- F7: `contradiction_free` is now a real blind structural check.
- F8: runner max output budget is 1024 and T6 checks it.
- F9: selector tie-break now prefers earliest turn rather than last artifact.

Please attack these repairs specifically.

Second-pass repairs:

- F1: runtime manifest is now sorted by opaque ID hash order; T5 checks truth
  parity and adjacent sibling leakage.
- F2: runtime manifest no longer carries bank hash or seed material; opaque IDs
  use a private salt stored only in the post-hoc scoring map.
- F3: first-turn bank is frozen to
  `docs/benchmark/holoverify_blind_canary_bank_2026_07_02.json`; T5 checks the
  manifest pin against that file.
- F4: source grep remains, and the package now adds runtime/scoring split tests;
  import-closure AST scan is still the main residual open item to review.

Third-pass repairs:

- B1: private runtime salt now uses `secrets.token_hex(32)` at package build
  time and is stored only in the post-hoc scoring map. T5 verifies the old
  public bank-hash recipe no longer matches the salt.
- B2: live-canary executor surface now exists at
  `holoverify_blind_runner_v0.run_blind_runtime_manifest`. It loads the runtime
  manifest plus opaque runtime payloads, calls injected transport, and writes
  trace/results. T5 now monkeypatches filesystem reads/writes so any read
  outside the runtime manifest + payload files fails.
- B3: T2 now scans the repo-local import closure of the registered runner, not
  only the entry file.

Current regenerated package notes:

- Runtime truth sequence after opaque-ID sort: `EAEEAEEEAAAAEAEAEAEA`
- Adjacent sibling pairs in runtime order: `1`
- Runtime manifest SHA-256:
  `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7`
- Post-hoc scoring map SHA-256:
  `5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b`

## Required Output

Return a read-only adversarial review with:

- `PASS_TO_CANARY` or `BLOCK_CANARY`
- ranked findings, highest severity first
- exact file/function evidence
- whether the finding is a truth leak, selector leak, mutation risk, sampling
  risk, budget/retry risk, or claim-language risk
- concrete repair recommendation
- residual risks even if all findings are fixed

Do not celebrate the result. Try to break it.
