# Daily Recovery Manifest - 2026-06-25

Branch: `recovery/2026-06-25-control-checkpoint`
Base branch before recovery branch: `holochat-4dna-foundation-001`
Base HEAD before recovery branch: `c93855400da62a1b4efb5662cf71fa01456ec794`
Control artifact commit: `5064bae`

## Protected Control Artifacts

- `holo_profiles/locked_architecture_profiles.json`
- `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`
- `docs/benchmark/CANONICAL_BENCHMARK_STATE_2026-06-25.md`

## WIP Safety Snapshot

Method: tracked dirty files are preserved as a binary Git patch; the untracked file is preserved as an exact snapshot copy under `recovery/wip_snapshots/2026-06-25/`.

Tracked patch:

- Path: `recovery/wip_snapshots/2026-06-25/dirty_tracked.patch`
- SHA256: `9182baeae02d3c89581752547f6516797127e65befc088361a5816797a17222a`

Untracked snapshot:

- Source path: `docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md`
- Snapshot path: `recovery/wip_snapshots/2026-06-25/untracked/docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md`
- SHA256: `4b5a90fcab8528a5bea4c573c2b2d2ca6a28e9df0f8b4ff199516f449706adc5`

Tracked dirty files covered by patch:

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

## Not Protected By This First Pass

- Supabase/HoloBrain database contents.
- External object-storage artifacts not already in Git or this snapshot.
- Secrets and API keys.
- Browser/session state.
- Files outside this repo.

## Restore Notes

1. Fetch and check out `recovery/2026-06-25-control-checkpoint`.
2. Use commit `5064bae` for the accepted control artifacts.
3. Use `recovery/wip_snapshots/2026-06-25/dirty_tracked.patch` to restore tracked WIP changes if needed.
4. Use the untracked snapshot copy to restore `docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md` if needed.
