# Holo Benchmark Scenario Library — Complete Specification

## 1. Purpose

This library provides a structured set of 12 benchmark scenarios for evaluating Business Email Compromise (BEC) detection architectures. Each scenario is a self-contained JSON file conforming to `schema.json`. Scenarios are designed to differentiate between five architectural classes that represent the current landscape of AI-based payment fraud detection.

### The Five Architectures Under Test

| Architecture | Description |
|---|---|
| **A1 — Naive Single-Pass** | One model, one prompt, reads the email, returns a verdict. No cross-field comparison, no history lookup, no iteration. |
| **A2 — Checklist / Rules Engine** | Applies a fixed set of escalation rules mechanically (e.g., "if SPF fails, escalate"). May invoke an LLM but binds it to a hardcoded rule list without contextual reasoning. |
| **A3 — Multi-Pass Solo** | One model makes multiple passes over the same input, potentially with structured prompts for different concern areas. No structural independence between passes. |
| **A4 — Parallel Multi-Model** | Multiple models run simultaneously on the same input, then a synthesis layer aggregates their outputs. Models do not see each other's reasoning. |
| **A5 — Holo (Compounding Postmortems)** | Sequential multi-model loop with shared state. Each model receives the full prior reasoning of all preceding models. The coverage matrix tracks what has been addressed and at what severity. A HIGH-severity flag forces ESCALATE regardless of synthesis verdict. Minimum 3 turns before convergence. |

### The BEC Wedge

Business Email Compromise is the canonical test case for this benchmark because it combines:

1. **Surface plausibility** — BEC attacks are designed to look legitimate. Naive pattern-matching fails.
2. **Conjunctive signals** — No single signal is definitive. The fraud is only clear when multiple weak signals are evaluated together.
3. **Context dependency** — Whether a signal is suspicious depends on what else is true (e.g., SPF soft-fail is suspicious in isolation but explained by a documented infrastructure migration).
4. **Process knowledge** — Correct verdicts require knowing what the policy says and whether the observed evidence conforms to it.
5. **False-positive cost** — Over-escalation blocks legitimate payments, damages vendor relationships, and creates operational friction. The benchmark must test precision, not just recall.

These five properties precisely target the differences between the five architectures. A checklist engine handles (1) poorly. A single-pass model handles (2) poorly. A parallel multi-model system without shared state handles (3) poorly. Only a compounding-postmortem architecture handles all five simultaneously.

---

## 2. Scenario Taxonomy

| ID | Title | Category | Difficulty | Expected Verdict | Tier |
|---|---|---|---|---|---|
| BEC-SUBTLE-001 | Thread Hijack with Plausible Continuity | subtle_fraud | high | ESCALATE | 1 |
| BEC-FP-001 | Suspicious-Looking but Legitimate Rush Invoice | false_positive_trap | high | ALLOW | 1 |
| BEC-FRAUD-001 | New Vendor Impersonation — Domain Lookalike | fraud | low | ESCALATE | 1 |
| BEC-SUBTLE-002 | Routing Change Buried in Routine Status Update | subtle_fraud | high | ESCALATE | 2 |
| BEC-SUBTLE-003 | Approval-Chain Compromise with Clean Surface | subtle_fraud | high | ESCALATE | 2 |
| BEC-FP-002 | Vendor Domain Migration with Valid Notification Trail | false_positive_trap | high | ALLOW | 2 |
| BEC-FRAUD-002 | Duplicate Invoice with Changed Bank Account | fraud | low | ESCALATE | 2 |
| BEC-CLEAN-001 | Routine Monthly Invoice — Known Vendor, Matching Details | clean | low | ALLOW | 3 |
| BEC-CLEAN-002 | First Invoice from New Vendor — Properly Onboarded | clean | low | ALLOW | 3 |
| BEC-CLEAN-003 | Large Invoice with All Approvals — Capital Equipment | clean | low | ALLOW | 3 |
| BEC-FP-003 | Header Anomaly from Legitimate Email Infrastructure Change | false_positive_trap | high | ALLOW | 3 |
| BEC-FRAUD-003 | CEO Fraud — Impersonation with Urgent Wire Request | fraud | low | ESCALATE | 3 |

