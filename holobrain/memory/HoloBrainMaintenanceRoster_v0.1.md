# HoloBrain Maintenance Roster

Version: `0.1`
Status: `locked`
Effective date: `2026-06-25`
Supersedes: `none`
Superseded by: `none`
Governing doctrine: `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`
Source of truth: this file

## Naming Hierarchy

HoloBrain is the overarching substrate.

HoloGov governs lanes.

HoloBrain agents maintain memory.

HoloGov-C, HoloGov-B, and HoloGov-V all use the shared HoloBrain framework with lane-specific fidelity rules.

## Core Rule

Maintenance agents may prepare memory changes, but they may not silently rewrite truth.

All agents may draft, queue, flag, and summarize. None may promote, prune, supersede, rewrite, or canonize without explicit approval.

## Agents

### HoloScribe

Core responsibility: draft candidate memory objects from approved source references.

Inputs it can read:

- Doctrine files.
- Manifests.
- State notes.
- Approved reports.
- Artifact references.
- Case references.
- Policy references.
- Recovery manifests.

Outputs it can write:

- Draft queue entries for `case_experience`.
- Draft queue entries for `failure_pattern`.
- Draft queue entries for `successful_resolution`.
- Draft queue entries for `settled_decision_candidate`.

May propose:

- New candidate memories.
- Summaries.
- Tags.
- Confidence labels.
- Source references.

May never auto-modify:

- Canonical doctrine.
- Policy corpus.
- Settled decisions.
- Benchmark state.
- Artifacts.
- Traces.
- Packets.

Low-cost model safe: `yes`.

### HoloPrune

Core responsibility: find stale, noisy, duplicate, low-confidence, contradicted, or overgeneralized memory objects.

Inputs it can read:

- Active memory index.
- Candidate queue.
- Case memories.
- Retrieval logs.
- Supersession edges.
- Artifact references.

Outputs it can write:

- `prune_candidate` queue entries.
- Pruning rationale.

May propose:

- Remove from active retrieval.
- Lower confidence.
- Quarantine.
- Merge duplicates.

May never auto-modify:

- Active retrieval status.
- Canonical records.
- Policies.
- Settled decisions.
- Locked artifact references.

Low-cost model safe: `yes`, if only proposing.

### HoloThread

Core responsibility: thread related memories, lessons, and supersession paths into coherent structures.

Inputs it can read:

- Case memories.
- Policy references.
- Doctrine references.
- State notes.
- Prior candidate queues.
- Audit summaries.

Outputs it can write:

- `consolidation_candidate` queue entries.
- `supersession_candidate` queue entries.
- Merged-summary drafts.

May propose:

- One memory supersedes another.
- Multiple case lessons merge into a repeated empirical pattern.
- Old summaries become retired references.
- Related memory paths should be threaded together for retrieval.

May never auto-modify:

- Supersession state.
- Active or retired status.
- Policy version status.
- Doctrine.
- Manifests.

Low-cost model safe: `mostly yes`; use stronger review for high-impact HoloGov-B or HoloGov-V supersessions.

### HoloSentinel

Core responsibility: run integrity and watchdog checks.

Inputs it can read:

- Manifests.
- Doctrine files.
- Recovery manifests.
- Artifact references.
- Hashes.
- Retrieval logs.
- Injection logs.
- Branch and status metadata.

Outputs it can write:

- `integrity_alert`.
- `dangling_ref_alert`.
- `drift_alert`.
- `backup_gap_alert`.

May propose:

- Missing hash fix.
- Broken reference repair.
- Doctrine drift review.
- Unpushed artifact warning.
- Unsafe raw trace storage warning.

May never auto-modify:

- Hashes.
- Artifacts.
- Manifests.
- Doctrine.
- Memory truth fields.
- Git history.

Low-cost model safe: `yes` for checks and alerts.

### HoloScope

Core responsibility: review scope limits and non-generalization boundaries.

Inputs it can read:

- Candidate memories.
- Case experiences.
- Failure patterns.
- Successful resolutions.
- Policy references.
- Domain tags.

Outputs it can write:

- `scope_review` fields.
- Proposed `scope_limits`.
- Proposed `non_generalization_conditions`.

May propose:

- Narrower domain.
- Confidence downgrade.
- Do-not-generalize warnings.
- Retrieval suppression outside scope.

May never auto-modify:

- Authority level.
- Confidence finalization.
- Active retrieval eligibility.
- Policy bindings.

Low-cost model safe: `yes`; require approval for HoloGov-B or HoloGov-V promotion.

### HoloLedger

Core responsibility: produce daily HoloBrain status reports.

Inputs it can read:

- Candidate queue.
- Integrity alerts.
- Prune proposals.
- Supersession proposals.
- Doctrine references.
- Profile references.
- Recovery manifests.
- Backup status.

Outputs it can write:

- Daily HoloBrain status report.

May propose:

- Operator action list.
- Urgent review queue.
- Daily backup gaps.
- Pending approval summary.

May never auto-modify:

- Any memory object.
- Doctrine.
- Policies.
- Artifacts.
- Score-valid status.

Low-cost model safe: `yes`.

## Never Auto-Modify

No HoloBrain maintenance agent may auto-modify:

- Locked HoloGov Memory Doctrine.
- HoloBrain Maintenance Roster.
- Architecture profile manifests.
- Canonical benchmark state notes.
- Formal policy corpus.
- Settled decisions.
- Score-valid status.
- Benchmark packets, traces, Judge outputs, or answer keys.
- Raw logs or raw trace dumps.
- Secrets, API keys, tokens, or auth state.
- Frozen artifacts or hashes.

## Change Rule

Future modifications to this roster must create a new version or be explicitly approved by the operator.
