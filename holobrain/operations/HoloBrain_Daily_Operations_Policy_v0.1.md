# HoloBrain Daily Operations Policy

Version: `0.1`
Status: `locked`
Effective date: `2026-06-25`
Supersedes: `none`
Superseded by: `none`
Source of truth: this file

## Scope

This policy defines the daily backup routine and first-pass model assignment policy for HoloBrain maintenance agents.

HoloBrain is the overarching memory and intelligence infrastructure. HoloGov governs lanes. HoloBrain maintenance agents maintain memory, prepare changes, and report status without silently rewriting truth.

## Operating Rule

If the daily checklist is not completed, no benchmark execution may run that day.

This includes new benchmark packets, provider runs, scoring, judging, unblinding, or benchmark cleanup that changes packet or result state.

## Daily Backup Checklist

1. Verify repo state: run `git status --short --branch`, record the current branch, and confirm remote tracking.
2. Protect canonical changes: commit approved doctrine, manifests, state notes, roster files, smoke tests, recovery manifests, and operations policies with exact-file staging only.
3. Protect dirty or untracked work: create a dated WIP safety snapshot as patches and copied files under `recovery/wip_snapshots/YYYY-MM-DD/`.
4. Update `recovery/DAILY_RECOVERY_MANIFEST_YYYY-MM-DD.md` with branch, local HEAD SHA, pushed SHA, dirty snapshot hash, untracked snapshot hash, and known gaps.
5. Push the recovery branch and verify it with `git ls-remote origin <branch>`.
6. Confirm fresh-clone viability by checking that required files exist in the pushed commit tree.
7. Record what remains local-only, including secrets, `.env`, uncommitted benchmark documents, object-store gaps, Supabase gaps, and audit-log gaps.

## Later Automation Targets

- HoloLedger daily recovery manifest generation.
- HoloSentinel remote SHA verification and dangling-reference checks.
- Automatic WIP patch snapshot creation for unstaged tracked files.
- Object-store export checks for HoloBrain memory, policy corpus, case memory, audit logs, and benchmark artifacts.
- Supabase logical backup and export status checks.
- Secret-manager presence checks that report only `PRESENT` or `MISSING`.
- Daily status report assembly with unresolved backup gaps and operator action items.

## First-Pass Model Assignment

| Agent | First-pass model assignment | MiniMax safe | Review policy |
|---|---|---:|---|
| HoloScribe | MiniMax for candidate memory drafts | Yes | Operator review before promotion |
| HoloPrune | MiniMax for prune candidates | Yes | Operator review before removal, quarantine, or active retrieval change |
| HoloThread | MiniMax for simple clustering; stronger model for HoloGov-B or HoloGov-V supersession paths | Partial | Operator review required for supersession, merge, retirement, or authority change |
| HoloSentinel | MiniMax for mechanical integrity checks | Yes | Stronger review for doctrine drift, suspicious recovery gaps, or conflicting source-of-truth findings |
| HoloScope | MiniMax for first-pass scope warnings | Yes, with limits | Stronger review for HoloGov-B or HoloGov-V case promotion, suppression, or non-generalization changes |
| HoloLedger | MiniMax for daily status reports | Yes | Operator review if the report recommends any canonical change |

## MiniMax-Safe Roles

MiniMax may be used for:

- HoloScribe candidate drafting, when outputs remain queued.
- HoloPrune prune proposals, when no retrieval state changes automatically.
- HoloSentinel mechanical checks, hash checks, branch checks, and missing-reference alerts.
- HoloScope first-pass scope-limit and non-generalization warnings.
- HoloLedger daily status reports.

MiniMax outputs must remain proposals, summaries, alerts, or queue entries unless explicitly approved by the operator.

## Stronger-Model Or Operator-Review Roles

Use a stronger model, operator review, or both for:

- HoloThread supersession paths, merged lessons, authority ladder conflicts, and HoloGov-B or HoloGov-V consolidation.
- HoloScope non-generalization decisions that could suppress, promote, or broaden HoloGov-B or HoloGov-V case memory.
- Any proposed modification to doctrine, roster, architecture profiles, canonical state notes, operations policies, policy corpus, settled decisions, score-valid status, or benchmark status.
- Any deletion, promotion, supersession, retirement, quarantine, confidence finalization, or retrieval eligibility change.

## Wrong-Model Risks

- HoloPrune can over-prune useful memory if assigned a model that misses nuance or treats low-frequency lessons as noise.
- HoloScope can overgeneralize case lessons if it misses scope limits or non-generalization conditions.
- HoloThread can create false supersession chains if it compresses distinct cases into one pattern.
- HoloScribe can create prompt bloat if it writes verbose candidate memories without artifact references.
- HoloSentinel can create false confidence if it reports protection without remote, object-store, or database verification.
- HoloLedger can hide operational risk if it summarizes backup status without listing unresolved local-only gaps.
- Any low-cost agent can cause truth drift if allowed to promote, rewrite, supersede, prune, or canonize without approval.

## Change Rule

Future modifications to this policy must create a new version or be explicitly approved by the operator.
