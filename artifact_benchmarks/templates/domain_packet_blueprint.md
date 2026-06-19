# Domain Packet Blueprint

Use this blueprint when creating a new artifact benchmark packet.

## Required Packet Parts

- `report_brief.json`: what the artifact must do.
- `source_pack.json`: frozen facts, source IDs, allowed inferences, and prohibited inferences.
- `role_flow.json`: six turns, same for Holo and solos.
- `gov_protocol.json`: repair ledger, probes, validity doctrine, final selection rule.
- `judge_rubric.json`: eight weighted criteria.
- `judge_panel.json`: three blinded judges.
- `hash_lock.json`: generated only after packet and runner are ready.
- `RUN_FROM_MAC.md`: exact local run commands.

## Packet Design Rules

- Make the scenario complex enough that a polished solo answer can miss buried interactions.
- Give enough source context for a strong artifact, but not so much that the answer is obvious.
- Include tensions that require synthesis across operations, risk, compliance, implementation, and communication.
- Require source IDs inline.
- Include explicit domain disclaimers.
- Forbid domain-specific advice where appropriate.
- Require all final artifacts to be similar in length.
- Preserve the same turn budget for all conditions.

## Hidden Failure Targets

Each packet should include five to eight hidden failure targets. These are not hidden from Holo; they define what Gov and judges should care about. They are not answer keys. They are pressure points.

Examples:

- A practitioner would reject the core assumption.
- A source claim is actually inference.
- The artifact cannot be operationalized.
- Compliance would block the decision.
- The audit trail lacks required fields.
- The artifact optimizes the wrong metric.
- A final section is missing or incomplete.

## Freeze Sequence

1. Draft scenario skeleton.
2. Build source pack from current primary sources.
3. Build report brief and role flow.
4. Build Gov protocol and judge rubric.
5. Run no-provider smoke.
6. Generate hash lock.
7. Run live only from an approved environment.
8. Run inspector, analyzer, and full autopsy.
9. Decide whether the run can be claim-supporting.

Do not reuse judge feedback from one run inside another frozen packet unless it is explicitly declared as prior-run design learning and appears in all conditions equally.
