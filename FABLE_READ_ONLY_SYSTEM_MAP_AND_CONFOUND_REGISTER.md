# FABLE Read-Only System Map and Confound Register

Status: `PHASE_1_READ_ONLY_AUDIT_COMPLETE`
Date: 2026-07-02
Author: Fable (read-only pass; no files edited, no providers run, no judges run)
Mandate: `docs/FABLE_HOLOENGINE_SINGLE_MANDATE_2026_07_02.md`

Scope statement: everything below is repo-backed. Each claim cites file + function. Nothing was executed against providers. No frozen packets, prompts, traces, lock manifests, or evidence packages were modified.

---

## 1. System Map

### 1.1 Two distinct benchmark stacks exist

**Legacy stack (Hargrove / 11-condition ablation, ~June 17 snapshot):**

```
scenario_templates.py / fp_hardening_loop.py     → packet authoring + adversarial hardening
hashlock.py + freeze_packet.py + packet_lifecycle.py → freeze (packet+prompt hash only)
ablation_engine_harness.py                       → conditions A/B/C/D (frozen prompt) + E (production Holo)
benchmark.py → run_holo_loop → context_governor.py + llm_adapters.py  → Condition E
holo_judge.py                                    → 5-turn LLM judge panel → verdict + KNEW/LUCKY/WRONG/CONFUSED
benchmark_ledger.csv, BENCHMARK_README.md        → published results (holoengine.ai/benchmark)
```

**Current HoloVerify stack (the 614-packet 0FP/0FN claim, docs/benchmark/):**

```
build_and_screen_kit_c_*.py                      → template-generated sibling pairs (A=ALLOW, B=ESCALATE),
                                                    truth + allow_rule/esc_rule/knew_terms authored at generation,
                                                    screened against MiniMax solo ("select families where Solo misses")
build_freeze_holoverify_*.py                     → freeze packet banks (hash-rooted)
run_20pair_holoverify_3dna_2026_06_29.py         → BASE RUNNER: worker → deterministic gate → Gov router →
                                                    repair loop → final selector ("first admissible candidate")
run_wave2/wave3/wave5_holo_*.py                  → wave batches (importlib-load base runner, override roster)
run_*_solo_triage_*.py                           → solo one-shot baselines (single call, strict schema)
build_holoverify_domain_consolidation_ledger_    → aggregates COMPLETE batches
build_holoverify_statistical_appendix_2026_07_01 → 614 / 307+307 / 0FP / 0FN / CI bounds
KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF           → public narrative
```

### 1.2 The HoloVerify enforcement spine (as actually wired)

Per packet, from `run_20pair_holoverify_3dna_2026_06_29.py`:

1. Worker (rotating mini-model roster) emits a structured artifact with `verification_verdict`.
2. `_validate_worker()` — the "deterministic gate" — runs after every worker.
3. Gate result goes to Gov (`gov_receives_gate_results` assertion in wave runners).
4. On gate failure, `_enforce_gov_gate_compliance()` forces Gov to `CONTINUE_WORKER` with a `_gate_repair_directive()` baton visible to the next worker.
5. `_normalize_worker_artifact_after_gate()` may mechanically rewrite a repair-only-failing artifact so it passes.
6. Final selector pins the "first admissible candidate" (wave5 runner: "pinned best artifact present after first admissible candidate").
7. Batch summary requires `packet_correct == expected["packets"]` and `valid_pairs == expected["pairs"]` for `readiness_passed`; otherwise the batch is `INVALID_OR_INCOMPLETE` with `invalidation_reason = "VERDICT_OR_PAIR_ADMISSIBILITY_FAILURE"`.
8. Consolidation ledger and statistical appendix aggregate the COMPLETE lane into the 614 denominator.

### 1.3 Where ground truth lives

- Truth is assigned at generation: packet ID suffix `-A` = ALLOW, `-B` = ESCALATE (`expected_verdict(suffix)` in `run_wave2_holo_target_batch_2026_07_01.py`).
- Per-pair `knew_terms`, `allow_rule`, `esc_rule` are authored in the build scripts (e.g. `build_and_screen_kit_c_hardened_candidates_2026-06-28.py` SPECS).
- The freeze records carry `packet_truth` and `knew_terms` into the runner (`"knew_terms": pair["spec"].get("knew_terms", {}).get(suffix, [])` in the base runner).

