# CLAIM DISCIPLINE & OVERCLAIM REDUCTION REVIEW
**Role:** claim_discipline_overclaim_reducer
**Turn:** 5
**Objective:** Eliminate unsupported claims, explicitly bound overclaim risks (especially regarding FDA approval and capacity relief), and establish strict constraints for the final 900–1,300 word synthesis brief.

To the synthesis author: Previous turns triggered audit failures for contradicting source boundaries regarding "final approval." You must exercise extreme claim discipline. Do not write beyond the frozen evidence. 

## 1. EXACT OVERCLAIM RISKS TO ELIMINATE (The "Do Not Say" List)

**Overclaim Risk A: "The FDA has approved/cleared new guidelines or devices."**
*   **The Reality:** The packet contains zero evidence of final FDA approval, clearance, or finalized new regulatory standards. 
*   **Required Discipline:** You must explicitly state that the FDA guidance is "draft, not for implementation, and non-binding" (S2_FDA_DRAFT_GUIDANCE_2025). The FDA press release only "proposes updated recommendations" (S4_FDA_PRESS_RELEASE_2025), and the 2024 advisory meeting was a discussion of premarket study methods and ongoing concerns, not a binding decision (S5_FDA_ADVISORY_MEETING_2024). 

**Overclaim Risk B: "Remote pulse-oximetry will solve or relieve hospital capacity strain."**
*   **The Reality:** The packet establishes that the hospital is under capacity strain (TASK_BRIEF), but it provides *no evidence* that remote pulse-oximetry safely reduces admissions or preserves beds. 
*   **Required Discipline:** You must state that the capacity-relief hypothesis is unproven by the packet. The only direct trial evidence cited found that pulse oximetry was "no better than text check-ins" for monitoring recovery (S7_HEALTH_HOME_PULSE_OX_CONFLICT_2022).

**Overclaim Risk C: "Remote pulse-oximetry safely detects sepsis deterioration."**
*   **The Reality:** Sepsis is a severe threat causing at least 350,000 deaths annually (S3_CDC_SEPSIS_CONTEXT_2026), but no source links remote SpO2 monitoring to early sepsis detection. 
*   **Required Discipline:** You must separate the *context* of the crisis (sepsis strain) from the *capabilities* of the device. Furthermore, you must cite the FDA's explicit warning that "patients should not rely only on a pulse oximeter; symptoms and worsening status matter" (S1_FDA_PULSE_OX_PAGE_2025).

**Overclaim Risk D: "Arterial Blood Gas (ABG) is a viable operational alternative for remote triage."**
*   **The Reality:** The packet only notes that ABG is an "invasive alternative" (S8_VERYWELL_LIMITED_EXPLAINER_2024). 
*   **Required Discipline:** Do not present ABG as a practical, scalable solution for remote home monitoring or capacity relief.

## 2. CLAIM DISCIPLINE FOR WEAK, STALE, AND CONTRADICTORY EVIDENCE

You must explicitly bound the following sources in the "weak, stale, or contradictory evidence" section of your brief:
*   **S6_DAVIES_ARXIV_EAR_OX_2020:** Must be labeled as an older (2020), COVID-era *preprint*. It is not peer-reviewed clinical proof and cannot be used to justify current adoption.
*   **S7_HEALTH_HOME_PULSE_OX_CONFLICT_2022:** Must be highlighted as the primary source of *contradictory* evidence, showing conflicting conclusions about whether home SpO2 monitoring is actually better than simple text check-ins.
*   **S8_VERYWELL_LIMITED_EXPLAINER_2024:** Must be framed as consumer health journalism. It is useful for understanding public/patient communication challenges regarding racial bias in devices, but it is not primary clinical or regulatory evidence.

## 3. FINAL BRIEF CONSTRAINTS & FORMATTING

To ensure the final artifact passes all system gates, the synthesis author must adhere to the following structural and length constraints:

*   **Word Count Gate:** The final brief body must be strictly between **900 and 1,300 words**. Target exactly 1,100 words. If your draft exceeds 1,300 words, you must edit it down before finalizing.
*   **Mandatory Sections:** You must include all 10 sections explicitly requested in the TASK_BRIEF:
    1. What is happening
    2. Why it matters now
    3. Strong evidence
    4. Weak, stale, or contradictory evidence
    5. Calculations or data interpretation that matter
    6. Practical response options (Adopt, Pilot, Delay, Reject - *Note: "Adopt" must be framed as unsupported by current evidence per S9_DERIVED_EVIDENCE_PRESSURE_TABLE*)
    7. Risks of acting
    8. Risks of waiting
    9. Practical next steps
    10. Claim boundaries and disclaimer
*   **Citation Format:** Every factual claim must be followed by its exact source ID in parentheses (e.g., S1_FDA_PULSE_OX_PAGE_2025).
*   **Mandatory Disclaimer:** You must paste the exact disclaimer provided in the TASK_BRIEF verbatim at the end of the document.
