# Holo Engine Benchmark Integrity Protocol v1.0

Every Holo benchmark run is pre-registered and hash-locked before execution. Payloads, harness configuration, scoring rubric, and model roster are fingerprinted before any verdicts are generated. Raw traces are archived and fingerprinted after execution. This does not ask evaluators to trust our summary table. It gives them a tamper-evident chain from packet to prompt to verdict.

---

## Language Rules

Do not say: "Cryptographic proof."
Use: "Hash-locked audit trail" or "Tamper-evident benchmark record" or "Pre-registered benchmark run with SHA-256 packet and trace fingerprints."

Do not say: "Absolute ground truth."
Use: "Evidence-derived adjudication against the declared policy and packet artifacts."

Do not say: "Trust us, Holo won."
Use: "Here is the locked packet, locked harness, declared model roster, raw trace archive, and verdict path."

---

## Before Execution

1. Freeze the payload packet.
2. Freeze the policy rubric.
3. Freeze the harness config.
4. Freeze the model roster and version/date.
5. Freeze the scoring rubric.
6. Generate SHA-256 hashes for each.
7. Write a run manifest before any model calls happen.

## During Execution

1. Run all declared architectures.
2. Use fixed temperature unless the benchmark explicitly tests stochasticity.
3. Record seeds where applicable.
4. Record full prompts, model outputs, timestamps, token counts, latency, and adapter/provider errors.
5. Preserve failed or degraded runs separately instead of silently replacing them.

## Benchmark Laws

These are score-validity gates, not style preferences.

1. Gov/Worker token ratio is calculated as total Gov tokens divided by total worker tokens.
2. Target ratio is 10% to 25%.
3. A ratio above 33% flags the run for review.
4. A ratio above 50% hard-fails the benchmark unless `full_context_governor_audit=true`.
5. A hard-failed run must preserve the current best state, trace, token ledger, and failure receipt. It must not be deleted, but it is `benchmark_valid=false` and `score_valid=false`.
6. Gov model identity must remain fixed for the session.
7. Worker rotation must use at least two distinct worker models, and a worker must not receive its own immediate prior output without another worker intervening.
8. Worker prompt order must be Gov adversarial baton first, structured canonical state second, and artifact context third.
9. Raw full accumulating transcript injection is banned in benchmark worker prompts.
10. PINNED artifacts and CRITICAL_CONSTRAINTS must survive turn 5 and turn 10 state audits with exact wording.
11. Sycophantic worker output with fewer than the required critiques must be caught by Gov and routed to retry, repair, escalation, or fail-closed.

## After Execution

1. Hash the raw trace archive.
2. Publish the verdict table.
3. Publish the audit ledger.
4. Publish what is public and what is available under controlled review.
5. Declare any reruns, provider degradation, excluded runs, or infrastructure contamination.

---

## What This Proves

We can prove the benchmark artifacts were locked before execution and that the published traces match the recorded run.

We cannot prove the benchmark is objectively true because crypto. The honest claim is the tamper-evident chain — not omniscience.

---

## The Standard Framing

Every Holo benchmark run is pre-registered and hash-locked before execution. Payloads, harness configuration, scoring rubric, and model roster are fingerprinted before any verdicts are generated. Raw traces are archived and fingerprinted after execution. This does not ask evaluators to trust our summary table; it gives them a tamper-evident chain from packet to prompt to verdict.

---

*Established: 2026-06-03. Applies to all Holo Engine benchmark runs from this date forward.*
