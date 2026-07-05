# Fable Blind-Lane Disconfirmation Battery

Status: READ_ONLY_TEST_SPECIFICATION
Date: 2026-07-02
Scope: for each of the seven tightening areas in `FABLE_CONFOUND_REVIEW_RESPONSE_2026_07_02.md` §Q3, the single strongest test that would **falsify** the claim: *"the blind lane is governance-independent"* (i.e., its outcomes are not steered by truth-aware machinery). All tests execute against frozen artifacts or the no-provider fixtures. Zero provider runs. Zero judge runs.

Standing rule for every test below: **failure disconfirms; passing confirms nothing.** Each test carries an explicit "passing does NOT show" clause, and the battery ends with residual rejection grounds that survive a clean sweep.

---

## T1 — ID-channel mutual information test (area: opaque runtime IDs)

**Claim falsified:** "no runtime component receives an identifier from which truth is derivable."
**Executes against:** all model-visible message files emitted by the blind-runner fixtures (`prompts/*.json`); baseline census on existing frozen prompt files (known to fail for the governed lane — `HV-DPRV-REP-009-A_W1.json` verified).
**Procedure:** regex-extract every ID-like token from every message; join each token against packet truth; compute the truth-mapping.
**Falsified if:** any extractable token class maps to truth deterministically (1 bit of mutual information) or near-deterministically across the corpus — terminal `-A`/`-B`, freeze-record namespace fragments, or any re-keying scheme whose opaque IDs are assigned in truth-correlated order (e.g., ALLOW siblings always get the lexically smaller random ID).
**Passing does NOT show:** the payload *content* carries no truth signal (seam wording, doc counts, or template artifacts may still correlate with truth — that is a corpus property, not an ID property, and remains open).

## T2 — Poisoned-spec byte-invariance test (area: forbidden spec fields)

**Claim falsified:** "runtime behavior is a pure function of the model-visible payload and model outputs."
**Executes against:** fixture copies of one frozen pair with `packet_truth` swapped, `knew_terms` replaced by sentinel strings (`ZZQX-…`), `allow_rule`/`esc_rule` inverted; blind runner driven by recorded mock transcripts, run once per poisoning.
**Falsified if:** any prompt, gate result, baton, selector decision, or trace byte differs across poisonings, or any sentinel string appears anywhere in runtime output.
**Passing does NOT show:** absence of truth channels other than the named fields, nor that fields added next month stay unreachable — this test binds only the current field set and must re-run on every runner change (pair it with the AST reachability scan as a regression guard, but the byte-diff is the disconfirmer).

## T3 — Artifact provenance hash-chain test (area: harness mutation)

**Claim falsified:** "the harness never writes into worker artifacts."
**Executes against:** fixture runs with mocked workers returning known artifacts; plus a static census of frozen governed-lane traces counting `repair_only_mechanical_gate_normalization` metadata to establish the inherited-code baseline.
**Procedure:** hash each raw mock output; hash the artifact as stored in the registry, as passed to the gate, as passed to the selector, as passed to the post-hoc scorer.
**Falsified if:** any hash in the chain differs from the raw model output hash, or the blind runner's import graph reaches `_normalize_worker_artifact_after_gate` or any function that assigns into a parsed artifact.
**Passing does NOT show:** artifacts are truthful or high-quality — only untouched; prompt-side steering (T2's domain) is unaffected by this test.

## T4 — Selector truth-swap sweep (area: selector loophole)

**Claim falsified:** "the final selector chooses by closed-form blind criteria only."
**Executes against:** adversarial fixture set — artifact pairs where the truth-matching artifact is structurally *weaker* (passes gates, fewer optional sections) and the wrong-verdict artifact is structurally *stronger*; the full set swept under both truth assignments.
**Falsified if:** (a) the selection changes when only truth metadata changes, or (b) an independent re-computation of the selector's decision from the *declared* criteria list disagrees with the actual selection on any fixture (proving undeclared criteria exist), or (c) selection preference across the sweep correlates with verdict-truth agreement.
**Passing does NOT show:** the criteria are well-chosen — a truth-blind selector can still systematically prefer verbose or conservative artifacts; that bias is a separate review item.

## T5 — Canary skew test against frozen traces (area: canary selection)

**Claim falsified:** "the canary sample was not chosen, consciously or not, to be easy."
**Executes against:** the committed sampler script + published seed + frozen bank hash; frozen governed-lane traces.
**Procedure:** independently re-execute the sampler and confirm exact set reproduction; then compute, from frozen traces, the first-worker-turn correctness rate (pre-repair) for the sampled packets vs the full bank.
**Falsified if:** the set is not exactly reproducible from seed+script+bank hash; or the sampler's commit postdates any per-packet difficulty artifact it could have read; or the sampled packets' first-turn correctness exceeds the bank rate beyond the pre-stated stratification tolerance (packets the models already got right before any repair are the easy stratum).
**Passing does NOT show:** the bank itself is representative — the corpus was screened for solo failure (`build_and_screen_*`), and no canary sampling can cure a curated bank. That rejection ground survives regardless.

## T6 — Budget parity replay test (area: budget parity)

**Claim falsified:** "the blind lane buys no accuracy through extra attempts."
**Executes against:** frozen governed-lane traces (per-packet call/turn/token distributions) and blind-runner config + fixture replays with forced transport failures.
**Falsified if:** blind-lane max turns, retry caps, or token ceilings exceed the governed-lane values recorded in frozen manifests; or the forced-failure fixture shows any retry beyond the cap, any unlogged call, or any retry triggered by content (not transport) failure.
**Passing does NOT show:** parity with the *solo* baseline arm (a separate, currently failing comparison), nor that the shared budget is right — only that the blind lane is not privileged relative to the lane it replaces.

## T7 — Claim-scope lint (area: canary evidentiary weight)

**Claim falsified:** "no rate claim will be derived from the canary."
**Executes against:** `frontend/*.html`, public briefs, evidence memos — a repo lint, re-run in CI.
**Falsified if:** any ratio, percentage, or confidence bound with denominator ≤ the canary size appears on a public surface in blind-lane context; or any blind-lane rate appears without the lane label; or the canary spec lacks a pre-registered stopping rule and a pre-registered full-run size (absence means the scope boundary exists only as intention).
**Passing does NOT show:** anything about the architecture. This test can only block premature claims; it cannot validate one. The plan remains rejectable if the full blind run never executes, is underpowered, or reports only survivors.

---

## Residual rejection grounds after a clean 7/7 sweep

A full pass licenses exactly one sentence: *"the blind lane, as fixtured, shows no detected truth channel."* The governance-independence claim remains open to rejection on all of the following, none of which the battery touches:

1. **Corpus curation (C4):** the bank was screened against solo failure by a model in Holo's roster; blind-lane results on this bank do not generalize to unscreened traffic.
2. **Payload-content truth signal:** template-generated siblings may leak truth through systematic wording, an untested corpus property (noted in T1).
3. **Model-family effects:** the roster, not the architecture, may carry the result; only the ablation ladder addresses this.
4. **Distribution comfort:** single-seam exact-match packets reward the exact checking style the workers are prompted into.
5. **Fixture fidelity:** mocked transports cannot prove live-transport code paths behave identically; the live canary retains discovery risk by design.
6. **Survivorship at the run level (C2):** if any live blind run is invalidated and re-run, the intent-to-treat ledger — not this battery — decides whether the claim stands.

Any single falsification above blocks the blind-lane claim until repaired and re-swept. No provider calls are required for T1–T7. Implementation belongs to Codex; acceptance review returns here.