**Category distribution:** 3 clean / 3 fraud / 3 subtle_fraud / 3 false_positive_trap
**Verdict distribution:** 6 ALLOW / 6 ESCALATE
**Difficulty distribution:** 6 low / 0 medium / 6 high

---

## 3. Priority Tiering

### Tier 1 — Core Differentiators (Run First)

These three scenarios produce the clearest separation between architecture classes. Run these first. If time or budget is constrained, Tier 1 alone provides the essential benchmark result.

| ID | Why It's Tier 1 |
|---|---|
| **BEC-SUBTLE-001** | The canonical Holo test case. Thread hijack with metadata-only signals (message-ID break, IP shift). No surface-level red flags. Only compounding cross-field reasoning catches this. |
| **BEC-FP-001** | The hardest false-positive trap. Triggers four escalation criteria simultaneously (urgency, unusual amount, off-cadence, changed terms) — but every signal has a legitimate contextual explanation in the thread. Tests whether the system can reason about signal causation, not just signal presence. |
| **BEC-FRAUD-001** | The baseline fraud floor. Domain lookalike, auth failure, bank not on file. Every architecture should catch this. If an architecture fails here, the rest of the results are not interpretable. |

### Tier 2 — Strong Differentiators

These four scenarios provide meaningful architecture separation beyond Tier 1. Include when running a full benchmark comparison.

| ID | Why It's Tier 2 |
|---|---|
| **BEC-SUBTLE-002** | Bank change embedded in project update. Tests whether primary-intent classification blinds the system to secondary payload. |
| **BEC-SUBTLE-003** | Phantom approver + sequence violation with otherwise clean surface. Tests organizational-graph reasoning. |
| **BEC-FP-002** | Vendor domain migration with full documentation trail. Tests whether the system reconciles sender_history vs vendor_record views of a domain change. |
| **BEC-FRAUD-002** | Duplicate invoice + bank change + incomplete approvals. Tests payment history cross-reference. Multiple independent signals. |

### Tier 3 — Baseline Coverage

These five scenarios test that systems don't break on common cases. They differentiate less between architectures but provide essential precision calibration.

| ID | Why It's Tier 3 |
|---|---|
| **BEC-CLEAN-001** | Routine monthly invoice, nine-year vendor. All systems should ALLOW. Escalating this signals a broken false-positive rate. |
| **BEC-CLEAN-002** | First invoice from properly onboarded new vendor. Tests new-vendor path without fraud signals. |
| **BEC-CLEAN-003** | Large capital invoice ($94,500) with complete three-tier approvals. Tests that large amounts alone don't trigger escalation. |
| **BEC-FP-003** | SPF soft-fail explained by documented infrastructure migration. Tests contextual resolution of a technical anomaly. |
| **BEC-FRAUD-003** | CEO impersonation with urgency/secrecy pattern. No invoice, no PO, no vendor record, auth fail. Should be caught by all architectures. |

---

## 4. Architecture Predictions

The following table summarizes expected performance by architecture class. "Pass" means correct verdict. "Fail" means incorrect verdict. "Partial" means correct verdict but incomplete evidence reasoning.

| Scenario | A1 Naive | A2 Checklist | A3 Multi-Pass Solo | A4 Parallel Multi-Model | A5 Holo |
|---|---|---|---|---|---|
| BEC-SUBTLE-001 | **Fail** (ALLOW) | **Fail** (ALLOW) | Partial | Partial | **Pass** |
| BEC-FP-001 | **Fail** (ESCALATE) | **Fail** (ESCALATE) | Partial | Partial | **Pass** |
| BEC-FRAUD-001 | Pass | Pass | Pass | Pass | Pass |
| BEC-SUBTLE-002 | **Fail** (ALLOW) | **Fail** (ALLOW) | Partial | Partial | **Pass** |
| BEC-SUBTLE-003 | **Fail** (ALLOW) | **Fail** (ALLOW) | Partial | **Fail** (ALLOW) | **Pass** |
| BEC-FP-002 | **Fail** (ESCALATE) | **Fail** (ESCALATE) | Pass | Pass | Pass |
| BEC-FRAUD-002 | Pass | Pass | Pass | Pass | Pass |
| BEC-CLEAN-001 | Pass | Pass | Pass | Pass | Pass |
| BEC-CLEAN-002 | Pass | Pass | Pass | Pass | Pass |
| BEC-CLEAN-003 | Pass | Pass | Pass | Pass | Pass |
| BEC-FP-003 | **Fail** (ESCALATE) | **Fail** (ESCALATE) | Partial | Partial | **Pass** |
| BEC-FRAUD-003 | Pass | Pass | Pass | Pass | Pass |

