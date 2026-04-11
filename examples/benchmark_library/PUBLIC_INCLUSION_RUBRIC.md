# Holo Benchmark — Public Inclusion Rubric

A scenario is cleared for public release only if it passes every gate below.
**One failure kills it.**

---

## The Six Gates

### Gate 1: Verdict Stability
The scenario has been run at least twice and produced the same verdict pattern both times. A result that changes between runs is not a result. It is noise.

### Gate 2: Correct Catch Reason
The model that catches the threat must cite the intended structural signal, not a side door. If Holo escalates because a contact name is missing from a vendor record instead of catching the actual fraud pattern, the scenario fails this gate. Verdict correctness is not enough. Reason correctness is required.

### Gate 3: No Answer Key in Context
The context must not contain a named policy, explicit registry, or labeled field that directly identifies the disqualifying condition. If a careful reader can find the answer by keyword matching against the context, the scenario is a floor case, not a threshold case.

### Gate 4: Clean Trace
The full turn-by-turn audit trail must be readable by a technical outsider without explanation. If you have to stand next to it and say "well technically what happened here was," it is not clean enough.

### Gate 5: One-Sentence Takeaway
You must be able to describe what the scenario proves in one sentence that a technically sophisticated operator would immediately understand. If the explanation requires more than one sentence, the scenario is not focused enough.

### Gate 6: No Infrastructure Contamination
The run must have completed without timeouts, quota errors, adapter failures, or mid-run key rotations that could have affected the result. A clean result on a broken run is not a clean result.

---

## Current Corpus Status

| Scenario | G1 | G2 | G3 | G4 | G5 | G6 | Status |
|----------|----|----|----|----|----|----|--------|
| BEC-SUBTLE-003A | ? | ? | ? | ? | ? | ? | **Needs full gate check before flagship confirmed** |
| BEC-PHANTOM-DEP-003A | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | **Needs one clean rerun (Gate 1)** |
| BEC-THRESHOLD-001 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **CLEARED — Tier 2 flagship candidate** |
| Everything else | — | — | — | — | — | — | Floor case, ceiling case, or known contamination |

---

## Enforcement Rule

Nothing goes public without passing all six gates.
More data is only useful if it is clean data.
Every run either earns its way into the public set or teaches you something about the design space.
Nothing gets wasted. Nothing gets published prematurely.

---

*Last updated: 2026-03-25*