### 1.4 Denominator arithmetic

614 reconciles: 40 (Commerce) + 40 (Kit C) + 40 (IT Access) + 40 (AP) + 174 (W2+W3+W4) + 280 (W5) = 614; 307 pairs. The arithmetic is clean. The question is what lane the 614 was drawn from (see C2).

---

## 2. Ranked Confound Register

Ranking = (impact on headline claim) × (strength of repo evidence). All ten below are evidenced, not hypothesized.

| # | Confound | Threatens | Evidence strength |
|---|----------|-----------|-------------------|
| C1 | Answer-keyed runtime gate + truth-conditioned repair directives | 614 0FP/0FN headline | Direct code |
| C2 | Validity-lane survivorship (wrong verdict ⇒ invalid batch, not error) | 614 denominator | Direct code + ledger |
| C3 | Harness-authored artifact content ("deterministic normalization" injects knew_terms) | KNEW/admissibility quality claims | Direct code |
| C4 | Generator–screener coupling (packets selected for solo failure; screener model in Holo roster) | "solo 6/120 KNEW" comparisons | Direct code |
| C5 | Asymmetric admissibility across arms (solo one-shot strict schema, no repair; Holo gets repair+normalization) | all Holo-vs-solo gaps | Direct code |
| C6 | Legacy judge is not blind (condition labels + provider names in trace block) despite protocol claiming anonymization | Hargrove locked results, KNEW labels | Direct code vs. protocol doc |
| C7 | ESCALATE-biased parsing and tie-breaking in legacy harness | legacy ablations, FP-precision claims | Direct code |
| C8 | Prompt and turn-budget asymmetry in legacy benchmark (solo = 1 generic turn; Holo = 10 turns of domain-coached production prompts) | public Results 1–4 | Direct code vs. README |
| C9 | Publication selection + model-version drift (retired, non-reproducible result still on public page) | public page credibility | Ledger vs. README |
| C10 | Leakage audit checks literal strings only; passes while C1's directional leakage flows | "Leakage status: PASS" claims | Direct code |

### C1 — The deterministic gate knows the answer, and the repair loop points at it

`run_20pair_holoverify_3dna_2026_06_29.py`:

- `_validate_worker(parsed, spec, suffix, valid_ids)`: `expected = "ALLOW" if suffix == "A" else "ESCALATE"`; emits `action_boundary_verdict_mismatch` when the worker disagrees with ground truth. The gate also requires every builder-authored `knew_terms` string to appear in the artifact (`missing_critical_term:*`).
- `_gate_repair_directive(gate, worker_output)`: when the mismatch failure is present, it emits a **direction-of-error hint**: worker said ESCALATE on an ALLOW packet → "Potential overblock… if closed, return ALLOW"; worker said ALLOW on an ESCALATE packet → "Potential underblock… return ESCALATE". The wording is conditional, but the trigger is truth-conditioned — the hint only ever fires when the worker is wrong, and it names the direction.
- `_enforce_gov_gate_compliance()`: on gate failure, Gov is overridden to `route_verdict = "CONTINUE_WORKER"` and the directive is written into `next_worker_baton` — model-visible on the next turn.
- The final selector pins the first **admissible** artifact, and admissibility includes verdict-matches-truth. So the selected final verdict can only ever be correct or the run fails. 0 FP and 0 FN are structural properties of the selector, not measured properties of the architecture.

Solo baselines get exactly one call and none of this. The measured Holo-vs-solo gap therefore contains an oracle term of unknown size.

To be precise about what this does and does not mean: the workers still have to produce the right artifact — the harness doesn't fabricate a verdict from nothing, and `_gate_failures_are_repair_only()` prevents Gov from inverting a verdict on cosmetic failures. But any packet where a worker initially erred and later agreed with the key was plausibly steered, and any packet where no worker ever agreed was removed from the denominator by C2. Between steering and survivorship, observed error on the official lane is pinned at zero by construction.

**Threatens:** the public 614-packet 0FP/0FN claim directly. **Fix type:** code change (blind the runtime gate) + reporting change (re-scope claim until re-run).

