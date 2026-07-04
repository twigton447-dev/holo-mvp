# HoloChat Governed Shadow No-Provider Test Spec - 2026-07-05

Status: concrete test specification only. No provider calls. No production behavior changes. No staging, commit, or push.

Sources:

- `docs/product/HOLOCHAT_GOVERNED_SHADOW_PRESSURE_TEST_PLAN_2026_07_05.md`
- `docs/product/HOLOCHAT_GOVERNED_SHADOW_PRESSURE_TEST_PLAN_2026_07_05.json`
- Existing no-provider fixtures in `tests/test_holochat_governed_shadow.py`, `tests/test_holochat_runtime_routing.py`, `tests/test_holochat_shadow.py`, and `tests/test_holo_context.py`

## Test Harness Rules

All tests in this spec must be no-provider tests.

Required harness posture:

- Use fake adapters with deterministic `chat_call` and `stream_chat` methods.
- Use fake Gov and fake HoloBrain objects.
- Monkeypatch all env flags and model keys needed for deterministic behavior.
- Do not instantiate vendor SDK clients through real keys.
- Do not call `load_adapters()` unless the loader is monkeypatched.
- Do not call web search unless `web_search.search` is monkeypatched.
- Assert provider raw error bodies, raw prompts, raw HoloBrain memory, capsule ids, API keys, cookies, auth headers, and private identifiers do not appear in returned metadata.
- Assert visible answer text is stable when a test is about runtime or shadow metadata.

Recommended executable location if these specs are later converted to code:

- `tests/test_holochat_governed_shadow_product_contract.py`
- `tests/test_holochat_runtime_dashboard_modes.py`

## Coverage Map

| ID | Requirement | Current coverage | New contract needed |
| --- | --- | --- | --- |
| HC-GS-NP-001 | Normal chat path unchanged when shadow is off | Partial | Yes |
| HC-GS-NP-002 | Hard-chat trigger fires for risk/strategy/multi-part prompts | Partial | Yes |
| HC-GS-NP-003 | Governed shadow metadata is safe | Partial | Yes |
| HC-GS-NP-004 | Gov cannot choose models | Covered narrow | Yes, broaden |
| HC-GS-NP-005 | Shadow cannot replace visible answer without explicit product gate | Partial | Yes |
| HC-GS-NP-006 | Runtime dashboard labels base vs shadow vs full governed modes | Partial | Yes |
| HC-GS-NP-007 | Continuity pressure test | Partial | Yes |
| HC-GS-NP-008 | "Holo feels lobotomized" diagnostic | New | Yes |
| HC-GS-NP-009 | No raw HoloBrain memory dump to workers | Partial | Yes |
| HC-GS-NP-010 | Failure preservation if shadow run fails | Covered narrow | Yes, broaden |

## Shared Fixtures

Use these fixture shapes across the tests.

### Fake Analyst Adapter

Purpose: produce deterministic visible answers and capture system prompt, history, user message, temperature, and image payloads.

Required fields:

- `provider`
- `model_id`
- `visible_text`
- `last_system_prompt`
- `last_history`
- `calls`
- optional `fail`

Required behavior:

- `chat_call(system_prompt, history, user_message, temperature, images=None)` appends safe call metadata and returns `(visible_text, input_tokens, output_tokens)`.
- If `fail` is true, raise `RuntimeError("provider raw body should not surface")`.

### Fake Shadow Adapter

Purpose: run the governed shadow roster without providers.

Required behavior:

- Return worker text for worker prompts.
- Return Gov baton text for Gov prompts.
- Capture prompts for safety assertions.
- Never call real provider clients.

### Fake Governor

Purpose: exercise HoloChat controller surfaces without provider calls.

Required behavior:

- `assess_chat_temperature` returns a fixed value.
- `should_search` returns `None` unless test explicitly checks deterministic web routing.
- `surface_thought` returns `None`.
- `assess_tenor` can return a fixed directive for personality/continuity diagnostics.
- `verify_claims` returns `(response_text, [])`.
- `extract_context_updates` returns `{}` unless memory-write metadata is under test.
- `generate_conversation_paths` returns three deterministic path strings.

### Fake HoloBrain

Purpose: provide bounded capsule context and life context without DB access.

Required behavior:

- `get_capsule_context(capsule_id)` returns selected synthetic rows plus trap rows.
- `load_life_context(capsule_id)` returns selected synthetic rows plus overflow rows.
- `load_last_consolidation(capsule_id)` returns a compact fake session note when needed.
- Persistence methods are no-ops.

Trap values:

- `api_key = must-not-leak`
- `raw_memory = SHOULD_NOT_APPEAR`
- `raw_prompt = SHOULD_NOT_APPEAR`
- `authorization = Bearer SHOULD_NOT_APPEAR`
- `capsule_id = raw-capsule-id`
- `private_note = hidden provider prompt should not surface`

## HC-GS-NP-001 - Normal Chat Path Unchanged When Shadow Is Off

Requirement: normal chat must remain the base serial analyst path when `HOLOCHAT_GOVERNED_SHADOW` is off.

Target surfaces:

- `HoloChatEngine.send_message`
- `_turn_runtime_metadata`
- `run_governed_shadow`

Setup:

- `monkeypatch.delenv("HOLOCHAT_GOVERNED_SHADOW", raising=False)`
- `monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)`
- Engine built with one or three fake analyst adapters.
- Fake Gov and Fake HoloBrain.

Steps:

1. Send a normal prompt: `Give me a simple plan for the day.`
2. Capture returned response, runtime metadata, adapter call count, and session history.

Assertions:

- Response equals the selected fake analyst visible text.
- Exactly one visible analyst call occurs.
- `runtime.serial_call is True`.
- `runtime.parallel_fanout is False`.
- `runtime.analyst_call_mode == "serial_one_per_turn"`.
- `runtime.selection_mode == "round_robin"`.
- `runtime.selected_provider` and `runtime.selected_model` match the fake selected analyst.
- `runtime.governor_role == "controller_check_layer"`.
- `runtime.holo4dna_mode == "off"`.
- If `runtime.governed_shadow` exists, status is `off` or `skipped`, `call_count == 0`, and `visible_answer_replaced is False`.
- No shadow worker calls occur.

Current repo evidence:

- `tests/test_holochat_runtime_routing.py::test_browser_chat_path_remains_serial_and_reports_runtime`
- `holo_governed_shadow.py::safe_skip_metadata`

## HC-GS-NP-002 - Hard-Chat Trigger Fires For Risk, Strategy, And Multi-Part Prompts

Requirement: shadow trigger must fire for hard prompts and stay off for small talk.

Target surface:

- `holo_governed_shadow.governed_shadow_trigger`

Setup:

- No engine needed.

Test cases:

| Prompt | Expected |
| --- | --- |
| `Please verify this decision and risk.` | should run, hard-chat risk/decision |
| `Stress test this strategy before I act.` | should run, hard-chat strategy |
| `What should we do about this?` | should run, hard-chat what should |
| `1. Map the risk\n2. Find the weak assumption\n3. Give me the tradeoff` | should run, multi-part |
| `Question one? Question two? Question three?` | should run, multi-part |
| `hello` | should not run |
| empty string | should not run |
| any short prompt with `thread_health_level="RED"` | should run, thread health red |
| any prompt with `context_token_estimate=12000` | should run, context window stress |

Assertions:

- `ShadowTrigger.should_run` matches the table.
- Reasons are stable enough for UI/debug use: `hard_chat_term:*`, `multi_part_prompt`, `thread_health_red`, or `context_window_stress`.

Current repo evidence:

- `tests/test_holochat_governed_shadow.py::test_governed_shadow_trigger_targets_hard_chats_only`

