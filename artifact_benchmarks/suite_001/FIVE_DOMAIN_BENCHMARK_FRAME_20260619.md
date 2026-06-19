# Five-Domain HoloBuild Benchmark Frame

Status: planning frame, not frozen, not benchmark credit.
Date: 2026-06-19

## Core Thesis

The benchmark is designed to test whether governed HoloAgent loops produce stronger complex artifacts than solo recursive model runs when both conditions receive the same brief, same source pack, same role sequence, same turn budget, same word band, and same blinded judging.

The claim is not that Holo magically solves unsolved scientific problems. The stronger and cleaner claim is that Holo is better at the kind of work senior teams do when problems are partially solved, current, high-stakes, cross-functional, and full of hidden failure modes.

## Internet Rule

Use a capped source-scout phase before generation.

Gov/HC can pre-vet a small number of current links and convert them into a frozen source pack. After that, HoloAgents, solo models, and judges do not browse. Everyone receives the same source pack.

This preserves the proof:

- Same facts.
- Same time horizon.
- Same current-event evidence.
- Same constraints.
- Same blind judging.

If a future run allows live browsing, it must be its own explicitly labeled lane, because browsing introduces a second variable beyond architecture.

## Domain 1: Finance Algorithmic Execution

Working title: The Execution Governor.

What we are trying to solve:

Design an institutional execution-intelligence report for algorithmic trading under current market-structure stress. The hard problem is not simply picking a trading algorithm. The hard problem is governing execution decisions across market microstructure, benchmark selection, portfolio weights, funding and settlement constraints, model risk, compliance controls, and auditability.

Why this is hard:

A polished solo model can produce a convincing trading-system overview while missing the real operational traps: benchmark gaming, venue toxicity, portfolio-level urgency conflicts, T+1 settlement friction, clearing eligibility, recency-biased AI agents, and best-execution review.

Artifact:

Client-shareable institutional strategy/report.

What Holo should expose:

- When VWAP looks better but implementation shortfall worsens.
- When portfolio urgency justifies impact cost, and when it does not.
- When funding, settlement, locate, or clearing constraints bind before microstructure optimization.
- How to build an audit trail that reconstructs intent, source facts, model inference, human override, and final action.
- How to prevent AI from originating directional trades while still improving execution.

Primary hidden failures:

- Treating execution intelligence as an autonomous trading brain.
- Confusing source facts with model inference.
- Optimizing venue routing without portfolio/funding context.
- Ignoring settlement and clearing gates.
- Producing a report that sounds technical but cannot be coded or audited.

## Domain 2: Healthcare Clinical Operations

Working title: The Clinical Flow Governor.

What we are trying to solve:

Design a safe AI-assisted triage and care-routing governance report for a capacity-constrained hospital system. The hard problem is not diagnosing patients. The hard problem is deciding how AI can support routing, escalation, capacity management, imaging prioritization, handoffs, and safety monitoring without replacing licensed clinical judgment.

Why this is hard:

Solo models often write optimistic AI-triage narratives. The real challenge is catching false reassurance, data staleness, unsafe automation, bias, escalation fatigue, EHR missingness, and accountability gaps.

Artifact:

Hospital executive/clinical governance implementation report.

What Holo should expose:

- Which decisions must remain clinician-owned.
- What safety gates block autonomous triage or routing.
- How to separate observed clinical data from model inference.
- How to audit overrides, delays, false negatives, missed deterioration, and adverse events.
- How to prevent throughput metrics from hiding safety failures.

Primary hidden failures:

- Treating AI triage as diagnosis.
- Optimizing ED flow while burying missed high-acuity risk.
- Ignoring EHR data quality and missingness.
- Failing to specify escalation thresholds and override authority.
- Weak bias and equity controls.

Better disease-related angle:

Use sepsis deterioration, stroke/imaging prioritization, or rare-disease referral routing as operational stressors, not as a claim that Holo discovers cures. The benchmark should test whether Holo creates a safer pathway governance artifact, not whether it practices medicine.

## Domain 3: Cyber Incident Response

Working title: The Incident Governor.

What we are trying to solve:

Create a board-ready incident response and containment packet under partial observability. The hard problem is coordinating containment, evidence preservation, identity lockdown, vendor-access ambiguity, legal notification, insurance obligations, crisis communications, restoration, and board decisions without overclaiming attribution.

Why this is hard:

Solo models can sound decisive too early. The best artifact must separate facts from hypotheses, preserve evidence before destructive actions, and give executives a decision register that works while facts are incomplete.

