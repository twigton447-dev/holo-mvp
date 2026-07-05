# Fable Blind Runner V0 Adversarial Review

Status: READ_ONLY_ADVERSARIAL_REVIEW_COMPLETE
Date: 2026-07-02
Reviewer: Fable. No providers run, no judges run, no frozen evidence edited, no packets/prompts/traces/public copy mutated. The 22/22 result was independently reproduced this session before review.

---

## VERDICT: `BLOCK_CANARY`

The runner source itself is clean — question 1's answer is genuinely "no detected truth path in `holoverify_blind_runner_v0.py`." The block is earned elsewhere: the evidence that the firewall *works* is far thinner than the green board implies, the canary sampling has a seed-shopping affordance, and one of my own suite checks turns out to be mathematically unfailable at canary size. A 22/22 board where two detectors were never seriously exercised and one cannot fire is not a firewall pass; it is a firewall demo.

---

## Ranked Findings

### F1 — HIGH — Canary seed is not pre-committed and the sampler is structured for re-seeding — **sampling risk**

**Evidence:** `docs/benchmark/build_blind_canary_manifest_2026_07_02.py`: `SEED = "HOLOVERIFY_BLIND_CANARY_V1_2026_07_02"` is an author-chosen string written *after* the bank difficulty data existed (the script itself imports `first_turn_correctness` and had the full difficulty table in hand). `main()` returns exit 1 on `skew_violation` — the documented workflow on a bad draw is to edit `SEED` and rerun, with nothing recording rejected seeds. The manifest then embeds its own passing `skew_check`, so selection and audit are the same artifact.
**Category:** sampling risk (seed-shopping / pre-registration theater).
**Repair:** derive the seed from data outside author control: `SEED = bank_hash` (already computed in the manifest — sha256 of the full first-turn table). That leaves zero seed freedom: one bank, one sample. Move the skew check to a separate audit script, and add a manifest field `rejected_draws: []` with a hard rule that any re-draw is logged with reason. Commit the sampler before regenerating.
**Residual risk after repair:** algorithm-shopping (choosing the sampling *procedure* after seeing data) remains possible in principle; mitigated only by committing the procedure and never re-editing it.

### F2 — HIGH — The T1 "blind lane" evidence is five prompt files from one synthetic packet — **claim-language / false-confidence risk**

**Evidence:** `docs/benchmark/generate_blind_lane_fixture_prompts_2026_07_02.py` runs the runner once on `SYNTHETIC_PAIR_SPEC`, side `"A"` only. The prompts dir contains exactly `PKT-FCBBFA862447_{W1,W2,W3,G1,G2}.json`. The T1 deterministic-token detector requires ≥3 pairs of support; it had one packet, zero pairs — it could not have fired on anything. `HOLOVERIFY_BLIND_RUNNER_V0_NO_PROVIDER_PROOF_2026_07_02.md` reports "Prompt files scanned: 5 / hits: 0" as a Key Check.
**Category:** false confidence (a scanner that cannot fire counted as a pass).
**Repair:** regenerate fixtures over the full 20-packet canary manifest, both message roles, using the opaque-ID re-keying path end-to-end (legacy payloads in, opaque prompts out) — no providers needed, mock transcripts suffice. T1 must scan ≥20 packets spanning ≥10 pairs before its blind-lane pass means anything. Add a floor to the test: fail if `prompt_files_scanned < 50` or pairs represented < 10.
**Residual risk after repair:** T1 still cannot see payload-*content* truth correlation (template wording); that is a standing residual documented in the battery.

### F3 — HIGH — T1's detector-validation was weakened from fail-on-broken to skip-on-broken — **suite-integrity risk**

