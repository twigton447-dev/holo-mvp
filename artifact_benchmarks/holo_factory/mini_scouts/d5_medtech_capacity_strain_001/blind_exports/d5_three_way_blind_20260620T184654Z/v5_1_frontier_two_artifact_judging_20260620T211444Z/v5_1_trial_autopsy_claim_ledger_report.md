# v5.1 D5 Provider-Judge Trial Autopsy and Claim-Ledger Fix Candidate

## Scope

This is a no-provider, no-unblinding autopsy of the v5.1 D5 two-artifact scoring trial in:

`artifact_benchmarks/holo_factory/mini_scouts/d5_medtech_capacity_strain_001/blind_exports/d5_three_way_blind_20260620T184654Z/v5_1_frontier_two_artifact_judging_20260620T211444Z/`

The review used only anonymous artifact labels, the accepted and failed judge outputs, the v5.1 validator result, and the frozen judge-visible packet. The anonymization map was not accessed.

## Trial Outcome

- Accepted judge output: `heldout_xai_grok_4_3`, accepted after one repair.
- Failed judge output: `heldout_minimax_m3`, failed after one repair.
- Accepted scores: `ARTIFACT_001 = 89`, `ARTIFACT_003 = 89`.
- Accepted pairwise result: all pairwise dimensions `TIE`.
- Accepted caps/ceilings/gates: no hard caps, no expert ceilings, no failed gates.

## Why v5.1 Accepted The 89/89 Tie

The v5.1 validator enforced structural and self-consistency rules, but it did not independently verify the judge's source-fidelity conclusions. The accepted repaired xAI JSON passed because:

- `protocol_id` matched v5.1.
- exactly two artifact rows were present: `ARTIFACT_001` and `ARTIFACT_003`.
- raw category scores summed to `89` for each artifact.
- final scores did not exceed raw scores.
- the judge reported no applicable hard caps or expert ceilings.
- every gate field was set to `true`.
- final scores were below the v5.1 threshold that requires multiple avoided failure modes above 90.
- required defect-audit fields were nonempty after repair, including `material_repairs_required`.
- pairwise fields used exact allowed labels, including `TIE`.

That means the validator checked whether the judge's own JSON was internally coherent. It did not force the judge to prove, claim by claim, that the artifacts' cited sources actually support the claims.

## Did xAI Perform Claim-Level Source Verification?

No. The accepted xAI output is rubric-level impression scoring, not claim-ledger verification.

Signs:

- The same score and near-identical findings were assigned to both artifacts.
- `source_boundary_findings` says only: `All claims tied to listed source IDs`.
- `unsupported_or_weak_claims` says only: `Older preprints and secondary sources correctly labeled weak`.
- `weakest_source_to_claim_link` says only: `S7 secondary journalism used only for conflict signal`.
- No major claims are enumerated.
- No claim text is mapped to cited source IDs.
- No cited source is classified as supported, partially supported, unsupported, contradicted, or not in packet.
- No source-status claims are separately audited.
- Pairwise all-TIE was accepted without claim-ledger evidence showing material indistinguishability.

The accepted JSON therefore demonstrates that v5.1 can reject malformed scoring JSON, but not that it can force source-fidelity discovery.

## MiniMax Failure Classification

MiniMax's primary output appears substantively more discriminating than the accepted xAI output, but it failed the v5.1 machine contract.

Primary output issues:

- included `<think>` reasoning before JSON, creating unacceptable judge-output hygiene risk;
- used category values that did not match raw score exactly;
- included or triggered an expert-ceiling interpretation that caused `final_score_exceeds_expert_ceiling:83.0`;
- omitted required `material_repairs_required` values for scores above 85;
- nevertheless produced useful comparative findings, including an `ARTIFACT_001` edge over `ARTIFACT_003` for operational specificity.

Repair output issues:

- again included `<think>` text;
- included multiple code-fenced / prose regions;
- produced extra data around JSON, causing `JSONDecodeError: Extra data` after the single allowed repair;
- remained parse-failed, so no MiniMax score was accepted.

Classification: schema difficulty plus over-complex prompt, invalid ceiling/cap handling, missing required fields, and repair-output formatting failure. Pairwise formatting in the primary output was not the main problem; the primary issue was inability to produce clean schema-valid JSON under a complex scoring packet.

## Anonymous Artifact/Source Examples Needing Claim-Ledger Audit

The artifacts are both strong and may be close. The failure is not that v5.1 should automatically punish either one; the failure is that v5.1 cannot prove why no punishment is due.

A claim ledger would force closer review of examples like these:

1. Task-premise citation vs source citation
   - `ARTIFACT_001` uses `TASK_BRIEF` for the capacity-strain premise. `TASK_BRIEF` is not a source ID in the frozen source list. This may be allowed as task context, but the ledger should classify it as task-brief support, not source-packet support.

2. Capacity-pressure attribution to S9
   - `ARTIFACT_003` says the hospital system is under respiratory/sepsis capacity pressure and cites `S9_DERIVED_EVIDENCE_PRESSURE_TABLE`. The S9 excerpt says the table separates source support and frames adopt/pilot/delay/reject under uncertainty; the crisis premise comes from the task brief. This is at least a partial source-to-claim mismatch that a ledger should classify.

3. Operational recommendation support
   - Both artifacts recommend pilots with escalation, subgroup monitoring, outcome tracking, and stop/revise/scale logic. Those may be sensible inferences from S1/S2/S4/S5/S9, but they are not directly stated as operational protocols in the sources. A ledger should mark them as `partially_supported` or `inference_from_limits`, not full source support by default.

4. FDA draft/advisory/press status
   - Both artifacts correctly say FDA draft guidance is draft, non-binding, and not final approval. A ledger should record these as source-status claims and avoided failure modes, not simply roll them into a broad `no overclaim` impression.

5. Weak or stale evidence handling
   - S6 is an older arXiv preprint; S7 is secondary journalism reporting conflict; S8 is a consumer explainer. Both artifacts appear to bound these sources. A ledger should still explicitly verify that no claim upgrades S6/S7/S8 into decisive current evidence.

6. Negative-space limitations
   - The key negative-space limitation is that the packet does not prove admission reduction, mortality reduction, or capacity relief. Both artifacts state this. A ledger should require every recommendation to carry that limitation through to stop/go logic, not just mention it once.

## Root Cause

v5.1 failed for both judge behavior and validator weakness.

Judge behavior:

- xAI gave high-level rubric impressions and did not audit claims.
- MiniMax did more analytic work but could not satisfy the output contract.

Validator weakness:

- The validator can reject schema inconsistency but cannot detect undiscovered source defects.
- It trusts judge-reported caps/gates.
- It allows all-TIE pairwise output if labels are valid, even without evidence that the artifacts are materially indistinguishable.
- It does not require claim-level source support statuses before final scores.

## Required Fix

Replace the scoring flow:

`read artifact -> assign score`

with:

`audit claims against frozen sources -> derive caps/gates/ceilings -> assign score`

The proposed candidate is `unified_artifact_scoring_protocol_v5_2_claim_ledger_candidate`. It is not a longer rubric. It is a mandatory pre-score claim ledger that must be completed before scoring.

## Recommendation

v5.1 should not be locked for future domains. It should be replaced by a claim-ledger v5.2 candidate before any future domain scoring. The claim-ledger candidate should be trialed no-provider first, then with providers only after the JSON contract is simplified enough that at least two held-out judges can return accepted outputs.
