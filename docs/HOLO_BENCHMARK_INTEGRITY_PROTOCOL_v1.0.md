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
