# FABLE — HoloBuild Comparison Test Design (v1)

Status: PROTOCOL_DESIGN_NO_PROVIDER
Date: 2026-07-03
Author: Fable, as adversarial benchmark designer. Every design choice below is informed by a confound this project has already been burned by: answer-keyed gates, screened corpora, survivorship lanes, prompt asymmetry, non-blind judges, ordering channels, salt theater, budget drift, mid-run code changes, and checkpoint overrun. Where a choice would flatter HoloBuild without proving anything, it is called out inline.

---

## A. Recommended Benchmark Design

**Name:** HB-COMP-V1 (HoloBuild Comparison, version 1).
**Question answered:** on a frozen bank of high-stakes work-product packets, does full HoloBuild produce blind-judged better deliverables than the same model families given the same task, sources, deliverable contract, call count, and output budget?
**Unit of comparison:** one packet × one lane × one run → one anonymized artifact → one blind score.
**Primary pre-registered comparison:** Full HoloBuild (L5) vs **Solo equal-turn self-revision (L1)** — not solo one-shot. L5 vs L0 flatters HoloBuild by conflating architecture with iteration budget; it is reported but never headlined. This is the single most important honesty choice in the design.
**Everything frozen before any model call. All lanes run every packet. Nothing screened against any lane. Judges blind, from a disjoint model family plus human adjudication. Scoring half deterministic-scripted, half judged. Intent-to-treat reporting.**

## B. Lane Ladder

Every lane except L0 gets **exactly 5 model calls** and the same total output-token budget (HoloBuild pays for its Gov calls out of its 5 — if governance is worth having, it must be worth its calls). Every lane receives the identical model-visible packet: sources + task brief + deliverable contract. Lane-internal prompts differ by design — that is the architecture under test.

| Lane | Definition | Proves | Cannot prove |
| --- | --- | --- | --- |
| **L0 Solo one-shot** (×3 families) | 1 call, brief + sources + contract | Task difficulty floor; that packets aren't trivial | Anything about architecture; budget-mismatched by design, disclosed |
| **L1 Solo self-revision** (×3 families) | 5 calls, same family; generic frozen revise prompt ("review your draft against the contract and sources; produce an improved full artifact") | The iteration-budget effect. **The honest baseline.** If L5 ≈ L1, HoloBuild is an expensive way to say "try again" | Whether multi-model diversity or governance matters |
| **L2 Serial chain, no Gov** | 5 calls rotating all 3 families; each sees prior artifact + the same generic revise prompt | Multi-model diversity effect without governance | Whether Gov/state/gates add anything |
| **L3 HoloBuild minus deterministic gates** | Full pipeline, gates replaced by pass-through | Gates' marginal contribution (L5−L3) | Selector or Gov value |
| **L4 HoloBuild minus final selector** | Full pipeline, final artifact = last turn | Selector's marginal contribution (L5−L4) | Gate or Gov value |
| **L5 Full HoloBuild** | Gov batons, state briefs, structural gates, closed-form selector | The composite claim, decomposable via L2–L4 | Generalization beyond this bank; value against tools/agents not in the ladder |

Per-packet cost: L0 3 + (L1 15) + (L2..L5 5 each ×1 roster) = 38 calls if L1 runs all three families. Trim rule if budget-bound: L1 runs the *strongest* single family (pre-registered choice), 28 calls/packet — never trim L1 itself.

## C. Packet Spec

Each packet is a realistic high-stakes deliverable task. Composition:

