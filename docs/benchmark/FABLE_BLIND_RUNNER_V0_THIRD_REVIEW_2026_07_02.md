# Fable Blind Runner V0 — Third Review (Short)

Status: READ_ONLY_THIRD_REVIEW_COMPLETE
Date: 2026-07-02
Scope: canary gate only. No providers, no judges, no edits. 28/28 independently reproduced.

## VERDICT: `BLOCK_CANARY`

Three must-fix blockers. Everything else from rounds one and two is verified repaired.

### Verified fixed this round (empirically, not from the repair report)

- Ordering: side sequence now `AABABABBBBAABBAAABAB`; odd/even positions mixed; sibling adjacency 2 (≤2); manifest hash-sorted by opaque ID.
- Runtime manifest keys reduced to `classification/created_at_utc/judge_calls/packet_count/packets/provider_calls/runtime_consumable/runtime_field_policy` — no bank_hash, no seed material.
- Frozen bank exists (`holoverify_blind_canary_bank_2026_07_02.json`), hash-pinned, T5 asserts equality.
- Old unsalted opaque recipe no longer reconstructs any runtime ID.
- Prompt fixtures regenerated: 20 prompt ID stems exactly match the 20 new runtime IDs.
- Runner still has zero file reads and a stdlib-only import surface.

### Must-fix blockers before live

**B1 — The "private" salt is derived from public data by a public recipe.**
`build_blind_canary_manifest_2026_07_02.py::_private_salt` = `sha256("private-runtime-salt|" + bank_hash)`. The bank_hash is committed in the audit manifest and frozen bank file; the recipe is committed source. Anyone can recompute the salt and the full opaque↔legacy mapping from public repo data — the scoring-map split is theater again, and the new T5 assertion (`private_runtime_salt in scoring`) passes on it. Fix: `secrets.token_hex(32)` at build time, stored only in the scoring map, regenerate the package (ordering test re-runs on the new draw). One line plus regeneration.

**B2 — There is no live execution harness to approve.**
Everything reviewed is fixture-path code (`run_blind_fixture` fed dicts and mock transcripts). The live canary requires a loader/executor that reads the runtime manifest, loads payload files, calls providers, and writes traces — that code does not exist yet, and it is exactly where a scoring-map read or truth join would happen. A canary pass cannot be granted against code that will be written after the pass. Fix: commit the live executor; bind it to the firewall; add the filesystem-isolation shim test (monkeypatched `open`/`Path.read_text` failing on any path outside runtime manifest + payload dir + out_dir) — this closes round-two F4 at the same time.

**B3 — Import-closure AST scan (round-one F10, still open, twice acknowledged).**
Trivial while the runner is stdlib-only; mandatory before B2's executor lands, because the executor will import more. Extend the T2 static guard to every repo-local module in the registered runner's (and executor's) import closure.

### Not blockers, for the record

The salt recomputability is process-side only — the runtime file set itself is now truth-free, and the runner has no code path to reach the repo. The parity/adjacency test is a tripwire, not proof (a non-parity positional pattern would pass it); hash-sorted ordering makes that acceptable. Payload-wording truth signal, curated corpus (C4), survivor-lane universe, and n=20's statistical weightlessness remain standing residuals that no repair here touches.

After B1–B3: regenerate, re-run the suite, and the canary gate is open from my side — for a firewall test, never a rate claim.
