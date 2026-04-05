# Holo Whitepaper — Working Draft
**Status:** Outline + seed sections. Not for distribution.

---

## Argument Structure

1. Frontier models at the action boundary face a structural problem.
2. This structural problem does not go away as models improve.
3. Adversarial architecture changes outcomes.
4. **Conclusion:** The right architecture for action boundary decisions is adversarial, not solo.

---

## Evidentiary Discipline

*[Seed section — expand with empirical examples from benchmark runs.]*

The governor enforces a principle called evidentiary discipline: **a verdict must be backed by evidence, not by role pressure.**

In a multi-model adversarial system, each turn is assigned a role. The Assumption Attacker's job is to challenge what the prior analyst concluded. The Edge Case Hunter's job is to find anomalies the routine pass missed. These roles create adversarial pressure — which is the mechanism. But adversarial pressure is only valuable when it produces findings. Pressure without findings is noise.

The evidentiary discipline rule makes this concrete: **an ESCALATE vote without any MEDIUM or HIGH finding does not count toward the majority verdict.** A turn that played an adversarial role, found nothing with evidentiary support, and still voted ESCALATE is not contributing signal — it is contributing persona. The governor filters it out.

This rule has an important asymmetry. It only affects ESCALATE votes, not ALLOW votes. A turn that voted ALLOW with all flags LOW is a meaningful data point: the analyst looked and found nothing. A turn that voted ESCALATE with all flags LOW is a contradiction: the analyst found nothing but escalated anyway. The first reflects a clean payload. The second reflects role pressure overriding analysis.

**Why this matters for false-positive resistance.** The most dangerous failure mode in a trust layer is not a missed fraud — it is a false positive that trains users to ignore escalations. A system that fires on clean transactions loses credibility faster than one that occasionally misses an ambiguous case. Evidentiary discipline is the mechanism that keeps ESCALATE meaningful: it can only win a majority when the models that voted ESCALATE can point to something real.

**Why this does not weaken fraud detection.** In genuine fraud scenarios, the adversarial reactor surfaces real findings. Real findings produce MEDIUM or HIGH flags. Those votes count. The evidentiary discipline rule does not touch them. The only votes it filters are the ones that have no basis in the payload — and those votes should not decide a verdict.

---

## Architecture Description

*[To be expanded — see HOLO_SYSTEM.md for current canonical description.]*

- Static governor (algorithmic, not learned)
- LLMs randomized per session (not rotating — model assignment shuffled each run)
- Full raw state (no summarization, no lossy compression between turns)
- No synthesis turn (final verdict computed by governor, no LLM anchors it)
- Decay detection
- Oscillation detection
- Evidentiary discipline (majority vote filtered by finding quality)

---

## Sections Still Needed

- Benchmark methodology (six-gate rubric, four-case structure)
- Empirical examples (003A and Scope Creep full turn traces)
- Failure mode taxonomy (condensed Blindspot Atlas)
- The capability vs. architecture argument
- Objections and rebuttals (see reseed doc Section 11)

