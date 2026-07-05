# Daily Recovery Manifest - 2026-06-25

Branch: `recovery/2026-06-25-control-checkpoint`
Base branch before recovery branch: `holochat-4dna-foundation-001`
Base HEAD before recovery branch: `c93855400da62a1b4efb5662cf71fa01456ec794`
Current state refresh: `2026-06-26` daily control closeout
Latest protected local HEAD before this manifest closeout: `5dd1e5b0cb30b9cf7735196383ef54a87dcd7b48`
Latest protected remote SHA before this manifest closeout: `5dd1e5b0cb30b9cf7735196383ef54a87dcd7b48`
Remote branch: `origin/recovery/2026-06-25-control-checkpoint`
Post-closeout remote SHA: the commit containing this manifest update; verify with `git rev-parse origin/recovery/2026-06-25-control-checkpoint`.

## Protected Commits

- `5064bae5a7392409d396d0e4ae2ad4fa088fe30d` - Lock control recovery artifacts.
- `5ccbfb296264ca69a384b91b1e54b9b4244e1984` - Add daily recovery WIP snapshot.
- `04d3ef487f8bef48e4dee97c42d01126654cd5a9` - Add HoloBrain Phase 1 smoke contracts.
- `625cc39ee3bc540d17a172d76018db8016e51bf5` - Lock HoloBrain daily operations policy.
- `337c2c9f89e1c377d8c1b81fddfc705ad6e1016c` - Reference HoloBrain daily operations policy in the canonical benchmark state note.
- `955ad1b42f08b13099dfd4a6b4dcccf6d98d0f82` - Add HoloBrain operations Sentinel and Ledger.
- `5dd1e5b0cb30b9cf7735196383ef54a87dcd7b48` - Reconcile `docs/whitepaper.md` to the Version 7.4 markdown source.

## Protected Control Artifacts

- `holo_profiles/locked_architecture_profiles.json`
- `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`
- `holobrain/memory/HoloBrainMaintenanceRoster_v0.1.md`
- `holobrain/memory/contracts.py`
- `holobrain/operations/HoloBrain_Daily_Operations_Policy_v0.1.md`
- `holobrain/operations/sentinel.py`
- `holobrain/operations/ledger.py`
- `docs/benchmark/CANONICAL_BENCHMARK_STATE_2026-06-25.md`
- `tests/test_holobrain_phase1_smoke.py`
- `tests/test_holobrain_operations_phase2.py`
- `docs/whitepaper.md` - Version 7.4 markdown whitepaper source.

## Current HoloBrain Control Status

- HoloSentinel required artifacts present: `true`
- HoloSentinel required artifacts tracked: `true`
- HoloSentinel locked metadata present: `true`
- HoloLedger benchmark gate: `BLOCK`
- Benchmark execution allowed today: `false`
- HoloSentinel local-only fragility at closeout read: `branch ahead of upstream by 1 commit(s); worktree has 11 dirty tracked path(s); worktree has 1 untracked path(s)`
- Gate reason: daily checklist is incomplete and local-only worktree fragility remains.
- Note: the branch-ahead warning is expected until this manifest closeout commit is pushed. The remaining dirty tracked files should be the paths listed below.

## Current Known Local-Only Gaps

Dirty tracked files still present:

- `chat_engine.py`
- `frontend/benchmark.html`
- `frontend/chat.html`
- `frontend/whitepaper.html`
- `holo_state.py`
- `llm_adapters.py`
- `main.py`
- `tests/conftest.py`
- `tests/test_api.py`
- `tests/test_holochat_runtime_routing.py`
- `tests/test_holochat_web_checked.py`

Untracked files still present:

- `docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md`

## WIP Safety Snapshot

Method: tracked dirty files are preserved as a binary Git patch; the untracked file is preserved as an exact snapshot copy under `recovery/wip_snapshots/2026-06-25/`.

Tracked patch:

- Path: `recovery/wip_snapshots/2026-06-25/dirty_tracked.patch`
- SHA256: `9182baeae02d3c89581752547f6516797127e65befc088361a5816797a17222a`

Untracked snapshot:

- Source path: `docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md`
- Snapshot path: `recovery/wip_snapshots/2026-06-25/untracked/docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md`
- SHA256: `4b5a90fcab8528a5bea4c573c2b2d2ca6a28e9df0f8b4ff199516f449706adc5`

Tracked dirty files covered by the original snapshot:

- `chat_engine.py`
- `docs/whitepaper.md`
- `frontend/benchmark.html`
- `frontend/chat.html`
- `frontend/whitepaper.html`
- `holo_state.py`
- `llm_adapters.py`
- `tests/test_holochat_runtime_routing.py`
- `tests/test_holochat_web_checked.py`

## Intentional Working Tree State After Snapshot

The original dirty files remain dirty and unmodified in the working tree. The snapshot is recovery-only and does not classify the WIP as accepted architecture work.

The original WIP snapshot still preserves the pre-closeout dirty tracked state, including the earlier `docs/whitepaper.md` WIP. Since then, `docs/whitepaper.md` has been reconciled and protected in commit `5dd1e5b0cb30b9cf7735196383ef54a87dcd7b48`, so the current dirty tracked set no longer exactly matches the original snapshot list.

The current untracked path is still represented by the snapshot copy. This does not make the WIP canonical or benchmark-valid.

## Not Protected By This Git-Backed Pass

- Supabase/HoloBrain database contents.
- External object-storage artifacts not already in Git or this snapshot.
- HoloBrain policy corpus outside this repo.
- HoloBrain case memory outside this repo.
- Audit logs outside this repo.
- Secrets and API keys.
- Browser/session state.
- Files outside this repo.

## Restore Notes

1. Fetch and check out `recovery/2026-06-25-control-checkpoint`.
2. Use commit `5dd1e5b0cb30b9cf7735196383ef54a87dcd7b48` for the latest protected public-source state before this manifest closeout.
3. Use commit `955ad1b42f08b13099dfd4a6b4dcccf6d98d0f82` for the latest protected HoloBrain control infrastructure.
4. Use commit `5064bae5a7392409d396d0e4ae2ad4fa088fe30d` for the original accepted control artifacts if a narrower recovery point is required.
5. Use `recovery/wip_snapshots/2026-06-25/dirty_tracked.patch` to restore the original tracked WIP snapshot if needed.
6. Use the untracked snapshot copy to restore `docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md` if needed.