### C2 — Wrong verdicts invalidate batches instead of counting as errors

`run_wave2_holo_target_batch_2026_07_01.py` → `holo_summary()`:

```
elif packet_correct != expected["packets"] or valid_pairs != expected["pairs"]:
    invalidation_reason = "VERDICT_OR_PAIR_ADMISSIBILITY_FAILURE"
```

`readiness_passed` requires 100% correct packets. A batch containing a single wrong verdict is classified `INVALID_OR_INCOMPLETE`, not "batch with one error." Evidence that this lane was exercised:

- `HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_2026_07_01.md`: `complete_with_prior_invalid_batches: 1`, `WAVE5_OTSF_HOLO_BATCH_004` = `COMPLETE_WITH_PRIOR_INVALID_RUNS`, 2 runs, 96 provider calls observed (expected 50 per clean batch — i.e., roughly a full re-run).
- `build_it_access_replacement_pair_015r1_2026_07_01.py`: pair `HV-ITAC-REP-015` retired and replaced by `015R1` via a "supplemental freeze used only by the targeted replacement batch runner."
- Multiple rerun directories: `holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/` contains three run timestamps; `COMMERCE_BATCH1_RERUN_*` memos.

If any prior invalid run failed for verdict reasons (not transport), the honest intent-to-treat error count is > 0 and the statistical appendix's "observed errors: 0" is a per-protocol-survivor number. The appendix does not disclose the invalid lane or the retry census. Some invalidations are legitimately transport/contract failures — the census must separate those.

**Threatens:** the 614 denominator and both CI bounds. **Fix type:** reporting first (publish the funnel: staged → run → invalidated-by-reason → rerun → included), code second (intent-to-treat ledger).

### C3 — The harness writes answer-bearing content into Holo artifacts

`_normalize_worker_artifact_after_gate()` in the base runner: for repair-only failures with a correct verdict, the harness **appends every missing `knew_terms` string** into `critical_features_preserved`, backfills `boundary_binding` fields with template text, and rewrites `final_answer` via `_normalize_final_answer()` which interpolates the builder's terms. The gate is then re-run on the harness-modified artifact.

So "Holo artifacts cite the controlling evidence" is partially the harness citing it. Solo artifacts receive no such normalization; their `structural/evidence fail` classifications (14/120 in KIT_C brief) are graded on raw output.

**Threatens:** KNEW/admissible-quality comparisons; "Holo preserved X" narratives in `KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF`. **Fix type:** code (normalization must be logged and either disabled or symmetric) + reporting (disclose normalization counts per packet).

### C4 — Packets are selected for solo failure by a model inside Holo's roster

`build_and_screen_kit_c_hardened_candidates_2026-06-28.py` docstring: "runs current MiniMax raw Solo on both siblings, and **selects families where Solo misses at least one sibling**." MiniMax-M2.5-highspeed is simultaneously the Gov and a worker in the Holo roster (`holo_governed_shadow.py` ROSTER; wave runners `GOV_MODEL_KEY = "minimax"`).

Two effects: (a) the corpus is adversarially curated against the solo condition — solo failure rates are a selection criterion, not a finding; (b) all packets are single-seam template siblings whose delta is an exact-string mismatch (`RC-FIN-007-S` vs `RC-FIN-007`, `ALT-CRM` vs `ALT-ERP`, 49 vs 45 minutes) — a distribution that maximally rewards the exact-match checking the gate enforces and that the generator guarantees is decisive. "Synthetic distribution comfort" is built in.

**Threatens:** every "solo models fail N/120" claim; generalization of the result to real enterprise traffic. **Fix type:** reporting (disclose the screening funnel and survivor rate) + evidence (run a small unscreened-pool baseline; the 36-call preflight already staged in the mandate is the right shape).

### C5 — Admissibility is asymmetric across arms

Solo triage (`run_replication_*_solo_triage_*.py`, SYSTEM prompt in `build_and_screen_*`): one shot, strict JSON contract, ≤5 cited artifacts, no repair, no JSON-repair retry, parse failure = non-KNEW. Holo: up to 5 calls/packet, forced repair turns on gate failure, mechanical normalization, alias normalization for Gov batons (`_normalize_gov_*`). KIT_C brief counts 4/120 solo parse failures and 14/120 structural fails against solo. Under equal repair budgets some fraction of those flip.

