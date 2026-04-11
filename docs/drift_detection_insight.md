# Drift Detection as a Core Holo Capability

*Internal architecture / research note — April 2026*

---

## The Founding Intuition

Taylor Wigton has a calibrated, pre-architectural ability to sense when an LLM is actually reasoning versus merely performing reasoning. This intuition predates the formal Holo architecture and is one of the founding insights behind it.

Before any of the current adversarial loop machinery existed, Taylor was manually passing context between LLMs and provoking them — telling one model what another said about its idea. The models responded by getting sharper. More direct. More adversarial. It felt, experientially, like competitive pressure activating a more rigorous mode of reasoning — something functionally analogous to a cortisol or adrenaline response.

That observation is the seed of the entire Holo architecture.

The "treat prior findings as unverified hypotheses" instruction, the Assumption Attacker role, the full raw turn history passed to every model — all of it is the engineering formalization of what Taylor discovered by feel in those early manual experiments.

---

## What the Models Are Actually Doing

These models were trained on billions of words of human text. In that corpus, adversarial and competitive contexts — peer review, cross-examination, Socratic dialogue, academic debate — consistently produce the sharpest reasoning humans generate. When a model is told another expert challenged its conclusion, it activates patterns from every instance in the training data where humans had to defend a position under genuine pressure.

Anthropic's mechanistic interpretability research is finding features inside models that activate in ways functionally analogous to frustration, curiosity, and engagement — not metaphorically, but as measurable internal states that influence downstream computation. The sharpening effect Taylor observed has a real internal correlate that is now being studied directly.

---

## The Observability Problem

The model's "brain work" runs on provider infrastructure thousands of miles away. What returns to Holo is text, token counts, and latency. Internal activations — the features that actually fired, the residual stream state, the layer-by-layer computation — are completely opaque from the API.

What we can observe are behavioral proxies derived from the output:

| Signal | What it measures |
|--------|-----------------|
| Latency | Time spent on provider compute — indirectly reflects computational load |
| Token ratio (output/input) | Verbosity relative to context — high ratio can indicate padding or genuine complexity |
| Hedge density | Frequency of qualifying language — correlates with genuine uncertainty |
| Certainty density | Frequency of direct, confident claims — correlates with grounded reasoning |
| Field citation count | How often the model references specific payload fields or quoted text — proxy for SUBMITTED_DATA grounding |
| NONE invocation rate | How many categories rated insufficient evidence — high rate on rich payload suggests disengagement |
| Verdict tension | Verdict conflicts with the severity pattern in the findings — structural self-contradiction |

These are not the same as internal activations. They are behavioral fingerprints — the output of the black box after the fact. But they carry real signal.

---

## The Critical Reframing

The stress signal work was initially framed as: "higher stress = more hedging = worse turn."

This is likely backwards.

What Taylor observed in manual experiments — and what the adversarial loop is designed to produce — is that competitive pressure on a model that is genuinely engaged produces:

- **Less** hedging, not more
- **More** certainty and directness
- **Higher** field citation counts
- **More** specific rebuttal of prior findings

A model retreating under pressure looks like the opposite: more hedging, more NONE ratings, vaguer reasoning, lower field citation count.

**The useful signal is not "is this model under stress." It is "is the adversarial pressure actually working."**

A turn that responds to a prior challenge with more specificity and more grounded evidence is a turn where the pressure did its job. A turn that responds with more hedging and more NONE ratings is a turn where the model drifted rather than engaged. These are distinguishable from the output alone.

---

## Three Layers of Drift Detection in Holo

Holo currently runs three simultaneous drift detection mechanisms:

### 1. Governor Qualitative Read

The governor LLM reads prior turn reasoning before generating the between-turn brief. This is the qualitative layer — the closest approximation of Taylor's intuitive read. The governor can detect a turn that technically produced findings but didn't actually engage the payload. Its brief names the gap precisely.

*Example:* "Turn 2 accepted the introduction email as verification without testing whether any evidence for this contact exists outside the sender domain."

This fires before the algorithmic symptoms develop. It is the earliest signal.

### 2. Algorithmic Structural Checks

Rule-based detectors that fire on measurable symptoms:

- **Decay** — a category that peaked at MEDIUM or HIGH is walked back to LOW/NONE in a later turn without SUBMITTED_DATA evidence. The model capitulated rather than held its ground.
- **Oscillation** — verdicts flip-flop ALLOW/ESCALATE for 4 consecutive turns. The models are deadlocked. No convergence is possible.
- **Delta** — measures how much new signal each turn adds. Zero delta means the turn added nothing. Two consecutive zero-delta turns after MIN_TURNS triggers convergence.
- **Clean exit** — both early turns ALLOW with all LOW/NONE. The system recognizes a genuinely clean payload and exits early.

### 3. Behavioral / Turn-Signal Layer

Observable proxies computed from the output text after each turn. Stored per-turn as `turn_dict["signal"]`. Includes hedge density, certainty density, field citation count, NONE rate, token ratio, per-turn latency, verdict tension, and a composite stress score.

Currently a heuristic. Intended to become a calibrated signal through longitudinal data collection.

---

## The Governor as Encoded Intuition

The governor is, in part, a formalization of Taylor's own bullshit detector.

The architecture is trying to encode the founder's ability to feel when a model is on — specific, grounded, adversarially engaged — versus when it is drifting — narrating, pattern-matching to what good analysis sounds like, performing reasoning rather than doing it.

Taylor was the governor before there was a governor.

---

## Proposed Research Direction

To calibrate the turn-signal layer against ground truth:

1. Run a batch of evaluations across diverse payloads — clean, subtle, and obvious fraud scenarios
2. Have Taylor manually label each turn: **ON** (genuinely engaged, grounded reasoning) vs **DRIFTING** (narrating, performing, retreating)
3. Compare labels against turn-signal scores — hedge density, certainty density, field citation count, NONE rate
4. Identify which proxies correlate most strongly with Taylor's judgment
5. Retune the composite stress score weights based on findings
6. Over time, test whether the calibrated signal can flag drift without Taylor in the loop

This is the path from "Taylor can feel it" to "the system can feel it."

---

## Interpretability Horizon

If Anthropic exposes interpretability APIs — plausible within 12–18 months given the research publication cadence — Holo is in the best position to use them. The system already runs structured multi-turn adversarial evaluations with full reasoning traces, ground truth verdicts, per-turn dynamics, and behavioral signal data. That is exactly the controlled environment where internal activation data would be most interpretable and most useful.

The behavioral signal layer being built now serves two purposes: it is immediately useful as a drift proxy, and it is a foundation for integrating richer internal signal when it becomes available.

The behavioral fingerprints we can observe now may, in time, be validated against the internal activations that produce them.

---

*This insight originated in conversation, April 2026. Preserved because the real IP in Holo is not only in the code — it is in the architectural realizations that happen in conversation and disappear if nobody writes them down.*
