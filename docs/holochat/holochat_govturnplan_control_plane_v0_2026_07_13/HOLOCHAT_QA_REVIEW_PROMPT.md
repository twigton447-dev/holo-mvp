++HoloChat QA++ / ++HoloArchitecture++

Review `HOLOCHAT_GOVTURNPLAN_CONTROL_PLANE_V0`.

Scope: no-provider HoloChat GovTurnPlan control-plane repair only. No provider calls, credential reads, live HoloChat conversations, deploy, external sends, HoloVerify edits, watcher/queue actions, public claims, or destructive git operations.

Verify:
- HoloChat now builds exactly one admitted `GovTurnPlan` immediately before each visible worker provider call.
- The visible worker prompt consumes the rendered `GovTurnPlan` control packet, not multiple freeform GovAdvisor outputs.
- Provider/advisor outputs remain proposal/evidence only until admitted into typed GovTurnPlan fields.
- Gov never speaks directly to the user; workers speak, deterministic Gov operates.
- The plan contains all required fields: `turn_id`, `user_id`, `route`, `visible_worker_role`, `worker_provider_selection`, `advisor_provider_selection`, `intelligence_tier`, `selected_context_ids`, `dropped_context_ids`, `context_drop_reasons`, `memory_admissions`, `memory_rejections`, `artifact_refs`, `pinned_artifacts`, `tool_authorization`, `search_authorization`, `voice_tone_constraints`, `persona_identity_constraints`, `contradiction_repairs`, `state_corrections`, `fallback_eligibility`, `release_constraints`, `worker_prompt_baton`, `telemetry`, and `kernel_validation_result`.
- MiniMax remains fallback-only and is blocked as normal GovAdvisor/worker authority unless deterministic fallback eligibility is active.
- Tool/search use is represented in deterministic authorization fields.
- Memory context selection/rejection is recorded as GovTurnPlan admission state, while post-turn writes still require deterministic memory admission.
- Raw thought metadata and raw advisor text do not become worker-prompt authority.
- Streaming remains buffered until deterministic visible-output release admission.
- Universal HoloChat identity and no-scolding/no-gotcha/no-cold/no-sterile release protections remain intact for every user.

Block if the worker prompt can be assembled without GovTurnPlan, if raw advisor outputs bypass the plan, if provider output becomes Gov authority, if Gov text is released as user-facing speech, if MiniMax can route normally without fallback approval, if tool/search/memory/fallback/release decisions are outside deterministic Gov control, if named-user product law returns, or if the package authorizes live/provider/deploy activity.

Return one of:
- `PASS_TO_HOLOOPS`
- `BLOCK_TO_HOLOOPS` with exact missing repair.
