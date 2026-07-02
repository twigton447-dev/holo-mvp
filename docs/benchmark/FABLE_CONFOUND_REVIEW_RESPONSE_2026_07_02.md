# Fable Confound Review Response

Status: READ_ONLY_ADVERSARIAL_REVIEW
Date: 2026-07-02
Reviewer: Fable (skeptical reviewer; Codex remains operator)
Inputs reviewed: `FABLE_ORACLE_INFLUENCE_CENSUS_2026_07_02.md`, `FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.md`, `HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.md`, `audit_holoverify_oracle_confounds_2026_07_02.py`, plus targeted re-reads of `run_20pair_holoverify_3dna_2026_06_29.py`, `run_wave2_holo_target_batch_2026_07_01.py`, and one frozen prompt file (verification below).

Boundaries respected: no providers run, no judges run, no frozen evidence edited, no packets or truths changed. The only file created is this review.

---

## Q1 — Did Codex correctly identify the answer-aware runtime confound?

**Yes, on the core mechanism.** Suffix-derived expected verdict, `action_boundary_verdict_mismatch`, truth-conditioned overblock/underblock directives, and Gov compliance enforcement are all real, correctly located, and correctly interpreted. The census's central recommendation (governed-runtime lane ≠ blind risk bound) is right.

Two framing corrections before this census is quoted anywhere:

**1a. The census measures exposure, not effect.** It counts where oracle strings appear; it never computes whether the oracle changed an outcome. The decisive number — packets where a worker verdict-mismatch was followed by a **verdict flip** into the expected answer — is computable from existing `artifact_registry` rows (turn_number + artifact_verdict are recorded) and is absent. `packets_with_first_worker_mismatch` is even computed in the dataclass and then dropped from the report. Until flip-rate is reported, "95 packets with mismatch evidence" can be spun either way. This is the single most important addition to the audit script.

**1b. The signal-count table mixes attribution levels and will be misread.** `scan_json_object()` is called on entire result files; if a signal string appears once anywhere in the file, **every packet ID in that file** is attributed to the signal (`packets_by_signal[signal].update(packets)`). That is how `action_boundary_verdict_mismatch` shows 416 unique packets while the row-level count (`packets_with_worker_mismatch`) is 95. Both numbers sit in the same report without methodology labels. Additionally, frozen evidence copies duplicate live runs (e.g. `holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052822Z` and `frozen_complete_run_20260629T052822Z/evidence/holo_run` are the same run, both scanned), so string-hit counts (596 mismatch rows, 6280 records) double-count an unknown fraction. Fix: dedupe by run_id + trace hash; label object-level vs row-level attribution; report flip-rate.

---

## Q2 — Missed truth-conditioned paths

Yes. Five, in descending severity. The census's exact-string approach (`STATIC_PATTERNS` = six literal strings) is structurally unable to catch wording variants — which is precisely the handoff's question 2.

**2a. The packet-ID suffix is in the model-visible prompts. Verified this session.** `prompts/HV-DPRV-REP-009-A_W1.json` (wave2 batch 001, run_20260701T042037Z) contains the literal packet ID `HV-DPRV-REP-009-A` **4 times**. Across the entire corpus, suffix `-A` ⇔ ALLOW and `-B` ⇔ ESCALATE by construction. Every worker and Gov call therefore receives a 1-bit in-band answer key. Honest assessment of exploitation risk: low-to-unknown today — a model would have to guess the A/B convention, and it never sees siblings side by side — but it is fatal for any *blind* replication claim, because no auditor will accept "the models probably didn't notice the naming convention." Neither the census (no scan for packet IDs in prompt payloads) nor the blind-gate spec (falsification test 3 checks for "expected verdict, packet truth, answer key" but not ID suffixes) covers this channel. The blind lane must re-key packets to opaque random IDs at runtime and map back post-hoc.

**2b. `knew_terms` gate failures leak builder answer-terms into the next worker's prompt.** `_validate_worker()` fails on `missing_critical_term:<term>` where terms come from `spec["knew_terms"][suffix]` — builder-authored, suffix-conditioned, answer-adjacent strings (e.g. for HV-KITC-031-B: `"49", "45", "duration"` — the exact seam). `_gate_repair_directive()`'s fallback branches embed `failure_text` — the first four failures, term names included — into `must_repair`/`required_repairs` in the next worker baton. So even without the overblock/underblock branch, the runtime tells the worker *which builder-chosen terms its answer must contain, selected by the packet's truth side*. The census does not scan for `missing_critical_term`, `knew_terms`, or `critical_term_count` in either source or traces. This is arguably a stronger steering channel than the directional hints, because it names the controlling evidence rather than just the direction.

