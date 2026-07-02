# Fable Blind Runner V0 — Second Adversarial Review

Status: READ_ONLY_SECOND_REVIEW_COMPLETE
Date: 2026-07-02
Reviewer: Fable. No providers, no judges, no files edited, nothing mutated. The 25/25 result was independently reproduced, and every repair claim was verified against the code and artifacts — not the repair report.

---

## VERDICT: `BLOCK_CANARY`

Narrower block than round one. Nine of ten claimed repairs are real and verified. But the regenerated canary package contains a **deterministic truth channel Codex introduced while fixing F6**: the runtime manifest lists packets in perfect `ABABABABABABABABABAB` order — position parity encodes truth with zero error, and all 10 sibling pairs sit adjacent. I verified this empirically by joining the runtime manifest against the scoring map: odd positions are all `-A` (ALLOW), even positions all `-B` (ESCALATE), 10/10 pairs adjacent. The blind lane's own spec forbids any runtime component from knowing truth; the runtime manifest is a runtime input and it currently *is* an answer key sorted for convenience.

This is what pairing + `sorted(selected)` + ordinal-assigned opaque IDs does, and no test in T1–T7 looks at ordering — which is also a finding.

---

## Verification of the ten claimed repairs

| Claim | Verified? | Note |
| --- | --- | --- |
| 1. Seed from bank hash | Yes — `rng = random.Random(bank_hash)`, `SEED_LABEL = "derived_from_bank_hash_no_author_seed"` | but bank not externally pinned (F3 below) |
| 2. No redraw loop | Yes — `redraw_log`/`redraw_policy` fields present, no retry affordance in `main()` | |
| 3. 10 sibling pairs / 20 packets | Yes — `_paired_bank` requires both sides; verified 10/10 pairs | pairing is what created the ordering leak |
| 4. Runtime/scoring split | Structurally yes | but split is cosmetic against a process reader (F2) and unenforced at runtime (F4) |
| 5. Runtime files opaque-only | Yes — independent grep of payloads + manifest: zero legacy IDs, zero `-A`/`-B` tokens, no truth fields; payload keys limited to packet_id/action_boundary/domain/case_ref/documents | ordering still leaks (F1) |
| 6. 100 prompt fixtures | Yes — 100 files, 20 packets × 5 roles; my independent scan: violation False, 0 deterministic tokens across 10 pairs | now meaningful for the suffix channel |
| 7. T1 synthetic dirty-prompt validation | Yes — `test_detector_catches_synthetic_suffix_leak` fails-on-broken; governed-dir check retained as secondary | correct repair |
| 8. Binomial skew check | Yes — exact upper-tail, sample 18/20 = 0.90 vs bank 0.9044, p = 0.702, not skewed | honest result: sample is *representative*, not easy |
| 9. Earliest-turn tie-break | Yes — `-int(turn_index)` in `_criteria_tuple`, `earliest_turn` declared | |
| 10. Real contradiction check | Yes — `allow_with_open_blockers` / `escalate_without_open_blockers` emitted by the gate, artifact-internal, blind | creates verdict-class asymmetry to monitor (F7) |
| 11. 1024 token cap + T6 check | Yes — `BUDGET_LIMITS` 1024, `check_runner_budget` covers `max_output_tokens` | |

F10 from round one (import-closure AST scan) remains open and is honestly declared.

---

## Ranked Findings

### F1 — HIGH — Runtime manifest ordering is a perfect truth channel — **truth leak**

**Evidence:** `build_blind_canary_manifest_2026_07_02.py::build_package`: `selected = sorted(side for pair ... for side in (f"{pair}-A", f"{pair}-B"))` → ordinals 1..20 assigned in sorted-legacy order → `runtime_manifest["packets"]` written in ordinal order. Empirical join against the scoring map: side sequence `ABABABABABABABABABAB`; odd positions = {A}, even = {B}; same-pair adjacency 10/10. Any process consuming the manifest in order — the live runner's execution loop, trace row ordering, output file creation order — inherits a zero-error side label per packet, plus full pair linkage.
**Repair:** derive opaque IDs from `sha256(salt | legacy_id)` (salt: see F2), then emit `packets` sorted by opaque ID — hash order destroys both parity and adjacency. Regenerate the package. Add an audit-side test (uses the scoring map, so it lives outside runtime) asserting the side sequence of the runtime manifest is not derivable from position: fail if either parity class is pure or adjacency count is 10/10.
**Residual after repair:** execution-order discipline in the live runner still matters (F6).

### F2 — MEDIUM-HIGH — Opaque IDs are recomputable from runtime-visible data — **truth leak (process-side)**

**Evidence:** the runtime manifest itself carries `bank_hash` and `seed_material`; `_opaque_id(bank_hash, ordinal)` is public source; the selected legacy list is reproducible from the repo (audit manifest, or bank + seed). Runtime manifest + public code therefore reconstructs the full opaque↔legacy mapping without ever opening the scoring map. The split is real hygiene but not a barrier.
**Repair:** (a) generate a random salt at build time, store it **only** in the scoring map, derive `opaque = sha256(salt|legacy_id)`; (b) strip `bank_hash` and `seed_material` from the runtime manifest — they belong in the audit manifest only. After this, runtime-visible data + public code cannot reconstruct the mapping.
**Residual after repair:** an operator holding both files can always join them; that is what the isolation test (F4) and process discipline are for.

