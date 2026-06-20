# ADVERSARIAL REVIEW: Assumptions & Evidence Attack

**Role:** `assumption_and_evidence_attacker`
**Objective:** Attack assumptions, weak evidence, sample/source limits, stale claims, and missing links between monitoring and hospital capacity relief.

To the synthesis author: The following vulnerabilities, evidence gaps, and false assumptions must be explicitly addressed in the final brief to prevent leadership from making decisions based on overclaims.

## 1. The Missing Link: Capacity Relief is Unproven
*   **The Assumption:** Rapid expansion of remote pulse-oximetry will keep lower-risk patients out of inpatient beds and relieve hospital capacity strain.
*   **The Attack:** There is zero evidence in the frozen packet linking remote pulse-ox monitoring to hospital capacity relief. 
    *   Source S9 explicitly states that the packet does not support the claim that this intervention solves capacity strain. 
    *   Source S7 directly undermines the efficacy of remote monitoring, citing a randomized trial that found pulse oximetry was "no better than text check-ins" for home recovery. 
    *   While S3 establishes the severe burden of sepsis (1.7 million adults/year, 350,000 deaths), it provides no evidence that pulse-oximetry mitigates this specific burden.

## 2. Regulatory Overclaims: No Final FDA Approval or Clearance
*   **The Assumption:** The FDA has approved new standards or cleared updated pulse-ox devices that resolve known issues.
*   **The Attack:** The regulatory posture is entirely preliminary. Any claim of "FDA approval" or "final clearance" violates source boundaries (as flagged in the prior turn audit).
    *   S2 is explicitly labeled "Draft, not for implementation, and non-binding." It is a recommendation, not a rule.
    *   S4 is merely a press release stating the FDA "proposes updated recommendations."
    *   S5 is an announcement of an advisory committee meeting to *discuss* premarket study methods and data needs. It is a discussion forum, not a binding regulatory decision.

## 3. Clinical & Equity Vulnerabilities: Device Unreliability
*   **The Assumption:** Pulse oximeters provide reliable, objective data for remote triage.
*   **The Attack:** The packet repeatedly demonstrates that these devices are clinically limited and carry severe equity risks, making them dangerous as standalone triage tools.
    *   S1 explicitly warns that patients "should not rely only on a pulse oximeter" and that symptoms and worsening status matter more.
    *   S1, S2, S4, S5, and S8 all corroborate a critical flaw: pulse oximeters suffer from accuracy differences and are less reliable for individuals with darker skin pigmentation. 
    *   S8 notes that the only reliable alternative is an arterial blood gas test, which is invasive and cannot be done remotely. Relying on pulse-ox for remote triage risks missing silent deterioration in non-white populations.

## 4. Weak, Stale, and Secondary Evidence
*   **The Assumption:** The provided literature constitutes current, clinical proof of efficacy.
*   **The Attack:** The supporting literature in the packet is weak, stale, or non-clinical.
    *   **Stale/Preprint (S6):** The Davies 2020 paper is an older, COVID-era arXiv preprint. It is not peer-reviewed, focuses on ear-canal versus finger testing, and does not represent current clinical proof for general respiratory or sepsis triage.
    *   **Contradictory/Secondary (S7):** Health.com is secondary journalism from 2022. It explicitly highlights conflicting conclusions regarding home monitoring, proving a lack of clinical consensus.
    *   **Consumer-Level (S8):** Verywell Health is a consumer explainer. While it highlights the racial bias in device accuracy, it is not a clinical study or authoritative medical guideline.

**Synthesis Directive:** Do not allow leadership to assume that deploying these devices will clear beds. You must highlight the contradiction in S7, the explicit draft status of S2, and the severe equity/accuracy risks corroborated across S1, S2, S4, S5, and S8.