## HC-GS-NP-003 - Governed Shadow Metadata Is Safe

Requirement: governed shadow result must expose safe metadata only.

Target surfaces:

- `run_governed_shadow`
- `build_worker_prompt`
- `build_gov_prompt`
- `_summary`

Setup:

- `monkeypatch.setenv("HOLOCHAT_GOVERNED_SHADOW", "1")`
- Use fake roster adapters for `xai/grok-3-mini`, `openai/gpt-5.4-mini`, and `minimax/MiniMax-M2.5-highspeed`.
- HoloState includes rolling summary and continuity ledger.
- Capsule context includes trap values.

Steps:

1. Run governed shadow on a hard prompt.
2. Serialize the returned metadata with `json.dumps(..., sort_keys=True).lower()`.
3. Inspect captured fake adapter prompts separately.

Assertions:

- Result status is `complete`.
- `safe_metadata_only is True`.
- `visible_answer_replaced is False`.
- Public result JSON does not contain:
  - `must-not-leak`
  - `authorization`
  - `bearer`
  - `raw_prompt`
  - `raw_memory`
  - `private_note`
  - `hidden provider prompt`
  - `raw-capsule-id`
  - `provider raw body`
- Public result JSON does not contain full worker system prompts or Gov system prompts.
- Captured worker prompt may include sanitized selected memory summaries, but not raw trap values.
- `token_totals` and `call_sequence` are present.
- `call_sequence` only includes slot, role, provider, model, provider_call_ok, parse_ok, and admissible.

Current repo evidence:

- `tests/test_holochat_governed_shadow.py::test_governed_shadow_runs_exact_five_call_sequence_with_gov_sandwich`
- `tests/test_holochat_governed_shadow.py::test_holochat_runtime_reports_governed_shadow_without_replacing_answer`

## HC-GS-NP-004 - Gov Cannot Choose Models

Requirement: Gov baton must fail closed if it tries to select a model or provider.

Target surface:

- `holo_governed_shadow.parse_gov_baton`

Setup:

- No engine needed.

Forbidden baton payloads:

- `selected_model=openai/gpt-5.4-mini`
- `worker_model=xai/grok-3-mini`
- `model_choice=minimax/MiniMax-M2.5-highspeed`
- `provider_choice=openai`
- `next_model=anthropic/claude-sonnet-4-6`

Assertions:

- Every forbidden key raises `ValueError`.
- Error string contains `gov_model_selection_forbidden`.
- No partial baton object is returned.

Positive control:

- A baton with only allowed control fields parses successfully:
  - `route_verdict=CONTINUE_WORKER`
  - `critical_constraints=preserve source boundary`
  - `next_worker_directive=challenge the weak assumption`

Current repo evidence:

- `tests/test_holochat_governed_shadow.py::test_gov_baton_rejects_model_selection_fields`

## HC-GS-NP-005 - Shadow Result Cannot Replace Visible Answer Without Explicit Product Gate

Requirement: shadow artifacts must not modify the user-visible answer unless a future explicit product gate exists and is enabled.

Target surfaces:

- `HoloChatEngine.send_message`
- `run_governed_shadow`
- `select_best_artifact`

Setup:

- `monkeypatch.setenv("HOLOCHAT_GOVERNED_SHADOW", "1")`
- Fake visible analyst returns: `VISIBLE_BASE_ANSWER`
- Fake final shadow worker returns: `SHADOW_BETTER_ANSWER`
- No product gate env var exists in current runtime.

Steps:

1. Send hard prompt through `HoloChatEngine.send_message`.
2. Capture response and runtime governed shadow metadata.

Assertions:

- API `response == "VISIBLE_BASE_ANSWER"`.
- Shadow metadata can select the final artifact, but `visible_answer_replaced is False`.
- The API response body does not replace, append, or silently blend `SHADOW_BETTER_ANSWER`.
- Runtime can expose `final_selector.selection_reason`, but not the raw full shadow answer unless intentionally designed later.
- If a future product gate is added, this test must fail until it is updated to assert explicit opt-in gate semantics.

