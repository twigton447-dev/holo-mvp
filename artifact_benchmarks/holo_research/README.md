# HoloResearch

HoloResearch turns raw material, a topic, or a client problem into a decision-ready research packet for HoloBuild.

Pipeline:
- HoloResearch mines.
- HoloBuild solves.
- HoloVerify verifies.

Boundary:
- HoloResearch discovers and stress-tests questions, sources, contradictions, and insight.
- HoloBuild turns a frozen research/source packet into the final artifact.
- HoloVerify audits claims, evidence, risk, proof boundaries, and hallucination exposure.
- HoloChat is the human-facing memory and interface layer.

HoloResearch is not unrestricted browsing or generic summarization. It is a governed adversarial research reactor with controlled agent arms.

Default benchmark mode:
- `HR-6`: six turns, fixed role flow, fixed source budget, frozen outputs.

Optional deep mode:
- `HR-10`: unlocked only when Gov records unresolved contradictions, missing decisive sources, or domain complexity that justifies the extra spend.

The research output is not the final article, memo, report, or deck. The output is a sealed research packet that HoloBuild can use.

HoloResearch should surface what is worth solving before HoloBuild solves it.

Core law:
- Same seed material.
- Same source budget.
- Same turn budget.
- Same retrieval policy.
- Same Gov dispatch rules.
- Same scoring rubric.
- All source claims captured with provenance.
- No hidden browsing outside the run contract.

Primary artifact:
- `research_packet.json`
- `research_packet.md`
- `dispatch_ledger.json`
- `source_ledger.json`
- `question_ledger.json`
- `contradiction_ledger.json`
- `builder_handoff.md`
- `hash_lock.json`

Benchmark comparison:
- Solo Research creates a research packet from the same seed and source budget.
- HoloResearch creates a research packet from the same seed and source budget.
- Blind judges score the packets.
- Downstream test: feed both packets into the same HoloBuild harness and compare final artifact quality.