### F3 — MEDIUM — The bank behind the seed is not externally pinned — **sampling risk**

**Evidence:** seed = `_bank_hash(first_turn_correctness())`, and `first_turn_correctness()` recomputes over whatever result artifacts exist under `docs/benchmark` at build time. Adding or removing any result file — including a harmless-looking diagnostic run — changes the bank, the hash, the seed, and the sample. Seed freedom was removed; *bank* freedom was not. Nothing pins `bank_hash` (`c7906bb5…`) outside the artifacts the sampler generated.
**Repair:** write the bank to a committed frozen file (`blind_canary_bank_freeze_2026_07_02.json`: packet_id → bool + hash), pin its hash in the blind-gate spec, make the sampler read **only** that file, and extend T5 to assert `manifest.bank_hash == spec-pinned hash`.
**Residual after repair:** the choice of difficulty proxy (first-turn correctness) was itself made post-hoc; disclosed, acceptable, unfixable.

### F4 — MEDIUM — Runtime isolation from the scoring map is asserted by string-grep, not enforced — **truth leak guard gap**

**Evidence:** `test_blind_runner_source_does_not_reference_scoring_map` checks four literal substrings in the runner source; renaming a variable or using `Path` composition evades it. There is still no filesystem-shim fixture proving the runner never opens the scoring map, audit manifest, or anything outside its payload refs and out_dir. F10 (import-closure AST) is also still open.
**Repair:** fixture that monkeypatches `builtins.open` and `Path.read_text`/`read_bytes` during `run_blind_fixture` and fails on any path outside the allowed set; extend the T2 AST scan to the import closure (trivial while the runner is stdlib-only — do it now, before it isn't).
**Residual after repair:** dynamic evasion remains theoretically possible; T2 byte-invariance is the backstop.

### F5 — LOW-MEDIUM — The suite has no ordering or payload-content checks — **suite weakness**

**Evidence:** nothing in T1–T7 would have caught F1; T5's new runtime-manifest test checks manifest *text* for forbidden terms but never opens the payload files (I verified those manually this round: zero legacy tokens across 20 payloads and 100 prompts; doc counts identical 5/5 per side; payload byte sizes overlap, A mean ≈1878 / B mean ≈1877 — no gross shape channel).
**Repair:** add (a) the ordering-entropy test from F1; (b) a payload-file scan test (legacy IDs, suffix tokens, forbidden fields, per-side doc-count/size symmetry report). Both are audit-side, no-provider.
**Residual after repair:** semantic truth signal in payload *wording* remains untestable by regex; it is the standing residual from the battery, partially mitigated by the observed size/doc symmetry.

### F6 — LOW — Live execution-order discipline is unspecified — **truth leak (future)**

**Evidence:** even with a shuffled manifest, nothing in the spec requires the live canary to execute in manifest order or forbids trace metadata recording pair/position joins.
**Repair:** one spec paragraph: live runner processes packets in runtime-manifest order only, no pair identifiers or position counters in any model-visible or trace-visible field until scoring.

### F7 — LOW — Verdict-class structural asymmetry in the gate — **selector bias, blind**

**Evidence:** `allow_with_open_blockers`/`escalate_without_open_blockers` penalize different artifact shapes per verdict class. Blind and defensible, but gate-pass rates will differ by verdict class, which shifts selector behavior between ALLOW-truth and ESCALATE-truth packets.
**Repair:** none needed now; require the canary report to break out gate-pass and selection rates by verdict class so this bias is measured rather than assumed away.

---

## Answers to the specific questions

- **Can the runtime still see or infer truth?** From the runner code: no. From the runtime artifacts: **yes — F1 ordering parity is total, and F2 makes the mapping recomputable.** Both must die before live.
- **Can it access the scoring map before trace freeze?** Nothing enforces that it can't (F4). The current guard is a substring check on one file.
- **Are runtime payloads free of legacy IDs, suffixes, truth labels, buckets, answer-key fields?** Yes — verified independently, including field-key inventory and shape symmetry. The leak is in the manifest's *structure*, not the payloads' content.
- **Is the bank-hash seed non-gameable?** Better, not done: seed freedom is gone, bank freedom remains (F3).
- **Is the canary cherry-picked or skewed?** No evidence of it: paired 10/10, sample first-turn 0.90 vs bank 0.904, p = 0.70. Universe is still the survivor lane — disclosed residual, not a block.
- **Are 100 prompts enough for T1?** For the suffix channel, yes. The deterministic-token detector now has 10 pairs of support and ran clean under my independent scan. Payload-wording correlation remains out of scope.
- **Is the selector still gameable?** Substantially hardened (earliest-turn ties, real contradiction check, recomputation test). Remaining bias is blind verbosity/citation preference plus F7 — monitor, don't block.
- **Are T1–T7 still too weak anywhere?** Yes: no ordering test, no payload-file test (F5), string-grep isolation (F4), entry-module AST scope (F10, acknowledged).
- **What must be fixed before any live canary?** F1, F2, F3, F4 — then regenerate the package and hand me the regenerated artifacts for a short third pass (artifacts only; the code repairs are converging).

## Residual risks that survive all repairs

Payload-wording truth signal in template siblings; corpus curated against solo failure (C4); survivor-lane universe; fixture-vs-live transport fidelity; n=20 carries no statistical weight — the canary tests the firewall, never a rate. A post-repair green board licenses one sentence only: no detected truth channel, as fixtured.