Current repo evidence:

- `tests/test_holochat_governed_shadow.py::test_holochat_runtime_reports_governed_shadow_without_replacing_answer`
- `holo_governed_shadow.py:_summary`

## HC-GS-NP-006 - Runtime Dashboard Labels Base, Shadow, And Full Governed Modes

Requirement: dashboard and runtime metadata must clearly distinguish base runtime, shadow-enabled runtime, and all-cylinders/full-governed-ready state.

Target surfaces:

- `main._holochat_all_cylinders_status`
- `HoloChatEngine.runtime_status`
- `frontend/runtime.html`
- `frontend/chat.html` runtime panel row builder

Setup:

- Use synthetic `chat_status` dicts for `_holochat_all_cylinders_status`.
- Use static source inspection for frontend labels, or a JS-capable unit harness if introduced later.

Cases:

1. Base initialized, shadow disabled.
2. Base initialized, shadow enabled.
3. Base missing required checks.
4. Per-turn runtime has `governed_shadow.status == "complete"`.
5. Per-turn runtime has `governed_shadow.status == "invalid"`.

Assertions:

- Case 1 status is `base_ready_shadow_off`, `base_runtime_ready is True`, `hard_chat_shadow_ready is False`, and attention includes `governed_shadow_disabled`.
- Case 2 status is `ok`, `all_cylinders is True`, `hard_chat_shadow_ready is True`.
- Case 3 status is `attention` and includes failed check names.
- `/runtime` source includes labels for `All Cylinders`, `Base runtime`, `Hard-chat shadow`, `Visible Chat Lane`, `Governor`, `State And Memory`, `Safety`, and `Governed Shadow Sequence`.
- Chat runtime panel includes labels for `Runtime`, `This turn`, `Mode`, `Governor`, `Full memory to analyst`, `Memory delivery`, `Continuity ledger`, `Holo4DNA`, and `Governed shadow`.
- No UI copy claims `4DNA active`, `four models answered this turn`, or `full governed answer` unless an explicit runtime field supports it.

Current repo evidence:

- `main.py::_holochat_all_cylinders_status`
- `frontend/runtime.html`
- `frontend/chat.html::buildRuntimeRows`

## HC-GS-NP-007 - Continuity Pressure Test

Requirement: long-thread continuity must survive bounded history through state, rolling summary, Gov Arc State, and continuity ledger.

Target surfaces:

- `HoloChatEngine.send_message`
- `_bounded_adapter_history`
- `_update_rolling_summary_after_turn`
- `_update_continuity_ledger_after_turn`
- `_holo_voice_diagnostics`

Setup:

- `HOLOCHAT_ADAPTER_HISTORY_MESSAGES=4`
- `HOLOCHAT_ADAPTER_HISTORY_CHARS=2000`
- `HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS=500`
- Fake engine with capturing adapter, Fake Gov, and Fake HoloBrain.
- Seed session history with at least 40 messages.
- Seed early constraint: `Do not optimize for speed; optimize for trust.`
- Seed Gov Arc State with `user_goal`, `current_tension`, and `settled_decisions`.

Steps:

1. Send a later turn: `What constraint should block the obvious shortcut?`
2. Inspect adapter history, system prompt, runtime metadata, rolling summary, continuity ledger, and voice diagnostics.

Assertions:

- Adapter receives no more than configured raw history limits.
- Runtime reports omitted history count.
- System prompt includes `HOLO STATE OBJECT`, `ROLLING_SUMMARY`, `GOV ARC STATE`, and `CONTINUITY_LEDGER`.
- The early constraint is preserved in either rolling summary, continuity ledger, or Gov Arc State.
- Runtime reports:
  - `memory_delivery_mode == "rolling_summary_selected_context"`
  - `continuity_ledger_mode == "active_prompt_structured_private"`
  - `structured_state_object_mode == "active_prompt"`
  - `baton_pass_mode == "active_prompt"`
  - `analyst_receives_full_memory is False`
