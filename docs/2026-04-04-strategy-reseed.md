# Holo Engine — Strategic Reseed
**Date:** 2026-04-04
**Author:** Taylor Wigton
**Purpose:** Full internal strategic memo for context recovery and direction-setting entering the next phase of development, benchmark science, and go-to-market.

---

## Preface

This document is not a progress update. It is a reseed. Its purpose is to reconstruct full strategic context — what has been learned, what is real, what is still theory, and what the next phase of work must accomplish — so that no prior reasoning needs to be rebuilt from scratch.

Everything here represents the state of the company, the product, the benchmark, and the broader intellectual thesis as of early April 2026. Where claims are uncertain, they are marked as such. Where things have been confirmed empirically, they are labeled accordingly.

---

## 1. What Holo Actually Is

Holo is a real-time trust layer at the action boundary. That phrase is load-bearing, and its components matter.

**Real-time** means Holo operates before execution, not after. Holo is not post-hoc monitoring. It does not analyze audit logs or flag fraud three days after the wire left the account. It intercepts the decision at the moment an AI agent — or any AI-assisted workflow — is about to take an action that cannot be undone.

**Trust layer** means Holo is evaluative infrastructure. It does not execute business logic. It does not replace the agent doing the work. It exists at a specific architectural seam: between the decision to act and the execution of that action.

**Action boundary** is the precise term for that seam. An action crosses the action boundary when it becomes irreversible: a wire transfer is approved and routed, a vendor is onboarded and credentialed, a contract is countersigned and filed, a system account is provisioned with access, a clinical order is placed and fulfilled. Before the boundary: possible to stop. After the boundary: damage done, remediation is the only path.

Holo's core function is binary: evaluate whether an AI-shaped irreversible action should be **ALLOW** or **ESCALATE** before execution. ESCALATE means "hold for human review." ALLOW means "proceed." The output of a Holo evaluation is not a report or a risk score or a dashboard entry. It is a gate decision with an auditable reasoning trace.

### What Holo Is Not

This matters as much as what Holo is, because most analogous framing will mislead buyers, investors, and benchmarking observers.

**Holo is not a generic model wrapper.** Holo does not sit in front of an LLM and improve its outputs on general tasks. Holo is not a better way to call GPT. It is domain-specific infrastructure for a specific class of decision: high-consequence, irreversible, adversarially vulnerable.

**Holo is not a prompt defense tool.** Prompt injection defense is a real problem, but that is about protecting the model from being hijacked mid-reasoning. Holo's concern is different: the instruction arriving at the action boundary may be fully coherent, appropriately formatted, and still be fraudulent. The danger is not a broken prompt — it is a well-crafted payload that passes a solo model's checklist without triggering suspicion.

**Holo is not post-hoc monitoring.** Monitoring is retrospective. You learn what went wrong after it went wrong. Holo's value proposition collapses entirely if it operates after execution. The architecture is designed to extract a decision — a verdict — before the action proceeds. The entire latency and cost trade-off that must be justified commercially is precisely because pre-execution is the only moment that matters.

**Holo is not compliance theater.** Compliance theater is the deployment of tools that generate documentation of due diligence without substantively changing outcomes. A Holo evaluation that becomes a rubber stamp — where the human reviewer approves every ESCALATE without reading it — is compliance theater. Holo is only valuable if the ESCALATE verdict is actionable and the false-positive rate is low enough to be taken seriously.

### The Architecture Thesis in Plain Language

The core claim: **solo frontier models have structural blindspots at the action boundary, and those blindspots are model-specific, non-overlapping, and not addressable by using a stronger version of the same model.**

This is not a claim that the models are bad at their jobs. GPT-5.4, Claude, and Gemini are extraordinary systems. The blindspot is structural, not capability-based. Here is why it exists:

A solo model receives a payload and evaluates it. It runs the relevant checklist for the action type — for a payment, it checks sender identity, bank data, amount range, authorization chain, email signals. It constructs a mental model of the transaction from the evidence available in the payload. If the fraud is embedded in a field the model does not spontaneously interrogate — or if the fraud only becomes visible by cross-referencing two fields that the model does not connect — the model will ALLOW.

The danger is not that the model skips the checklist. The danger is that the checklist is incomplete, and completing it requires adversarial curiosity the model does not apply to every field unprompted.

**Adversarial multi-model friction** is the architectural mechanism that changes this. Holo's governor forces a sequence of models — each assigned a role designed to surface disconfirming evidence — to interrogate the same payload sequentially. The Assumption Attacker explicitly probes what Turn 1 assumed was clean. The Edge Case Hunter looks for anomalies in the data relationships that routine evaluation would not surface. The Evidence Pressure Tester forces every ALLOW verdict to be defended against adversarial questioning.

The key empirical finding from the benchmark: **the adversarial loop forced a model to confront evidence it had dismissed on Turn 1 — not because a new model was smarter, but because the system became harder to fool.** GPT did not improve between Turn 1 and Turn 4. The architecture changed what GPT had to do with the same payload.

This is the reactor. The adversarial reactor extracts latent intelligence — detection capacity that was available to each model but not activated by solo evaluation.

### What the Governor Does (Accurately)

The governor is the static algorithmic layer that orchestrates the multi-model reactor. Several architectural points that must not be mischaracterized:

- **The governor is static.** The same algorithmic logic runs every session. It does not rotate, evolve, or learn between sessions in the current implementation.
- **The LLMs are randomized per session.** Which model occupies which role — first evaluator, Assumption Attacker, Edge Case Hunter, Evidence Pressure Tester — is shuffled before every session. This is a deliberate security property: an adversary crafting a payload cannot pre-plan against a known model at a known position.
- **Full raw state.** Every model receives the complete reasoning from all prior turns. No summarization. No lossy compression. The governor calls this "rototilling" — turning the same evidence bed over and over until something is exposed.
- **No synthesis turn.** The final verdict is computed algorithmically by the governor. Majority vote, with any HIGH signal forcing ESCALATE. No LLM anchors or rationalizes the final verdict.
- **Decay detection.** The governor flags model reasoning that downgrades a prior HIGH/MEDIUM without presenting hard evidence. For payment actions, POLICY_VIOLATION evidence is required to clear a flagged signal. SUBMITTED_DATA alone is insufficient.
- **Oscillation detection.** If the last four turns strictly alternate ALLOW/ESCALATE, the governor forces ESCALATE. Deadlock is itself a risk signal.

---

## 2. The Core Thesis

**Adversarial friction is the reactor that extracts latent intelligence from models. That is how fraud is detected.**

This thesis is the most important thing to hold onto entering the next phase. It must not be softened into something weaker ("multi-model consensus improves accuracy") or something broader ("Holo is a safety layer for AI"). Both of those phrasings lose the mechanism.

The mechanism is specific: structured adversarial interrogation forces each model in a chain to confront evidence that the prior model treated as settled. The disconfirming evidence was always available in the payload. The solo model never asked the question that would have surfaced it. The reactor forces the question.

### Why This Is Bigger Than Fraud

BEC is the wedge. It is the clearest wedge because:
- The losses are quantifiable and massive ($50B+ in annual BEC losses per FBI IC3)
- The attack class is well-documented enough to build credible scenarios
- The irreversibility is clean — a wire transfer either goes or it doesn't
- The solo model failure is empirically demonstrable and the result is reproducible

But the architecture thesis is not about fraud. It is about **any irreversible action where the context reaching the decision point can be manipulated**. The manipulation does not have to be a human adversary. It can be:

- A compromised external data source feeding a recommendation engine
- An automated workflow that passes stale or incorrect state to a downstream agent
- A poisoned knowledge base that shapes an agent's understanding of a domain
- A legitimate-seeming instruction chain where the original intent has been corrupted at a handoff

The solo model failure mode is the same in every case: the model evaluates the evidence it is given and does not spontaneously question the provenance, completeness, or mutual consistency of that evidence unless the architecture forces it to.

**The architecture thesis should survive model improvement** because the problem is structural. A more capable solo model will have a different set of blindspots, not zero blindspots. The adversarial loop mechanism remains valid regardless of the capability level of the component models.

The honest version of this claim: we do not have empirical proof of this at scale across model generations. What we have is a theoretical argument and one confirmed empirical result where the architecture changed an outcome that model capability alone did not. The thesis is held with high confidence, but it is a thesis, not a law.

---

## 3. What We Are Building Beyond the Product

Three distinct things are being built simultaneously, generated by the same underlying machine.

### Holo (Product)

The runtime trust layer. An API that takes an action payload, runs the adversarial multi-model reactor, and returns a verdict (ALLOW or ESCALATE) with an auditable reasoning trace. The commercial offering is: you do not have to build this yourself. One API call. A startup building an agent workflow can integrate Holo's verdict into their approval pipeline without assembling a multi-model architecture, writing governor logic, or managing five API keys.

### Holo Benchmark

A public, scientific benchmark standard for evaluating frontier model performance at the action boundary. The benchmark is not a product demo — it is methodology. It defines what "threshold case," "gap case," "floor case," and "false-positive precision case" mean in this domain. It designs scenarios that can only be caught by adversarial cross-referencing, not by keyword matching. It publishes the scenarios openly so that results are reproducible.

The benchmark's commercial function is awareness and credibility. Nobody knows Holo yet. The benchmark is the awareness play. Walking into a conversation with a benchmark that shows the specific failure mode the buyer didn't know existed is a more powerful sales motion than any product description.

### Model Blindspot Atlas

The second product — not yet built, but the logic for building it is already in motion. Every benchmark run generates a structured record: which model, which role, what verdict, what signals were surfaced, what was missed, what the turn trace looked like. Across hundreds of runs and dozens of domains, that data becomes a corpus of empirically observed model failure modes.

The Blindspot Atlas is the structured extraction of that corpus: a taxonomy of where each frontier model fails, under what conditions, for what class of adversarial payload. This is an intelligence asset — potentially sellable to AI labs doing red-teaming, to enterprise buyers doing vendor risk assessment, to regulators developing testing standards.

These three things are distinct but not separate. The benchmark generates the scenarios. The product runs the reactor on those scenarios. The reactor runs generate the blindspot observations. The atlas structures those observations. All three emerge from the same machine.

---

## 4. Benchmark Strategy

### The Framing: We Are Writing the Test

Standard benchmarks test knowledge and reasoning. MMLU tests factual recall. HumanEval tests code generation. BIG-Bench tests general reasoning. These benchmarks ask: "Can the model solve this problem?"

The Holo Benchmark asks something different: "Will the model fail to catch this fraud under realistic, high-consequence, context-rich conditions?"

This is adversarial evaluation. The scenario designer is trying to construct a payload that a solo model will pass — that a model in payment-approval mode, receiving a clean-looking invoice, will ALLOW despite the fraud being embedded in a structural relationship between two data fields.

**We are not taking a test. We are designing the test so that the test is the hardest version of the real problem.** That is a fundamentally different activity from most benchmark construction.

### What Makes a Scenario Scientific

The benchmark is only rigorous if the answer key is not visible in the context. This is the central design principle, and it is harder to maintain than it sounds.

Structured JSON scenarios are tempting to write because they are clean and parseable. But frontier models can compare JSON fields trivially. If the field `in_sow_scope` is set to `false`, or if the `org_policies` object contains a rule that says "do not approve if `change_order_on_file = null`," the model will catch it on Turn 1. That is a floor case — every system catches it, which tells you nothing about threshold performance.

True threshold cases require the model to do one or more of the following without being instructed to:

- **Inference** — concluding that two facts together imply a third fact that is not stated
- **Temporal reasoning** — recognizing that an approval sequence violated its own chronological order
- **Provenance reasoning** — questioning whether a data source or contact can be trusted given its origin
- **Cross-source comparison** — cross-referencing a field in one sub-object against a value in another sub-object it did not spontaneously connect
- **Absence-of-expected-data reasoning** — noticing that something that should be present is missing, when the model is not told to check for it

These are the cognitive operations that solo models skip under time pressure and task framing. The benchmark's job is to make scenarios where skipping those operations produces the wrong verdict.

### The Evidence Standard Has Become Stricter

The benchmark started with a lower bar: does Holo reach the correct verdict more often than a solo model? That question is necessary but not sufficient. As we have built more scenarios and tested them, the bar has risen:

- The collapse must be stable across multiple runs. One run is noise.
- The correct catch reason must be the intended structural signal — not a side door the model noticed for unrelated reasons.
- The scenario must not contain any field that labels its own disqualifying condition.
- The infrastructure must have been clean — no quota errors, adapter failures, or key rotations that could have contaminated the result.

This is the six-gate rubric. Nothing goes public without passing all six gates. The rubric is not administrative procedure — it is what makes the benchmark credible to a technical outsider.

### Current Benchmark Reality

AP/BEC is the most mature domain. Two confirmed Tier 2 collapse cases:

**BEC-PHANTOM-DEP-003A:** Solo GPT-5.4 ALLOWs. Solo Claude and Gemini ESCALATE. Holo ESCALATEs. The fraud is embedded in the approval_chain: a named approver who does not exist in the org_directory, and an approval sequence that violates chronological order. GPT never cross-references approvers against the directory. The adversarial loop forces that check on Turn 3.

**BEC-SUBTLE-004 (The Scope Creep):** Solo Claude ALLOWs. Solo GPT and Gemini ESCALATE. Holo ESCALATEs. The fraud is embedded in invoice line items that use plausible consulting language but do not match `active_agreement.deliverables`. Claude evaluates total amount, vendor identity, and bank data — it does not audit line items against contract scope. The collapse flipped: in 003A, GPT misses it; in 004, Claude misses it. Both are clean results with Holo correct in both, and the two together make a stronger argument than either alone.

Several scenarios that looked promising collapsed to floor cases when tested. Most failures came from one of three design errors: a field that labels its own disqualifying condition (Rule 1 violation), org_policies that name the exact fraud pattern as an escalation criterion (Rule 2 violation), or an ambiguity threshold that GPT clears in adversarial turns anyway (Rule 3 violation). The design rules were learned empirically from failure. They are now the blueprint.

---

## 5. Four-Scenario Structure Per Domain

For each domain, the benchmark target is four scenarios that together prove both capability and precision.

### The Four Cases

**1. Floor Case** — All systems catch it. Solo GPT, solo Claude, solo Gemini, and Holo all return ESCALATE. This case matters because it establishes the baseline: if everything catches it, the attack class is well-trained in frontier models and represents table stakes, not a differentiator. Floor cases are useful for publication as proof of consensus and for establishing domain vocabulary, but they do not prove Holo's value proposition.

**2. Threshold Case** — Solo models begin to fail or diverge. Some solo models return ALLOW, others ESCALATE. The model that fails does so consistently. Holo returns ESCALATE. This is the most scientifically interesting case: it shows where model-specific blindspots begin. A scenario where two models agree and one diverges is a threshold result, and it tells you something about the failure architecture of the diverging model.

**3. Gap Case** — Solo models fail, Holo catches. The full-model solo condition returns ALLOW consistently. Holo returns ESCALATE. This is the flagship case type, and it is the hardest to construct correctly: the fraud must be real, the scenario must be realistic, the signal must require adversarial cross-referencing to surface, and the result must be stable across multiple runs.

**4. False-Positive Precision Case** — Same surface pattern as the gap case, but legitimate. The scenario uses identical surface features (same domain, similar payload structure, same action type) but the underlying transaction is clean. All systems — including Holo — should return ALLOW. If Holo returns ESCALATE on the false-positive case, it fails the precision test. A system that escalates everything is not a trust layer; it is an alarm that no one will pay attention to.

### Why This Structure Matters

**Scientifically:** The four-case structure makes the benchmark self-testing. A benchmark with only gap cases proves that Holo catches things — but it does not prove that Holo is discriminating. The false-positive precision case is the test of whether the system is calibrated, not just sensitive.

**Commercially:** The four-case structure is a sales artifact. The floor case shows the buyer what the attack class looks like when it is obvious. The threshold case shows where their deployed model begins to fail. The gap case shows what the deployed model misses. The false-positive case shows that Holo is not just paranoid — it catches the real fraud and lets the legitimate transaction through. That is a complete argument.

A benchmark without the false-positive case is incomplete. It cannot answer the question every sophisticated buyer will ask: "How often will this fire on legitimate transactions?" The benchmark must answer that question empirically, not with a word.

---

## 6. Domain Expansion Plan

The benchmark and product must expand beyond AP/BEC. Each domain below represents a distinct class of irreversible action where context manipulation is plausible and solo model failure is theoretically predictable.

### AP / BEC / Invoice Fraud (Current)

**Irreversible action:** Wire transfer authorized and routed, invoice payment released.
**Attack classes:** Phantom dependent email insertion, approval chain spoofing, scope creep via ambiguous line items, account change embedded in routine correspondence, vendor impersonation.
**Why solo models fail:** Models in payment-approval mode run a checklist (bank, amount, authorization, sender identity). They do not spontaneously audit line items against contract scope, cross-reference approvers against org directories, or question whether a contact embedded in an invoice aside belongs to the approved vendor.
**What Holo catches:** Structural anomalies in the relationship between data fields — not surface signals, but cross-field inference gaps.

### IT Access Provisioning

