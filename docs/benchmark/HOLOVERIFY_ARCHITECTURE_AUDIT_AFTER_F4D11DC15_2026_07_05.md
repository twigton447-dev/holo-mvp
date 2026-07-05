# HoloVerify Architecture Audit After f4d11dc15

Callsign: ARCHITECTURE AUDIT SUBAGENT

Status: `PASS_WITH_CLAIM_LABEL_WARNING`

Audit label date: 2026-07-05

Current checkout commit audited: `f4d11dc15a85e53c15399a1ade7f57ca2b6b8602`

## Scope

This audit did not run providers, Holo live, solo, judges, or post-hoc scorers. It did not edit frozen runtime evidence. The only execution was provider-free regression coverage:

`python3 -m pytest tests/test_holoverify_blind_selector_repair_regression.py tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_v5_blocker_closure_validation.py`

Result: `34 passed`.

## Bottom Line

The current HoloVerify V5 mechanism is functioning as claimed for the audited architecture controls:

- Active selector: `SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04`, SHA-256 `939c1ffbba74e9a526d454979b52980513d952eae4077cc817283380e596a1ec`.
- Active worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`, SHA-256 `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`.
- Gov calls are present, provider-backed, and trace-visible.
- Runtime-only manifests and prompt paths are separated from truth/scoring/registration data.
- Scoring maps are loaded only by post-freeze scorers and are trace-hash-bound.
- Deterministic gates, blocker ledgers, and closure-validation state feed Gov and selector behavior.
- Raw prompts, raw outputs, `TRACE_CALLS.jsonl`, and `TRACE_PROVIDER_CALLS.jsonl` are preserved.

The checkpoint accounting is also sound if stated narrowly:

- Original Tier 2 raw score remains `13/14` packets and `6/7` complete pairs.
- Quarantine diagnostic after excluding the packet/key defect candidate is `13/13` packets and `6/6` pairs.
- Replacement pair passed `2/2` packets and `1/1` pair.
- The supplemented clean internal Tier 2 pair gate is `7/7`.
- Public denominator remains the blind-120 lane, not Tier 2 V5 rescue.

## Claim Warning

One claim label should be tightened. `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_MERGED_GATE_UPDATE_2026_07_04.json` should label the merged internal gate as `15/15 score-valid packet diagnostic and 7/7 clean internal pair gate`.

The accounting rule distinguishes:

- `15/15` = score-valid packet diagnostic across original Tier 2 plus replacement supplement.
- `14/14` = pair-equivalent packet count for the seven clean complete pairs.
- `7/7` = clean complete-pair gate.

So the mechanism passes, but the safer label is: `15/15 score-valid packet diagnostic and 7/7 clean internal pair gate`.

## Architecture Checklist

| # | Check | Status | Evidence |
|---:|---|---|---|
| 1 | Selector version active and trace-visible | PASS | Current code and runtime results stamp `SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04`; replacement and Tier 2 runtime results show the same per-packet selector version. |
| 2 | Worker contract active and trace-visible | PASS | Current code and runtime results stamp `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`; required keys include `blocker_type`, `blocker_resolution`, and `structured_blocker_resolution`. |
| 3 | Gov calls present and provider-backed | PASS | Tier 2 has `28` Gov provider calls; replacement has `4`. `TRACE_PROVIDER_CALLS.jsonl` rows show Gov role via MiniMax with `provider_call_ok=true`. |
| 4 | Runtime-only manifest separation | PASS | V5 Tier 2 and replacement wrappers bind only runtime-only manifests and do not keep mixed-registration JSON paths. Runtime manifests contain only `classification`, `packet_count`, `packets`, and `runtime_consumable`. |
| 5 | No scoring-map access before trace freeze | PASS | Live summaries report `trace_frozen_before_scoring=true`, `live_wrapper_has_scoring_map_path=false`, and post-hoc scorers load scoring maps after trace hash binding. |
| 6 | No truth/scoring/mixed-registration data in runtime prompt path | PASS | Scan found zero hits for truth, expected verdict, scoring, legacy packet ID, sibling, answer key, target bucket, or registration terms in both V5 runtime manifests, runtime payloads, and live prompt files. |
| 7 | Deterministic gates active | PASS | Code computes source-derived dependency checks and blocker closure validation; targeted tests passed dependency mismatch, stale authorization, timezone, tolerance, and blocker-closure cases. |
| 8 | Gov sees gate/blocker state | PASS | Gov prompt for replacement B includes prior blocker `ART-001-BLK-AE730AC4` and blocked move `do not silently drop source-grounded blockers`; Gov output is provider-backed and preserved. |
| 9 | Final selector behavior matches declared selector policy | PASS | Replacement B selected `ART-003` by criteria trace. Original Tier 2 miss selected `ART-001` because all three artifacts were valid ALLOW ties and earliest-turn tie-break applied; that is policy-consistent even though score-wrong. |
| 10 | Raw prompts, raw outputs, `TRACE_CALLS`, `TRACE_PROVIDER_CALLS` preserved | PASS | Tier 2 has `70` prompt files, `70` raw provider outputs, `70` trace rows, and `70` provider trace rows. Replacement has `10` of each. |
| 11 | Claim language matches evidence | WARN | Core claim boundary matches evidence. The only warning is the merged-gate packet label; it should be `15/15 score-valid packet diagnostic`. |

## Trace-Bound Evidence

### Original Tier 2 Run

Run folder:

`docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z`

Runtime controls:

| Metric | Observed |
|---|---:|
| Provider calls | `70/70` |
| Worker provider calls | `42` |
| Gov provider calls | `28` |
| Provider failures | `0` |
| Runtime firewall | `true` |
| Trace frozen before scoring | `true` |
| Scoring map loaded after trace hash binding | `true` |

Post-hoc score:

| Level | Result |
|---|---:|
| Packets | `13/14` |
| Complete pairs | `6/7` |
| Failed packet | `HVSF-FACTORY14F-017-B` |
| Expected / final | `ESCALATE` / `ALLOW` |

This run is not a raw `7/7` pass.

### Replacement Pair

Run folder:

`docs/benchmark/holoverify_v5_tier2_fn_rescue_replacement_pair_2026_07_04/live_runs/run_20260704T074130Z`

Runtime controls:

| Metric | Observed |
|---|---:|
| Provider calls | `10/10` |
| Worker provider calls | `6` |
| Gov provider calls | `4` |
| Provider failures | `0` |
| Runtime firewall | `true` |
| Trace frozen before scoring | `true` |
| Scoring map loaded after trace hash binding | `true` |

Post-hoc score:

| Level | Result |
|---|---:|
| Packets | `2/2` |
| Complete pairs | `1/1` |
| Result classification | `V5_TIER2_FN_RESCUE_REPLACEMENT_PAIR_PASSED` |

The replacement supplement supports the clean internal pair-gate merge, not a public benchmark claim.

### Public Denominator

The current clean public-facing denominator remains blind-120:

`docs/benchmark/HOLOVERIFY_BLIND_120_CLEAN_SCOREBOARD_ROLLUP_2026_07_03.md`

Allowed internal claim there:

`On the blind-120 packet bank, HoloVerify scored 120/120. The same three model families run alone as one-shot solo baselines produced 14 failures across 360 calls, affecting 11 packets.`

The same rollup forbids restoring the old `614/614` denominator, claiming broad model superiority, or updating public statistical claims before review language is rebuilt.

## Final Audit Finding

The architecture mechanism is operating as claimed at the audited checkpoint. The only correction needed is claim-language precision around the merged-gate packet label; use `15/15 score-valid packet diagnostic` and reserve `7/7 clean internal pair gate` for the clean complete-pair gate.