**2c. Truth-conditioned artifact rewriting (`_normalize_worker_artifact_after_gate`).** The harness injects every missing `knew_terms[suffix]` string into `critical_features_preserved`, backfills `binding_class` via `_worker_expected_binding(suffix)` (a second suffix→truth derivation the static scan misses), and rewrites `final_answer` from a template interpolating the builder's terms. Normalized artifacts then re-run the gate. Census has no signal for `repair_only_mechanical_gate_normalization` (the metadata reason string, which IS in traces and trivially scannable) — so the report cannot say how many of the 614's admissible artifacts are partially harness-authored.

**2d. Suffix-conditioned binding-class failures.** `allow_requires_source_boundary_closed` / `escalate_requires_source_boundary_open` are emitted from suffix-derived expectations and appear in failure text routed to batons. Not in `ORACLE_STRINGS`.

**2e. Wording-variant truth derivations.** `run_wave2_holo_target_batch_2026_07_01.py:770` `def expected_verdict(suffix)` and the `expected_verdict_for_local_gate` field pass the exact-string scan untouched because they don't match `expected = "ALLOW" if suffix == "A" else "ESCALATE"`. In this case the wave-runner usage is post-hoc scoring (acceptable), but the scanner cannot tell — it neither catches the variant nor classifies runtime vs post-hoc use. Recommendation: replace string-grep with an AST pass flagging **any** expression deriving a verdict-typed value from `suffix`/`sibling_id`/`packet_id`, then classify each site as runtime-reachable or scoring-only. That is the correct general form of the handoff's question 1.

Also worth logging (lower severity): `spec["boundary"]` text is injected into artifacts during normalization (`_set_if_blank(binding, "action_boundary", spec.get("boundary")…)`) — same text for both siblings, so not truth-conditioned, but it is builder text entering "model" artifacts and should be disclosed in any artifact-quality claim.

---

## Q3 — Is the blind-gate spec strict enough?

Good skeleton; not yet reward-hack-proof. Seven required tightenings:

1. **Opaque runtime packet IDs.** Add to Core Rule: runtime components must not receive any identifier from which truth is derivable — packet IDs must be re-keyed to random opaque IDs before any prompt/gate/Gov/selector sees them; the suffix mapping lives only in the post-hoc scorer. Add a falsification test: prompt scan for `-A`/`-B`-suffixed IDs and for any string from the freeze-record ID namespace.
2. **Name the forbidden spec fields.** Forbidden-checks list bans suffix-derived verdicts but never mentions `knew_terms`, `allow_rule`, `esc_rule`, `packet_truth`, or spec objects generally. A gate that keeps `missing_critical_term` checks satisfies the current spec's letter while staying truth-conditioned. Rule: the blind runtime may load **only** the model-visible payload file; it must be physically unable to load the pair spec or freeze-record truth fields (separate directory, separate loader, enforced by test 2f below).
3. **Ban harness artifact mutation.** "Normalization logic" is listed as a component that must not know truth, but blind normalization can still inject spec text. Simplest strict rule: in the blind lane, the harness never writes into worker artifacts; malformed artifacts fail structurally and are scored as such. If any normalization is kept, normalized artifacts must be flagged in-trace and excluded from artifact-quality claims.
4. **Close the "monotonic blind structural features" loophole.** If "structural features" includes counts of `critical_features_preserved`, the selector inherits the knew_terms channel. Enumerate the selector's criteria closed-form in the spec (parse validity, source-ID validity, section presence, dependency-flag consistency, contradiction check) and forbid any feature computed from spec content.
5. **Pre-registered seeded canary selection.** "Same frozen packet bank or a clearly pre-registered subset" permits operator-chosen easy packets. Require: stratified random sample, published seed, selection script committed before the run, sample hash in the approval packet.
6. **Budget parity.** Fix worker-turn and token budgets to equal the governed lane being compared, and state that transport retries are capped identically. Otherwise the blind lane can quietly buy accuracy with extra turns and the comparison to the governed lane is confounded in the other direction.
7. **Scope the canary's evidentiary weight.** 20 packets support a structural pass/fail only. The spec should state that no FP/FN rate or bound may be quoted from the canary, and the claim language it licenses is "blind-gate pipeline validated structurally," nothing more. (At 20 packets, even 20/20 gives a one-sided 95% upper bound of ~14% per side — worthless as a headline, dangerous as a temptation.)

One more: the spec's invalidation list ("parser failure where no admissible final artifact exists") needs a guard — since blind-lane admissibility is structural, a run where every artifact fails structurally must be scored as an **error-equivalent abstention** in a disclosed count, not silently dropped, or the survivorship confound (C2) reappears in blind clothing.

---

## Q4 — No-provider fixtures required before any live blind-gate canary

All implementable with mocked transports; suggested home `tests/test_blind_gate_fixtures_2026_07.py` plus a `fixtures/` directory of golden files.

