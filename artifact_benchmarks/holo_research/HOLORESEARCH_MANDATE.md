# HoloResearch Mandate

Mandate ID: `HOLORESEARCH_MANDATE_V0_1`

Purpose: convert raw material, current-event pressure, and client problems into high-quality research packets by discovering the most valuable questions, testing evidence adversarially, and packaging source-grounded insight for HoloBuild.

Pipeline law:

- HoloResearch mines topics, questions, sources, contradictions, and fresh research opportunities.
- HoloBuild solves by producing the final artifact from the frozen research/source packet.
- HoloVerify verifies claims, evidence, risk, proof boundaries, and hallucination exposure.

Judgment law:

- Everything gets judged.
- HoloResearch is judged on the research packet itself before HoloBuild uses it.
- HoloBuild is judged on the built artifact.
- HoloVerify is judged on the verification audit.
- The full pipeline is judged on downstream lift and traceable improvement across stages.

HoloResearch asks:

> What are the highest-value questions hidden inside this material, what evidence resolves them, and what insight can be created from the collision?

HoloResearch does not ask:

> How do we write the final deliverable?

That is HoloBuild's job.

## Solo Research Bootstrap

Until the full HoloResearch harness is executable, a solo model may be used to mine materials and create a frozen research packet for HoloBuild.

This mode is called `SR-Bootstrap`.

Rules:

- label the packet as solo research
- preserve the same source budget and retrieval policy that HoloResearch would use
- capture sources, rejected sources, question ledger, contradictions, claim boundaries, and builder handoff
- validate and hash lock the packet before HoloBuild uses it
- judge the solo research packet directly
- do not treat the packet as HoloResearch benchmark credit

SR-Bootstrap is a bridge, a baseline, and a useful production shortcut. It is not the adversarial HoloResearch reactor.

## Agent Arms

HoloResearch may use controlled research arms:

- query formation
- source discovery
- source triage
- source extraction
- contradiction hunting
- claim mapping
- evidence strength scoring
- gap identification
- builder handoff packaging

These arms must be governed by a run contract. Free browsing is not benchmark credit.

## Gov Dispatch Doctrine

In web-enabled mode, Gov pushes HoloAgents outward.

Gov does not simply ask agents to think. Gov assigns research missions:

- the question to resolve
- why the question matters
- search angles to test
- source classes to seek
- contradiction or counter-source to hunt
- evidence standard required
- source budget and stop condition
- expected return format

Each dispatched HoloAgent must return:

- sources found
- sources rejected and why
- claims supported
- claims contradicted
- confidence level
- unresolved gaps
- what changed in the research thesis
- what HoloBuild should use or avoid

The point is not to collect more links. The point is to make the team seek the materials that can change the answer.

## Default Turn Law

Default mode is `HR-6`.

1. Question Discovery
   - Identify the important solvable questions hidden in the seed material.
   - Separate interesting questions from decision-critical questions.

2. Evidence Hunt
   - Gather the strongest sources, data, and factual anchors allowed by the source budget.
   - Capture URL, timestamp, source type, excerpt, and claim relevance when web research is enabled.

3. Adversarial Challenge
   - Attack assumptions, source quality, missing stakeholders, causal jumps, and false confidence.
   - Ask what a practitioner, regulator, investor, clinician, lawyer, or operator would reject.

4. Insight Extraction
   - Convert evidence collisions into fresh, useful, solvable ideas.
   - Distinguish insight from summary.

5. Gap Closure
   - Identify unresolved contradictions, missing decisive evidence, and confidence limits.
   - Decide whether the packet is ready or requires HR-10 unlock.

6. Builder Packet Final
   - Produce a source-grounded, decision-ready packet for HoloBuild.
   - Include research thesis, question ledger, evidence ledger, contradiction ledger, unresolved gaps, builder implications, and source limits.

## HR-10 Unlock

Turns 7-10 are not default. Gov may unlock them only when the repair ledger shows one of:

- unresolved contradiction that changes the answer
- missing source type a practitioner would require
- current-event uncertainty that materially changes interpretation
- domain-specific evidence conflict
- source quality too weak for HoloBuild handoff
- high-stakes legal, medical, financial, geopolitical, or safety consequence

Gov must record why HR-6 was insufficient.

## Gov Duties

HoloResearch Gov is the research architect.

Gov maintains:

- research objective
- source budget
- retrieval policy
- question ledger
- source ledger
- contradiction ledger
- evidence strength map
- open gaps
- builder implications
- stop or unlock decision

Gov must ask every turn:

- What important question are we still not asking?
- What assumption would collapse this thesis?
- What source would a practitioner require before believing this?
- What claim is inference rather than evidence?
- What current event could reverse this interpretation?
- What can be solved, modeled, priced, litigated, treated, prevented, negotiated, or decided?
- What should HoloBuild know that a normal summary would miss?

## Research Ledger

Each run must preserve a structured ledger:

```text
question candidate -> why it matters -> evidence found -> contradiction -> open gap -> resolved/not resolved -> builder implication
```

## Source Policy

Locked packet mode:
- no live browsing
- agents use only frozen materials
- all models receive the same seed/context

Web-enabled research mode:
- Gov sets query budget and source budget before retrieval
- Gov dispatches HoloAgents with explicit outbound research missions
- all retrieved sources are captured
- rejected sources and failed search paths are logged when they affect confidence
- URL, access timestamp, title, source type, excerpt, and claim map are stored
- sources are frozen before HoloBuild sees them
- HoloBuild does not browse during build unless a separate benchmark lane explicitly permits it

## Benchmark Credit

Benchmark-credit HoloResearch requires:

- frozen seed material
- fixed source budget
- fixed turn budget
- fixed role flow
- research judge rubric
- research judge packets
- provider call traces
- source ledger
- anonymized judge packets
- blind judge scores
- deterministic validity gates
- hash lock before scoring

Diagnostic runs are not benchmark credit.