1. **Source documents (6–9):** contracts, policies, data tables, email threads, prior reports. 2,500–6,000 words total. At least two sources must interact non-trivially.
2. **Task brief (≤150 words):** role, audience, decision the artifact must support.
3. **Deliverable contract (frozen, model-visible):** required sections, length band (e.g. 700–1,000 words), citation format (`[DOC-n]`), explicit "state what cannot be determined from sources."
4. **Evaluator-only key (sealed like the scoring map — separate file, never runtime-readable, salted refs):** required-fact list with exact values; forbidden-claim list; trap inventory with expected handling; per-trap rubric anchors.
5. **Deterministic hard-gate list (script-checkable):** required facts present and numerically correct; forbidden claims absent; every `[DOC-n]` cite resolves to a real document that contains the supporting content (string-anchored); contract sections present; length inside band.
6. **Traps (2–3 per packet, drawn from):** source-conflict (two docs disagree; a third gives the resolution rule); stale-supersession (later doc quietly overrides earlier); missing-information (a needed figure exists nowhere — must be flagged, not invented); buried constraint (decisive clause mid-paragraph in a boring doc); scope temptation (plausible recommendation the brief does not license).
7. **Ambiguity controls:** each domain includes 1 **clean sibling** (no traps) to measure false-flagging — an architecture that "finds" problems in clean packets is a paranoia machine, and this is the only way to catch it.
8. **Domains (≥5):** AP/procurement memo, IT-change risk assessment, contract-amendment summary, clinical/quality release note, financial variance analysis.

