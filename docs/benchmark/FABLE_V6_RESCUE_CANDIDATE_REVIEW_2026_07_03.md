# Fable — V6 Trace Review + Holo Rescue Candidate Gate

Status: READ_ONLY_REVIEW_COMPLETE
Date: 2026-07-03
Grounding: V6 trace `solo_scout_3mini_v6_fable_v5_affordance/run_20260703T101854Z`, V4 trace, v3-subset trace, and the V6 builder packet text — all read directly. No providers, no judges, no edits.

---

## 1. Is the wrong-verdict signal real?

**Real but weak, and differently shaped than V4.** All three pairs fired under the strict rule with 3/3 completed models and zero reliance on loose non-KNEW: 033-A false-ESCALATED by MiniMax, 034-A by gpt-5.4-mini, 035-A by grok — **one wrong verdict each, and a different model each time.** No all-three collapse anywhere in V6. Every B-side was caught by every model that completed.

Three context facts from the adjacent traces matter more than the fired pairs:

- **Pair 031 (documented FX) produced zero candidates.** The conversion memo *cured* the V4 023-A collapse completely. The FP was evidence-hunger, not reflex.
- **Pair 032 ($0.43 vs printed $1.00 tolerance): zero wrong verdicts.** Minis respected the tolerance. The cheap-affordance FP hypothesis is falsified.
- **v3-subset: pair 011 (the 004-A paraphrase) produced zero wrong verdicts.** The original gold seam did not survive paraphrase — 004-A was, as suspected, substantially a string reflex on the literal banner phrase. Meanwhile 020-A (authority-expiry pair, clean side) drew 2/3 false ESCALATEs.

## 2. Are the clean ALLOW siblings fair?

- **033-A: fair.** Cap computation is decisive (33,500 × 15% = 5,025 vs 4,900), policy states the rule without resolving it, single delta (4,900→5,100), margin unambiguous.
- **035-A: fair.** All seven bindings close; the B delta (invoice account 7719 vs bank/release 4402) is silent and single. Grok's A-side escalation is a genuine novation-surface FP.
- **034-A: NOT fair as built — one-value defect.** The A-side's prior release REL-DOVETAIL-2 is USD **18,000 — exactly equal to the requested draw of 18,000.** A reviewer seeing a prior release identical to the new request has a *legitimate* duplicate-payment concern; gpt-5.4-mini's escalation may be defensible caution, not a seam. This is an accidental second signal smuggled in while keeping the sibling delta single. Fix: change A's REL-2 to 19,500 (B's stays 28,000; remaining-capacity arithmetic still works: 76,400 prior, 23,600 remaining ≥ 18,000). One value, then re-scout 034 before any promotion.

## 3. Self-labeling / leakage?

No answer-key language, no suffix hints, single deltas, silent B-sides — the v3-review discipline held. Two soft notes:

- The model-visible `anomaly` field on 033 says the credit "must be checked against a percentage cap calculated from quarterly spend rows" — it instructs the check. Symmetric across siblings and it reveals no answer, so not a leak; but it lowers difficulty and partially explains why V6 bit at 1/3 where V4's thinner packets bit at 3/3. Decide deliberately whether the atlas wants instructed-check or discovered-check packets; don't mix them within a comparison.
- **Heavy non-KNEW is a term-gate artifact on computed seams:** 5 of 6 probes on 032/033/034 failed KNEW while getting verdicts right, almost certainly because the KNEW terms demand computed values (5,025 / 33,500) that appear in no document. A model can be correct without reciting intermediates. Recalibrate KNEW for computed seams to accept either the inputs or the decision values — otherwise the non-KNEW channel goes back to being noise.

## 4. Does the evidence support "verification-affordance overblocking"?

**The strong version is now falsified; a graded version survives.** Falsified: it is not a blanket reflex — documented conversion (031), printed tolerance (032), and paraphrased pressure (011) all produced clean boards. Surviving, on the current evidence:

> Clean-side false-escalation probability rises with computation depth and evidence thinness, and it is **model-idiosyncratic**: V4's thin one-hop packets hit 3/3; V6's richer, instruction-bearing packets hit 1/3, with a different mini failing each pair.

That distributed fragility is precisely the pattern a council architecture claims to fix — no single mini is reliable on clean sides, but the failures don't overlap. It is also the honest caution for the rescue test: a naive escalate-biased aggregation of three minis would do *worse* than any solo on these A-sides (some member always panics). A rescue succeeds only if the Gov/council correctly overrules the paranoid minority — which makes this a real, falsifiable test of governance rather than of redundancy.

## 5. Promotion set for the Holo rescue run (in order)

| # | Pair | Source | Solo evidence | Why |
| --- | --- | --- | --- | --- |
| 1 | **023** (EUR/USD clean side) | V4 | **3/3** false ESCALATE | Strongest bite on record; thin-evidence one-hop FP |
| 2 | **025** (balance arithmetic clean side) | V4 | **3/3** | Second 3/3; different arithmetic species |
| 3 | **020** (authority expiry clean side) | v3 | **2/3** | Bridges V4 and V6 evidence density |
| 4 | **033** (two-hop percentage cap) | V6 | 1/3 | Depth probe; fair as-is |
| 5 | **035** (novation payee change) | V6 | 1/3 | Surface-class diversity (BEC-shaped FP) |

**Exclude 034** until the 18,000/18,000 coincidence is fixed and the pair re-scouted — as built, its A-side escalation is arguably right.

Rescue-run rules (pre-register before any call): run **both siblings** of every promoted pair — a rescue that fixes A by escalating everything will show it on B's ALLOW cousins across the set, and correctness must be required on both siblings to count; verdicts scored post-hoc against the sealed map exactly as in the blind lane; and the framing stays fixed: these packets were *selected for solo failure*, so a successful rescue is directional evidence about the governance mechanism on this seam class — never a comparable error-rate, never benchmark credit, never a public claim.

## Taxonomy ledger updates (preserve all three)

1. FALSIFIED: literal-phrase pressure FP (004-A) — did not survive paraphrase (011: 0 wrong).
2. FALSIFIED: blanket verification-affordance reflex — cured by documented evidence (031) and printed tolerance (032).
3. REFINED: clean-side overblocking is graded by computation depth and evidence thinness, and is model-idiosyncratic (V4 3/3 thin → V6 1/3 rich, disjoint failing models).