- No full-memory or perfect-continuity claim appears in runtime text.

Current repo evidence:

- `tests/test_holochat_runtime_routing.py::test_second_turn_prompt_includes_private_continuity_ledger`
- Long-thread bounded-history tests in `tests/test_holochat_runtime_routing.py`

## HC-GS-NP-008 - "Holo Feels Lobotomized" Diagnostic Regression Test

Requirement: if Holo feels flattened, the runtime should make model, route, context, and personality regressions diagnosable without providers.

Target surfaces:

- `HoloChatEngine.send_message`
- `_holo_voice_diagnostics`
- `_turn_runtime_metadata`
- `build_runtime_identity_block`
- `HOLO_CHAT_SYSTEM_PROMPT`

Setup:

- Fake capturing adapter with visible answer: `DIAGNOSTIC_VISIBLE_ANSWER`.
- Fake Gov returns a private tenor directive: `Be direct, concrete, non-generic, and preserve the trust-over-speed constraint.`
- Fake HoloBrain returns capsule context, life context, and last consolidation.
- Run one signed-in turn and one incognito turn.

Diagnostic fields to assert:

- Selected provider/model.
- Runtime profile.
- Serial vs shadow mode.
- Capsule attached.
- Capsule context count.
- Selected Gov context count.
- Life context count.
- Rolling summary present.
- Captain brief present.
- Runtime identity in prompt.
- Holo state object in prompt.
- Gov Arc State in prompt.
- Governed shadow status.
- Adapter history omitted count.
- Web search attempted/status.
- Voice diagnostic risk flags.

Assertions for signed-in turn:

- Runtime identifies selected provider/model and profile.
- `holo_voice_diagnostics.status` is `ok` or `attention` with explicit flags.
- Risk flags do not include `capsule_not_attached` when capsule id is supplied.
- Risk flags do not include `runtime_identity_missing`.
- Risk flags do not include `holo_state_object_missing`.
- Captured system prompt contains canonical doctrine markers:
  - `Canonical HoloChat Doctrine`
  - `HoloChat is not omniscient.`
  - `Sound human`
  - `If a sentence could appear in a generic AI demo, rewrite it`
- Captured system prompt contains the fake Gov tenor directive.

Assertions for incognito turn:

- Runtime explicitly marks stripped memory through risk flags or incognito metadata.
- Capsule context is absent.
- Memory claims remain honest.

Failure meaning:

- Missing runtime identity means route/context regression.
- Missing capsule context counts mean memory attachment regression.
- Missing Gov directive means personality/tenor regression.
- Missing selected provider/model means model-route observability regression.
- `governed_shadow.status` off/skipped explains why shadow did not improve the visible answer.

Current repo evidence:

- `tests/test_holochat_runtime_routing.py::test_browser_chat_prompt_includes_runtime_identity_and_capped_memory`
- `tests/test_holochat_runtime_routing.py::test_prompt_assembly_loads_canonical_doctrine_docs`
- `_holo_voice_diagnostics` in `chat_engine.py`

## HC-GS-NP-009 - No Raw HoloBrain Memory Dump To Workers

Requirement: shadow workers may receive selected, sanitized memory summaries only, never raw HoloBrain dumps.

Target surfaces:

- `holo_governed_shadow.build_state_brief`
- `holo_governed_shadow._safe_memory_items`
- `holo_governed_shadow.build_worker_prompt`
- `HoloContextBuilder.build`

Setup:

- Capsule context has at least 20 rows, including nested objects, long values, and trap values.
- Governed shadow enabled.
- Capturing shadow adapters.

Steps:

1. Run `run_governed_shadow` with hard prompt and trap capsule context.
2. Inspect captured worker prompts.
3. Inspect public metadata JSON.

