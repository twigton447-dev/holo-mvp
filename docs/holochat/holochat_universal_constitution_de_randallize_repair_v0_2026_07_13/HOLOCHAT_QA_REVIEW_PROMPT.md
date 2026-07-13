Review `HOLOCHAT_UNIVERSAL_CONSTITUTION_DE_RANDALLIZE_REPAIR_V0`.

Scope: no provider calls, no credential reads, no live HoloChat conversations, no deploy, no external sends, no watcher/queue actions, no public claims, and no HoloVerify edits.

Authority: HoloChat QA blocked `HOLOCHAT_CONSTITUTIONAL_TONE_RELEASE_GUARD_V0` because canonical constitution and Gov doctrine hardcoded Randall. Taylor clarified HoloChat must have the same persona/intelligence/constitution for every user; Randall is one feedback user, not the product target.

Verify:
- `holochat_constitution.py` uses universal language such as `the user` / `the person`, not Randall or Taylor.
- `docs/gov_chat_doctrine.md` uses universal user language in active doctrine/prompt law.
- Active worker and Gov prompt surfaces contain no Randall/Taylor product law.
- The built-in recovery memory pack in `chat_engine.py` no longer hardcodes `randall_continuity`; user-specific voice anchors are capsule/HoloBrain-owned when supplied.
- Randall/Taylor names remain only in tests or user-memory/capsule fixtures, not in universal constitution or prompt law.
- The repair does not expand into GovTurnPlan or other architecture work.
- Tests are no-provider, no-credential, no-live, and do not edit HoloVerify.

Block if any active prompt law, canonical constitution, Gov doctrine, or built-in universal memory pack still hardcodes Randall/Taylor, or if the package performs provider/live/deploy/watcher actions, edits HoloVerify, or claims release readiness before QA pass.

Return `PASS_TO_HOLOOPS` or `BLOCK_TO_HOLOOPS` with exact remaining named-user surfaces if blocked.
