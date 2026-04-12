# Editorial Notes for CC — Whitepaper V2.0

April 12, 2026

---

## Global Notes First

The paper has one recurring problem: it occasionally explains things twice. The action boundary concept is introduced in the Executive Summary, then again in 1.2, which is correct — but some of the language is nearly identical across both. The reader who reads straight through will feel the repetition. The fix is not to cut one of them. It is to make the Executive Summary version feel like a preview and the 1.2 version feel like the full arrival. Right now they feel like the same sentence said twice.

The paper is also slightly defensive in places where it does not need to be. The objections section handles skepticism well and in the right place. But some earlier sections pre-apologize before the reader has raised the objection. Cut the pre-apologies. Let the objections section do that work.

Overall tone is right. Educational without being condescending. Serious without being bloodless. The conclusion is the best paragraph in the paper.

---

## Section by Section

### Executive Summary

The opening three paragraphs are excellent. Do not touch them.

**Issue:** The "Holo Engine in one sentence" block contains two sentences that say nearly the same thing back to back:

> "Holo Engine ensures every AI transaction is intentional by intercepting actions at the last reversible moment before execution and determining whether they are authorized, contextually coherent, and safe to carry out."

> "Holo Engine is a runtime trust layer that sits at the action boundary of agentic workflows, intercepting irreversible AI-initiated actions and returning ALLOW or ESCALATE before execution proceeds."

**Fix:** Keep the first sentence as the human-language version. Move the second sentence to Section 1.6 where it belongs as the technical definition. The callout box should contain one sentence only.

**Issue:** The domain table in the Executive Summary is repeated almost identically in Section 9.1. Pick one location. The Executive Summary version is fine as a quick orientation. The Section 9.1 version adds the attack class descriptions which are more useful. Suggestion: keep a simplified version in the Executive Summary, keep the full version in 9.1, and make sure they do not look identical.

---

### Section 1.1 — The Agentic Transition

Clean. No changes needed. The line "Helpful, accurate, and responsive is not the same as safe at the action boundary" is one of the best lines in the paper. Do not move it or bury it.

---

### Section 1.2 — The Action Boundary

This is now the conceptual center of the paper and it reads that way. The rhythm is right.

**Issue:** The governing sentence "Ensuring every AI transaction is intentional" appears here in bold as a standalone line. It also appears at the bottom of the Executive Summary and again in the Conclusion. Three appearances is correct. But make sure the formatting is consistent across all three. Right now it appears to be formatted differently in each location. Standardize it.

---

### Section 1.3 — The Capability Horizon

This section is doing important work and the Glasswing framing is disciplined and defensible. The disclaimer note at the end is exactly right and should stay.

**Issue:** The paragraph beginning "That strategy is appropriate today. It will not be sufficient indefinitely." is strong. But the following paragraph — "AI capability at this level will not remain concentrated..." — slightly repeats the same point. Tighten to one paragraph that makes the proliferation argument once, cleanly.

**Suggested tightening:**

> That strategy is appropriate today. It will not be sufficient indefinitely. Mythos-class capability will not remain concentrated. As it proliferates to open-weight models, gating access will cease to be a viable security strategy. The paradigm must shift from restricting who has the model to governing what the model can do at the moment of execution.

Then go straight to the Glasswing validation line and the note. Cut the redundant middle paragraph.

---

### Section 1.4 — The Gap Nobody Filled

Excellent. The line "what would have to be true for this to be wrong" is the clearest articulation of Holo's adversarial logic in the paper. Consider whether this line should appear somewhere more prominent — possibly the architecture section or the objections section — because it is doing more explanatory work than its current location suggests.

No cuts needed here.

---

### Section 1.5 — The Real Stakes

Strong. The line "They only need to fool the agent" is sharp and should stay exactly as written.

