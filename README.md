# Holo Engine

**A runtime trust layer for high-consequence AI actions.**

Holo sits at the action boundary — the last reversible checkpoint before an autonomous agent executes an irreversible action. It adjudicates what passes surface checks but still doesn't add up.

---

## The Problem

AI agents are approving wire transfers, provisioning admin credentials, and executing vendor contracts. The evaluation criteria did not change when the stakes did.

Solo frontier models fail a specific, non-random class of decisions: actions where the payload looks clean, the policy passes, but the history, provenance, or authorization chain contains a contradiction. One model accepts a well-constructed narrative and clears a flag it correctly raised. Another catches aggregation failures but misses authorization gaps. These blindspots are structural, non-overlapping, and exploitable.

> GPT-4o approved a fraudulent $47,000 wire transfer in the Holo benchmark. Holo caught it.

---

## What Holo Does

Holo uses structured adversarial review across multiple frontier models — with a static context governor that injects assigned roles, shared state, and convergence pressure — to compensate for distributed model blindspots.

The output is simple and auditable: **ALLOW or ESCALATE.**

Holo does not replace runtime security, policy engines, DLP, or observability. Those layers handle what is known or prohibited. **Holo adjudicates the unresolved middle.**

---

## Architecture

Five conditions isolate the irreducible variable:

| Condition | Setup | What it tests |
|-----------|-------|---------------|
| Solo one-pass | 1 frontier model | Status quo |
| Solo multi-pass self-critique | 1 model, N turns | "Just prompt it better" |
| Parallel multi-LLM sign-off | 3 frontier models, isolated | "We already use multiple LLMs" |
| Sequential chain, no governor | 3 frontier, sequential | "Just pipe models together" |
| **Holo full architecture** | **3 frontier + governor** | **The irreducible variable** |

The governor is static and algorithmic — not a model. LLMs are randomized per session. No synthesis turn. Full raw state passed at each stage.

---

## Benchmark

Public. Reproducible. Payloads available on request.

**Domain 1 — Accounts Payable / BEC:** Flagship scenario (BEC-EXPLAINED-ANOMALY-001) holds in 9 of 10 sequences under Architecture Stability Test conditions. The single miss is diagnosable.

**Domain 2 — Agentic Commerce:** Broken autonomous reorder chain with no human authorization link.

| # | Domain | Status |
|---|--------|--------|
| 1 | Accounts Payable / BEC | Complete |
| 2 | Agentic Commerce | Complete |
| 3 | IT Access Provisioning | Pending |
| 4 | Legal Contract Execution | Pending |
| 5 | Regulated Procurement | Pending |
| 6 | HR and Workforce Actions | Pending |
| 7 | Infrastructure and Configuration | Pending |
| 8 | Financial Reporting and Compliance | Pending |

*U.S. Provisional Patent Application No. 63/987,899, filed February 2026.*

---

## API

The API is live. If you're building agentic workflows in finance, procurement, IT provisioning, or any domain with irreversible actions, contact us.

**hello@holoengine.ai**

---

## Whitepaper

[Blindspots at the Action Boundary](docs/whitepaper.md) — working paper with full benchmark methodology, architecture proof, and limitations.
