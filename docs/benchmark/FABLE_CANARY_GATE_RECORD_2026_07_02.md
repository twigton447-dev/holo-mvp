# Fable Canary Gate Record

Date: 2026-07-02
Gate: final read-only review before live 20-packet blind canary
Reviewer: Fable. No providers, no judges, no edits.

## VERDICT: `PASS_TO_CANARY`

All three third-review blockers verified closed against the artifacts, not the repair report:

- **B1 salt:** `_private_salt()` now returns `secrets.token_hex(32)` (sampler line 47-49); scoring-map salt does not equal the old public recipe; anti-recipe regression test present (`test_private_salt_is_not_public_bank_hash_recipe`).
- **B2 live executor:** `run_blind_runtime_manifest` exists; requires caller-supplied transport; refuses manifests without `runtime_consumable`; loads only the runtime manifest and its opaque payload refs via `Path.read_text`; writes only under out_dir; filesystem shim test (`test_runtime_executor_reads_only_runtime_manifest_payloads_and_outdir`) enforces exactly that access set.
- **B3 import closure:** `scan_import_closure_for_truth_reachability` active with its own test.

Independently recomputed from runtime manifest + scoring map: truth sequence `EAEEAEEEAAAAEAEAEAEA` (both parity classes mixed), sibling adjacency 1, runtime manifest keys truth-free, prompt fixture IDs exactly match the regenerated opaque IDs. Suite: 31 passed, 0 skipped, 0 failed, reproduced locally.

## Scope of this pass

The canary is approved as a **runtime-firewall test only**. It cannot support any error-rate, FP/FN, or architecture-advantage claim at n=20. Standing residuals unchanged and out of scope for this gate: payload-wording truth signal, corpus curated against solo failure (C4), survivor-lane sampling universe, fixture-vs-live transport fidelity, and the shim's coverage of `Path` methods but not `builtins.open` (guarded by the import-closure scan; extend if the executor ever grows).

Live execution still requires Taylor's explicit provider approval with exact scope, per the standing mandate.
