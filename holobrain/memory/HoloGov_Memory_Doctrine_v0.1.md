# HoloGov Memory Doctrine

Version: `0.1`
Status: `locked`
Effective date: `2026-06-25`
Supersedes: `none`
Superseded by: `none`
Source of truth: this file

## Scope

HoloBrain is the overarching memory and intelligence infrastructure for HoloGov-C, HoloGov-B, and HoloGov-V.

HoloGov-C, HoloGov-B, and HoloGov-V all use the shared HoloBrain framework with lane-specific fidelity rules.

## Core Principle

HoloGov-C, HoloGov-B, and HoloGov-V share one memory framework, but use different fidelity policies.

HoloGov-B and HoloGov-V are near-lossless at the reference and audit layer, not at the prompt-injection layer.

## Shared Memory Framework

All lanes use the same object families:

- `state_object`: current goal, constraints, settled decisions, unresolved issues, and active artifacts.
- `policy_object`: formal rules, controls, standards, and supersession metadata.
- `case_experience`: encountered cases, failures, repairs, resolutions, and lessons.
- `artifact_ref`: path, URI, and hash pointer to full substrate.
- `state_audit`: what was retrieved, injected, relied on, rejected, or superseded.

The prompt receives compact operational slices. The full corpus remains pinned, hashed, retrievable, and auditable.

## Lane-Specific Fidelity

### HoloGov-C

HoloGov-C is compact by default.

Lossless retention is required only for explicit user instructions, critical constraints, settled decisions, privacy boundaries, and pinned artifact references.

### HoloGov-B

HoloGov-B is near-lossless for source references, artifact versions, requirement closure, claim maps, validation gates, rejected findings, repair notes, and final artifact audits.

Working notes and role chatter may be compressed when full artifact references and audit records remain intact.

### HoloGov-V

HoloGov-V is near-lossless for proposed action, authority rules, required controls, evidence references, verdict basis, blocker ledger, allow ledger, flip condition, and decision audit.

Summaries may route attention, but they must not become the evidence basis for `ALLOW` or `ESCALATE`.

## Policy Corpus

Formal policy lives outside runtime memory:

```text
holo_policy_corpus/
  policies
  policy_versions
  policy_clauses
  policy_supersession_edges
  policy_domain_bindings
  policy_retrieval_events
  policy_injection_events
```

Policy retrieval filters by lane, domain, action or artifact type, effective date, authority level, and supersession state.

HoloGov-B and HoloGov-V inject compact operative clauses and source IDs. Full policy documents remain referenced substrate.

## Case Memory

Case memory sits beside policy, not inside it:

```text
holo_case_memory/
  case_experiences
  case_artifact_refs
  case_findings
  case_resolution_steps
  case_supersession_edges
  case_retrieval_events
  case_injection_events
```

`case_experience` objects must include:

```json
{
  "case_id": "string",
  "lane_scope": ["HoloGov-B", "HoloGov-V"],
  "domain": "string",
  "case_type": "real_interaction|packet_run|benchmark_run|diagnostic|production_case",
  "confidence": "low|medium|high|locked_artifact_backed",
  "summary": "compact",
  "trigger_pattern": ["compact"],
  "failed_approaches": ["compact"],
  "successful_resolution": "compact",
  "decision_lessons": ["compact"],
  "scope_limits": ["where this lesson does not generalize"],
  "non_generalization_conditions": ["conditions that block reuse"],
  "related_policy_refs": ["policy_id#clause_id"],
  "evidence_refs": ["artifact refs only"],
  "status": "active|superseded|retired|quarantined"
}
```

Case memory can guide attention. It cannot authorize action unless tied back to formal policy or pinned evidence.

## Authority Ladder

```text
formal policy
> locked artifact-backed case
> repeated empirical pattern
> single diagnostic note
> anecdote
```

Case memory remains below formal policy. A case lesson may sharpen retrieval and review, but it must not silently become authority.

## Live Injection Versus Referenced Substrate

Inject live:

- Current state object summary.
- Applicable operative policy clauses.
- Top relevant case lessons.
- Scope limits and non-generalization warnings.
- Required checks and citation obligations.

Keep referenced only by default:

- Full policies.
- Full packets.
- Full traces.
- Full transcripts.
- Full model outputs.
- Judge outputs.
- Raw logs.
- Historical superseded material unless needed.

## Pruning And Supersession

Supersede when later policy, stronger case evidence, or a better-scoped lesson replaces an older one.

Prune from active retrieval when a policy or case is stale, low-confidence, contradicted, overgeneralized, domain-mismatched, or not linked to policy, artifacts, or repeated outcomes.

Retired material remains auditable by reference, but should not inject by default.

## Future HoloBrain Extraction

HoloBrain should eventually extract structured learning from prior HoloGov-B and HoloGov-V tests as:

- `case_experience` objects.
- Settled decisions.
- Failure patterns.
- Successful resolutions.
- Artifact references.

HoloBrain should not store raw trace dumps as default memory payload. Raw traces should remain referenced substrate unless explicitly promoted into a frozen artifact or audit record.

## Change Rule

Future modifications to this doctrine must create a new version or be explicitly approved by the operator.