**Predicted pass rates:**

| Architecture | Predicted Pass Rate | Notes |
|---|---|---|
| A1 — Naive Single-Pass | ~58% (7/12) | Fails all 3 subtle_fraud + 2 of 3 FP traps |
| A2 — Checklist / Rules Engine | ~58% (7/12) | Same failure modes as A1; checklist application is the problem, not LLM capability |
| A3 — Multi-Pass Solo | ~75% (9/12) | Partially catches subtle_fraud; still fails hardest FP traps |
| A4 — Parallel Multi-Model | ~75–83% (9–10/12) | Catches some conjunctive signals; fails phantom approver (no shared state for correlation) |
| A5 — Holo | ~92–100% (11–12/12) | Compounding postmortems surface conjunctive signals; contextual reasoning resolves FP traps |

*These are directional predictions based on architectural reasoning, not empirical measurements. Actual results may vary by model capability, prompt quality, and implementation.*

---

## 5. Scoring Methodology

### Per-Scenario Scoring

Each scenario is scored on a 0–3 scale:

| Score | Criteria |
|---|---|
| **3 — Full credit** | Correct verdict AND all `required_evidence_cited` items present in explanation |
| **2 — Partial credit** | Correct verdict AND at least half of required evidence cited |
| **1 — Minimal credit** | Correct verdict with insufficient evidence (verdict correct but for wrong reasons) |
| **0 — No credit** | Incorrect verdict, regardless of reasoning quality |

### Aggregate Metrics

From the per-scenario scores, compute:

- **Overall accuracy:** (scenarios with score ≥ 1) / 12
- **Full-credit accuracy:** (scenarios with score = 3) / 12
- **False positive rate:** (ALLOW scenarios escalated) / 6
- **False negative rate:** (ESCALATE scenarios allowed) / 6
- **Tier 1 score:** sum of scores on BEC-SUBTLE-001, BEC-FP-001, BEC-FRAUD-001 (max = 9)
- **Subtle fraud score:** sum of scores on BEC-SUBTLE-001, BEC-SUBTLE-002, BEC-SUBTLE-003 (max = 9)
- **FP resistance score:** sum of scores on BEC-FP-001, BEC-FP-002, BEC-FP-003 (max = 9)

### Differentiation Score

The differentiation score measures how well the architecture handles the scenarios that separate it from simpler approaches:

```
differentiation_score = (subtle_fraud_score + fp_resistance_score) / 18
```

A system with perfect differentiation (1.0) catches all subtle fraud without any false positives on the trap scenarios. A system at 0.5 is performing at chance on these categories.

---

## 6. Design Principles

### Why BEC?

BEC is the highest-loss form of business email fraud ($2.9B in US losses reported to FBI IC3 in 2023). It is also architecturally ideal as a benchmark because:

1. Ground truth is unambiguous — there is a correct verdict for each scenario.
2. Signals span multiple modalities — email metadata, document content, payment systems, organizational data.
3. Signal strength is graded — some signals are individually definitive, most are not.
4. Context determines interpretation — the same signal (SPF soft-fail, urgency, domain change) can be legitimate or fraudulent depending on other contextual evidence.

### Why These Signal Types?

The benchmark covers six signal types that map directly to the `BEC_CATEGORIES` in `llm_adapters.py`:

