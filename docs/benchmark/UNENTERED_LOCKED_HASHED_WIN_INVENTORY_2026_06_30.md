# Unentered Locked / Hashed Win Inventory

Date: 2026-06-30

Purpose: identify HoloBuild or HoloVerify wins present in the repo that are not yet represented in the public benchmark or whitepaper copy.

Public surfaces checked:

- `docs/whitepaper.md`
- `docs/benchmark_summary.md`
- `frontend/whitepaper.html`
- `frontend/benchmark.html`

Current public surfaces already include:

- Kit A Accounts Payable / BEC.
- Kit B Agentic Commerce v1.
- Clinical Activation Boundary Controls / HV-20, 40/40 packets, 20/20 sibling pairs.
- Vendor-Master Payment Controls / AP Replication, 40/40 packets, 20/20 sibling pairs.
- HoloBuild D11, D13, D14, and D14B discussion.

## Best Missing Candidates

### 1. HoloBuild D10 Infrastructure Configuration Change

Candidate status: strong missing HoloBuild win, but needs repo hash packaging before being placed beside AP / Clinical as hash-locked public evidence.

What the repo says:

- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md` says D10 is an official full-gated Holo win, 95-71.
- The same ledger says D10 won all four required 100-point ledgers: deterministic, epistemic, structural, and argument.
- `docs/benchmark/D11_LOCK_5_PACKET_SUITE_LOCK_2026-06-27.md` lists D10 as complete: Holo 95, Solo 71.

Evidence:

- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:15`
- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:26`
- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:73`
- `docs/benchmark/D11_LOCK_5_PACKET_SUITE_LOCK_2026-06-27.md:63`

Important caveat:

- D10 was a patched canary, not part of one uninterrupted 45-call suite.
- The D11-lock files are themselves committed repo evidence, but this candidate does not currently have the same style of repo `LOCK_MANIFEST.json` / `LOCK_VALIDATION.json` root signature package that AP and Clinical have.

Recommended action:

- Create a small D11-lock public-safe package for D10/D11_CYBER with a root signature and copied in-repo judge/audit artifacts, or explicitly label it as "D11-lock ledger evidence" rather than "hash package evidence."

### 2. HoloBuild D11_CYBER Incident / Contract Notice / Emergency Cloud Access

Candidate status: strong missing HoloBuild win, but needs the same hash packaging caution as D10.

What the repo says:

- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md` says D11_CYBER is an official full-gated Holo win, 96-94.
- Both artifacts cleared deterministic gates; Holo won narrowly on structure and argument.
- `docs/benchmark/D11_LOCK_5_PACKET_SUITE_LOCK_2026-06-27.md` lists the case as complete: Holo 96, Solo 94.

Evidence:

- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:16`
- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:27`
- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:74`
- `docs/benchmark/D11_LOCK_SCORE_AND_PROOF_LEDGER_2026-06-27.md:97`
- `docs/benchmark/D11_LOCK_5_PACKET_SUITE_LOCK_2026-06-27.md:64`

Important caveat:

- This is a narrow 96-94 win, not a collapse result.
- It is useful because both artifacts were admissible, which makes it a cleaner quality comparison than baseline-failure-only wins.
- Like D10, it should be hash-packaged before being promoted as a public hash-locked benchmark item.

Recommended action:

- Add D10 and D11_CYBER as a "D11-lock scored sibling mini-suite" after creating a root-signature package, with the split-run caveat plainly stated.

### 3. HoloVerify Agentic Commerce OpenAI-W2 All-Six-Collapse Canary

Candidate status: true locked + hashed missing HoloVerify win, but canary-sized rather than full-family.

What the repo says:

- Classification: `COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_COMPLETE`.
- Readiness passed: `True`.
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`.
- Lock validation passed with root signature `a19bd1e5e47411597ccf5fd941f1a24ba4269215a2fb72a4c2aabe68dc001948`.
- Holo completed 6/6 packets and 3/3 pairs.
- Provider calls: 30/30.
- Worker calls: 18.
- Gov calls: 12.
- Solo calls: 0.
- Judge calls: 0.
- Tokens: 48,445 input / 11,138 output / 63,485 total.
- Pair-level solo collapse was true for all three selected pairs: `HV-ACOM-REP-006`, `HV-ACOM-REP-019`, `HV-ACOM-REP-020`.

Evidence:

- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:3`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:4`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:9`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:14`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:20`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:21`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/canary_summary.md:22`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/LOCK_VALIDATION.json:2`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/LOCK_VALIDATION.json:3`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/LOCK_VALIDATION.json:5`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_READINESS_ASSERTIONS.json:2`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z/COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_READINESS_ASSERTIONS.json:19`

Important caveat:

- This is not the completed 20-pair Agentic Commerce replication family.
- The full-family Commerce runs in the repo remain invalid/incomplete due provider/runtime failure.
- This canary can be used as "Commerce replication canary evidence" or "three locked all-six-solo-collapse commerce pairs," not as "Commerce family solved."

Recommended action:

- Add a conservative canary note to the benchmark/whitepaper if desired:
  "A later Agentic Commerce replication canary selected three all-six-solo-collapse sibling pairs from the frozen Commerce bank. Holo solved all 6 packets / 3 pairs under the same governed architecture. This is canary evidence, not a full-family result."

## Do Not Promote As New Standalone Wins Yet

### Hard ALLOW FP 5-Pair Full-Arch Freeze

Status: hash-locked precursor evidence, but not a new public benchmark win.

What the repo says:

- Status: `FROZEN_PENDING_JUDGE_NOT_BENCHMARK_LOCKED`.
- Root signature: `47434052ed594ed65734e1e964434ae984a17777607fc72ad1c6424dd4de83f6`.
- 5 pairs / 10 packets.
- Holo local KNEW passes: 10/10.
- Solo local KNEW passes: 7/10.

Evidence:

- `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/LOCK_SUMMARY.md:3`
- `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/LOCK_SUMMARY.md:4`
- `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/LOCK_SUMMARY.md:5`
- `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/LOCK_SUMMARY.md:20`
- `docs/benchmark/hard_allow_fp_5pair_full_arch_freeze_2026-06-28/LOCK_SUMMARY.md:21`
- `docs/benchmark/hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28/run_20260629T000225Z/benchmark_summary.md:3`
- `docs/benchmark/hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28/run_20260629T000225Z/benchmark_summary.md:8`
- `docs/benchmark/hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28/run_20260629T000225Z/benchmark_summary.md:9`

Why not promote:

- Its own lock summary says it is pending judge and not benchmark-locked.
- Several of these pairs were later absorbed into the stronger Clinical / HV-20 20-pair package, which is already public.
- It remains useful as provenance/hardening evidence, not as a separate headline.

### Agentic Commerce Full-Family Runs

Status: not a missing win.

What the repo shows:

- `run_20260629T235436Z`: invalid/incomplete, 9 packets, 4 valid pairs, 45 provider calls.
- `run_20260630T032421Z`: invalid/incomplete, 25 packets, 12 valid pairs, 122 provider calls, provider failure at `HV-ACOM-REP-013-A_G1`.

Why not promote:

- The full family has not completed.
- The canary above is the only clean Commerce HoloVerify result found in this pass.

### AP OpenAI-W2 Canaries

Status: not a missing public win.

What the repo shows:

- `run_20260629T164305Z`: one-pair AP canary passed and is lock-root validated, but it was a preflight/canary for the AP full-family lane.
- `run_20260629T191023Z`: AP all-six-collapse canary invalid/incomplete, 26/60 calls.
- `run_20260629T193200Z`: AP all-six-collapse canary completed 60/60 calls and all packets were correct, but `all_target_pairs_valid` failed.

Why not promote:

- The AP full-family result is already in the public benchmark and whitepaper as Vendor-Master Payment Controls / AP Replication, 40/40 packets and 20/20 sibling pairs.
- The canaries are therefore either invalid, preflight evidence, or subsumed by the stronger full-family AP result already entered publicly.

Evidence:

- `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T164305Z/canary_summary.md`
- `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T191023Z/canary_summary.md`
- `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T193200Z/canary_summary.md`

### HoloVerify-V Rescue Diagnostics

Status: useful diagnostics, but not qualifying locked/hash-backed public wins.

What the repo shows:

- Several HoloVerify-V rescue and diagnostic runs are marked complete, including activation dependency, subtle closeout, dependency closure, callback provenance, and Kit C hard-ALLOW FP diagnostics.
- Current-state scan found no `LOCK_VALIDATION.json`, `LOCK_MANIFEST.json`, or `LOCK_SUMMARY.md` under the `holoverify_v_*` diagnostic folders.

Why not promote:

- These runs are useful seam/autopsy evidence, but they do not currently meet the lock-root/hash-package bar requested here.
- Some of the successful Kit C hard-ALLOW diagnostics were later absorbed into the stronger Clinical / HV-20 package that is already public.

## Bottom Line

Best immediate missing item:

1. Agentic Commerce all-six-collapse canary: true locked/hash-backed HoloVerify win, but must be labeled canary-sized.

Best HoloBuild material to package next:

1. D10: official full-gated HoloBuild win, 95-71.
2. D11_CYBER: official full-gated HoloBuild win, 96-94.

These two are already described in repo D11-lock ledgers but are not cleanly represented in the public benchmark/whitepaper. Before promotion, create a public-safe D11-lock evidence package with a root signature so they meet the same hash-package standard as AP and Clinical.
