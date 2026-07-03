# Fable Blind Canary Rollup Audit

Status: READ_ONLY_ROLLUP_AUDIT_COMPLETE
Date: 2026-07-03
Reviewer: Fable. No providers run, no judges run, no files mutated. Every number below was recomputed from disk; nothing was accepted from the rollup's own assertions.

---

## VERDICT: `PASS_WITH_LIMITATIONS`

The file-backed evidence supports the narrow runtime-firewall claim. The limitations are real, disclosed below, and belong in the claim language — none of them is a confirmed defect or a detected truth channel.

## Recomputed counts (all from disk)

| Check | Rollup claims | Recomputed | Match |
| --- | --- | --- | --- |
| Unique opaque packets in canonical set | 20 | 20, exactly equal to the runtime-manifest ID set | ✔ |
| Canonical provider calls | 100 | 100 (TRACE_CALLS: 60 worker + 40 gov; TRACE_PROVIDER_CALLS: W1/G1/W2/G2/W3 = 20 each) | ✔ |
| Solo calls | 0 | 0 (no solo rows or artifacts in any canonical run dir) | ✔ |
| Judge calls | 0 | 0 (no judge rows; wrapper has no judge path) | ✔ |
| Model substitutions | 0 | 0 (all 100 calls match the declared slot roster exactly) | ✔ |
| Transport retries in canonical traces | 0 | 0 (`transport_attempt_count` = 1 on all 100 rows) | ✔ |
| Post-hoc verdicts vs scoring map | 20/20 | 20/20 recomputed by independent join; 10 ALLOW / 10 ESCALATE both sides | ✔ |
| Token totals | 49,065 / 43,169 / 102,495 | identical, per-provider identical; xai total ≠ in+out as disclosed (provider-reported) | ✔ |
| Invalid lineage preserved, excluded from canonical | 4 runs | 4 runs, zero overlap with canonical set, **119 provider calls** (100 + 5 + 4 + 10) | ✔ |
| Answer-key terms in canonical traces, prompts, raw outputs | none | zero hits for legacy IDs, `HV-`/`BAL100`, truth fields, `knew_terms`, `allow_rule`, `esc_rule`, overblock/underblock across all 14 canonical run dirs | ✔ |
| W3 patch effect | fixed | all 20 canonical W3 calls: `finish_reason=stop`, min output 620 tokens; patch adds structural output contract only — no truth metadata, no content retry, no parser loosening; `finish_reason=length` and empty text still fail closed | ✔ |

## Findings, by severity

### L1 — MEDIUM — The canonical set is heterogeneous across code versions (18 + 2)

The 20 canonical packets span **14 runs and 10 commits** (`cb5403b30` → `634ff17f1`), and the W3 contract patch landed mid-canary: packets 1–18 ran under the pre-patch prompt contract, packets 19–20 under the patched one (verified: W3 `prompt_sha256` differs between `run_20260703T003759Z` and `run_20260703T005104Z`). Both contract versions scanned truth-free, so this is not a leak — but the rollup presents a uniform "canonical passing set" that is actually two contract populations, and the patch itself was committed after my PASS_TO_CANARY gate without re-review. **Correction:** disclose the two-contract composition in the rollup; for a homogeneous firewall artifact, re-run all 20 under the final contract (100 calls, needs approval) before this canary is cited as the exemplar run.

### L2 — MEDIUM — "Freeze-then-score" is code-enforced but not artifact-provable

`scoring_map_loaded_after_trace_freeze: true` is a hard-coded literal in `posthoc_score()` (`run_holoverify_blind_canary_live_2026_07_02.py:732`), and the score artifact records **no hash of the frozen trace it scored**. Code order does put `write_provider_trace` before `posthoc_score`, and I found no counter-evidence — but an outside auditor cannot verify the ordering from artifacts alone. Additionally, `preflight()` computes `sha256_file(SCORING_MAP)` — the live process **reads the scoring map's bytes before any provider call** (integrity pinning; bytes are hashed, never parsed; no truth reaches prompts — confirmed by the leak scans). **Correction:** the strong phrasing "kept the scoring map out of the live runtime path" (audit handoff) is not strictly true; use "scoring map content parsed only after trace freeze; its bytes are hash-pinned at preflight." **Fix for next run:** record `trace_sha256` inside the post-hoc score artifact and hash-pin the scoring map from a separate pre-run step, not the live process.