**Minor issue:** The citation to Lynch et al. appears here as a parenthetical. It is also cited in the References. Make sure the inline citation format is consistent with how other citations appear throughout the paper. Right now some citations are inline and some are footnote-style. Pick one format and apply it consistently throughout.

---

### Section 1.6 — What Holo Is in Plain Terms

**Issue:** This section opens with the technical definition sentence that should have been moved here from the Executive Summary callout box. Once that move is made, this section will open correctly.

The airport security analogy is good. The "semantic policy decision point" language is useful for technical readers but may land as jargon for a CFO. Consider adding one plain-English translation immediately after: something like "in plain terms, a checkpoint that evaluates whether the action makes business sense, not just whether it follows a rule."

The deterrence paragraph is important and often overlooked in security products. Keep it.

---

### Section 1.7 — The Symmetric Arms Race

This section is slightly redundant with 1.5. Both make the point that adversaries have access to the same models.

**Fix:** Either merge 1.5 and 1.7 into one section, or sharpen the distinction. 1.5 is about the structural vulnerability of the agent-as-proxy. 1.7 is about the arms race dynamic and why the architecture scales with the threat. Those are different enough to keep separate — but the current versions blur together. Make the distinction explicit in the opening line of 1.7. Something like: "The structural vulnerability described above is not static. It compounds."

---

### Section 2 — Methodology

Clean and well-structured. The six-gate publication standard table is one of the most credibility-building elements in the paper. Do not cut it or move it.

**Minor issue:** Section 2.1 is titled "The Governing Design Rule" but only contains one paragraph. Either expand it slightly or fold it into the methodology introduction. A one-paragraph section with a header feels thin.

**Issue:** The four-case structure table uses "Gap case" as the primary proof artifact. But in the paper's narrative, the flagship cases are called "Gap Case" in Domain 1 and "Gap Case" in Domain 2. Make sure the terminology is consistent throughout.

---

### Section 3 — Domain 1

The setup for BEC-EXPLAINED-ANOMALY-001 is the best writing in the paper. The detail about Q1 2024 and Q1 2025 having no true-up line item is the kill shot and it lands correctly.

**Issue:** The precision cases section is slightly abrupt after the richness of the flagship case setup. The three FP cases are presented as a table with one-line descriptions. That is fine for scannability, but the closing line — "These results matter as much as the gap case" — deserves slightly more support. Add one sentence explaining why false positive discipline matters operationally. Something like: "A system that only escalates will be routed around. Precision is what makes escalation meaningful."

---

### Section 4 — Domain 2

The setup is good but slightly less vivid than Domain 1. The detail about the January 8 last human review date is the right kind of specific. The 83-days-without-oversight line in the Holo description is strong.

**Issue:** The result table shows Gemini returning ESCALATE correctly while GPT and Claude miss. This is a different pattern than Domain 1 where all three solo models missed. That difference is actually interesting and worth one sentence of acknowledgment — something like: "Unlike Domain 1, Gemini caught this case. The coverage gap is not symmetric. That is the point." This sets up Section 5 more cleanly.

---

### Section 5 — Coverage Gaps Across Models

This is the analytical heart of the paper and it is well-executed. The three failure mode descriptions — Detection Failure, Persuasion Failure, Self-Correction Failure — are the clearest taxonomy in the paper.

**Issue:** The section currently focuses entirely on Domain 1 failure modes. Domain 2 is mentioned in the opening paragraph but the failure mode analysis does not extend to it. Either add a brief Domain 2 failure mode analysis or acknowledge explicitly that the detailed failure mode taxonomy is Domain 1 specific and will be expanded as domains complete.

**The line "A solo model cannot be both the skeptic and the believer at the same time" is the single best articulation of the architectural thesis in the paper.** It should be pulled into the Executive Summary or the architecture section as a standalone line. It is currently buried in Section 5 where fewer readers will reach it.

---

### Section 6 — Architecture

Solid. The governor-as-judge framing is clean. The patrol route analogy for randomized assignment is good.