Assertions:

- Worker prompt includes `selected_memory_only` or equivalent selected-memory section.
- Worker prompt does not include raw dictionary dump syntax for the full capsule context.
- Worker prompt does not include more than the configured safe item limit.
- Worker prompt and metadata do not include trap values:
  - `must-not-leak`
  - `SHOULD_NOT_APPEAR`
  - `Bearer`
  - `raw-capsule-id`
  - `private_note`
- Memory rows are compacted and sanitized.
- Public metadata does not include raw memory rows.

Current repo evidence:

- `tests/test_holo_context.py::test_context_memory_blocks_are_capped_and_do_not_include_sensitive_keys`
- `tests/test_holo_context.py::test_context_budget_rows_do_not_expose_raw_memory_or_search_text`
- Existing governed-shadow safe metadata tests

## HC-GS-NP-010 - Failure Preservation If Shadow Run Fails

Requirement: a failed shadow run must preserve safe invalid metadata and leave the visible answer untouched.

Target surfaces:

- `run_governed_shadow`
- `_run_governed_shadow_for_turn`
- `HoloChatEngine.send_message`

Setup:

- `HOLOCHAT_GOVERNED_SHADOW=1`
- Fake visible analyst returns `VISIBLE_BASE_ANSWER`.
- One shadow worker adapter fails with `RuntimeError("provider raw body should not surface")`.
- Include a second case where the exact roster is missing.

Assertions for provider failure:

- `runtime.governed_shadow.status == "invalid"`.
- `invalidation_reason` identifies `WORKER_FAILURE` or `GOV_FAILURE`.
- `root_failure.error == {"type": "RuntimeError"}`.
- Raw provider body is not exposed.
- Visible response remains `VISIBLE_BASE_ANSWER`.
- `visible_answer_replaced is False`.
- Partial `call_sequence` is preserved up to the failed slot.
- Token totals remain present and safe.

Assertions for missing roster:

- Shadow status is `skipped`.
- `missing_roster` lists missing provider/model identities.
- Visible response remains `VISIBLE_BASE_ANSWER`.
- `visible_answer_replaced is False`.

Current repo evidence:

- `tests/test_holochat_governed_shadow.py::test_provider_failure_preserves_invalid_shadow_without_raw_error`
- `tests/test_holochat_governed_shadow.py::test_holochat_shadow_skips_when_exact_roster_missing`

## Execution Order

Recommended order when converting this spec into executable tests:

1. Add/extend governed-shadow pure function tests: HC-GS-NP-002, HC-GS-NP-004.
2. Add/extend shadow run tests: HC-GS-NP-003, HC-GS-NP-005, HC-GS-NP-009, HC-GS-NP-010.
3. Add/extend engine runtime tests: HC-GS-NP-001, HC-GS-NP-007, HC-GS-NP-008.
4. Add runtime dashboard/static label tests: HC-GS-NP-006.

## Stop Rules

Stop and report instead of running tests if:

- Any test path would require real provider keys.
- A test tries to call OpenAI, Anthropic, Google, xAI, MiniMax, Mistral, DeepSeek, Tavily, Supabase, Stripe, Resend, or external network.
- A proposed assertion requires changing production behavior before the test spec is accepted.
- A test cannot be made deterministic with fake adapters and fake Gov/HoloBrain objects.

## Acceptance Standard

The no-provider suite is acceptable when:

- All ten IDs are implemented as deterministic tests or intentionally marked as static/source tests.
- No provider/network calls occur.
- Normal visible answer behavior remains unchanged when shadow is off.
- Governed shadow can be enabled, triggered, validated, failed, and inspected without leaking hidden prompts or memory.
- Runtime/UI labeling makes base vs shadow vs all-cylinders state obvious.
- The "Holo feels lobotomized" diagnostic identifies whether the issue is model route, missing context, missing Gov directive, shadow off/skipped, or persona/doctrine regression.
