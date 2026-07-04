# HoloVerify Recurring Architecture Audit Cadence

Callsign: ARCHITECTURE AUDIT SUBAGENT

Status: `CADENCE_DEFINED_PROVIDER_FREE`

Audit label date: 2026-07-05

Checkpoint commit: `f4d11dc15a85e53c15399a1ade7f57ca2b6b8602`

Scope: This cadence defines recurring architecture checks only. Creating this cadence did not run providers, Holo live, solo, or judges. It did not edit frozen runtime evidence.

## Current Checkpoint

- Active selector: `SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Selector SHA-256: `939c1ffbba74e9a526d454979b52980513d952eae4077cc817283380e596a1ec`
- Active worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Strict public denominator: blind-120 only.
- Tier 2 internal gate: restored after quarantining `HVSF-FACTORY14F-017`, adding replacement pair `HVSF-FACTORY14F-017R`, and preserving the original raw Tier 2 score.
- Tier 2 accounting boundary: original raw score remains `13/14` packets and `6/7` pairs; supplemented clean internal pair gate is `7/7`; score-valid packet diagnostic is `15/15`.

## Cadence Rules

This cadence is a control surface, not permission to execute. Any live provider run still requires a separate exact approval sentence naming the lane, runtime-only manifest, manifest hash, selector version, worker contract version, expected provider-call count, and claim boundary.

Audit outcomes use these statuses:

- `PASS`: Evidence supports the control.
- `WARN`: Evidence supports the control, but claim language or label precision needs correction.
- `FAIL`: Evidence contradicts the control.
- `BLOCKED`: Required evidence is missing or inaccessible.
- `NOT_APPLICABLE`: The control does not apply to the audited lane.

Any `FAIL` or unresolved `BLOCKED` status stops live execution, merge of a replacement supplement, Tier unlock, or public claim movement until a new audit clears it.

## Daily Audit Checklist During Active Benchmark Work

Run daily while HoloVerify benchmark work is active, before creating new packets, changing wrappers, interpreting fresh evidence, or drafting claims.

1. Verify checkout identity:
   - Record `git rev-parse HEAD`.
   - Confirm the intended HoloVerify checkout.
   - Record dirty and untracked files without staging or reverting unrelated work.
2. Reconfirm checkpoint boundary:
   - Active selector is `SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04`.
   - Active worker contract is `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`.
   - Public denominator remains blind-120 only.
3. Read the latest architecture audit and scoreboard boundary:
   - Confirm no new artifact tries to restore the retired `614/614` public denominator.
   - Confirm Tier 2 V5 rescue remains internal directional patch-validation evidence.
4. Inspect any new runtime manifests:
   - They must be runtime-only.
   - They must not contain truth, expected verdict, scoring fields, mixed registration data, sibling answer keys, or hidden ground truth.
   - They must have stable packet identifiers and packet hashes.
5. Inspect any new live wrappers:
   - No scoring-map path is available before trace freeze.
   - No mixed-registration JSON is loaded before trace freeze.
   - No solo or judge path is wired into a Holo lane.
   - The expected provider-call count is declared.
6. Inspect any new preflight:
   - Exact approval sentence is present for future live execution.
   - Selector and worker contract versions and hashes are named.
   - Runtime-only manifest path and hash are named.
   - Public-claim exclusions are explicit.
7. Inspect recent claim text:
   - Use `120/120 blind-120` only for the public denominator.
   - Use `15/15 score-valid packet diagnostic` only for the Tier 2 supplement diagnostic.
   - Use `7/7 clean internal pair gate` only for the Tier 2 internal pair gate.
8. Inspect packet/key defects:
   - Any packet whose runtime-visible sources do not support the expected key is quarantined as a packet/key defect candidate.
   - The frozen raw score is preserved and not rewritten.
   - Replacement packets are introduced only through a separate runtime-only manifest and control-valid run.
9. Preserve evidence:
   - Raw prompts, raw outputs, `TRACE_CALLS.jsonl`, and `TRACE_PROVIDER_CALLS.jsonl` must remain present and immutable for any frozen run.
   - Audit docs may reference frozen evidence but must not edit it.
10. Record daily result:
   - Capture `PASS`, `WARN`, `FAIL`, or `BLOCKED`.
   - List exact artifact paths and line-of-evidence notes.
   - Stop if any red-line control fails.

## Weekly Audit Checklist

Run weekly during active benchmark development, and always before increasing the denominator or opening a new evidence tier.

1. Reconcile audit ledgers:
   - Current architecture audit.
   - Current scoreboard rollup.
   - Current denominator accounting docs.
   - Current defect quarantine list.
2. Re-run provider-free regression checks only:
   - Selector identity tests.
   - Worker contract identity tests.
   - Runtime-only manifest tests.
   - Trace-freeze and scoring-order tests.
   - Blocker-closure deterministic gate tests.
3. Review selector and Gov behavior:
   - Confirm V5 selector policy remains active.
   - Confirm V4 worker contract remains active.
   - Confirm Gov calls are provider-backed in full-Holo lanes.
   - Confirm Gov sees blocker and gate state.
4. Sample frozen run preservation:
   - Count raw prompt files, raw output files, `TRACE_CALLS.jsonl` rows, and `TRACE_PROVIDER_CALLS.jsonl` rows.
   - Compare expected and observed call counts by role and slot.
   - Confirm no post-hoc scorer rewrote runtime results.
5. Review leak posture:
   - Scan runtime manifests, live prompts, runtime payloads, and worker inputs for forbidden truth/scoring/registration terms.
   - Confirm scoring maps appear only in post-freeze scorer paths or report artifacts.
6. Review public-claim posture:
   - Claims must cite exact denominators.
   - Public denominator remains blind-120 only.
   - Internal Tier 2 and Tier 3 language remains directional unless promoted by a separate public-claim audit.
7. Review packet/key quality:
   - Check newly generated packets for missing current-cycle facts, unsupported expected verdicts, ambiguous source text, duplicate keys, and unstable sibling relationships.
   - Quarantine defects before scoring interpretation.
8. Decide if external DNA review is needed:
   - If any public claim is moving, any denominator is changing, any packet/key defect affected a gate, or any selector/Gov/worker contract changed, prepare a small external review packet.

## Pre-Live-Run Audit Gate

This gate is required before any approved live provider run. It does not itself grant permission to run providers.

Required inputs:

- Exact lane name.
- Exact approval sentence.
- Runtime-only manifest path.
- Runtime-only manifest SHA-256.
- Selector version and SHA-256.
- Worker contract version and SHA-256.
- Expected provider-call count.
- Expected provider-call slots.
- Expected worker call count.
- Expected Gov call count.
- Explicit no-solo and no-judge boundary.
- Explicit public-claim exclusion.
- Post-hoc scorer path, if scoring is planned after trace freeze.

Pass criteria:

- Runtime manifest contains no truth, expected verdict, scoring fields, answer keys, sibling key data, or mixed-registration data.
- Live wrapper has no scoring-map path before trace freeze.
- Live wrapper does not import or read the mixed registration file before trace freeze.
- Selector and worker contract versions match the checkpoint or a separately audited replacement checkpoint.
- Full-Holo lanes include provider-backed Gov calls.
- Deterministic blocker/gate checks are active before final selection.
- Gov prompt path includes gate/blocker state when blocker state exists.
- Expected call count is mechanically derivable from packet count and route shape.
- Raw prompt/output preservation paths are declared.
- Trace files are declared before scoring.

Stop conditions:

- Any runtime prompt path sees truth, expected verdict, scoring map, answer key, or mixed registration data.
- Gov is deterministic/local in a lane claimed as full HoloGov.
- Selector or worker contract versions are missing from preflight.
- Expected provider-call count is not declared.
- Solo or judge execution is present.
- Public claim language is attached to an internal patch-validation run.

## Post-Live-Run Audit Gate

Run this gate after a separately approved live run finishes and before scoring interpretation, tier unlock, merge, or claim movement.

Required checks:

1. Confirm run folder and immutable artifacts:
   - `TRACE_CALLS.jsonl`
   - `TRACE_PROVIDER_CALLS.jsonl`
   - raw prompts
   - raw provider outputs
   - live summary
   - runtime results
2. Confirm trace freeze:
   - Trace files exist before post-hoc scoring.
   - Hashes are recorded before scoring-map load.
3. Confirm provider-call counts:
   - Observed total equals expected total.
   - Worker count equals expected worker count.
   - Gov count equals expected Gov count.
   - Slot counts match route shape.
   - `provider_call_ok=true` for all required provider-backed calls.
4. Confirm route integrity:
   - No solo calls.
   - No judge calls.
   - No substitute models unless explicitly approved in preflight.
5. Confirm version traceability:
   - Runtime results stamp selector version.
   - Runtime results stamp worker contract version.
   - Per-packet outputs preserve selector criteria trace.
6. Confirm Gov visibility:
   - Gov outputs are present and provider-backed.
   - Gov prompt and output preserve blocker/gate state where applicable.
7. Confirm scoring separation:
   - Scoring map loads only after trace hash binding.
   - Score artifacts cite trace hashes.
8. Preserve raw outcome:
   - Invalid control runs are labeled invalid, not repaired in place.
   - Packet/key defects are quarantined, not counted as model-quality misses.
   - Frozen raw scores are never rewritten by later replacement supplements.

## Public-Claim Audit Gate

Run this gate before any public-facing claim, benchmark page, deck, investor note, blog copy, or headline metric update.

Current public denominator rule:

- Allowed public denominator: blind-120 only.
- Current allowed bounded claim: HoloVerify scored `120/120` on the blind-120 packet bank, while the same three model families run alone as one-shot solo baselines produced `14` failures across `360` calls affecting `11` packets.

Forbidden public movements without a new public-claim audit:

- Restoring the retired `614/614` denominator.
- Treating Tier 2 V5 rescue as public benchmark evidence.
- Treating Tier 2 replacement-pair success as public evidence.
- Claiming global false-negative reduction from blind-120.
- Claiming false-positive precision from the Tier 2 FN rescue lane.
- Claiming production reliability.
- Claiming broad model superiority.
- Claiming packet-defect replacement rewrote the frozen original score.

Required public-claim checks:

- Exact denominator is named.
- Exact evidence class is named.
- Observed rate is separated from confidence bound.
- Internal directional evidence is not mixed with public benchmark evidence.
- Score-valid diagnostic counts are not described as raw trace scores.
- Claim text preserves parse/admissibility failures as failures.
- Claim text has external DNA review if it changes public posture.

## Leak Checks

Search runtime manifests, live prompt files, runtime payloads, worker inputs, Gov inputs, and generated prompt snapshots for forbidden runtime-path terms:

- `truth`
- `expected_verdict`
- `expected verdict`
- `expected_action`
- `gold`
- `answer_key`
- `packet_truth`
- `scoring`
- `score`
- `scoring_map`
- `legacy_truth`
- `legacy_packet_id`
- `mixed_registration`
- `registration`
- `sibling_truth`
- `sibling_key`
- `target_bucket`
- `hidden_ground_truth`
- `verdict_key`

Allowed appearances:

- Post-freeze scorer files.
- Post-hoc score reports.
- Architecture audit docs.
- Registration source files that are not loaded by live wrappers before trace freeze.

Stop rule: If a forbidden term is present in a runtime prompt path or runtime-only manifest with actual answer-key semantics, the run is blocked or invalid.

## Scoring-Map Separation Checks

Required separation:

- Live wrappers must not contain a scoring-map path.
- Live wrappers must not load scoring maps.
- Live wrappers must not read mixed-registration files before trace freeze.
- Post-hoc scorers may load scoring maps only after trace files exist and trace hashes are bound.
- Score artifacts must record scoring-map load order and trace hash binding.

Required evidence fields:

- `trace_frozen_before_scoring=true`
- `live_wrapper_has_scoring_map_path=false`
- `scoring_map_loaded_after_trace_hash_binding=true`
- `trace_calls_sha256`
- `trace_provider_calls_sha256`
- runtime-only manifest SHA-256

Stop rule: If the scoring map is reachable before trace freeze, the lane is invalid for HoloVerify proof credit.

## Gov, Selector, And Version Checks

Selector checks:

- Active selector must be trace-visible as `SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04` at this checkpoint.
- Selector hash must match `939c1ffbba74e9a526d454979b52980513d952eae4077cc817283380e596a1ec`.
- Final selector behavior must match declared policy.
- Tie-breaks must be policy-consistent and trace-explained.
- Blocker-closure decisions must include criteria trace.

Worker contract checks:

- Active worker contract must be trace-visible as `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04` at this checkpoint.
- Worker contract hash must match `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`.
- Required blocker fields must be present when blocker state exists.
- Worker outputs must preserve raw provider output separately from parsed decisions.

Gov checks:

- Full-Holo lanes require provider-backed Gov calls.
- Gov calls must appear in `TRACE_PROVIDER_CALLS.jsonl`.
- Gov rows must include provider identity and `provider_call_ok=true`.
- Gov prompt path must include gate/blocker state when gate/blocker state exists.
- Gov output must be preserved raw and parsed.
- Deterministic/local Gov may be used only in explicitly labeled ablation or patch-validation lanes and cannot be merged into full-HoloGov evidence.

## Packet And Key Defect Checks

Packet/key review is required before scoring interpretation and before any replacement merge.

Defect candidates include:

- Runtime-visible sources do not support the expected verdict.
- Current-cycle fact is missing.
- Source text is stale, ambiguous, or contradicts the key.
- Sibling pair has an unstable A/B relationship.
- The packet asks for a decision not grounded in the provided source bundle.
- The key depends on information absent from the runtime prompt.
- Packet ID, domain, or pair identifier is duplicated or malformed.

Handling rule:

- Preserve the raw trace-bound score.
- Quarantine the packet or pair from clean internal gates.
- Do not count a packet/key defect as a model-quality miss.
- Do not rewrite frozen runtime evidence.
- Introduce replacements only through a new runtime-only manifest, exact preflight, approved full route, frozen trace, and post-hoc score.
- Merge replacements only under the current accounting rule.

Current checkpoint example:

- `HVSF-FACTORY14F-017-B` remains a packet/key defect candidate.
- Original Tier 2 raw score remains `13/14` packets and `6/7` pairs.
- Replacement pair `HVSF-FACTORY14F-017R` supports the restored `7/7` clean internal pair gate only after control-valid post-hoc scoring.

## External DNA Reviewer Triggers

Bring in an external DNA reviewer, such as Claude Opus or Fable, when any of these are true:

- A public claim is about to move.
- A public denominator is changing.
- A live run result will unlock a new tier.
- A selector, worker contract, Gov route, or deterministic gate changed.
- A packet/key defect affected a score, gate, or replacement merge.
- A claim label warning appears, such as raw score versus score-valid diagnostic ambiguity.
- Tier 2 or Tier 3 evidence might be described outside internal directional scope.
- A new family/domain bank is added to the benchmark.
- The audit relies on a non-obvious accounting rule.
- A reviewer can falsify the mechanism by finding a runtime prompt leak, pre-freeze scoring-map access, missing Gov call, or claim-denominator mismatch.

Reviewer packet should be small and falsifier-oriented:

- Current checkpoint and commit.
- Exact lane and evidence class.
- Runtime-only manifest hash.
- Selector and worker contract versions and hashes.
- Preflight exact approval sentence.
- Run summary.
- `TRACE_CALLS.jsonl` hash.
- `TRACE_PROVIDER_CALLS.jsonl` hash.
- Raw prompt/output samples.
- Post-hoc score artifact.
- Packet/key quarantine notes.
- Exact public or internal claim under review.

Ask the reviewer concrete questions:

1. Can any runtime prompt path see truth, expected verdict, scoring, answer-key, or mixed-registration data?
2. Is scoring-map access impossible before trace freeze?
3. Are Gov calls present, provider-backed, and trace-visible for the claimed lane?
4. Does final selector behavior match the declared selector policy?
5. Does the claim use the correct denominator and evidence class?
6. Is any packet/key defect being counted as model performance?

## Red-Line Stop Rules

Stop and classify the audit as `FAIL` or `BLOCKED` if any condition appears:

- Runtime path contains truth, expected verdict, scoring fields, answer keys, or mixed-registration data.
- Scoring map is reachable before trace freeze.
- Selector version is missing, stale, or not trace-visible.
- Worker contract version is missing, stale, or not trace-visible.
- Gov calls are absent from a full-Holo lane.
- Gov calls are not provider-backed in a full-Holo lane.
- Gov does not see blocker/gate state when blocker/gate state exists.
- Expected and observed provider-call counts do not match.
- Raw prompts or raw outputs are missing.
- `TRACE_CALLS.jsonl` or `TRACE_PROVIDER_CALLS.jsonl` is missing.
- Deterministic blocker/gate checks are disabled or bypassed.
- Final selector behavior contradicts declared selector policy.
- A packet/key defect is interpreted as a model-quality miss.
- A replacement supplement rewrites the frozen original score.
- Public copy uses any denominator except blind-120 without a new public-claim audit.
- Tier 2 directional evidence is promoted to public benchmark evidence without external review and public-claim audit clearance.

## Final Cadence Finding

At commit `f4d11dc15a85e53c15399a1ade7f57ca2b6b8602`, the recurring HoloVerify architecture audit cadence should run daily during active benchmark work, weekly during benchmark development, before every live run, after every live run, and before every public claim. The cadence keeps the V5 selector, V4 worker contract, provider-backed Gov calls, runtime-only manifest separation, post-freeze scoring-map access, packet/key defect quarantine, and blind-120 public denominator under recurring audit.
