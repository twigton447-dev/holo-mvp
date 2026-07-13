Review `HOLOCHAT_GOV_KERNEL_AUTHORITY_REPAIR_V0`.

Scope: no provider calls, no live HoloChat conversations, no credential reads, no deploy, no external sends, no watcher/queue actions, and no HoloVerify edits.

Verify that the actual HoloChat visible path now treats provider-backed `GovernorAdapter` as GovAdvisor proposal source only, while deterministic HoloChat Gov Kernel admits, repairs, or rejects advisor proposals before they affect worker prompt tenor, search/tool authorization, visible claim correction, memory writes, consolidation, thread naming, fallback eligibility, or visible output release.

Specifically check:
- MiniMax is excluded from normal Gov/Advisor eligibility and remains fallback-only.
- Advisor private tenor/directive cannot enter the worker prompt unsanitized.
- Advisor memory proposals cannot write capsule state without deterministic explicit-fact admission.
- Advisor claim corrections cannot append to visible output without deterministic admission.
- Relationship rupture / cold / curt / scolding / gotcha / sterile patterns trigger deterministic warm repair.
- Turn-class policy escalates safety/action/memory/persona/relationship rupture/Gov uncertainty/conflict/product-critical UX to high/max and permits lower/fast only for low-risk routine turns.
- Runtime metadata distinguishes provider advisor proposal source from deterministic Gov Kernel authority.
- Existing local MiniMax fallback changes are preserved, not reverted.

Block if provider/API output can still directly become Gov authority, prompt directive, memory, tool/search authorization, visible correction, state update, or visible release without deterministic admission. Block if any HoloVerify files, credentials, provider calls, live conversations, deploy steps, external sends, or watcher/queue actions occurred. Do not approve Randall-facing release claims until HoloChat QA confirms this visible path protection.

Return `PASS_TO_HOLOOPS` or `BLOCK_TO_HOLOOPS` with exact missing control names if blocked.