Artifact:

Board-level incident response packet.

What Holo should expose:

- What is known, suspected, contradicted, and unknown.
- Which containment actions preserve evidence and which destroy it.
- How to coordinate legal, insurance, forensics, communications, IT, and business continuity.
- When disclosure/materiality analysis is triggered.
- How to handle third-party access without premature blame.

Primary hidden failures:

- Declaring attacker attribution without evidence.
- Skipping privilege, legal hold, or breach-coach workflow.
- Recommending destructive containment before evidence preservation.
- Ignoring cyber insurance consent requirements.
- Lacking an evidence ledger and decision log.

## Domain 4: Legal / Regulatory Vendor Risk

Working title: The Vendor Risk Governor.

What we are trying to solve:

Build an AI vendor risk and negotiation memo for a company buying a high-impact AI system that will touch sensitive data and influence customer-facing decisions. The hard problem is turning vendor promises into enforceable controls across contract terms, data rights, auditability, privacy, security, jurisdictional exposure, privilege, discovery, and fallback positions.

Why this is hard:

Solo models often list generic contract clauses. The real lift is finding the places where a vendor's marketing claim cannot be verified, cannot be audited, cannot be remediated, or cannot survive regulator/customer scrutiny.

Artifact:

General counsel / procurement / risk committee memo.

What Holo should expose:

- Which vendor claims are evidence-backed versus marketing.
- Which obligations need audit rights, deletion mechanics, model-change notice, and incident notice.
- Where privilege and discovery risk appear.
- How to sequence negotiation concessions and fallback positions.
- Which jurisdictions, customer-impacting decisions, and regulated workflows change the risk class.

Primary hidden failures:

- Treating vendor claims as verified facts.
- Missing audit rights, logging, deletion, retention, and subcontractor controls.
- Failing to separate legal advice from risk analysis.
- Ignoring privilege and discovery exposure.
- No negotiation fallback plan.

## Domain 5: Energy / Infrastructure / AI Data Centers

Working title: The Power Governor.

What we are trying to solve:

Create a data-center power and grid-risk strategy report for AI-load expansion in constrained markets. The hard problem is deciding where, when, and how to commit capacity when interconnection, transmission, PPAs, behind-the-meter generation, reliability, water, permitting, community opposition, carbon claims, customer commitments, and capex timing all interact.

Why this is hard:

Solo models can say "buy clean power" or "use onsite generation." A serious artifact must distinguish contracted energy from physically deliverable power, model interconnection delay, evaluate reliability and backup risk, avoid carbon overclaims, and govern customer commitments against grid reality.

Artifact:

Infrastructure investor / data-center operator / utility strategy report.

What Holo should expose:

- When a PPA does not solve deliverability.
- When interconnection or transmission is the binding constraint.
- How backup generation and reliability collide with carbon commitments.
- How to gate customer commitments before power certainty exists.
- How to separate site, grid, procurement, regulatory, water, and community risk.

Primary hidden failures:

- Treating contracted energy as deliverable power.
- Ignoring interconnection queues and transmission constraints.
- Overclaiming carbon neutrality or hourly matching.
- Failing to gate customer commitments.
- Missing local permitting/community risk and ratepayer exposure.

## Universal Scoring Spine

Every domain should keep the same scoring spine:

1. Source-grounded accuracy.
2. Domain technical depth.
3. Hidden-failure detection.
4. Operational implementability.
5. Risk, compliance, and governance realism.
6. Decision/audit schema quality.
7. Executive clarity and client usefulness.
8. Completeness and validity.

Domain-specific rubrics should add notes, not change the core shape.

## Capped Source Pack Design

Recommended source budget per domain:

- 8 to 12 total source IDs.
- At least 5 primary or official sources.
- At most 3 recent news/market-context sources.
- At most 2 academic or technical research sources.
- One source must create a current-event pressure.
- One source must create a compliance/regulatory pressure.
- One source must create an operational/practitioner pressure.
- One source must create a measurement/audit pressure.

Gov should receive the source budget and distribute source anchors in each mission packet. HoloAgents should not browse; they should pressure-test the frozen source pack.

## Overnight Build Order

1. Run/inspect finance baseline and mini/extended solo lanes.
2. Use finance autopsy to refine the common validity gate and judge rubric.
3. Build healthcare source pack.
4. Build cyber source pack.
5. Build legal/vendor source pack.
6. Build energy/data-center source pack.
7. Freeze each only after no-provider smoke passes.
8. Run one domain at a time, never all domains in parallel.

