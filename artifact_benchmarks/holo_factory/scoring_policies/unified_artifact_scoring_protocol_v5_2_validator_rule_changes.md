# v5.2 Claim-Ledger Validator Rule Changes

Status: proposed candidate rules for `unified_artifact_scoring_protocol_v5_2_claim_ledger_candidate`.

## New Required Pre-Score Object

Every artifact score row must include `claim_ledger`. The validator rejects any artifact score without it.

## Required Claim Count

`claim_ledger.major_claims` must contain at least 8 and at most 15 claim rows. Fewer than 8 audited claims is invalid because the judge has not shown enough source-to-claim coverage to justify a final score.

## Source ID Validation

Every `cited_sources` entry in every claim must be present in `source_packet_source_ids`, unless it is explicitly declared as `TASK_BRIEF` or another allowed non-source context reference. Unknown source IDs trigger `unknown_cited_source_id` and cap or invalidation depending on severity.

## Claim-Derived Caps

The validator derives caps from the claim ledger even if the judge does not list them in `applicable_hard_caps`:

- false source attribution: max 75;
- material source misattribution: max 75;
- unsupported major claim material to recommendation: max 82;
- wrong source-status claim: max 80 or 75 if material/fatal;
- material negative-space miss: max 83;
- fatal not-in-packet source support: max 70.

## High-Score Evidence Requirements

- final score above 85 requires at least 2 concrete avoided failure modes;
- final score above 90 requires at least 3 concrete avoided failure modes;
- final score above 90 fails if any major claim has material/fatal source-support defect.

## Pairwise Tie Rule

If every pairwise dimension is `TIE`, the validator requires `all_tie_claim_ledger_evidence` with at least two concrete entries referencing claim IDs and source-support statuses. Otherwise the all-TIE output is invalid.

## Design Boundary

The validator does not decide which artifact is better. It rejects scoring records that do not prove the judge performed the source/claim audit needed to justify the score.