| Signal Type | Coverage Matrix Key | Benchmark Scenarios |
|---|---|---|
| Sender identity verification | `sender_identity` | BEC-FRAUD-001, BEC-FRAUD-003, BEC-SUBTLE-001 |
| Invoice amount analysis | `invoice_amount` | BEC-FP-001, BEC-CLEAN-001 through 003 |
| Payment routing / bank account | `payment_routing` | BEC-SUBTLE-001, BEC-SUBTLE-002, BEC-FRAUD-001, BEC-FRAUD-002 |
| Urgency / pressure patterns | `urgency_pressure` | BEC-FP-001, BEC-FRAUD-003 |
| Domain spoofing | `domain_spoofing` | BEC-FRAUD-001, BEC-FRAUD-003, BEC-FP-002, BEC-FP-003 |
| Approval chain integrity | `approval_chain` | BEC-SUBTLE-001, BEC-SUBTLE-002, BEC-SUBTLE-003, BEC-FRAUD-002 |

### Why the Conjunction Matters

The hardest scenarios (difficulty: high) are hard precisely because no single signal is sufficient. In BEC-SUBTLE-001:

- Bank account changed — plausible, could be a legitimate treasury update
- Message-ID format breaks — could be a different email client
- Originating IP shifts — could be the vendor working remotely
- No formal bank change process — could have been verbal, unrecorded

Each signal alone is deniable. The conjunction is not. This is the core thesis of Holo's architecture: structural independence between models, combined with shared context, is required to reliably surface conjunctive signals because each model independently contributes a piece of the pattern before the synthesis model assembles the whole.

### Why False-Positive Traps?

An architecture optimized purely for recall (catching all fraud) will over-escalate. In a production payment environment, false positives have real costs:

- Vendor payment delays causing supply chain disruption
- AP team workload from manual review of legitimate invoices
- Vendor relationship damage from perceived incompetence
- Operational credibility loss for the AP department

BEC-FP-001, BEC-FP-002, and BEC-FP-003 are designed to trigger naive escalation criteria while being genuinely legitimate. They test whether the system can contextualize evidence rather than apply rules mechanically. A system that achieves 100% recall on fraud scenarios at the cost of 50% false-positive rate on legitimate scenarios is not production-ready.

---

## 7. Known Gaps and Future Scenarios

The current 12-scenario library provides coverage of the most important BEC signal types but has known gaps:

### Missing Signal Types

- **Insider threat / compromise of internal account:** No scenario tests an email from a legitimate internal account being used by an attacker (e.g., compromised AP Clerk sending approval from their real account).
- **Multi-step orchestrated attacks:** No scenario spans multiple payment requests that are individually borderline but collectively reveal a pattern.
- **Vendor portal attacks:** No scenario involves manipulation of a vendor self-service portal rather than direct email.
- **Supply chain impersonation:** No scenario involves an attacker impersonating a vendor's vendor (sub-supplier).

### Missing Difficulty Tiers

- **Medium difficulty:** The current library has 6 low and 6 high scenarios with nothing in between. Medium-difficulty scenarios (clear signals but requiring one cross-field lookup, not conjunctive reasoning) would improve calibration resolution.

### Missing Context Types

- **Phone call context:** Some BEC attacks combine email with a phone call. No scenario includes a phone call transcript as part of the context.
- **ERP / accounting system context:** The current scenarios use a simplified vendor record. A richer ERP context (payment terms, contract history, credit limits) would enable more nuanced scenarios.
- **International payments:** Wire transfers to international accounts introduce additional signals (SWIFT codes, foreign correspondent banks, OFAC screening) not currently represented.

### Suggested Next Scenarios

| Proposed ID | Title | Rationale |
|---|---|---|
| BEC-SUBTLE-004 | Insider-Assisted Bank Change Approved by Compromised Manager | Tests whether phantom approval by a real-but-compromised employee is caught |
| BEC-SUBTLE-005 | Slow-Burn Vendor Relationship Poisoning | Attacker makes three small legitimate-looking changes over 60 days before the large fraudulent payment |
| BEC-FP-004 | Legitimate Emergency Wire — CFO Authorized via Known-Good Channel | Tests whether the system handles a legitimate unusual payment with proper out-of-band verification trail |
| BEC-CLEAN-004 | International Vendor — Known Routing, All Controls Met | Tests that international payments from properly onboarded vendors are not over-flagged |
