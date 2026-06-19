# Artifact Benchmark Mandate

Mandate ID: `ARTIFACT_BENCHMARK_MANDATE_V1`

Purpose: compare solo recursive artifact generation against Holo Governor-orchestrated adversarial artifact generation under the same brief, source context, role sequence, turn budget, and rubric.

Core metrics: `loop_uplift` and `holo_advantage`.

Governor doctrine: the Governor creates a Gov mission packet with current best state, new learnings, highest-value flaw, source context anchors, next-role objective, constraints, open tensions, and convergence target. The source context remains the truth base. The mission packet is the steering layer.

Gov artifact-validity doctrine: deterministic validity gates run before qualitative selection. A final artifact that is missing, empty, truncated, outside the word band, contaminated with internal process labels, missing a brief-required disclaimer, or citing source IDs outside the provided context is not selectable for clean benchmark scoring. Technical density cannot rescue an invalid deliverable. If the richer candidate fails validity and a complete candidate passes, Gov selects the complete candidate; if neither passes, Gov must require a surgical repair/merge and the run remains diagnostic.

Gov repair doctrine:

- Incomplete artifact is automatic fail.
- Specificity is not enough; Gov must ask whether the artifact is technically richer and complete, readable, source-grounded, and client-ready.
- Gov maintains a repair ledger: `open issue -> repaired -> regressed -> still missing`.
- Hidden-failure probes are mandatory: what assumption would a practitioner reject, what field is missing from the audit trail, what decision cannot be coded, what source claim is actually inference, and what would compliance/risk/domain ownership block.
- Model judgment is separated from deterministic gates. Code checks word count, ending completeness, required sections, unknown source IDs, internal process labels, and disclaimer presence before Gov quality selection.
- Judge rationales can be used as feedback for future runs, but not leaked into blinded judging for a run already in progress. Preserve winning features unless they violate source grounding or validity gates.

Judges see brief, source context, deliverable spec, rubric, and anonymized Document X / Document Y. Judges do not see model names, provider names, condition labels, traces, Governor mission packets, or identity maps.

Diagnostic POC not benchmark credit. Locked benchmark requires frozen context, prompts, model lineup, seeds, traces, judge packets, scoring, and anonymization maps.
