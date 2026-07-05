# Borrowed Discipline

Date: 2026-07-05

Callsign: Standards Archaeologist

Scope: benchmark-methodology memo only. No providers, Holo live, solo live, Gov, judges, public site edits, staging, commit, or push.

## Source Notes

- SWE-bench defines real GitHub issue tasks and reports Verified as a 500-instance expert-verified solvable subset; OpenAI's SWE-bench Verified note describes professional developer annotation, severe-label filtering, three annotators per sample, difficulty labels, and a deliberate distinction between filtering impossible samples and making a benchmark easier: <https://www.swebench.com/SWE-bench/> and <https://openai.com/index/introducing-swe-bench-verified/>.
- LiveCodeBench continuously collects new contest problems, labels release dates, reports time-window results, and exposes release versions and scoring commands: <https://livecodebench.github.io/> and <https://github.com/LiveCodeBench/LiveCodeBench>.
- HELM emphasizes standardized scenarios, multi-metric reporting, raw prompt/response transparency, and a UI for inspecting individual prompts and responses: <https://github.com/stanford-crfm/helm> and <https://arxiv.org/abs/2211.09110>.
- MLPerf documents fixed benchmark rules, reference implementations, anti-detection rules, fixed seeds, replication requirements, audit mechanics, and exact dataset/quality/latency constraints: <https://raw.githubusercontent.com/mlcommons/inference_policies/master/inference_rules.adoc>.
- METR reports task success as a function of human task duration, repeats tasks, publishes raw data/analysis code, and warns when a claimed time horizon exceeds the suite's reliable range: <https://metr.org/time-horizons/>.
- Artificial Analysis documents per-evaluation weights, repeats, pass@1 scoring, prompt templates, answer extraction, and AA-Omniscience components that separately penalize hallucination and reward knowledge calibration: <https://artificialanalysis.ai/methodology/intelligence-benchmarking>.

## Three Rules We Should Steal

### 1. Name the lane before the score

Borrowed from SWE-bench Verified, LiveCodeBench, METR, and MLPerf: every counted result needs a declared population, admission rule, exclusion rule, and reliability claim class before the run is interpreted.

Why it protects credibility: it makes "hard" and "verified" mean different things. SWE-bench Verified filters for feasible, well-specified tasks; LiveCodeBench uses date windows to reduce contamination; METR ties difficulty to human task time; MLPerf forces submissions into rule-defined divisions. HoloVerify should do the same: a blind public lane, a hard-case stress lane, and internal repair lanes are all useful, but they are not interchangeable denominators.

Exact methodology wording:

> HoloVerify results are reported by predeclared lane. The current public denominator is the blind-120 lane only: 120 frozen action-boundary packets, balanced across 60 ALLOW and 60 ESCALATE truths, scored only after trace freeze. Stress-selected packets, selected repair lanes, canaries, packet-key defects, and historical/internal material are reported separately and do not change public FPR/FNR unless admitted into a new clean public lane before scoring.

### 2. Show the spread, not only the average

Borrowed from SWE-bench's resolved-instance matrix, LiveCodeBench's scenario and time-window breakdowns, HELM's scenario/metric grid, METR's task-level success curves and repeated attempts, and Artificial Analysis' per-evaluation components.

Why it protects credibility: a leaderboard average hides jagged risk. For HoloVerify, the risk is exactly the packet/model boundary: a solo model can be mostly green and still make one dangerous ALLOW or overblock. The public page should make those red, amber, and gray cells legible rather than flattening them into a single story.

Exact methodology wording:

> HoloVerify publishes lane-scoped packet-level accounting. For solo stress lanes, each sibling pair reports six solo opportunities: three model families across the ALLOW and ESCALATE siblings. Wrong verdicts, parse/admissibility failures, source/evidence failures, packet quarantines, and HoloVerify outcomes are shown as distinct cells. A lane average may be shown only after the matrix remains available and the denominator is named.

### 3. Freeze construction rules and audit artifacts

Borrowed from MLPerf's reference implementations, anti-benchmark-detection rules, fixed seeds, replicability requirement, and audits; LiveCodeBench release versions; SWE-bench's Docker harness and instance results; and HELM's raw prompt/completion release practice.

Why it protects credibility: score inflation usually enters through quiet construction changes: replacing misses, moving packets between lanes after seeing results, changing prompts or gates midstream, or letting the answer key leak into runtime. The antidote is boring and strong: immutable manifests, truth-free runtime inputs, trace-bound scoring, quarantine logs, and exact admission rules.

Exact methodology wording:

> A HoloVerify packet counts only if its packet id, lane, freeze hash, runtime manifest, prompt/gate version, scoring map hash, and quarantine rule were recorded before score interpretation. Runtime inputs must be truth-free. Final wrong answers count as false positives or false negatives after trace freeze. Packet replacement, post-hoc lane movement, and answer-key-aware runtime behavior invalidate public-denominator credit.

## How To Admit The 300-Packet Expansion

The 300-packet expansion should be admitted in one of two ways, and the page must say which one it is.

1. Clean public lane: admit 180 new blind packets before score interpretation, balanced as 90 ALLOW and 90 ESCALATE, then report a new `blind-300` lane only after all 300 packet ids, sibling structure, domain tags, freeze hashes, runtime manifests, scoring-map hashes, trace locations, quarantine rules, and FP/FN accounting are published. Until then, the public denominator remains blind-120.
2. Hard-case stress lane: if packets enter because at least one solo call failed across the six solo opportunities, disclose the 1-in-6 solo-failure admission rule up front. Label the lane `hard-case/stress-selected`, not natural population FPR/FNR. Report it as stress coverage and failure-seam evidence, not as public reliability prevalence.

The old 614 material must not be combined with blind-120 or used to pad blind-300. V5/V6 repair evidence, Solo Failure Factory evidence, canaries, preflights, and packet/key quarantine material stay in their own lanes unless a future clean public lane is preregistered and admitted before scoring.

## What Counts As Cherry-Picking Or Score Inflation

- Calling a 1-in-6 solo-failure-selected lane a natural FPR/FNR denominator.
- Disclosing the stress-selection rule only after seeing that HoloVerify did well.
- Replacing, excluding, or moving misses after trace freeze.
- Combining blind-120 with old 614, V5/V6 repair runs, canaries, or stress inventory.
- Hiding parse, admissibility, source, or evidence failures as harmless non-attempts.
- Reporting only an aggregate score when packet-level or model-level inconsistency exists.
- Changing prompts, deterministic gates, worker routes, scoring rules, or quarantine rules after outcomes are known without opening a new lane.
- Letting runtime inputs, Gov, deterministic gates, or final selection see ALLOW/ESCALATE truth.
- Publishing a public denominator without a manifest, root hash, trace map, scoring map, and quarantine log.

## Paste-Ready Public Summary

> HoloVerify separates clean public benchmark evidence from hard-case stress evidence. The current public denominator remains blind-120 unless and until a new clean public lane is preregistered, frozen, run under truth-free runtime controls, and scored only after trace freeze. A 300-packet expansion selected by a disclosed 1-in-6 solo-failure rule is a hard-case/stress-selected lane, not a natural population FPR/FNR estimate. Historical 614-era material, internal repair runs, canaries, and stress-selected packets are not combined with blind-120 for public risk bounds.
