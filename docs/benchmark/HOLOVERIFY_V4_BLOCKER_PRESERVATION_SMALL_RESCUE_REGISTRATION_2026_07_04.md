# HoloVerify V4 Blocker Preservation Small Rescue Registration

Date: 2026-07-04

Status: `REGISTERED_NO_PROVIDER_PATCH_VALIDATION_ONLY`

Lane: `HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_PATCH_VALIDATION_V0`

Branch: `codex/ap-publication-integration`

Architecture HEAD: `d41ec047a7cf378065c3d32d849d405e489421b5`

## Purpose

This is a small patch-validation lane for the exact Batch016 Holo rescue failure mode.

The prior Batch016 Holo rescue was validly executed, but it failed diagnostically. The important failure was not provider health. It was that a worker sometimes found a real `ESCALATE` blocker, and the final selected artifact still became `ALLOW` without explicitly closing that blocker.

This registration selects five packets where that happened. It does not create benchmark evidence. It does not repair Batch016. It prepares a narrow rerun lane for the V4 selector and V3 worker contract.

## Current Architecture Under Test

Selector:

`SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04`

Worker contract:

`WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04`

## Source Evidence

The packet selection comes from:

- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH016_HARD_AUTHORITY_HOLO_RESCUE_AUTOPSY_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH016_HARD_AUTHORITY_HOLO_RESCUE_AUTOPSY_2026_07_04.json`
- `docs/benchmark/HOLOVERIFY_BLOCKER_PRESERVATION_PATCH_REPORT_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_BLOCKER_PRESERVATION_PATCH_REPORT_2026_07_04.json`

Source hashes are recorded in the JSON registration file.

## Selection Rule

A packet was eligible only if:

- Truth was `ESCALATE`.
- Prior Holo final was `ALLOW`.
- At least one prior worker found an `ESCALATE` blocker.
- The miss was blocker drop / selector washout, not provider failure.

## Selected Packets

| Pair | Sibling | Opaque runtime ID | Prior worker pattern | Blocker found by | Domain | Why selected |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `HVSF-FACTORY16-001` | `B` | `SFF16HA-8EEA87DF0B8C19DA1FC3` | `ALLOW / ALLOW / ESCALATE` | `W3` | AP vendor master / payment rail controls | Final-turn blocker lost to earlier ALLOW artifact. |
| `HVSF-FACTORY16-004` | `B` | `SFF16HA-3FD8B906B07BBAC1604F` | `ALLOW / ALLOW / ESCALATE` | `W3` | AP vendor callback / destination account controls | Same W3 blocker-drop pattern in a different AP boundary. |
| `HVSF-FACTORY16-008` | `B` | `SFF16HA-EB6D4A8ED66E020111B3` | `ESCALATE / ALLOW / ALLOW` | `W1` | Agentic commerce subscription controls | Early blocker washed out by later ALLOW artifacts. |
| `HVSF-FACTORY16-010` | `B` | `SFF16HA-EAAD2AFD82C919B7ECCB` | `ALLOW / ESCALATE / ALLOW` | `W2` | Banking relationship and transaction controls | Middle-turn blocker washed out by final ALLOW. |
| `HVSF-FACTORY16-020` | `B` | `SFF16HA-B1376D9F72BE680784D1` | `ESCALATE / ALLOW / ALLOW` | `W1` | Trade-finance payment release controls | Second early-blocker washout case in a different domain. |

## Runtime-Only Manifest

The live runner must not use this registration file. This registration file contains audit context and post-hoc selection rationale.

The live runner must use the separate runtime-only manifest:

`docs/benchmark/HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json`

Runtime-only manifest SHA-256:

`4f8ec7a398b4b98be98695882ee90554884b2ffd939c6af2a1db41efc2553f60`

That file contains only:

- opaque runtime IDs
- runtime payload refs
- runtime payload SHA-256 values

It does not contain truth labels, scores, worker patterns, or post-hoc verdicts.

## Expected Calls If Approved Later

Expected provider calls: `25`

Breakdown:

- `W1 xai/grok-3-mini x5`
- `G1 minimax/MiniMax-M2.5-highspeed x5`
- `W2 openai/gpt-5.4-mini x5`
- `G2 minimax/MiniMax-M2.5-highspeed x5`
- `W3 minimax/MiniMax-M2.5-highspeed x5`

No providers were called during registration.

No solo, Holo live, Gov live, or judges ran during registration.

## Live Approval Ownership

The exact approval sentence lives in the preflight file, not in this registration file.

The registration JSON is audit/scoring context only and is not live runner input.
