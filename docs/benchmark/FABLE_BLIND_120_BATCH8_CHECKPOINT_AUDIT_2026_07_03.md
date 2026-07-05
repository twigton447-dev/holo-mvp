# Fable Blind 120 — Batch-8 Checkpoint Audit

Status: READ_ONLY_CHECKPOINT_AUDIT_COMPLETE
Date: 2026-07-03
Reviewer: Fable. No providers, no judges, no solo, no reruns, no edits. Every number recomputed from frozen artifacts on disk; nothing accepted from summary prose.

---

## VERDICT: `PASS_WITH_LIMITATIONS_CONTINUE`

The first 80 packets are a clean blind runtime-firewall checkpoint — verified independently, not from the rollup. The limitations are process-discipline issues, not truth channels. And one blunt fact up front:

**The checkpoint was overrun before it was audited.** The request scopes "through Batch 8, indices 1–80, 400 calls." Disk shows **11 canonical batches, indices 1–110, 550 calls** — batches 9, 10, and 11 ran before this audit cleared batch 8. Their evidence verifies just as cleanly (see below), so nothing is lost — but a checkpoint that execution drives past before the auditor arrives is not a checkpoint, it's a diary entry. If the audit had found a truth channel at batch 6, you'd now have three more contaminated batches and 150 wasted calls.

## Top findings, by severity

**F1 — MEDIUM (process) — Execution ran ahead of the audit gate.** As above. No evidence harm found; batches 9–11 verify identically. Fix: batch 12 does not run until this audit is filed and acknowledged, and future checkpoints halt the runner, mechanically, not by intention.

**F2 — MEDIUM (provenance) — One commit per batch, and run summaries record only `current_head`, not the wrapper/runner file hashes.** The 11 canonical runs span 11 distinct commits (evidence-preservation commits between batches, most likely). From this mount (detached worktree, no git objects) I **cannot prove the wrapper and runner code were byte-identical across all 11 batches**. Strong indirect evidence says they were: max-token settings are uniform across all 550 calls (W1/G1/W2/G2 = 1024, W3 = 2048), the roster is exact on every call, and the G1/W1/W3 static prompt headers are identical across batches — the one G1 variance I chased is dynamic baton state after a W1 structural gate failure (`repair_target=repair blind structural gate failures`), generic and direction-free, not a contract change. Fix: add `wrapper_sha256` and `runner_sha256` to every run summary (one line), and have Codex confirm via `git log --stat` that the 11 commits touched only evidence paths. Until then, cross-batch code invariance is attested, not proven.

**F3 — LOW (budget, disclosed) — Two declared deviations from the original envelope.** W3 runs at `max_output_tokens=2048` (vs the 1024 envelope; declared, test-covered, motivated by the W3 length failures) and the attempt policy now says `transport_retries_per_call: 2` (vs 1). Observed behavior: **every one of the 550 calls has `transport_attempt_count=1`** — no retry was ever used, so no hidden rescue occurred. Both deviations must appear in the comparison memo's parity accounting: the solo baseline gets equivalent output budget or the asymmetry is disclosed.

**F4 — LOW (labeling) — Run summaries in the 120 lane still carry canary artifact names and `HOLOVERIFY_BLIND_CANARY_LIVE_RUN_SUMMARY_V0` classifications** (`blind_canary_live_summary.json` etc. alongside `blind_120_live_summary.json`). Cosmetic inheritance from the wrapper delegation; an outside auditor will trip on it. Label the lane consistently in the final rollup.

## Verified clean (all recomputed from disk)

- **Batches and coverage:** 11 canonical runs, each exactly 10 packets × 5 calls = 50 provider calls; slot counts perfect (W1/G1/W2/G2/W3 = 110 each over 11 batches; 80 each over the audited 8). Manifest indices per batch are exact contiguous decades; **first 8 batches cover indices 1–80 exactly**; no duplicates anywhere; no batch overlap.
- **Calls:** 400 across batches 1–8 (550 through batch 11). No judge calls, no solo calls, zero model substitutions against the declared roster on all calls.
- **Scores:** independent join of `blind_120_posthoc_score_trace_bound_v1.json` rows against the scoring map: **80/80 for batches 1–8 (and 110/110 through batch 11)**; per-row `posthoc_truth` matches the scoring map on every row; truth balance in the first 110 = 54 ALLOW / 56 ESCALATE, consistent with the 60/60 bank.
- **Trace-hash binding:** all 44 recorded bindings (4 per canonical run × 11) recomputed and matched — `trace_calls`, `trace_provider_calls`, `runtime_results`, `live_summary`. The M2/L2 fix is real and holding.
- **Leakage:** zero hits across all canonical run dirs (prompts, traces, raw outputs) for legacy IDs, `HV-`/`BAL100`, `packet_truth`, `knew_terms`, `allow_rule`, `esc_rule`, `expected_verdict`, and overblock/underblock-style directional hints.
- **Scoring-map isolation:** wrapper verified at the pre-run gate; score artifacts assert `scoring_map_loaded_after_trace_hash_binding` and are bound to the frozen traces they scored — the binding, not the flag, is what I verified.
- **Invalid lineage preserved and excluded:** the full-120 attempt `run_20260703T020428Z` (died at call 117, `G1_empty_text` at Gov max 512 — the failure that motivated the Gov hardening to 1024) and `run_20260703T024113Z` (G2 contract failure, 14 calls) are on disk, marked failed, and contribute zero score rows. Two empty run dirs (014044Z/014102Z) predate artifacts; harmless but worth a one-line note in the rollup. Attempt budget (1 content attempt, 1 live attempt per packet) was respected: no packet appears in more than one canonical batch.
- **Bank integrity unchanged:** freeze root and manifest hashes match the pins from my wrapper gate; the bank's blindness properties (hash-sorted order, no adjacency, truth-free runtime manifest, salted opaque IDs) were verified there and the bank is immutable by hash.

## What remains unproven

1. Cross-batch code invariance (F2) — attested by uniform behavior, not by commit diff.
2. Payload-*wording* truth signal — the standing residual no regex can close; only the solo arm and ablation give it empirical teeth.
3. Representativeness — the 120 packets descend from the curated corpus (C4). 110/110 on this bank says the blind firewall works and the architecture handles *this distribution*; it says nothing about unscreened traffic.
4. Anything quantitative. 80/80 (or 110/110) remains a runtime-firewall result. FP/FN rates, intervals, and any Holo-vs-solo statement stay forbidden until the sequence lock's chain completes: solo one-shots on the same 120, comparison memo, ablation subset.

## Exact next recommended action

1. File this audit; **hold batch 12** until F2's two fixes land (wrapper/runner sha256 in summaries; Codex confirms the 11 batch commits touched evidence paths only — a five-minute `git log --stat` on the primary checkout).
2. Run batch 12 (indices 111–120) under the same approval discipline.
3. Then the full-120 rollup with the intent-to-treat lineage (2 invalid attempts, 131 invalid calls, 2 empty dirs) in the headline, and go straight to the solo one-shot arm per the sequence lock — that comparison, not this lane, is where any claim about the architecture gets earned.