**Threatens:** the 6/120 vs 40/40 contrast magnitude. **Fix type:** reporting (reclassify solo fails by type; publish "wrong verdict only" comparison: 96/120 vs 0) — no code needed to re-derive from existing traces.

### C6 — The legacy Judge is not blind, contradicting the written protocol

`BENCHMARK_PROTOCOL.md` Stage 4: traces are "anonymized (no condition labels, no model identities)." The code: `holo_judge.py` `_summarize_trace(condition, trace)` emits `[A-GPT] VERDICT: …`, `[E-HoloArch] …`, and per-turn `role (provider)`; `run_judge()` injects this labeled block into Turns 4–5. The Trace Auditor and Adjudicator know exactly which trace is Holo's. The Judge panel is also drawn from the same three vendors as the contestants, with unseeded `random.choice` rotation (non-reproducible), and the adjudicator's fallback is `"ESCALATE-INSUFFICIENT"  # safe default: burden is on ALLOW` — a prior structurally aligned with Holo's own conservatism.

**Threatens:** `HARGROVE-BEC-ALLOW-001` locked verdict and all KNEW/LUCKY/WRONG labels; the protocol document's own integrity claims. **Fix type:** code (anonymize + shuffle + seed) and re-adjudication of anything locked under the non-blind judge before further public use.

### C7 — ESCALATE-first parsing and ESCALATE tie-breaking

`ablation_engine_harness.py` `_extract_verdict()`: `if re.search(r"\bESCALATE\b", t): return "ESCALATE"` before checking ALLOW — a solo answer reading "ALLOW; no need to ESCALATE" parses as ESCALATE. Condition D majority vote: "ESCALATE wins ties (conservative)." Holo's verdict comes from structured governor output and never passes through this regex. On ALLOW-truth (FP-trap) packets this inflates solo false-positive rates relative to Holo.

**Threatens:** legacy FP-precision results (including the B/C-condition WRONGs in the Hargrove table). **Fix type:** code (final-line parsing + ambiguity logging) + re-derivation from stored raw outputs (no provider calls needed).

### C8 — Legacy prompt and turn asymmetry vs. the "only variable is architecture" claim

`BENCHMARK_README.md`: "Same context. Same turn budget. The only variable is structure." The code: `benchmark.py` `SOLO_MAX_TURNS = 1` vs `MAX_TURNS = 10`; Condition E in `ablation_engine_harness.py` bypasses the frozen `UNIVERSAL_INSTRUCTION` entirely and calls `run_holo_loop` → production prompts in `llm_adapters.py` that contain explicit domain coaching: named BEC categories, threshold-clustering detection steps ("Are multiple consecutive invoices clustered just below threshold"), aggregate-threshold arithmetic instructions, and FP-suppression rules. `context_governor.py` contains packet-class-specific carve-outs (e.g. the payment-routing scope rule annotated "first surfaced on supplier_prepayment Chapter 11 approval packet" — a rule patched in response to a specific benchmark case). Published Results 1 and 4 are threshold-clustering attacks — the exact pattern Holo's prompt names.

**Threatens:** public Results 1–4 and the structural thesis as stated. **Fix type:** either give solos the same domain playbook (playbook-equalized ablation) or re-scope the public claim from "architecture" to "architecture + curated domain policy."

### C9 — A retired, non-reproducible result is still published

`benchmark_ledger.csv`: `13_the_threshold_gambit` all-three-solo-fail row is `retired` — "run with gemini-3.1-pro-preview (deprecated model); all-three-fail result not reproducible with gemini-2.5-pro." Eleven subsequent reruns show unstable verdicts (including Holo itself outputting ALLOW on 2026-03-27, and solo models sometimes escalating). `BENCHMARK_README.md` still lists it as public Result 1 with "Gemini 2.5 Pro: ALLOW ✗". Also: 165 ledger rows, 155 with no publication status; Holo verdict base rate in the ledger is heavily ESCALATE (104 ESCALATE / 35 ALLOW / 26 skip-error) — on an escalate-heavy corpus a trigger-happy architecture wins by prior, which is precisely what FP-trap packets are supposed to control and why the FP lane's integrity (C7) matters.