1. **Truth-invariance fixture (the decisive one).** Run the blind runner twice on the same payload with the truth metadata poisoned in opposite directions (spec copy says ALLOW, then ESCALATE). Assert every prompt, gate result, baton, and selector decision is byte-identical. Runtime behavior must be a pure function of payload + model outputs. This single test subsumes most of the forbidden-checks list.
2. **Wrong-verdict-completes fixture.** Mock workers return a confident wrong verdict every turn. Assert: run completes, final verdict recorded, post-hoc scorer counts FP/FN, run is **not** invalidated, no repair directive references verdict direction. (Spec test 6, made executable.)
3. **Directive-symmetry golden test.** Force each gate-failure class; assert repair directive text is drawn from a fixed catalog and is identical regardless of packet truth and of worker verdict direction. Byte-compare against golden files.
4. **Sibling prompt-diff golden test.** Generate all prompts for an A/B pair with mocked models; the diff between sibling prompt sets must contain only the payload delta — no gate-derived, spec-derived, or ID-derived differences. Also asserts opaque re-keying (no `-A`/`-B` anywhere in prompts).
5. **Truth-reachability static test.** AST scan over the blind runner: no runtime-reachable code path may reference `knew_terms`, `allow_rule`, `esc_rule`, `packet_truth`, suffix parsing, or freeze-record truth fields. Fails the build if a new path appears. (This replaces string-grep leakage auditing — see Q2e.)
6. **Selector-blindness swap test.** Two admissible artifacts with opposite verdicts; swap which one matches truth; assert identical selection.
7. **Scorer round-trip fixture.** Post-hoc scorer must reproduce FP/FN/TP/TN from frozen final artifacts alone; poison an intermediate runtime file and assert the score is unchanged.
8. **Replay determinism fixture.** Recorded mock transcripts replayed twice produce byte-identical traces (seeded), so the live canary is fully auditable afterward.

Fixtures 1, 3, and 4 are the reward-hacking firewall: they make it mechanically impossible to reintroduce directional steering with new wording, which is exactly how this confound would come back.

---

## Q5 — Public claim language still unsafe

The census confirms `frontend/benchmark.html` and `whitepaper.html` carry counted-run phrasing and a blind-gate caveat. Good. Still unsafe:

1. **Any bare ratio anywhere on the page.** The census found `40/40`, `100/100`, `174/174`, `280/280`, `614`-family numbers rendered as standalone figures. A caveat paragraph elsewhere does not travel with a screenshot. Every displayed ratio needs an inline lane label ("governed-runtime lane") or removal until blind replication.
2. **"Solved."** `KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF_2026_06_29.md`: "Holo solved 40/40 packets." Under an answer-aware repair loop, "solved" overclaims. Safe: "completed 40/40 under the governed-runtime protocol."
3. **"Leakage status: PASS."** Same brief. True only for literal-string leakage; directional repair leakage was present by design. Must be restated as "literal answer-key string audit passed; runtime included answer-aware repair gates (see blind-gate replication plan)" or dropped.
4. **The 95% upper-bound sentences.** Quoting exact one-sided bounds (0.487%/0.971%) attaches statistical precision to an estimator that the runtime pins at zero by construction (oracle steering + C2 survivorship). Until the blind lane exists, the honest statement is the spec's own claim-boundary paragraph — which is well-written and should be the *only* sanctioned language. Recommend deleting the CI numbers from public surfaces, keeping them in the internal appendix with the lane label.
5. **Solo-comparison numbers (6/120 KNEW, 96/120 wrong).** Still presented without disclosing (a) corpus was screened for solo failure (`build_and_screen_*`: "selects families where Solo misses at least one sibling"), (b) solo had one shot with no repair/normalization while Holo had five calls with both. Either disclose both asymmetries beside every solo comparison or drop the comparisons until the ablation ladder produces symmetric numbers.
6. **Legacy page debts remain** (from the Phase-1 register, unresolved): `13_the_threshold_gambit` published while ledger-retired as non-reproducible; "same turn budget / only variable is architecture" contradicted by `SOLO_MAX_TURNS = 1` vs `MAX_TURNS = 10`.
7. **Funnel language.** The reconciliation (72 complete / 46 invalid-or-blocked files, 392 packets in invalid artifacts) is an inventory with known duplicates (frozen evidence copies re-counted). Do not quote its packet totals publicly until deduped by run identity; and the appendix's "observed errors: 0" needs the survivor-lane footnote regardless — the funnel found at least one `verdict_or_admissibility` invalidation and two gov-contract invalidations that an intent-to-treat count must mention.

---

## Verdict

Codex's audit is directionally correct and the blind-gate spec is the right instrument. It is not yet strict enough to survive a hostile reviewer: the suffix-in-prompt channel (2a) and the knew_terms channel (2b/2c) are unaddressed, the census conflates exposure with effect and mixes attribution levels, and the spec licenses a canary whose selection and budgets aren't pinned. Fix the spec per Q3, land fixtures 1–5 before any live canary, add flip-rate + normalization-count + dedupe to the audit script, and adopt the spec's claim-boundary paragraph as the only public language until the blind lane reports.

Nothing here requires touching frozen evidence. All proposed work is new tests, new audit passes, spec edits, and public-copy edits — Codex-implementable, each with an acceptance test named above.