**Evidence:** `tests/test_blind_lane_t1_id_channel.py::_find_governed_prompt_dir` now returns only directories where `id_channel_report(path)["violation"]` is already true. If the detector silently breaks, no directory qualifies, the function returns `None`, and the validation test **skips** instead of failing. The validation is circular: it can only examine evidence the detector already flags.
**Category:** suite integrity (the firewall's own smoke alarm was disconnected).
**Repair:** pin the known-leaky directory explicitly (e.g. `holoverify_replication_packet_freeze_3families_wave2_2026-07-01/.../run_20260701T042037Z/prompts`); if it exists and scans clean ⇒ **fail**; skip only if the pinned path is absent from the checkout. Keep the `blind_lane` exclusion — that part of the edit was correct.
**Residual risk after repair:** none specific; this restores the original semantics.

### F4 — HIGH — The T5 canary skew check is mathematically unfailable at n=20 — **sampling risk (my defect)**

**Evidence:** `blind_lane_suite/canary_skew.py::skew_check` uses `sample_rate > bank_rate + 0.10`. Bank first-turn rate is 0.9044, so the threshold is 1.0044 — above the maximum possible sample rate of 1.0. The check literally cannot fire on this bank. The current manifest's sample sits at **0.95**, already easier than the bank, reported as `skew_violation: False`. This is my design bug from the original suite, surfaced by the real bank rate.
**Category:** sampling risk / false confidence.
**Repair:** replace the additive tolerance with a one-sided exact binomial test: under H0 p = bank_rate, fail if P(X ≥ observed | n, p) < 0.10 or if `sample_rate == 1.0` while `bank_rate < 1.0`. At n=20, p=0.9044: 20/20 easy has probability ≈ 0.134 — n=20 is intrinsically weak, so also record the skew p-value in the manifest rather than a binary pass.
**Residual risk after repair:** at canary size the test stays low-powered; skew control is real only at the 120-packet full run. Say so in the manifest.

### F5 — MEDIUM — The legacy↔opaque mapping lives in the artifact the runtime will consume, and nothing forbids the runtime from reading it — **truth-leak risk (process-side)**

**Evidence:** `holoverify_blind_canary_manifest_2026_07_02.json` contains `packet_ids` (legacy, suffix-bearing) and `runtime_id_map` side by side; the MD table publishes the full mapping. `_opaque_id` is `sha256(SEED|legacy)[:16]` with a public SEED — any process holding the legacy list recomputes the map trivially. The "runtime_identity_rule" is a string in the manifest, not an enforcement. No test asserts the runtime never opens this file.
**Category:** truth leak (process-side; model-side inversion is impractical, so severity is medium not high).
**Repair:** split into two files — `*_runtime.json` (opaque IDs + payload refs only) and `*_scoring.json` (the mapping), with the scoring file in a directory the runner is tested never to read. Add a fixture test: run the blind runner under a filesystem shim (patched `open`/`Path.read_text`) that fails the test if any path containing `scoring` or `manifest` is touched. Salt the opaque digest with a value stored only in the scoring file.
**Residual risk after repair:** an operator can always hand the runtime the mapping out-of-band; process discipline, not code, is the last layer.

### F6 — MEDIUM — The canary is not sibling-paired and its universe is the survivor lane — **sampling risk**

**Evidence:** `build_blind_canary_manifest_2026_07_02.py` draws `rng.sample(allow_ids, 10)` and `rng.sample(escalate_ids, 10)` independently — 20 packets from up to 20 *different* pairs. The universe is `first_turn_correctness()` ≈ 638 packets, i.e., only packets that reached complete governed runs (C2 survivors).
**Category:** sampling risk.
**Repair:** sample 10 *pairs* and take both siblings — preserves the product's both-sibling proof structure and gives per-pair FP/FN symmetry. Document the survivor-universe limitation in the manifest; widening the universe requires the intent-to-treat ledger, which doesn't exist yet.
**Residual risk after repair:** corpus curation (C4) is untouched — the bank was screened against solo failure regardless of how the canary samples it.

### F7 — MEDIUM — `contradiction_free` is a hard-coded constant; the spec's contradiction check is unimplemented — **selector-leak risk (integrity, not leak)**

**Evidence:** `holoverify_blind_runner_v0.py::_artifact_from_row` sets `"contradiction_free": True` unconditionally. It sits in `SELECTOR_CRITERIA` and `_criteria_tuple` but can never discriminate. The spec's allowed check "contradiction between answer body and chosen verdict" does not exist; `parse_valid = bool(parsed)` passes any text containing one `=` character.
**Category:** selector integrity / false confidence (a declared criterion that is decorative).
**Repair:** either implement a real blind contradiction check (verdict token vs `open_blockers` emptiness vs `binding_class` consistency — all artifact-internal, no truth needed) or remove the criterion from the declared list. Tighten `parse_valid` to require all `REQUIRED_WORKER_KEYS` present. Add a T4 fixture where the only difference is an internal contradiction, so the criterion is exercised.
**Residual risk after repair:** answering question 3 fully — verdict-*correlated* structure (ESCALATE artifacts naturally list blockers; ALLOW artifacts naturally cite closure) is inherent and blind. It biases the selector's tie behavior toward a verdict class, not toward truth. Watch it in the full run as a verdict-class base-rate, not a leak.

### F8 — LOW/MEDIUM — Token ceiling unchecked; runner exceeds the governed Gov cap — **budget/retry risk**

**Evidence:** `blind_lane_suite/budget_audit.py::check_runner_budget` checks three keys but not `max_output_tokens`. Runner declares 1200; the governed lane's Gov cap is 1024 (`WAVE2_GOV_MAX_TOKENS`, `run_wave2_holo_target_batch_2026_07_01.py`).
**Category:** budget parity.
**Repair:** add `max_output_tokens` to the envelope (extract worker/Gov caps separately — they differ in the governed lane) and to `check_runner_budget`.
**Residual risk after repair:** solo-arm budget parity remains a separate, unaddressed comparison (C5).

### F9 — LOW — Selector tie-break is last-artifact-wins — **selector bias, blind**

**Evidence:** `_criteria_tuple` ends with `str(artifact_id)`; `max()` therefore prefers `ART-003` on full ties — the final worker, the most-batoned turn. Blind and declared, but it silently encodes "last-turn recency" — the exact selection style the Phase-1 handoff told us to distrust in HoloBuild.
**Category:** selector integrity.
**Repair:** tie-break on first-admissible (min artifact_id) to match the governed lane's "pinned best artifact after first admissible" semantics, or justify recency explicitly in the spec.
**Residual risk:** none material once declared.

### F10 — LOW — T2's AST scan is entry-module-only and passing coincidentally — **suite weakness**

**Evidence:** `tests/test_blind_lane_t2_poisoned_spec.py` scans `runner_source_path(runner)` only. It suffices today solely because `holoverify_blind_runner_v0.py` imports nothing but stdlib. The first refactor into helper modules silently shrinks coverage to near zero.
**Category:** suite weakness.
**Repair:** walk the import closure (any module whose `__file__` lives under the repo) and scan every file; assert in the test that the closure size ≥ 1 and list scanned files in the failure message.
**Residual risk after repair:** dynamic imports and `getattr` string construction can still evade AST scanning; the T2 byte-invariance test is the backstop that doesn't care how the leak is coded.

---

## Answers to the six questions, compressed

1. **Runner truth paths:** none found in `holoverify_blind_runner_v0.py`. It reads only `packet_id` and `documents` from the payload; extra payload fields do not reach prompts; gate, baton, and selector are truth-free. The clean AST result is real but currently coincidental in scope (F10).
2. **Prompt fixtures:** no legacy IDs, suffixes, or evaluator fields — but the corpus is 5 files from 1 synthetic packet, so this is weak evidence, not clearance (F2).
3. **Selector:** blind in mechanism; partially decorative in declaration (F7), recency-biased on ties (F9). Verdict-correlated artifact shape is inherent and should be tracked as base-rate, not treated as a leak.
4. **Canary manifest:** yes — seed-shopping affordance (F1), unfailable skew check (F4), unpaired sample from a survivor universe (F6), and mapping co-located with the runtime artifact (F5).
5. **T1–T7 weaknesses:** confirmed in four places — T1 validation circularity (F3), T1 fixture floor absent (F2), T5 tolerance defect (F4), T2 entry-module scope (F10). The volatile-key stripping in T2's canonicalizer is currently safe (runner emits no stripped keys) but stays on the acceptance checklist.
6. **Before any live canary:** fix F1–F5 (mandatory), F6–F8 (strongly recommended, cheap), then regenerate the manifest and fixtures and re-run the suite. All repairs are no-provider.

## Residual risks even after all repairs

Payload-content truth signal in template-generated siblings; corpus curation against solo failure (C4); fixture-vs-live transport fidelity; n=20 statistical weightlessness (firewall test only, never a rate); and operator-side discipline on the mapping file. A post-repair 22/22 licenses exactly the proof memo's own sentence — "no detected answer-key channel under the current tests" — and nothing more.