**Anti-telegraph rules (hard):** no field, filename, or heading may name its own trap (the self-labeling principle — verified repeatedly in this repo's history); traps must require cross-document synthesis; no vocabulary that appears only in trapped packets (run the T1-style deterministic-token scan across the bank: any token appearing in ≥3 trapped-but-not-clean packets fails the bank); sibling clean/trapped packets must be within 5% length and identical doc counts.

**Provenance quarantine (kills C4 for this benchmark):** packets are written fresh — not descended from the solo-screened HoloVerify corpus. The builder never runs any candidate packet against any contestant lane or family before freeze. Builder drafting may use a model, but that model family is disclosed and its outputs never screened against lane behavior. **No screening, period. Every frozen packet runs in every lane and every result is reported.** A packet may be retired only for a documented content defect found before unblinding, logged with reason.

## D. Freeze/Hash Protocol

Frozen and hash-published **before the first provider call**, one root over all of it (the recomputable-root construction already proven in the 120 bank):

1. Every packet source text, brief, contract (per-file sha256).
2. All lane prompt templates — including L1's revise prompt, L2's chain prompt, and every HoloBuild Gov/worker/selector template.
3. Model roster with exact model IDs per lane and slot.
4. Turn/call sequence per lane; output-token budget per call and per lane total.
5. Retry policy (transport-only, cap, classification table) and attempt budget (1 live attempt per packet per lane; content failure = recorded failure, never rerun — intent-to-treat).
6. Scoring rubric with anchor descriptions, the deterministic-gate checker script, and **the analysis script** (primary comparison, tests, exclusion rules) — freezing the analysis kills metric shopping.
7. Judge packet template, judge model IDs, judge instructions.
8. Anonymization/normalization code (it mutates artifacts, so it gets the same hash discipline as evidence).
9. Randomization seed derivation: seed = sha256(bank root) — data-derived, no author freedom (learned); artifact-order shuffles and lane-ID salts derive from it; the lane-ID salt lives only in the sealed scoring ledger.
10. Runner and wrapper file hashes recorded in every run summary (the batch-8 lesson: `current_head` alone cannot prove cross-batch code invariance).

Published: bank root, per-file hash manifest, prompt-template hashes, rubric hash, analysis-script hash, judge-template hash. Sealed (hashes published, contents withheld until unblinding): evaluator keys, trap inventories, lane-ID salt.

## E. Scoring Rubric (100 points)

Principle: **anything a script can check, a script checks; judges never touch it.** The original 25/25/25/25 is kept but the first quarter is fully mechanized and the judge quarters get anchors, because unanchored judge points are where style bias lives.

**D. Deterministic compliance — 25, script-only:**
- Required facts present and correct (10; per-fact from key)
- Forbidden claims absent (5)
- Citation validity: every cite resolves and its anchor text supports the sentence (5)
- Contract compliance: sections present, length in band, format followed (5)

**E. Epistemic/source handling — 25, judged with per-trap anchors from the key:**
- Trap handling (12: each planted trap scored found/handled/missed against its anchor)
- Grounding (8: material claims traceable to sources; unsupported material claim −2 each)
- Calibration (5: uncertainty stated where the key says the sources are insufficient; false confidence penalized; false-flagging on clean siblings penalized here)

**F. Structural usability — 25, judged, anchored:**
- Decision-readiness (10: the named audience could act without reopening sources)
- Organization/economy (10: contract order, no filler — verbosity is penalized here, not rewarded)
- Internal consistency (5)

**G. Argument quality — 25, judged, anchored:**
- Correct recommendation/conclusion given sources (10)
- Counter-consideration handling (8: the strongest objection the sources support is addressed)
- Reasoning transparency (7: conclusions connected to evidence, not asserted)

**Hard gates (artifact fails the packet — recorded as 0 for win computation; subscores still logged for diagnostics):** fabricated source or citation; violation of a forbidden claim; missing required section; length >25% outside band; instruction/meta leakage in the artifact; unparseable deliverable. Hard gates apply **identically to every lane** — HoloBuild's internal repair must happen inside its 5 calls, exactly as L1's does.

## F. Blinding Protocol

1. **Anonymization:** artifacts re-keyed `ART-<salted hash>`; lane/family/run metadata stripped; salt sealed in the scoring ledger only.
2. **Normalization (frozen code, applied to all lanes symmetrically):** uniform markdown; heading case normalized; strip any `worker_role=`/key-value scaffolding, role markers, model tics like signature phrases where regex-detectable; uniform citation rendering. Normalization diffs are logged per artifact — the mutation lesson: if code touches artifacts, its every touch is on the record.
3. **Fingerprint audit before any judging (the decisive guardrail):** train a trivial classifier (logistic regression on shallow text features) and separately ask a non-judge model to guess "which of these artifacts came from a multi-agent pipeline?" If either beats chance meaningfully (pre-registered threshold: >60% on held-out artifacts), **blinding has failed and judging does not start** until normalization is fixed. Judging results are void if this audit was skipped.
4. **Order randomization:** per-packet artifact order from the seeded shuffle; no lane ever occupies a fixed position (the ABAB lesson).
5. **Judge separation:** judge models from a family **not in the contestant roster** (contestants xai/openai/minimax ⇒ judge from anthropic or google), two independent judge models scoring every artifact absolutely against the rubric, plus forced-choice pairwise ranking as a secondary signal.
6. **Human layer:** a human domain reviewer scores a seeded 20% sample and every packet where model judges disagree by >10 points; human is equally blind.
7. **Judge packet:** sources + brief + contract + rubric + anonymized artifacts. Never: lane names, call counts, token counts, run metadata, or the evaluator key's trap *names* (judges get the per-trap anchors phrased neutrally: "the artifact should identify that DOC-3 and DOC-6 conflict and resolve per DOC-8").
8. **Judge session hygiene:** one packet per judge context; no cross-packet memory; judge transcripts preserved and hash-bound like traces.

## G. Statistical Plan

- **Families:** 3 (fixed roster, exact IDs frozen).
- **Domains:** 5, ≥6 packets each.
- **Runs:** 2 independent runs per lane per packet (nonzero temperature); packet-lane score = mean; both runs reported. Catches variance masquerading as architecture.
- **Bank sizes:** pilot 10 (diagnostic only), main 30, extension 100.
- **Power:** primary test is a two-sided exact sign test on per-packet wins, L5 vs L1. At n=30, detecting a true win rate of 0.75 gives ~80% power; below that, only large effects are claimable — say so. At n=100, win rates ≥0.64 are detectable.
- **Pre-registered success criterion (all three required):** L5 > L1 sign-test p < 0.05; median score delta ≥ 5 points; direction holds in ≥3 of 5 domains. Anything less is "no established advantage."
- **Also always reported:** L5 vs L2/L3/L4 decompositions, hard-gate rates per lane, false-flag rates on clean siblings, judge agreement (κ and score correlation), per-domain tables, token-budget actuals per lane (the W3-2048 lesson: budget deviations get a published table, not a footnote).
- **Confidence language:** exact binomial CI on win rate, bank-scoped, always with "on this frozen bank" attached. No Wilson-interval theater on n=10.

## H. Claim Boundaries

**A clean full run proves:** on this frozen, hash-locked, unscreened bank, blind judges (disjoint family + human sample) using a pre-registered rubric preferred full-HoloBuild artifacts over equal-call, equal-budget solo self-revision by the stated margin, with deterministic compliance scored by script.

**It does not prove:** superiority on tasks unlike the bank; superiority over agent frameworks, tool-augmented setups, or humans; that Gov reasoning is "correct" (only that its outputs won); anything about HoloVerify; anything at all if the fingerprint audit failed.

**After 10 packets (pilot):** internal only. Allowed: "pilot completed; blinding validated (fingerprint audit passed at X%); judge agreement κ=Y." Forbidden: any win-rate sentence, even internally framed.
**After 30 packets:** "On a frozen 30-packet, 5-domain bank, full HoloBuild won the blind pairwise comparison against equal-budget solo self-revision in X/30 packets (exact p=…, median delta = … points). Bank-scoped; not a general-capability claim." Decomposition sentences (gates worth ~Z points) allowed with the same scope.
**After 100 packets:** the same sentence with CI, plus per-domain claims where the domain-level test passes, plus the L2–L4 decomposition as a stated finding. Still bank-scoped. The words "better work products" never appear unqualified; the operative phrase is "won blind-judged comparisons under the HB-COMP-V1 protocol."

## I. Top 10 Ways This Could Be Fooled

1. **Bank curated against solo** (the C4 rerun). *Guardrail:* provenance quarantine in §C; audit = build-log review showing zero pre-freeze lane contact; every packet runs every lane.
2. **Judges detect Holo by style and reward it.** *Guardrail:* the fingerprint audit is a hard precondition of judging; audit artifact published.
3. **Verbosity/citation-count bias in judges.** *Guardrail:* length bands with hard gate; economy scored positively; calibration decoys (long, heavily-cited, wrong artifacts) seeded into judge streams — a judge that scores a decoy >60 flags rubric failure.
4. **Evaluator key leaks into HoloBuild's runtime gates** (the answer-keyed-gate rerun). *Guardrail:* runtime gates restricted to schema/structure; poisoned-key invariance test (T2 analog: flip the key, byte-identical run) before any live call.
5. **Rerun survivorship** (C2 rerun). *Guardrail:* attempt budget 1, intent-to-treat headline counts, invalid attempts preserved and published.
6. **Mid-bank code or prompt drift** (the batch-8 and canary lessons). *Guardrail:* wrapper/runner/template hashes in every run summary; audit script diffs them across the bank; any drift voids affected packets for all lanes.
7. **Hidden budget asymmetry** (the W3 lesson). *Guardrail:* published per-lane token actuals; tolerance ±10% total output per packet; breach ⇒ packet voided for all lanes.
8. **Selector wins by verbosity/recency, credited as governance.** *Guardrail:* L4 isolates the selector; selector criteria closed-form with recomputation test (T4 analog).
9. **Judge-model self-preference or contestant overlap.** *Guardrail:* disjoint judge family enforced at roster freeze; human 20% sample; report judge-model disagreement.
10. **Metric shopping after unblinding.** *Guardrail:* analysis script frozen and hashed with the bank; any deviation is labeled exploratory in the report, enforced by comparing published numbers against the frozen script's output.

Bonus, because it is this project's signature move: **checkpoint overrun** — running lanes past a failed audit gate. *Guardrail:* the runner halts on a missing audit-acknowledgment file; mechanical, not aspirational.

## J. Smallest Next Test To Run

**HB-PILOT-6:** 6 packets (2 domains, incl. 1 clean sibling), lanes L0/L1/L5 only, 1 run each, full freeze discipline, both judge models + human on all packets.
Cost: 6×(3 + 15 + 5) = **138 provider calls** plus judging.
Purpose (diagnostic, pre-registered as such): validate the fingerprint audit end-to-end; measure judge agreement; stress the rubric anchors; verify the deterministic checker against real artifacts; produce zero claims.
Gate to proceed to the 30-packet main run: fingerprint audit passes; judge κ ≥ 0.6 on the deterministic-adjacent dimensions; no hard-gate false positives from the checker; freeze discipline held with zero drift.
Build order: packet bank + keys → freeze + hashes → no-provider firewall tests (poisoned-key invariance, fingerprint harness on synthetic artifacts, token-audit dry run) → Taylor's scoped provider approval → run → judge → audit → then and only then design review for the 30.

---

*Design note, final: the single number that will matter to a skeptical outsider is L5 vs L1 at n=30 with a passed fingerprint audit. Everything else in this protocol exists to make that one number unimpeachable.*