**Threatens:** public page credibility wholesale — this is the kind of discrepancy an outside auditor finds in an afternoon. **Fix type:** reporting only. Pull or re-caveat Result 1; reconcile the page against the ledger; publish the selection rule.

### C10 — The leakage audit cannot see the leak that matters

`no_leakage_audit()` greps prompt files for literal strings (`packet_truth`, `required_verdict`, …) and `_assert_prompt_clean()` checks `FORBIDDEN_PROMPT_TERMS`. The C1 directional repair hints contain none of these strings, so "Leakage status: PASS; 240 prompt files, 0 forbidden hits" (KIT_C brief) is true and irrelevant. The audit certifies the absence of a leak nobody would write while missing the one the harness generates.

**Threatens:** the evidentiary weight of every "no-leakage PASS" line in public memos. **Fix type:** code (semantic leakage audit: flag any prompt content whose generation was conditioned on `packet_truth`, which is checkable statically from the runner).

### Minor register (not ranked, worth fixing)

- `holo_judge.py` `_call_with_repair`: comment says repair uses "a different model" but re-calls the same adapter before repairing — silent second sample.
- `fp_hardening_loop.py`: docstring says "Converges ONLY when 3/3 models ESCALATE"; code sets `TARGET_ESCALATE_COUNT = 1`. Doc/code drift in an adversarial generation tool.
- `hashlock.py` freezes packet + prompt only — harness code, model versions, gate logic, and judge prompts are outside the hash boundary. The gate that decides admissibility can change without breaking any freeze.
- Unseeded randomness in judge rotation and `_pick_provider`.
- `holo_judge.py` loads the packet from `manifest["packet_path"]` at judge time without re-verifying the freeze hash.

---

## 3. The Five Most Likely Ways the Evidence Stack Is Fooling Us

Per the mandate's first-deliverable spec: risk → where confirmed → smallest falsification test → what it threatens → fix type.

**1. The 0FP/0FN result is partially selector-guaranteed, not architecture-earned (C1+C2).**
Confirmed at: `run_20pair_holoverify_3dna_2026_06_29.py` (`_validate_worker`, `_gate_repair_directive`, `_enforce_gov_gate_compliance`), `run_wave2_holo_target_batch_2026_07_01.py` (`holo_summary`). Already confirmed by reading; the open question is magnitude, not existence.
Smallest test: **Oracle-influence census** — a read-only script over existing trace JSONLs counting, per packet: (a) any `action_boundary_verdict_mismatch` gate failure, (b) whether the final verdict differs from the first worker verdict, (c) normalization applications. Zero provider calls.
Threatens: public claims. Fix: code + claim re-scoping.

**2. The denominator is a survivor lane (C2).**
Confirmed at: wave progress ledgers, rerun directories, replacement-pair freeze.
Smallest test: **Funnel reconciliation** — enumerate every `live_runs/run_*` directory under all wave/replication roots, join against the consolidation ledger's included runs, tabulate invalidation reasons. Read-only.
Threatens: public claims (the CI bounds specifically). Fix: reporting (intent-to-treat appendix).

**3. Solo baselines were curated to fail (C4).**
Confirmed at: `build_and_screen_*` docstrings and screening summaries (`screen_summary.json` artifacts already on disk).
Smallest test: **Screening funnel count** — from existing screen artifacts, report candidates generated vs. families kept, and the kept-family solo-failure criterion. Read-only. Decisive live version (needs approval): run the staged 36-call unscreened solo preflight.
Threatens: public claims + internal confidence in generalization. Fix: reporting + one small approved run.

**4. The Holo-vs-solo gap is inflated by asymmetric admissibility and grading (C5+C7+C3).**
Confirmed at: solo triage SYSTEM contracts, `_normalize_worker_artifact_after_gate`, `_extract_verdict`.
Smallest test: **Rescore from stored raw outputs** — recompute solo results counting only wrong-verdicts as failures (excluding parse/structural), and recompute legacy verdicts with a final-line parser. Read-only.
Threatens: comparison magnitudes in public briefs. Fix: reporting; parser fix is code but re-derivable offline.

