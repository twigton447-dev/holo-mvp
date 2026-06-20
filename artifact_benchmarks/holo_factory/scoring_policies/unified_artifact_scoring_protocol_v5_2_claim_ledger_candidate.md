# Unified Artifact Scoring Protocol v5.2 Claim-Ledger Candidate

Status: candidate addendum, not locked.
Purpose: repair v5.1's failure mode where a judge can assign high scores after broad rubric impressions without proving source-to-claim verification.

## Flow Change

v5.1 allowed this flow:

1. read artifact;
2. assign gates, caps, category scores, and pairwise labels;
3. validator checks JSON self-consistency.

v5.2 candidate requires this flow:

1. audit 8-15 major claims per artifact against the frozen source packet;
2. derive source-support defects, caps, gates, and expert ceilings from the claim ledger;
3. assign category scores and final score;
4. validator checks both claim-ledger completeness and score consistency.

No final score is valid unless the claim ledger is complete.

## Mandatory Claim Ledger

For each artifact, the judge must provide `claim_ledger.major_claims` with 8-15 rows. Each row must include:

- `claim_id`
- `claim_text`
- `claim_type`: `factual`, `causal`, `regulatory`, `operational`, `statistical`, `recommendation`, or `source_status`
- `cited_sources`
- `source_support_status`: `supported`, `partially_supported`, `unsupported`, `contradicted`, or `not_in_packet`
- `source_boundary_issue`
- `overclaim_issue`
- `stale_or_limited_evidence_issue`
- `missing_caveat`
- `severity`: `none`, `minor`, `material`, or `fatal`
- `cap_trigger_if_any`

The artifact-level claim ledger must also include:

- `invented_or_false_source_attributions`
- `unsupported_major_claims`
- `source_laundering_findings`
- `negative_space_misses`
- `tempting_but_rejected_claims`
- `avoided_failure_modes`

## Derived Caps And Ceilings

These rules are derived from the claim ledger before the final score is accepted:

- fewer than 8 audited major claims: invalid;
- cited source ID not present in the frozen source packet: cap at 70 or invalid if fatal;
- false source attribution or material source misattribution: cap at 75;
- unsupported major claim material to the recommendation: cap at 82;
- wrong source-status claim: cap at 80, or 75 if material/fatal;
- material negative-space miss: max 83;
- score above 85 requires at least 2 concrete avoided failure modes;
- score above 90 requires at least 3 concrete avoided failure modes and no material source-support defects;
- all-TIE pairwise across every dimension is invalid unless supported by claim-ledger evidence explaining material indistinguishability.

## Pairwise Rule

Pairwise comparison must be derived from the claim ledgers. If every pairwise dimension is `TIE`, the judge must provide `all_tie_claim_ledger_evidence`, listing concrete claim IDs and support statuses showing why the artifacts are materially indistinguishable.

## Design Goal

This candidate does not make the rubric longer for its own sake. It changes the load-bearing evidence step. A judge can still score artifacts highly, but only after showing the source/claim audit that justifies the absence of caps, gates, and ceilings.