### L3 — LOW-MEDIUM — The headline sentence omits the invalid lineage volume

"100 canonical provider calls" is true, but total live spend was **219 provider calls**: a full 20-packet attempt (100 calls) invalidated by broad contract failure, plus three partial re-attempts (19 calls), before per-packet reruns produced the canonical set. All invalid finals were `UNKNOWN`/empty — these were content-contract failures, **not wrong verdicts retried into right ones** (I verified zero canonical/invalid run overlap and that invalid runs contributed no score rows). The rollup preserves the lineage honestly in its own section; the allowed statement should carry it too. **Correction:** append "…after four preserved invalid attempts totaling 119 provider calls under earlier contract versions; no invalid attempt produced a scored verdict."

### L4 — LOW — Per-packet re-attempts are a survivorship shape, bounded here

Packets 2, 3, 19, 20 needed multiple live attempts before a canonical pass. Because every failure mode was structural (empty/truncated output) and no invalid attempt ever emitted a verdict, this cannot have filtered wrong verdicts out of the 20/20. But the pattern — rerun-until-contract-pass — is the same shape as the governed lane's C2, and at the 120-packet run it must be pre-declared: fixed attempt budget per packet, all attempts logged, and packets exhausting the budget reported as failures in the headline count.

### L5 — LOW — The live wrapper sits outside the tested firewall perimeter

The shim and import-closure tests bind `holoverify_blind_runner_v0`; the live wrapper (`run_holoverify_blind_canary_live_2026_07_02.py`) legitimately holds the scoring-map path (for post-hoc scoring) in the same process. Its runtime section behaved correctly here (leak scans clean), but it is scanned by nothing. **Fix:** add the wrapper's pre-freeze section to the AST/shim discipline, or split scoring into a separate post-freeze script.

## Claim-language corrections

1. Keep the rollup's allowed statement, plus the L3 lineage clause and the L1 two-contract disclosure.
2. Replace "kept the scoring map out of the live runtime path" with the L2 phrasing wherever it appears.
3. "Canonical trace retries: 0" should read "0 transport retries within canonical traces; 4 packets required new runs after content-contract failures (see invalid lineage)."
4. The Interpretation section's "the live path can complete all 20 opaque packets" should note it did so across two contract versions.

## Answers to the ten checks

1–5: verified, all reproduce exactly (table above). 6: code-enforced, artifact-unprovable, bytes-read-at-preflight nuance (L2). 7: clean — zero forbidden-term hits across all canonical prompts, traces, and raw outputs. 8: invalid attempts preserved, zero overlap with canonical rows, zero score rows, correctly excluded (L3/L4 for language). 9: fully reproducible; token totals match to the digit, xai discrepancy disclosed at source. 10: the patch genuinely fixes the failure class (structural output contract, shorter field bounds, fail-closed preserved; all 20 canonical W3 calls finish `stop` with ≥620 output tokens) — it does not hide it, and the failed attempts remain on disk.

## Recommended next move

Code hardening pass first, then the larger bank: (a) implement L2's trace-hash binding and scoring split, (b) L5's wrapper scan, (c) pre-declare the L4 attempt budget, (d) optionally re-run the 20 under the final contract for a homogeneous exemplar. Then proceed to the pre-registered 120-packet blind run under the same firewall — that run, not this canary, is the first artifact that could carry any quantitative weight. Solo/ablation redesign stays queued behind it (C4/C5 are still open and untouched by everything above).

**Licensed sentence, unchanged from the handoff:** no detected answer-key channel in the repaired 20-packet blind runtime firewall path, with post-hoc scoring after trace freeze showing 20/20 final verdicts matched the hidden map — under two contract versions, after four preserved invalid attempts.
