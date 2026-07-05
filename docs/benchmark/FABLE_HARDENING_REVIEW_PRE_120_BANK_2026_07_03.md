# Fable Hardening Review — Pre-120-Packet Blind Bank

Status: READ_ONLY_HARDENING_REVIEW_COMPLETE
Date: 2026-07-03
Reviewer: Fable. No providers, no judges, no repo files edited or mutated. All tests independently re-run.

---

## VERDICT: `PASS_TO_BUILD_FREEZE_120_PACKET_BLIND_BANK`

The proof-quality limitations from my rollup audit (L2, L4, L5) are substantively closed in code and enforced by tests, not just described in reports. The 120-packet bank may be built and frozen next. This review approves the **no-provider build/freeze step only** — not provider execution, not public claims, per the sequence lock's own gate law.

## Recomputed test status

First run in my sandbox: **3 failed, 51 passed** — all three failures were one environment artifact: `preflight()` shells out to `git rev-parse HEAD`, and my mounted copy is a detached git worktree pointing at `/Users/taylorwigton/Desktop/holo-mvp/.git/...`, which doesn't exist here. With `git` stubbed on PATH (in /tmp, nothing in the repo touched): **54 passed, 0 skipped, 0 failed** — full wrapper suite plus T1–T7 with the runner registered. The handoff's claimed green board is reproduced.

## Verification of the nine points

| # | Check | Verified | Evidence |
| --- | --- | --- | --- |
| 1 | Live wrapper no longer loads/reads scoring map | ✔ | No `SCORING_MAP` path in wrapper (only the expected-hash constant for audit reference); `test_preflight_does_not_read_scoring_map_bytes` enforces it with a monkeypatched read shim — enforcement by test, not self-assertion |
| 2 | Post-hoc scorer separate from live execution | ✔ | `score_holoverify_blind_canary_posthoc_2026_07_03.py` is a standalone script; wrapper only reports the scoring command |
| 3 | Score artifact binds to frozen trace hashes | ✔ | Scorer writes `trace_calls_sha256`, `trace_provider_calls_sha256`, `runtime_results_sha256`, `live_summary_sha256`, `scoring_map_sha256`, and hard-fails on scoring-map hash mismatch; `test_posthoc_scorer_binds_score_to_frozen_trace_hashes` covers it — closes rollup-audit L2 |
| 4 | Live summary makes scoring a separate post-freeze step | ✔ | `posthoc_scoring_required_after_trace_freeze: true` + scoring command in summary; no score fields in live output |
| 5 | Attempt budget declared | ✔ | `BLIND_RUNTIME_ATTEMPT_BUDGET_V1_2026_07_03`: 1 content-contract attempt, 1 live-run attempt per packet, transport retries bounded separately — closes L4 |
| 6 | Content/schema failures not retried | ✔ | Retry loop retries only classified transport failures; `test_content_failure_is_not_retried_by_blind_runner`, `test_worker_contract_failure_is_fail_closed`, `test_gov_length_finish_is_fail_closed`, `test_unclosed_thinking_block_strips_to_empty_and_fails_closed` all present and green |
| 7 | Manual rerun requires new approval + preserved invalid trace | ✔ | Scoped approval sentences bind packet index/scope (`test_one_packet_approval_sentence_binds_packet_index`, `test_partial_batch_approval_sentence_binds_scope`); policy field asserts preserved-invalid-trace requirement |
| 8 | Wrapper under test/static discipline | ✔ | 23 wrapper tests incl. `test_live_wrapper_import_closure_scan_has_only_detector_literals` and truth-free prompt contract checks — closes L5 |
| 9 | Sequence lock prevents premature public claims | ✔ | Gate law: no step before the prior is file-backed; no providers without Fable clearance + frozen bank + firewall tests + Taylor's exact scope; no public claims until Holo 120 + solo one-shots + comparison memo + ablation (or explicit deferral) + rewritten claim language |

## Findings (all minor; none blocks the bank build)

**M1 — LOW — Hard-coded assurance literals remain in artifacts.** `scoring_map_not_read_by_live_preflight: True` and `scoring_map_read_by_live_process: False` are literals in the wrapper (lines ~653, ~667), same self-assertion pattern I flagged in L2. They are now *backed* by the read-shim test, so this is cosmetic — but artifacts should not present enforced-by-test properties as if measured at runtime. Fix: rename to `..._enforced_by: "tests/test_holoverify_blind_canary_live_wrapper.py::test_preflight_does_not_read_scoring_map_bytes"` or compute them.

**M2 — LOW — The rollup builder should verify score-artifact hash bindings.** The scorer now records trace hashes; nothing yet re-verifies them at rollup time. One loop in the next rollup builder: recompute `sha256(TRACE_CALLS.jsonl)` per run and compare to the score artifact before including a row. Cheap, and it makes the binding audit-closed end to end.

**M3 — LOW — Preflight depends on `git` in PATH and a healthy worktree.** Fails closed (good), but the 120-run operator should know a broken git state blocks preflight with an opaque subprocess error. Wrap it with a clear message.

**M4 — DOC — Sequence lock ablation step.** Step 8 allows "randomized ablation subset … or explicitly deferred" in the public-claim gate. Deferral is the right escape hatch, but the lock should require the deferral itself to be file-backed with a reason, or it becomes a quiet skip. One sentence.

## Language corrections

Only M1's artifact field naming and M4's deferral clause. The patch report's own claim boundary is accurate and appropriately narrow.

## May the 120-packet blind bank be built/frozen next?

Yes. Build/freeze is no-provider and the firewall it will be tested against is now the strongest it has been: separate scorer with hash binding, wrapper under shim + closure discipline, declared attempt budget, fail-closed content contracts, and a sequence lock that keeps claims frozen until the full evidence chain exists. Bank requirements in the lock (60/60 truths, multi-domain, opaque randomized order, runtime/scoring split, frozen hashes) match everything this review chain has established — build to that spec, then bring me the frozen bank and the firewall test results before any provider approval request goes to Taylor.

Standing residuals, unchanged and untouched by this patch: corpus curation (C4), payload-wording truth signal, survivor-lane universe of the difficulty proxy, and — for the eventual comparison memo — the solo-arm design debts (C5, C7) that the sequence lock correctly schedules after Holo 120.
