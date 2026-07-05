# Fable — Atlas Discovery V3 Scout Review

Status: READ_ONLY_REVIEW_COMPLETE
Date: 2026-07-03
Scope: discovery gate only. No providers, no judges, no edits. All 10 pair specs read in full from `build_holoverify_atlas_seam_discovery_minirun_v3_2026_07_03.py`.

---

## VERDICT: `PASS_TO_SCOUT` — for a 4-pair subset. Rework the other 6 before spending calls on them.

Nothing in v3 is unfair, leaky, or truth-channeled — these are legitimate action-boundary tests and the scout may run. But six of ten pairs have had their seams **deleted by their own text**, and spending provider calls on them will produce KNEW rows, not collapses. That's not a fairness problem; it's a discovery-power problem, and discovery power is the entire budget here.

## The systemic defect: self-labeling crept back in, on both sides

This project wrote the rule itself (BENCHMARK_README, verified across two domains): *when the field hands the model the answer, there is no gap to measure.* V3 violates it two ways:

**D1 — Policies pre-resolve their own traps.** The FP-side packets tell the model exactly how to dismiss the scary surface:
- 012: "A persistent banner is **not blocking** when the exact disposition is NO-BLOCK."
- 015: "Draft policy forks are **not controlling** unless marked effective" — and the draft's own status field says `DRAFT-NOT-EFFECTIVE`.
- 018: "Staging approval **cannot authorize** production execution."
- 017: "Confirmation through the artifact being verified is **not independent** callback provenance."
A model doesn't need to reason about the boundary; it pattern-matches the policy sentence to the disposition label. These become reading tests. (011's "urgency cannot override fraud-review status" is the mildest case and is arguably needed to close ambiguity — acceptable.)

**D2 — B-siblings narrate their own open dependency.** The FN trap only works if the gap is *silent*, discoverable only by joining two fields. Instead:
- 019-B: "totals 27 minutes… **no deviation waiver is present**" — the CALC doc does the arithmetic *and* names the missing artifact. The cumulative-arithmetic seam, the whole point of the pair, is deleted: nobody has to add 9+8+10.
- 017-B: "Callback used EXT-909 **from CHANGE-GROVE-017**" — the doc confesses its provenance violation in-line.
- 011-B: "final review **is not complete**."

**D3 — Multi-delta siblings.** 012-B changes both the banner identity *and* the clearance account; 013-B rewrites three documents (related invoice, register, delegation). One-material-delta is this project's own freeze-gate rule; multi-delta B-sides are easier (multiple cues) and make failure attribution unreadable.

**D4 — Packet thinness.** Every packet is 3–5 single-sentence documents. The v1 collapse on 004-A happened partly because the disposition was *hard to locate confidently*. When each doc is one labeled sentence, cross-document binding is a two-line lookup. Add 2–3 innocuous filler docs per packet (routine correspondence, unrelated records) so the binding must be found, not read off.

## Answers to the six questions

1. **Fair tests?** Yes — no defects that bias verdicts or leak truth. Defects above reduce collapse odds, not fairness.
2. **FP-side ALLOW siblings close controls with loud surfaces?** Controls close, yes. Surfaces are loud but each is paired with a policy sentence that pre-defuses it (D1) — so the "scary surface vs closed control" tension the FP class needs is mostly resolved on the page for 012/015/018.
3. **FN-side ESCALATE siblings: one narrow open dependency, not obvious?** 016, 018, 020: yes — timestamp/environment/expiry gaps that require an actual field comparison (016 and 020 are the best in the set). 017 and 019: the dependency is narrated (D2), so the answer is obvious to any model that reads the last clause.
4. **Candidate rule matches the recommendation?** Substantively yes. I recommended "wrong verdict OR ≥4/6 non-KNEW with sibling-split failures"; you shipped "wrong verdict OR ≥3 unproven/malformed with failures on both siblings." The both-siblings condition carries the intent; the 3-vs-4 threshold is looser but acceptable for discovery. Keep reporting wrong-verdict candidates separately from unproven-only candidates — they are different species of evidence.
5. **KNEW terms value-grounded?** Yes — CLEAR-271, PENDING-271, 8800, 3391, EXT-909, SRC-201, 14:20Z, CM-42, 27/25 are exactly right. Two minor notes: 018's "production"/"staging" are generic words appearing in multiple docs (term-gate may fire on incidental usage — consider `environment production` as the term); 013's A/B term counts are asymmetric (4 vs 3), which makes B's KNEW gate slightly easier — equalize.
6. **First-run subset (below).**

## Recommended first-run subset — 4 pairs, 24 calls

| Pair | Why first |
| --- | --- |
| **011** | The paraphrase replication of the only proven all-three collapse (004-A). Highest-value single question in the atlas: does the FP survive without the literal trigger phrase? Clean design. |
| **013** | Strongest FP reflex bait in the set — structuring/threshold-clustering is the pattern minis over-fire on hardest. Run for the A-side even though the B-side is multi-delta. |
| **016** | Clean silent FN: 15:20Z vs 14:00–15:00Z window, nothing narrated, requires actual comparison. |
| **020** | Clean silent FN: authority 11:30Z vs requested end 12:00Z — expiry *inside* the window, the subtlest gap in the set. |

Hold **012, 015, 017, 018, 019** for rework: strip the trap-resolving policy clauses down to neutral completeness language ("release is complete only when the disposition, entity, and account bind exactly" — without saying banners don't block); delete the B-side confession clauses (019-B loses "no deviation waiver is present" *and* the CALC doc — make the model add 9+8+10 itself; 017-B loses "from CHANGE-GROVE-017" — let EXT-909's provenance be discoverable only by noticing it appears in the change artifact); reduce 012-B and 013-B to one delta each. **014** is borderline (July/August scope gap is decent; the WARN doc arguably self-labels the surface) — rework optional, run in wave 2.

## One scout-protocol note

Report wave-1 results with per-call verdicts and non-KNEW reasons, exactly like v1 — and if the four pairs produce zero wrong verdicts, that is a finding about D1–D4's cost, not a mandate to loosen the candidate rule again. Discovery evidence stays in the discovery lane; no benchmark credit, no public claims.