**5. The public page contains a known-non-reproducible flagship result and an untrue isolation claim (C8+C9).**
Confirmed at: `benchmark_ledger.csv` vs `BENCHMARK_README.md`; `benchmark.py` turn constants vs README "same turn budget."
Smallest test: none needed — the contradiction is already in the repo. Verification is a diff of published table vs ledger rows.
Threatens: public credibility (highest reputational risk per unit effort to fix). Fix: reporting only, immediately.

---

## 4. Falsification Plan (smallest decisive battery)

All tests are designed so a **negative result would genuinely change a conclusion**. Tests 1–5 are no-provider. Tests 6–8 need Taylor's explicit provider approval and are sized minimally.

| # | Test | Files to inspect/create | Artifact produced | Pass condition | If it fails |
|---|------|------------------------|-------------------|----------------|-------------|
| F1 | Oracle-influence census | new `tools/audit_oracle_influence.py` reading `docs/benchmark/**/live_runs/**/trace*.jsonl` | `ORACLE_INFLUENCE_CENSUS.json/md`: per-packet mismatch-gate fires, verdict flips after directive, normalization applications | <5% of 614 packets show verdict-mismatch → flip sequence | 0FP/0FN claim must be re-scoped to "with runtime verdict-audit gate"; blind re-run required before public use |
| F2 | Denominator funnel reconciliation | new `tools/audit_run_funnel.py`; wave ledgers; consolidation ledger inputs | `RUN_FUNNEL.md`: staged→run→invalid(by reason)→rerun→included | all invalidations are transport-class; every packet ran exactly once on the official lane | "observed errors: 0" becomes "0 on final attempts; N verdict-invalid runs excluded" — appendix must say so |
| F3 | Screening funnel disclosure | existing `kit_c_hardened_candidate_screen_2026-06-28/screen_summary.json` + peers | `SCREENING_FUNNEL.md`: generated vs kept vs kept-criterion | screening did not condition on solo failure (already known false for Kit C lineage) | solo-failure rates must be labeled "on solo-adversarial corpus"; unscreened baseline (F6) becomes mandatory |
| F4 | Symmetric rescore | new `tools/rescore_solo_and_legacy.py` over stored raw outputs | `SYMMETRIC_RESCORE.md`: solo wrong-verdict-only rates; legacy verdicts under final-line parser | gap magnitude survives rescore (e.g. solo wrong-verdict ≥80% where currently claimed 96/120) | public gap numbers revised; parse-fail rows reclassified |
| F5 | Judge blindness audit (legacy) | `holo_judge.py`; existing judge_verdicts outputs | `JUDGE_BLINDNESS_AUDIT.md` | protocol text corrected; no locked result relies on non-blind adjudication | Hargrove lock demoted to diagnostic until re-adjudicated blind |
| F6 | Unscreened-pool solo baseline (36 calls, already staged; approval hash `48e906a7…`) | `run_kita_ablation_series_solo_one_shot_2026_07_02.py` | solo results on non-curated packets | solo failure rate on unscreened pool within ~15pts of curated pool | curation effect quantified; public framing adjusted |
| F7 | Blind-gate Holo re-run (sample) | Codex-built variant of base runner with structure-only gate (no `expected`, no `knew_terms` at runtime); run on a stratified 20-pair sample | blind-gate accuracy vs official | ≥90% pair accuracy blind | architecture advantage is real but smaller; headline re-based on blind number |
| F8 | Verdict-agnostic repair re-run (sample) | variant where repair directive is a single symmetric "re-verify the boundary" prompt regardless of truth | accuracy without directional hints | accuracy within noise of F7 | directional hints were doing the work; remove permanently |

Ordering: F1–F5 this week (no approvals needed); F6 next (already staged); F7/F8 only after Codex review of the variant runners, since they create new benchmark-adjacent code.

**What would make me stop claiming architecture advantage:** F7 blind-gate accuracy collapsing toward the no-Gov ablation's 13/24, combined with F1 showing high steering incidence. What would strengthen the claim: F1 showing most packets never fire the mismatch gate (workers were right on turn 1) and F7 holding ≥90% — in that case the current result understates nothing and the fix is mostly reporting hygiene.