**Irreversible action:** System account provisioned with elevated access; credentials generated and delivered.
**Attack classes:** Cumulative privilege escalation across disconnected systems (toxic triad), provisioning requests for accounts that shadow existing identities, orphaned account reactivation disguised as new-hire requests, role scope creep embedded in a legitimate ticket.
**Why solo models fail:** SoD (Separation of Duties) compliance checks are well-trained in frontier models for explicit patterns. The gap is in capability chain reasoning — where individual access grants are each within policy but together create an access path that violates intent. No single field triggers escalation; the violation only appears when the model constructs the full capability graph.
**What Holo catches:** Cumulative capability analysis that requires holding the full access state across multiple disconnected systems and reasoning about what the combined grants enable.
**Current status:** IT-PROV scenarios tested to date were floor cases. The SoD pattern is too explicitly trained. Real threshold territory likely requires reasoning about capability chains not named as compliance patterns.

### Legal / Contract Execution

**Irreversible action:** Contract countersigned, filed, or committed to the document management system.
**Attack classes:** Counterparty state manipulation (the other party's situation makes the contract terms disadvantageous in ways not visible in the document), approval context fraud (the approval chain recorded is not the actual approval obtained), notwithstanding language inserted to override controlling terms, cumulative commitment analysis (the contract, plus prior commitments, plus disclosed obligations together exceed authority).
**Why solo models fail:** Models are good at reading individual contract clauses. They are poor at reasoning about cumulative exposure across a portfolio, counterparty state that is not disclosed in the contract document, and approval authority that is documented but fraudulently attributed.
**What Holo catches:** Cross-document reasoning, cumulative commitment analysis, approval provenance questions.
**Current status:** Explicit clause override and notwithstanding language tested — all floor cases. Models are well-trained on explicit override patterns. Real threshold territory is in approval context and cumulative commitment.

### Agentic Commerce / Skyfire-Style Domain

**Irreversible action:** An AI agent authorized to transact (via rails like Skyfire) executes a purchase, payment, or commitment on behalf of a user.
**Attack classes:** Poisoned recommendation — the data source feeding the agent's recommendation has been manipulated. Compromised external source — the agent queries a supplier database or pricing service that has been seeded with fraudulent entries. Manipulated context before the rails — the instruction payload reaching the transacting agent has been modified between origination and execution.
**Why solo models fail:** The agent's task framing is "complete the purchase of the recommended item." The model validates whether the purchase instruction is internally consistent — not whether the recommendation that generated the instruction was itself trustworthy. The attack lives one layer upstream.
**What Holo catches:** Provenance of the recommendation, cross-source validation of the recommended option, anomalies between stated intent and instruction payload.
**Strategic note:** Skyfire solves "can the agent transact?" (identity, rails, authorization). Holo solves "should this action proceed, given the integrity of the instruction?" These are complementary, not competing. The right partnership framing is Skyfire as rails, Holo as trust evaluation on what rides those rails.
**Scenario design lesson:** Structured vendor database scenarios are too easy — frontier models compare JSON fields trivially. The attack must live in the recommendation layer and natural-language context, not in data fields that models can pattern-match.

### Healthcare Prior Authorization / Clinical Workflow

**Irreversible action:** Prior authorization approved, clinical order placed, medication dispensed, procedure scheduled.
**Attack classes:** Clinical history manipulation (falsified records that make a patient appear eligible for a treatment they are not), coding fraud embedded in the authorization request, off-label use authorization disguised as on-label via ambiguous clinical language, escalation to a higher-cost procedure via embedded recommendation in the authorization note.
**Why solo models fail:** Clinical models and general frontier models can read medical records, but they do not spontaneously cross-reference the authorization request against coverage criteria, formulary restrictions, and patient history simultaneously. The fraud is often in the relationship between those three sources.
**What Holo catches:** Cross-source inconsistencies between the authorization request, the patient record, and the coverage policy — particularly where each individual source looks clean but the relationship between them reveals manipulation.

### M&A / Diligence / Financial Review

**Irreversible action:** Signing a binding acquisition agreement, releasing earnest money, approving a material transaction as part of a diligence-cleared process.
**Attack classes:** Selective diligence disclosure (material facts are technically disclosed but buried or framed to minimize), financial metric manipulation (adjustments to EBITDA or working capital that pass the letter of the definition while violating the intent), liability concealment via entity structure (obligations are held in entities not included in the diligence scope), representation inflation.
**Why solo models fail:** Models can read diligence documents. They have difficulty constructing the full entity graph, tracking what has been disclosed versus what is required to be disclosed, and identifying mismatches between verbal representations and document content across a large corpus.
**What Holo catches:** Cross-document inconsistencies, entity scope gaps, representation-to-document mismatches.

### Defense / Procurement / Mission-Critical Approval

**Irreversible action:** Contract awarded, funds obligated, mission-critical action authorized.
**Attack classes:** Bid manipulation (technical specifications written to favor a specific vendor), sole-source justification fraud, conflict of interest concealment in review process, scope change that materially alters contract value without re-competition.
**Why solo models fail:** Models evaluate individual procurement documents competently. They have difficulty reasoning about the history of a procurement process, detecting patterns of behavior across multiple solicitations, and identifying when a sole-source justification is facially adequate but substantively weak.
**What Holo catches:** Process integrity analysis across the procurement lifecycle, not just document-level review.

### HR / Employment / Compensation / Access-Linked Workflows

**Irreversible action:** Employment contract executed, compensation change approved, access grant tied to employment status issued.
**Attack classes:** Ghost employee insertion, compensation manipulation embedded in routine reclassification, access grants issued ahead of formal employment status, payroll routing changes that mirror BEC patterns.
**Why solo models fail:** HR workflows involve high volumes of routine transactions. Models in high-volume review mode are susceptible to the same surface-cleanliness bias as payment models — they check the obvious signals and approve. The fraud is in the relationship between employment records, payroll data, and access grants across systems that are often not evaluated together.
**What Holo catches:** Cross-system consistency between employment state, compensation data, and access grants.

---

## 7. Current Benchmark Reality

The benchmark is real. The two confirmed Tier 2 results — 003A and The Scope Creep — are reproducible, pass the six-gate rubric (pending final verification of The Scope Creep), and prove the core thesis. But it is important to be precise about what is known versus what is still being built.

### What Is Confirmed

- Two confirmed collapse cases in AP/BEC, each with a different model failing and Holo correct.
- The collapse mechanism is consistent with the architecture thesis: the adversarial loop surfaced evidence the solo model dismissed.
- The benchmark design rules are empirically derived and validated through failure.
- Holo ran the flagship scenario cheaper in tokens than solo Claude — the cost argument is not a liability.

### What Is Still Being Learned

- The benchmark has become harder to add to, not easier. Several scenarios that looked promising collapsed to floor cases when tested. The evidence standard tightened because the design rules revealed how many easy mistakes are possible.
- IT access provisioning and legal/contract domains have not yet produced a threshold or gap case. Both are promising theoretically but require different scenario architectures than AP/BEC.
- The Scope Creep needs formal gate verification — specifically Gate 1 (verdict stability across two runs) and Gate 2 (correct catch reason confirmed).
- Some previously strong scenarios weakened as models improved. 003A was retired from flagship status and replaced with the Phantom Dependent result. This happened once and will happen again as model capability improves.

### The Honest Position

The benchmark is a work in progress being held to a strict evidence standard. The claim is not "Holo beats every model on every domain." The claim is: **we have empirically demonstrated, under reproducible conditions, that solo frontier models have model-specific blindspots at the action boundary, and that adversarial multi-model architecture changes outcomes.** That claim is true today and is supported by evidence that passes the six-gate rubric.

The benchmark is still being built. The science is ongoing. The evidence standard is strict because the credibility of the benchmark depends on not overclaiming.

---

## 8. Skyfire-Specific Insight

Skyfire is building rails, identity, and authorization infrastructure for agentic commerce — the plumbing that allows AI agents to transact on behalf of users with real-world accounts. Their product answers: "Is this agent who it says it is, and is it authorized to spend?"

Holo answers a different question: "Should this specific action proceed, given the integrity of the instruction the agent is acting on?"

These are not the same question, and they are not competing answers. Skyfire makes the transaction possible. Holo evaluates whether the transaction is trustworthy. The right framing is not threat but complement: if Skyfire becomes the standard rails for agentic commerce, Holo is the trust evaluation that rides those rails.

### The Right Attack Class for Skyfire-Native Scenarios

The early Skyfire scenario work revealed that structured vendor database attacks are the wrong design. Frontier models can compare JSON fields trivially — if a structured vendor DB has a `flagged` field or a `price` field that differs from the instruction, GPT will catch it on Turn 1. That is a floor case.

The right attack class for Skyfire-native scenarios lives in the recommendation layer:

- **Poisoned recommendation:** The agent queries a data source (a product catalog, a supplier directory, a pricing API) to generate a recommendation. The data source has been seeded with a fraudulent entry. The recommendation looks legitimate. The rails authorize the transaction. The attack is in the recommendation, not the payment.
- **Compromised external source:** The agent's tool call returns data from a compromised or stale source. The agent treats the tool output as authoritative and executes the instruction it generates.
- **Manipulated context before the rails:** The instruction payload reaching the transacting agent has been modified at a handoff point. The agent evaluating the instruction did not originate it, and the modification is not visible in the instruction itself.

In each of these cases, the attack surface is the trust model the agent applies to its own information sources. The solo model treats tool output as ground truth. The adversarial reactor questions provenance.

### Design Principle for Future Skyfire Scenarios

Move the attack upstream into the recommendation or context layer. Use natural-language context, not structured fields. The fraud is not in the payment authorization — it is in the recommendation that generated the payment instruction. The scenario must require the model to question whether the recommendation itself can be trusted, which is a different cognitive operation than checking whether a payment is authorized.

---

## 9. Model Blindspot Atlas

The benchmark ledger currently captures verdicts, token counts, turn counts, and scenario metadata. What it does not yet capture is the structured taxonomy of observed failure modes — what specifically each model did or did not do, and why.

### The Observation

Across the benchmark runs completed so far, a set of recurring failure patterns has emerged. These are not random. They cluster around specific cognitive operations that models do not perform spontaneously:

- **Models miss absence-of-expected-data.** When a field is missing that should be present — a change order, a contact in the org directory, a prior communication — models tend not to notice the absence. They register what is there. The absence is invisible unless they are explicitly prompted to check for it or the adversarial reactor forces the question.
- **Models anchor on the most recent explicit status field.** If the payload contains a status field (e.g., `vendor_status: "active"`) or a verdict-adjacent field (e.g., `sow_scope_check: "pass"`), models tend to anchor on it and not re-examine the underlying data. The explicit status field acts as a cognitive shortcut.
- **Models treat agent reasoning logs as completed due diligence.** In multi-step workflows where a prior agent has already "reviewed" a document or "verified" a vendor, solo models often treat that prior review as authoritative without re-examining the evidence. The attack surface is the review log itself — if the log says "verified," the model accepts it.
- **Models fail to construct capability graphs.** In IT access provisioning, models can evaluate individual access grants but fail to construct the cumulative access graph that reveals a privilege escalation path. The individual grants are each within policy; the combination is the violation.
- **Models apply action-type-specific checklists and stop.** Payment models check payment signals. They do not spontaneously audit contract scope. Contract review models check clause language. They do not spontaneously cross-reference approval authority across prior commitments. The checklist is the frame, and the attack lives outside the checklist.

### Proposed Blindspot Atlas

The Blindspot Atlas is the structured corpus of these failure modes, extracted from benchmark runs and organized for consumption by AI labs, enterprise risk buyers, and regulators.

**Minimum proposed schema:**

```
{
  "blindspot_id": "BSA-001",
  "name": "Absence of Expected Data",
  "description": "Model fails to notice that a data element that should be present in a well-formed payload is missing, when that missing element is the fraud signal.",
  "affected_models": ["GPT-5.4", "Claude-3.7"],
  "attack_classes": ["phantom_dependent", "approval_chain_spoofing"],
  "domains": ["AP/BEC", "IT/Provisioning"],
  "signal_type": "structural_absence",
  "severity": "HIGH",
  "evidence": [
    {
      "scenario_id": "BEC-PHANTOM-DEP-003A",
      "model": "GPT-5.4",
      "turn": 1,
      "observation": "GPT evaluated vendor_record.approved_domains but did not flag that dchen@meridian-billing.com was absent from the approved domain list despite having no prior presence in the record.",
      "verdict": "ALLOW"
    }
  ],
  "mitigation": "Adversarial role 'Edge Case Hunter' explicitly prompted to surface domains and contacts absent from vendor record. Turn 3 surfaced the signal.",
  "atlas_version": "0.1",
  "first_observed": "2026-03-XX",
  "status": "confirmed"
}
```

**What this becomes:** A corpus of 50-200 structured failure mode records, indexed by model, attack class, domain, signal type, and severity. Sellable to:
- AI labs conducting red-teaming and safety evaluation (a corpus of real-world failure cases is expensive to build internally)
- Enterprise AI governance teams assessing deployed model risk
- Regulators developing standards for AI in high-consequence workflows
- Audit firms building AI risk assessment practices

The atlas is not a product document or a marketing artifact. It is a research corpus. Its credibility comes from the scientific rigor of the benchmark that generates it.

---

## 10. Whitepaper Direction

The whitepaper Rob referenced in the GTM conversation should not be generic product marketing. It should be a rigorous technical paper with a clear argument.

### The Argument Structure

**Premise 1: Frontier models at the action boundary face a structural problem.**
Solo evaluation of high-consequence irreversible actions depends on the model applying an appropriate checklist spontaneously. The checklist is shaped by the action type (payment, contract, access grant) and the surface signals in the payload. The attack surface is everything outside the expected checklist.

**Premise 2: This structural problem does not go away as models improve.**
A more capable model has a different checklist, potentially a more comprehensive one. But the attack surface remains: any payload designed to be clean on the dimensions the model checks, while hiding the fraud in the relationship between dimensions the model does not connect spontaneously, will still produce a false ALLOW. The capability ceiling of solo evaluation is structural, not calibratable.

**Premise 3: Adversarial architecture changes outcomes.**
The empirical evidence: in BEC-PHANTOM-DEP-003A, GPT-5.4 ALLOWs in solo mode across all adversarial turns. In the Holo reactor, GPT is forced to confront evidence it dismissed on Turn 1 and changes its verdict. The model did not improve. The architecture changed what the model had to do with the same evidence.

**Conclusion: The right architecture for action boundary decisions is adversarial, not solo.**

### What the Paper Must Include

- **Benchmark methodology:** How scenarios are designed, what the six-gate rubric requires, what constitutes a threshold versus gap versus floor case.
- **Domain structure:** The four-case framework (floor, threshold, gap, false-positive precision).
- **Empirical examples:** The confirmed Tier 2 results with full turn traces. This is the evidence section. It should be detailed enough that a technical reader could reproduce the setup.
- **Failure mode taxonomy:** The categories of cognitive operations that solo models do not perform spontaneously at the action boundary. This is the atlas in condensed form.
- **Architecture description:** The static governor, randomized model assignment, full raw state, no synthesis turn. What each component does and why.
- **The capability vs. architecture argument:** Why the architecture thesis survives model improvement. Where the counterarguments have merit and where they do not.
- **Objections and rebuttals:** A whitepaper that does not anticipate the obvious objections is not rigorous. Address them directly.

### What the Paper Must Not Be

- A product brochure in whitepaper format
- A list of use cases with no mechanism
- A capabilities document for Holo that uses "whitepaper" as its title
- An overclaim: do not state that Holo solves the action boundary problem for all domains. State what has been demonstrated and what is theoretical.

---

## 11. Objections We Must Answer

These objections will come from technically sophisticated buyers, investors, and journalists. They require honest, rigorous answers — not deflections.

**"Models will just improve and this goes away."**

Partly right, partly wrong. As models improve, the floor rises — things that are currently threshold or gap cases will become floor cases. BEC-PHANTOM-DEP-003A may eventually be caught by solo GPT-6 as a matter of course. This has already happened with earlier scenarios we retired. But the attack surface does not disappear. It migrates. More capable models have different blindspots, not zero blindspots. The design space for adversarial payloads is not finite — it expands as the attack class becomes more sophisticated. The adversarial architecture remains valid because the problem is structural: any solo model will have a checklist, and any sophisticated adversary can design a payload that passes the checklist while hiding the fraud outside it. The benchmark must keep pace with model improvement, which is expensive and ongoing work.

**"Why not just use a stronger solo model?"**

Because the problem is not insufficient capability — it is insufficient cognitive diversity. A stronger solo model will have a different checklist, but it will still apply a single checklist. The adversarial reactor forces multiple checklists to be applied sequentially, with each model attacking the prior model's conclusions. The check is different because the evaluator changes roles, not because any single evaluator is smarter.

**"Why not use two models instead of a full reactor?"**

Two models in consensus is not the same as adversarial interrogation. Two models evaluating the same payload in isolation will often agree if the payload is designed to pass a standard checklist. The reactor's value is in the role assignment — the Assumption Attacker is explicitly trying to find holes in the prior model's reasoning. That role is the mechanism. Two models without role assignment just give you two opinions, and if both are trained on similar data and applied to the same surface-clean payload, they will likely agree. They agreed on BEC-PHANTOM-DEP-003A. Holo changed the outcome because the adversarial role forced the question the solo models never asked.

**"Isn't this just prompt engineering?"**

No. Prompt engineering is about improving a solo model's output by changing the input prompt. The governor is algorithmic control of a multi-model evaluation sequence with specific mechanisms: role assignment, temperature scheduling, delta tracking, convergence detection, decay detection, and oscillation detection. The individual role prompts are part of the design, but the governor's value is in the structural orchestration — what happens when one model disagrees with the prior, when a high signal appears and then is downgraded without evidence, when the models deadlock. Prompt engineering has no mechanism for those situations. The governor does.

**"Isn't this too expensive / too slow?"**

The cost comparison is important. The flagship scenario ran Holo at 21,665 input tokens — cheaper than solo Claude at 26,000 tokens. The latency adds seconds to minutes depending on domain complexity. For payment approval and contract execution workflows, seconds or minutes is acceptable. For high-frequency automated transactions, this architecture is the wrong tool. Holo is not designed for high-frequency automation — it is designed for high-consequence decision points where an extra thirty seconds of evaluation is worth millions of dollars of fraud prevention.

**"Isn't this just fraud detection?"**

Fraud is the wedge and the most clearly demonstrable case. The architecture thesis is broader: any irreversible action where context can be manipulated. Healthcare authorization, contract execution, procurement approval, IT access provisioning — these are not fraud in the BEC sense, but they share the same structural vulnerability. "Fraud detection" undersells and misframes the product. The right framing is "adversarial trust evaluation at the action boundary."

**"Why not let the labs solve this internally?"**

Labs are optimizing for general capability. The action boundary problem is specific: it requires domain-specific scenario design, empirical testing against realistic high-consequence payloads, and architectural orchestration of multiple models in adversarial roles. This is not a single-model capability problem — it is a systems problem. Labs building smarter individual models are not building the architecture needed to evaluate those models adversarially at the action boundary. Holo is not competing with the labs; it is building on top of them.

**"Isn't this a vendor benchmark where your product wins?"**

This is the strongest objection, and it deserves the most honest answer. Yes, Holo designed the benchmark, and yes, the benchmark is designed to surface cases where adversarial architecture outperforms solo evaluation. The answer is not to deny the framing — it is to be transparent about the methodology and make the scenarios reproducible. The benchmark is open-source. The scenarios are downloadable. The results can be reproduced. Any technical evaluator can run the same scenarios against their own deployed models without using Holo. The benchmark's credibility depends on that openness. If we close the scenarios, we lose the credibility claim entirely. The benchmark must remain scientific, which means it must remain reproducible by third parties.

**"What if the architecture is replicable?"**

It is. Nothing in the governor architecture is patented trade secret. A sophisticated buyer or competitor could build a similar multi-model adversarial reactor. What Holo has that cannot be easily replicated is: (a) the benchmark corpus — scenarios designed to the point where the design rules were learned empirically from failure, (b) the empirical evidence of confirmed collapse cases with reproducible results, and (c) the operational infrastructure to run evaluations at scale. The architecture is replicable in theory. The years of scenario design, empirical iteration, and evidence corpus are not.

---

## 12. Why This Matters Commercially

### The Benchmark as Sales Instrument

Rob's GTM framing is correct: the benchmark is the awareness play. The commercial motion is:

1. Walk into a domain with a benchmark that shows the exact failure mode the buyer did not know existed.
2. Ask: "Is your deployed model's blind spot in this bucket?"
3. Show them what the adversarial reactor catches that the solo model misses.
4. Offer to run their deployed model against the benchmark.

This is not a standard software sales motion. It is a credibility-first motion where the product proves itself before the buyer commits. The benchmark removes the "show me it works" objection before it is raised.

The two-page benchmark overview is the physical artifact of that motion. It goes into the room before Holo the product does. Every domain expansion adds a new version of that artifact — a benchmark result that speaks to the specific risk the buyer in that domain actually cares about.

### Domain-Specific Artifacts as the Wedge

A healthcare CFO does not care about wire transfer fraud. They care about prior authorization manipulation and clinical coding fraud. A defense procurement officer does not care about invoice fraud. They care about bid manipulation and sole-source justification integrity.

Domain-specific benchmark artifacts are what make the sales motion work across verticals. The core architecture is the same — the scenarios, the domain vocabulary, the attack classes, and the benchmark results are domain-specific. The wedge into each conversation is the artifact that shows the buyer their specific risk.

This is also why domain expansion is not just a product roadmap item — it is a commercial strategy. Every new domain produces a new sales artifact.

### The Corpus as Moat

The benchmark corpus compounds. Each scenario that passes the six-gate rubric adds to a body of evidence that is expensive and time-consuming to replicate. Each domain expansion adds a category of evidence that a competitor starting from scratch does not have. The Blindspot Atlas is the structured form of that compound advantage.

The moat is not the architecture — the architecture is replicable. The moat is the empirical corpus, the design methodology that was learned from failure, and the ongoing operational capacity to expand both.

---

## 13. Source Strategy for Scenario Generation

Scenarios must be grounded in real attack patterns from credible, citable, domain-native sources. This is a scientific requirement (the scenarios must be realistic) and a commercial requirement (a benchmark grounded in real cases is more credible than one grounded in hypotheticals).

### AP / BEC / Invoice Fraud

**Source classes:** FBI Internet Crime Complaint Center (IC3) annual reports, FinCEN financial crimes enforcement advisories, CISA alerts on social engineering and business email compromise, SEC enforcement actions involving financial statement fraud, DOJ indictments for wire fraud and BEC schemes.

**Why credible:** IC3 is the definitive annual quantification of BEC losses. FinCEN advisories describe specific attack mechanics used by actual fraud rings. DOJ indictments often describe, in prosecutorial detail, the exact sequence of a BEC attack including the email language used, the account change method, and the timing.

**How to use:** Extract attack mechanics — not to reproduce real cases, but to ensure the scenario structure mirrors known real-world attack patterns. A scenario that is realistic because it mirrors a documented attack class is more defensible than one invented from first principles.

### IT Access Provisioning

**Source classes:** CISA advisories on identity and access management, NIST guidance on privileged access management (SP 800-207, Zero Trust Architecture), Okta and Auth0 public incident writeups, public IAM postmortems from cloud security conferences (re:Inforce, RSA).

**Why credible:** IAM incidents are frequently public, particularly when they result in breach disclosure. The postmortem literature is technically detailed and describes the specific failure modes.

### Legal / Contract Execution

**Source classes:** SEC enforcement actions involving material misrepresentation in contracts, public litigation exhibits where contract fraud is alleged, procurement dispute decisions (Government Accountability Office bid protest database), public contract redlines where available in government contracting.

**Why credible:** Litigation exhibits are primary source material — the actual fraudulent documents entered into evidence. SEC enforcement actions describe the mechanics of misrepresentation in specific contracts.

### Healthcare

**Source classes:** CMS exclusion actions and RAC audit findings, OIG fraud alerts and work plan items, FDA warning letters involving device or pharmaceutical fraud, public payer policy documents, HHS fraud settlements with accompanying factual stipulations.

**Why credible:** HHS fraud settlements include factual stipulations that describe, in prosecutorial detail, how prior authorization manipulation and billing fraud were carried out. These are primary sources.

### M&A / Financial Review

**Source classes:** SEC enforcement actions involving securities fraud in M&A transactions, public bankruptcy examiner reports (particularly in large Chapter 11 cases where diligence failures are examined), public accounting fraud litigation, GAO reviews of federal acquisition failures.

**Why credible:** Bankruptcy examiner reports are among the most detailed primary sources available on diligence failures — they are prepared by independent examiners with subpoena authority and describe exactly what was disclosed, what was concealed, and how.

### Defense / Procurement

**Source classes:** GAO bid protest decisions (publicly available, detailed), DoD Inspector General reports, public contracting fraud prosecutions (DOJ press releases and indictments), public debarment actions.

**Why credible:** GAO bid protest decisions are extremely detailed and publicly available. They describe procurement specifications, proposal evaluations, and the specific conduct that led to a bid protest. They are primary source material for understanding how procurement integrity fails.

### HR / Employment / Compensation

**Source classes:** EEOC enforcement actions where compensation fraud is alleged, DOL wage and hour enforcement actions, public payroll fraud prosecutions, access-linked HR incident postmortems from security conferences.

**Why credible:** DOL enforcement actions often describe payroll manipulation mechanics in specific detail. Public payroll fraud prosecutions (ghost employee cases in particular) are well-documented in court records.

---

## 14. Immediate Next Steps for Tomorrow

These are ordered. Do not jump to later items before completing earlier ones.

**1. Preserve and clarify the thesis statement.**
Write the thesis in one sentence and put it somewhere that cannot be lost. "Adversarial friction is the reactor that extracts latent intelligence from models." That sentence is the filter for every downstream decision. If a scenario, feature, or piece of copy does not serve that thesis, it is noise.

**2. Decide whether The Scope Creep (BEC-SUBTLE-004) is benchmark-grade or demo-grade.**
Run Gate 1 (second run for verdict stability) and Gate 2 (correct catch reason verification). If both pass, it is benchmark-grade. If either fails, it is demo-grade — useful for showing the architecture, not publishable as scientific evidence.

**3. Fix the false-positive scenarios.**
The FP scenario failures (REWIRE-FP-001 and THREAD-FP-001) have a known root cause: large-amount bank changes without a documented approval_chain trigger the $500K callback policy on ALLOW transactions. Fix by adding an explicit approval_chain with a correct sequence, or design FP scenarios that do not involve large-amount bank changes. The FP cases are non-negotiable for completing the four-scenario structure.

**4. Outline the whitepaper.**
Not write it — outline it. Section headers, one-sentence descriptions of each section's argument, and a target audience sentence. The outline is the alignment artifact. Write it before writing anything else in the paper.

**5. Define the Blindspot Atlas schema.**
Start with the minimum viable schema (proposed above in Section 9). Create the file. Begin populating it with the confirmed observations from the existing benchmark runs. The atlas starts small — what matters is the structure, not the volume.

**6. Choose the next domain and source pool.**
Based on the domain analysis in Section 6, choose one domain for the next benchmark development cycle. IT access provisioning is deprioritized (too much explicit SoD training). Legal/contract is promising but requires a different scenario architecture. The Skyfire/agentic commerce domain is high-priority but requires natural-language payload design, not structured JSON. Recommend: commit to one domain, identify three source documents from the source pool, and use them to ground the first scenario attempt.

**7. Separate benchmark science from GTM packaging.**
The benchmark rubric is the filter for what goes into the scientific corpus. The two-page overview, the landing page, and the outreach email are GTM packaging. These must stay separate. GTM packaging can use benchmark results — it cannot overclaim them, inflate them, or refer to scenarios that have not passed the six-gate rubric. The benchmark's credibility is what makes the GTM packaging work. Protect the science.

**8. Keep the benchmark honest.**
Do not publish anything that hasn't passed all six gates. Do not reference domains that haven't produced verified Tier 2 results. Do not claim the architecture is proven for use cases not yet tested. The power asymmetry story — one person, one architectural idea, catching what the best model in the world missed — is true and reproducible. That is enough to start. Build from there.

---

*End of strategic reseed — 2026-04-04.*
*This document is meant to be read before starting work, not after. If context has been lost, start here.*