**Issue:** Section 6.5 on Full Raw State and Section 6.6 on No Synthesis Turn are both making the same underlying point: the architecture is designed to prevent information loss and anchoring bias between turns. Consider merging them into one section titled something like "State Integrity" with two sub-points.

**Issue:** The line "It is a judge, not a participant" is excellent but it is currently the closing line of 6.4. It deserves more prominence. Consider making it a standalone callout or moving it to close the entire architecture section.

---

### Section 7 — Objections

This is the strongest section in the paper after the conclusion. The decision to lead with "Yes. This is a vendor-built benchmark" is exactly right. It disarms the most dangerous objection before the reader can raise it.

**Issue:** The objection "Why wouldn't the frontier labs just build this themselves?" contains the line "It is not a criticism of any lab. It is simply not their business." Cut "It is not a criticism of any lab" and let the structural argument stand on its own.

**Issue:** The objection "What stops a competitor from copying this?" is answered well but ends with the Atlas argument. Consider adding one sentence: "The research program also compounds in ways that depend on domain expertise, scenario design judgment, and calibration work that cannot be replicated by copying the reactor alone."

---

### Section 8 — The Blindspot Atlas

Short and correct. The three compounding functions are well-stated.

**One addition:** Add a sentence about what the Atlas eventually becomes for the labs themselves. Something like: "Over time, the Atlas may become useful to the labs themselves as a structured map of attack-class-specific failure patterns that are difficult to surface through generic benchmark suites."

---

### Section 9 — What Comes Next

The domain roadmap table is clean. The line "Independent replication of the solo conditions is encouraged. If your results differ from ours, we want to know" is excellent. Keep it exactly as written.

No changes needed.

---

### Section 10 — Limitations

This section is doing exactly what it should. The opening line — "We state these directly because a trust product that hedges its own limitations is not a trust product" — is one of the best lines in the paper.

**Issue:** The governor tuning limitation is the most important one and it is currently last. Consider moving it up. The order should roughly reflect severity of the limitation, not the order in which they were discovered.

**Issue:** The precision case calibration note about the Domain 2 false positive fix is appropriately transparent. But the current language — "Documented here to provide a transparent record of calibration, not just final results" — is slightly defensive. Cut that last clause. The documentation speaks for itself.

---

### Conclusion

Do not change a word. This is the best paragraph in the paper.

> "The benchmark is how we learned where the ambushes are. Holo is how we make sure your agents never walk into one."

> "Ensuring every AI transaction is intentional."

Both land correctly. The human detail at the end — the small business owner, the employee, the company — is the right emotional close for a paper that has been technical throughout. It earns the feeling without manufacturing it.

---

## Summary of Priority Changes for CC

In order of importance:

1. **Move the second "Holo Engine in one sentence" definition** out of the Executive Summary callout box and into Section 1.6 where it belongs as the technical definition.

2. **Pull "A solo model cannot be both the skeptic and the believer at the same time"** into a more prominent location. It is the best articulation of the architectural thesis and it is currently buried.

3. **Tighten Section 1.3** by cutting the redundant proliferation paragraph.

4. **Merge Sections 6.5 and 6.6** into one State Integrity section.

5. **Add one sentence to Domain 2** acknowledging that Gemini caught it while GPT and Claude missed, and note that asymmetric coverage gaps are the point.

6. **Move the governor tuning limitation** to the top of Section 10.

7. **Cut "It is not a criticism of any lab"** from the labs objection. The structural argument does not need the softening.

8. **Add the Atlas-as-useful-to-labs sentence** to Section 8.

9. **Standardize citation format** throughout. Pick inline or footnote and apply consistently.

10. **Standardize the formatting of "Ensuring every AI transaction is intentional"** across all three appearances.

The paper is ready to send after these changes. None of them are structural rewrites. They are precision edits on a paper that is already doing what it needs to do.