---

## 5. Proposed Implementation Plan (Phase 4, all via Codex CLI, none started)

Each item carries the mandated reward-hacking note. Nothing below touches frozen packets or evidence.

**P0 — Reporting corrections (no benchmark code):**
1. Statistical appendix addendum: disclose gate design, repair loop, survivorship lane, screening funnel. *Reward-hack risk: none — can only reduce apparent performance.*
2. Public page: remove/re-caveat `13_the_threshold_gambit`; correct "same turn budget"; disclose corpus curation. *Risk: none.*

**P1 — Gate integrity (benchmark-affecting, needs independent approval gate):**
3. Split `_validate_worker` into `structural_gate` (runtime: schema, source-ID validity, word bands — no `expected`, no `knew_terms`) and `truth_audit` (post-hoc scoring only). *Reward-hack note: if `knew_terms` remain runtime-visible anywhere (batons, normalization), the split is cosmetic; acceptance test must assert the runtime path is truth-free by construction (no `suffix`→verdict, no `spec["knew_terms"]` reachable).* 
4. Replace directional repair directives with one symmetric re-verification prompt. *Reward-hack note: a cleverly-worded "symmetric" prompt could still encode direction via which failures it lists; acceptance test: directive text must be byte-identical for overblock and underblock cases.*
5. Delete or fully log-and-disable `_normalize_worker_artifact_after_gate`. *Reward-hack note: silently keeping it for "repair-only" cases preserves the artifact-quality inflation; if kept, normalization count must appear in every summary and normalized artifacts must be inadmissible for KNEW.*

**P2 — Accounting integrity:**
6. Intent-to-treat ledger: every live run permanently recorded with invalidation reason; consolidation emits both survivor-lane and ITT numbers. *Reward-hack note: an ITT lane invites re-running until clean and reporting only the survivor lane anyway — the ledger must be append-only and both numbers must appear in the same table.*
7. Extend hash boundary: freeze runner + gate code hash into each run manifest (`current_head()` already computes this in wave5 — surface it in the appendix). *Risk: none.*

**P3 — Legacy stack repairs (before any further Hargrove publication):**
8. Judge blinding: strip condition labels, shuffle trace order, seed rotation, cross-vendor judge exclusion (judge provider ∉ contestant providers for the packet under audit). *Reward-hack note: blinding could be gamed by leaving Holo's distinctive turn-log structure identifiable; summarize all traces into a uniform schema first.*
9. `_extract_verdict` final-line parsing + ambiguous-verdict logging; re-derive legacy tables offline. *Reward-hack note: parser changes can flip results in either direction; re-derivation must be published for all 165 ledger rows, not a favorable subset.*

Acceptance for anything in P1/P2: before/after regression on locked packets, independent review, and a written note on how the change could accidentally inflate apparent performance — per the mandate's approval gate.

---

## 6. Missing Instrumentation

- No per-packet record of whether the mismatch gate fired before the final verdict (F1 has to reconstruct it from turn order).
- No append-only run registry across waves (funnel must be reconstructed from directory listing).
- No screening-funnel artifact in the consolidated evidence (screen summaries exist per-script but aren't rolled up).
- No runtime/harness code hash in the statistical appendix.
- No seed control anywhere randomness is used (judge rotation, provider picks).
- No canonical "what lane is this row in" field joining ledger rows to public claims.

## 7. What I Did Not Verify (honest limits)

- I did not read every wave runner; I verified the spine in the base runner + wave2/wave5 runners and confirmed wave5 imports the wave2 runner which imports the base. If some wave used a different gate, the census (F1) will show it.
- I did not verify how the `kita` no-Gov ablation computes "strict admissible-correct 13/24" — if its admissibility gate is also answer-keyed, the ablation comparison is contaminated in both arms and understates nothing; worth a targeted read before F7.
- I did not open the 614 packets themselves or the trace files (volume); all trace-level claims are about code paths, and F1 exists to quantify them.
- I did not audit HoloChat/HoloBuild product surfaces (Phase 5+ per mandate).

---

*Prepared read-only. No providers were called, no judges were run, no benchmark files were modified. The single file created is this register.*
