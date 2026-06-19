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

Bootstrap mode:
- `SR-Bootstrap`: a solo model mines materials and produces a frozen research packet for HoloBuild.
- This is useful now, but it is labeled as solo research, not HoloResearch benchmark credit.

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

Practical bootstrap:
- Use one solo model to create a research packet when the HoloResearch harness is not ready.
- Validate and hash lock the packet before HoloBuild uses it.
- Judge the solo research packet directly so later HoloResearch has a baseline to beat.

Research judgment:
- Judge the research packet directly before HoloBuild sees it.
- Judge whether the questions are important, source-backed, adversarially tested, and useful for build.
- Preserve the downstream score separately so packet quality and final artifact quality do not blur.

Rubric:
- `research_judge_rubric.json`

Solo bootstrap commands:

```bash
python3 artifact_benchmarks/holo_research/sr_bootstrap.py --generate-smoke
python3 artifact_benchmarks/holo_research/sr_bootstrap.py --validate /private/tmp/holoresearch_sr_bootstrap_smoke
python3 artifact_benchmarks/holo_research/sr_bootstrap.py --freeze /private/tmp/holoresearch_sr_bootstrap_smoke
python3 artifact_benchmarks/holo_research/sr_bootstrap.py --build-judge-packet /private/tmp/holoresearch_sr_bootstrap_smoke
```
