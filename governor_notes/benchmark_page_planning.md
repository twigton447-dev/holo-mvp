# Benchmark Page — Planning Note
*Internal. Not for publication. April 25, 2026.*

---

## The Decision

The benchmark page will lead with the **Architecture Stability Test** result.
The **Runtime Distribution** is reported separately, below the fold, with a clear label distinguishing it from the architecture result.

The two must never appear in the same paragraph, the same table, or the same summary claim without explicit labels.

---

## Definitions (locked)

**Architecture Stability Test**
A fixed-budget benchmark mode where every seed receives the same turn count and full adversarial pressure. No early convergence exit. Tests whether the architectural result depends on sequence, not convergence timing. The claim it supports: "the catch is a property of the architecture."

**Runtime Distribution**
A production-convergence benchmark mode where the governor exits when the case stabilizes. Some seeds run fewer turns. Characterizes what the deployed system experiences. The claim it supports: "across realistic runtime conditions, X% of sequences produce the correct verdict."

---

## Page Structure Requirements

**Lead section**
- Architecture Stability Test result for the current flagship scenario
- N-of-10 rotation summary with seed table or equivalent visualization
- Documented failure seed with specific diagnosis (not "one miss" — the reason)
- Solo model comparison (symmetric collapse or partial collapse, clearly labeled)

**Separate section**
- Runtime Distribution — labeled explicitly as such
- Reported as a range across independent sessions if multiple runs exist, not as a single number
- Clear statement that this reflects production-convergence conditions and may differ from Architecture Stability Test results

**Separation rule**
Never write "Holo catches this in 9 of 10 runs" without specifying which mode produced that number. The benchmark page must make the mode visible at every point where a number is cited.

---

## Rebuild Gate

**Do not rebuild the benchmark page until the following condition is met:**

BEC-EXPLAINED-ANOMALY-001 has a clean canonical Architecture Stability Test result with:
- All 10 seed integers documented in advance
- A single declared run (not the best of multiple sessions)
- Gate 2 verified for every passing seed (correct catch reason, not just correct verdict)
- Gemini error-handling protocol declared before the run, not after
- Result recorded in the ledger with run timestamp and model versions

The current state: three April 24 proof files showing 9/10, 2/2, and 6/10 from the same code session. No single canonical run exists. The 9/10 file is the best available evidence but has not been reproduced. The 6/10 is from the same session and must be explained, not ignored.

Until a canonical run exists, the benchmark page cannot honestly display a single Architecture Stability Test number. Rebuilding the page before that run would require either cherry-picking the 9/10 or acknowledging the 6-9 range — and neither of those is a clean foundation for a public page.

---

## What the Page Is Not

- Not a leaderboard. No ranking. No score comparison across scenarios.
- Not a marketing artifact that leads with the best number. The number comes with its conditions.
- Not a page that implies one result equals "Holo's performance." One result is one scenario under one attack class.

The page's job is to prove two things: (1) the architecture produces a structural advantage, not a lucky one, and (2) that advantage is inspectable when it fails. Everything on the page serves one of those two proofs or it does not belong on the page.
