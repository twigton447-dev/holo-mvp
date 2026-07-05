# HoloVerify Public Package Lineage Note

Date: 2026-06-29

Scope: read-only reconciliation of two committed HoloVerify evidence/package commits. No providers were run. No Holo or solo runs were rerun. No benchmark evidence was edited.

## Commits Reviewed

| Commit | Role | Summary |
| --- | --- | --- |
| `93118d7` | Underlying evidence commit | Full HoloVerify 20-pair / 3-DNA run plus matching one-shot solo baseline evidence package. |
| `87b39f2` | Public packaging commit | Additive public-safe 14-pair subset package, final public memo, no-provider audit, and public freeze package lock. |

## What `93118d7` Contains

`93118d7 benchmark: freeze holoverify 20pair 3dna and solo baseline` is the canonical underlying evidence commit.

It contains:

- The successful frozen HoloVerify run evidence.
- Holo final result: 40/40 packets correct.
- Holo valid sibling pairs: 20/20.
- Hard-ALLOW target pairs: 10/10.
- Hard-ESCALATE target pairs: 10/10.
- Guardrail siblings: 20/20.
- Matching one-shot solo baseline: 120/120 calls.
- Solo KNEW/admissible outputs: 6/120.
- Packet identity audit: PASS.
- Final readiness assertions: PASS.
- Judges: 0.
- Holo tokens: 426,002.
- Solo tokens: 206,839.
- Holo/Solo token ratio: about 2.06x.
- Original final evidence package lock root: `1681941a2a5c5eff6db9a5bf47d2159b360a29ab99a9f26586e3ebff5f5acebf`.

## What `87b39f2` Adds

`87b39f2 benchmark: freeze holoverify 20pair 3dna solo comparison` is the canonical public packaging commit.

It adds:

- `HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.json`
- `HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.md`
- `HOLOVERIFY_14PAIR_PUBLIC_PROOF_SUMMARY_2026_06_29.md`
- `HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO_2026_06_29.json`
- `HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO_2026_06_29.md`
- `HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.json`
- `HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.md`
- `PUBLIC_FREEZE_PACKAGE_LOCK_MANIFEST.json`
- `PUBLIC_FREEZE_PACKAGE_LOCK_VALIDATION.json`
- `build_holoverify_20pair_public_freeze_package_2026_06_29.py`

The added public package verifies:

- Clean all-six-solo-fail sibling pairs: 14.
- Clean subset packets: 28.
- Mixed pairs: 6.
- No-provider local audit: PASS.
- Required evidence files present: PASS.
- Same 40 packet hashes: PASS.
- Solo provider calls: 120 PASS.
- Holo provider calls: 200 PASS.
- No judges: PASS.
- No leakage: PASS.
- Evidence categories separated: PASS.
- Invalid hardening runs preserved: PASS.
- Public freeze package lock root: `5ffe3c41e5cf35324f9bb0518c24df118aad0eea15900abbb1d9996df1756695`.

## Did Evidence Change?

No benchmark run evidence changed between `93118d7` and `87b39f2`.

Read-only diff inspection found no changes under:

- `docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs`
- `docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z`
- `docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z`

The difference is additive packaging and audit material only. `87b39f2` does not mutate the frozen packets, Holo traces, solo traces, solo prompts, raw outputs, or provider metadata from `93118d7`.

## Why Lock Roots Differ

The lock roots differ because they lock different artifact scopes.

`93118d7` locks the original full final evidence package. Its `FINAL_EVIDENCE_PACKAGE_LOCK_VALIDATION.json` reports:

`1681941a2a5c5eff6db9a5bf47d2159b360a29ab99a9f26586e3ebff5f5acebf`

`87b39f2` adds a later public freeze package with a different file set: the clean 14-pair subset, public memo, no-provider audit, public summary, and public freeze lock. Its `PUBLIC_FREEZE_PACKAGE_LOCK_VALIDATION.json` reports:

`5ffe3c41e5cf35324f9bb0518c24df118aad0eea15900abbb1d9996df1756695`

This root difference is expected. It is not evidence drift. It reflects a new public packaging layer over the already committed evidence.

Note: a separate root value, `904fb31d351b8fdc57481f739ce7133687f036626561233883c9795af6dced77`, was referenced in a later instruction but was not the committed lock root found in `93118d7` or the public package lock root found in `87b39f2`.

## Canonical Public Package

Canonical public package commit:

`87b39f2 benchmark: freeze holoverify 20pair 3dna solo comparison`

Canonical public package lock root:

`5ffe3c41e5cf35324f9bb0518c24df118aad0eea15900abbb1d9996df1756695`

Canonical underlying evidence commit:

`93118d7 benchmark: freeze holoverify 20pair 3dna and solo baseline`

The correct public lineage is:

1. Use `93118d7` as the underlying frozen evidence source.
2. Use `87b39f2` as the public-safe packaging and publication source.

## Supersession Decision

`87b39f2` supersedes the earlier publication drafts created from `93118d7` for public copy purposes.

The older drafts should be treated as deprecated because they were written before the later public package lock, no-provider audit, and 14-pair clean subset package existed. Their numbers were directionally consistent, but their lock-root reference was incomplete for public use.

Use the updated drafts generated from `87b39f2` instead.

## Claim Boundary

Safe public framing:

- Architecture-at-action-boundary.
- Same frozen packet bank.
- Same mini-model families.
- HoloVerify solved 40/40.
- Solo one-shot baseline completed 120/120 calls with 6/120 KNEW/admissible.
- Fourteen clean all-six-solo-fail pairs.
- No leakage.
- About 2.06x token ratio.

Unsafe public framing:

- Holo beats all models.
- Holo is generally superior.
- Holo solved safety.
- Solo models cannot solve these packets under any stronger prompting or workflow.
- Internal Holo misses are standalone external solo failures.
