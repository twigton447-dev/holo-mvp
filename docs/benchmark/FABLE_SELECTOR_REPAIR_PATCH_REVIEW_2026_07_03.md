# Fable — Selector Repair Patch Review

Status: READ_ONLY_REVIEW_COMPLETE
Date: 2026-07-03
Method: patch code read in full; behavior probed empirically with a no-provider verdict-pattern sweep against the patched `select_final`; full blind suite + regression re-run (33 passed). No providers, no judges, no mutation.

---

## VERDICT: `PATCH_MORE`

The patch is truth-blind and genuinely fixes the observed failure. It is not ready to gate a rerun because it ships an **undisclosed architecture change with a measured new failure mode**, covered by exactly zero tests and absent from the patch report — the precise thing the standing mandate's inflation-note rule exists to catch.

## Empirical probe (run this session, patched selector, structural fields equal unless noted)

| Pattern (W1,W2,W3) | Patched pick | Reading |
| --- | --- | --- |
| E, A, E | **ART-003** | The observed 033-B failure: fixed ✔ |
| A, E, A (middle dissenter cited 9 vs 3) | **ART-003** | Truth-inverted twin: if truth is ESCALATE, the patch now *guarantees* the wrong pick. Pre-patch, the heavily-cited dissenter won this case. |
| A, A, E (final dissenter cited 9) | **ART-001** | **Majority-wrong lockout:** a dissenting correct repair can never win, regardless of quality. |
| E, E, A | **ART-001** | Consensus resists final drift — the good direction. |

## Answers

**1. Truth-blind?** Yes. `verdict_consensus_count` counts structurally-valid artifacts sharing a verdict; `final_turn_consensus_repair` is a pure function of turn index, validity, and verdict agreement patterns. No truth, suffix, or scoring fields are reachable; both fields are declared in `SELECTOR_CRITERIA`; `apply_criteria` ≡ `select_final` holds; T2 byte-invariance and the import-closure scan stay green. No new answer channel. One honest nuance: the *mechanism choice* was truth-informed (it was fit to a failure whose truth was known post-hoc). That's what all debugging is — but it's exactly why the rerun-framing rule below matters.

**2. Fixes the observed case?** Yes, verified: E/A/E now selects ART-003. Mechanically: consensus count (2 vs 1) sits above `cited_evidence_count` in the tuple, so the wrong middle artifact can no longer win on citation volume, and the repair flag breaks the W1/W3 tie toward the final repair.

**3. New recency bias?** The bias introduced is not primarily recency — it's **majority dominance**. Consensus count now outranks every quality signal below it, turning the selector into majority-vote-first with structural gates. Two measured consequences: (a) majority-wrong lockout (A,A,E) — on shared-reflex packets like the 020-A shape (2/3 solos wrong the same way), the patched selector locks in the wrong majority no matter how good the dissenting repair is; (b) the inverted pattern (A,E,A) flips from dissenter-wins to majority-wins. On the atlas seam class — model-idiosyncratic 1/3 failures — majority is usually right, so the patch will *look* excellent there. That is partly selection-of-seam-class, not selector wisdom, and it must be said out loud in the patch report.

**4. Regression tests strong enough?** No. Two tests: the fixed pattern and a truth-blindness check. Missing: the inverted pattern, the majority-wrong pattern, consensus-with-gate-failed-artifacts (gate-failed artifacts are correctly excluded from counts — untested), 2-artifact and tie cases, and a T4 truth-swap extension over consensus-bearing grids.

**5. Required no-provider fixtures before any rerun:**
- **R1 — Full 2³ verdict-grid test** with documented expected picks, including `A,E,A → ART-003` and `A,A,E → ART-001` as *asserted intended behavior* — encoding the tradeoff so it can never be discovered by surprise later.
- **R2 — Patch report addendum** (mandate-required inflation note): consensus dominance is an architecture decision, not a bugfix; name the majority-wrong lockout; state why it's acceptable for this lane. Taylor signs it.
- **R3 — T4 extension:** truth-swap sweep over consensus grids (swap which verdict is "true"; picks must be invariant), plus a gate-failed-artifact consensus-exclusion test.
- **R4 — Selector version/hash in run summaries**, so pre- and post-patch runs are mechanically distinguishable in every future rollup.

**6. Rerun now or tests first?** Tests first — R1–R4 are an hour of no-provider work. Then rerun, with the framing pre-registered: **a same-six-pair rerun is mechanical patch validation, not fresh governance evidence** — 033-B passing is guaranteed by construction, since the patch was fit to that exact artifact pattern. Expected result 12/12; it confirms the fix landed and nothing regressed, nothing more. Fresh governance evidence requires packets the patch has never seen — recommend adding 2–3 held V5 wave-2 pairs to the same approval scope so the rerun buys both validation and new signal in one spend.

## Evidence preservation

Confirmed intact: `run_20260703T140931Z` with all 12 opaque packet dirs, TRACE files, and the hash-bound post-hoc score artifact (11/12, all five trace bindings present). This run is **valid pre-patch evidence, not invalid or mixed** — it correctly characterizes the pre-patch selector and is the baseline the patch is measured against. It must appear alongside (never replaced by) any post-patch result, labeled with its selector version per R4.

## Severity-ranked findings

1. **MEDIUM-HIGH — Undisclosed tradeoff:** majority-wrong lockout and inverted-pattern flip exist, are measurable (table above), and appear nowhere in the patch report or tests. Fix via R1+R2.
2. **MEDIUM — Rerun-on-training-example risk:** without R4's pre-registered framing, a 12/12 rerun of the same six pairs will read as governance evidence when it is patch confirmation. Fix via framing + fresh pairs.
3. **LOW — Regression suite thinness** (2 tests). Fix via R1/R3.
4. **NONE — truth channels:** none found; blind suite fully green post-patch (33/33 in my environment with the git stub).
