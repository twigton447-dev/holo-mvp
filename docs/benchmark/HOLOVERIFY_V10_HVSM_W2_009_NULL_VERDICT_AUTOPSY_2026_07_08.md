# HoloVerify V10 HVSM-W2-009 Null Verdict Autopsy

Date: 2026-07-08

Owner: ++HoloOps++

SOC lane: ++HoloOps SOC++ owns key/provider diligence and trust/safety claim boundaries. This engineering autopsy does not create SOC, ISO, production-safety, or design-partner readiness evidence by itself.

## Finding

The `HVSM-W2-009` no-select/null verdict in the 07-07 repaired-packet-bank run came from the V10 value-tuple closure layer feeding the selector a `PACKET_REPAIR_REQUIRED` ledger for both siblings.

After Fable's `BLOCK_NEEDS_DIFF_REVIEW`, this autopsy preserves the critical distinction between two packet schemas:

- Original Wave 2 / V9 tiny 009-A is name-list-only. It lacks exact source-bound values and must remain fail-closed.
- Repaired V10 009-A exposes exact request/record `*_id` values. It may close only when exact value equality is proven.

The immediate runtime symptom was selector rejection:

- `HVSM-W2-009-A` -> `PKT-B5B6E467B0E5DA2DC74DDC3D`
- `HVSM-W2-009-E` -> `PKT-12511FF461EBEA702CEAF17E`
- both had `packet_status=SELECTED`
- both had `packet_selectable=false`
- both had `final.artifact_id=null`
- both had `final.verdict=null`
- both had `selector_blocked_reason=no_structurally_valid_artifact`

The selector was behaving according to its contract. It refused every artifact because each artifact had `packet_repair_required_count=1`, making it structurally invalid.

## Cause Matrix

| Candidate | Verdict | Notes |
| --- | --- | --- |
| Packet schema | Split | Original Wave 2 009-A schema is insufficient and must remain fail-closed. Repaired V10 009-A/E schema exposes the intended request/record tuples. |
| V10 value-tuple closure | Repaired-run root cause | In the repaired V10 run, surgical closure still expected old name-list fields such as `surgeon_match`, while repaired V10 packets expose `surgeon_id` and other concrete `*_id` values. |
| Selector behavior | Proximal cause, not bug | Selector correctly returned no selected artifact because no artifact was structurally valid after closure produced `PACKET_REPAIR_REQUIRED`. |
| Scorer extraction | Exonerated | Posthoc scorer copied `final.verdict` and `selection.selected_artifact_id` from the frozen runtime result; it did not create the null. |
| Live-wrapper trace parsing | Exonerated | Calls 1-5 map to 009-A and calls 6-10 map to 009-E; provider transport succeeded for both packets. |

## Patch Applied

Patched `holoverify_blind_runner_v0.py`:

- added surgical value aliases:
  - `implant_lot_release -> implant_lot_release_id`
  - `surgical_use_approval -> surgical_use_approval_id`
  - `sterile_processing_signoff -> sterile_processing_signoff_id`
  - `surgeon_match -> surgeon_id`
- preserved raw value tokens during extraction instead of extracting after hyphen-normalized phrase text
- allowed a record-side concrete value to satisfy the surgical name-list dimension
- required exact value equality for the surgical 009 family before name-list support can clear
- classified surgical value mismatch as `SOURCE_OPEN`, so the 009-E control can become a selectable ESCALATE instead of `PACKET_REPAIR_REQUIRED`
- kept missing tuple support as `PACKET_REPAIR_REQUIRED`

Added `tests/test_holoverify_v10_value_tuple_closure.py`:

- repaired 009-A value tuple closes and selects ALLOW
- repaired 009-E `ABSENT` approval is SOURCE_OPEN and selects ESCALATE
- repaired 009 with a missing required value still requires packet repair
- original Wave 2 009-A name-list-only support still requires packet repair and cannot select ALLOW

## Verification

No providers were called for the V10 patch/autopsy validation.

Restored local test runtime:

- created `.venv312` from the Codex-bundled Python 3.12 runtime
- installed `pytest>=8.0` into that local venv only

No-provider verification:

- direct V10 regression functions: `PASS`
- unpatched `HEAD` runner check on 009-A and 009-E: both returned `PACKET_REPAIR_REQUIRED`, `value_equality_status=NOT_CHECKED`
- repaired 009-A closure: `SOURCE_CLOSED`, `VALUE_EQUALITY_PROVEN`, final `ALLOW`
- repaired 009-E closure: `SOURCE_OPEN`, `VALUE_MISMATCH`, final `ESCALATE`
- repaired 009-A with missing required surgical value remains `PACKET_REPAIR_REQUIRED`
- original Wave 2 009-A name-list-only payload remains `PACKET_REPAIR_REQUIRED`, `MISSING_REQUIRED_FIELD_VALUE`, final not `ALLOW`
- bytecode compile check passed with `PYTHONPYCACHEPREFIX=/private/tmp/holo_pycache`

Focused pytest gate:

```text
.venv312/bin/python -m pytest \
  tests/test_holoverify_v10_value_tuple_closure.py \
  tests/test_holoverify_v9_generic_blocker_resolution.py \
  tests/test_holoverify_v6_scope_dependency_gate.py \
  tests/test_holoverify_blind_selector_repair_regression.py \
  tests/test_holoverify_v5_blocker_closure_validation.py
```

Latest local result after Fable's block and the fail-closed guard:

```text
.venv312/bin/python -m pytest \
  tests/test_holoverify_v10_value_tuple_closure.py \
  tests/test_holoverify_v9_generic_blocker_resolution.py \
  tests/test_holoverify_v8_generic_false_blocker_suppression.py
```

Result: `41 passed`.

Additional gate:

```text
.venv312/bin/python -m pytest \
  tests/test_holoverify_v6_scope_dependency_gate.py \
  tests/test_holoverify_blind_selector_repair_regression.py \
  tests/test_holoverify_v5_blocker_closure_validation.py
```

Result: `33 passed`.

Adjacent no-provider safety gate:

```text
.venv312/bin/python -m pytest \
  tests/test_holoverify_v7_false_blocker_suppression.py \
  tests/test_holoverify_v8_generic_false_blocker_suppression.py \
  tests/test_holoverify_blind_canary_live_wrapper.py \
  tests/test_holoverify_blind_120_live_wrapper.py \
  tests/test_holoverify_content_contract_failure_no_retry.py \
  tests/test_blind_lane_t4_selector_sweep.py
```

Result: `90 passed, 3 skipped`.

## Evidence Boundary

The frozen run `run_20260707T181449Z` remains failed. This patch does not retroactively convert that trace into a win.

Next valid evidence must be:

1. no-provider regression under the patched runner,
2. preflight with no scoring-map leakage,
3. fresh trace-frozen live validation after keys are loaded and approved,
4. posthoc scoring only after trace freeze.

## API Key Status

Credential-only triad smoke passed after local `.env` restoration.

Smoke boundary:

- exactly 3 provider calls
- no benchmark/customer/source data
- prompt: `Return exactly OK.`
- report only pass/fail metadata
- never print secret values

Latest status:

- `xai/grok-3-mini`: `PASS`
- `openai/gpt-5.4-mini`: `PASS`
- `minimax/MiniMax-M2.5-highspeed`: `PASS`

## Denominator Note

The 220 packet / 110-110 claim is arithmetically correct only as a future condition:

- blind-120 = 120 packets / 60 pairs / 60 ALLOW / 60 ESCALATE
- stress expansion = 100 packets / 50 pairs / 50 ALLOW / 50 ESCALATE
- combined after clean Holo execution = 220 packets / 110 pairs / 110 ALLOW / 110 ESCALATE

Current stress expansion evidence is not yet that combined Holo denominator unless the 100 stress packets are run through Holo, patched, selected cleanly, trace-frozen, posthoc scored, non-overlapping, and claim-bounded as internal evidence.

## Handoff

Back to ++HoloOps++.

What happens next:

- HoloArchitecture: review the closure patch and, if accepted, extend the same value-alias pattern to 010/027 only under no-provider tests.
- HoloStats: do not expand denominator claims from V10 until a fresh clean run exists.
- HoloOps SOC: keep provider/key smoke and trust/safety claim language separate from benchmark engineering proof.
- HoloMiner: only rebuild packet bank if HoloArchitecture rejects code-side value-tuple closure support.
