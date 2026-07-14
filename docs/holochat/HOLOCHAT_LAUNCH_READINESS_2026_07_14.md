# HoloChat Launch Readiness - 2026-07-14

## Candidate

- Branch: `holochat-context-governor-001`
- Base commit inspected: `8d9ea7a93c420a15319775ad37ef7cde1c80d652`
- Candidate state: local uncommitted worktree
- Provider calls during no-provider verification: `0`
- Credential reads during no-provider verification: `0`
- Supabase writes during no-provider verification: `0`
- Pushes or deploys: `0`

## Proven Locally

| Requirement | Evidence | Status |
| --- | --- | --- |
| Frontier visible workers | Canonical policy forces OpenAI `gpt-5.5` and xAI `grok-4.3`; stale economy env is ignored outside experiment mode | PASS |
| Economical private HoloGov | Canonical HoloGov is MiniMax `MiniMax-M2.7-highspeed`, never a visible worker | PASS |
| One paid HoloGov call per turn | Canonical mode ignores stale multi-call env; provider SDK retries are disabled; invalid Gov output falls back to the local deterministic kernel, not another provider | PASS |
| HoloGov precedes worker | GovTurnPlan control-plane tests and eight-turn fake runtime event order | PASS |
| High-fidelity bounded worker context | Full canonical ledger remains private; worker projection has recursive nested-data bounds and a hard estimated-token ceiling | PASS |
| Long-thread continuity mechanism | Eight-turn fake runtime evolves the rolling summary through turn 8 while forcing raw-history omission | PASS |
| Worker rotation | Eight-turn fake runtime alternates OpenAI/xAI four times each | PASS |
| HoloBrain boundary | Fake HoloBrain context reaches the HoloGov-selected projection; workers never receive raw-library access | PASS |
| HoloBrain projection modes | `NONE`, `HASHES_ONLY`, and `ARTIFACT_REFS` cannot leak capsule, life-context, or prior-session memory text into the worker packet | PASS |
| Canonical story integrity | Provider rolling-summary updates retain an origin/decision/open-question/anchor/contradiction spine; recent portrait updates remain visible | PASS |
| Constitutional release behavior | Tone/release suite plus eight-turn warm response admission | PASS |
| Cost observability | Each fake turn records one MiniMax Gov call and a complete estimated turn cost | PASS |
| Duplicate-turn protection | Browser sends exactly one paid streaming POST per click and never auto-replays through `/v1/chat` after an ambiguous network failure | PASS |
| Production spend telemetry | Server records combined worker-plus-HoloGov estimated cost and preserves unknown cost instead of writing zero | PASS |
| Canonical startup | Both OpenAI and xAI workers are required; stale one-gate experiment configuration and stale Gov model/budget overrides are rejected | PASS |
| Pressure-test honesty | Unexercised compaction or topic lifecycle dimensions are excluded from the score | PASS |
| Dry-run accounting | Economy, balanced, and frontier A/B/C/D manifests regenerated; all report `provider_calls_made=false` | PASS |

Final no-provider gate after the legacy-schema and adaptive-audit repairs: `313 passed, 9 subtests passed`; compile and diff checks passed.

## Authorized Live-Lap Preflight

Taylor authorized one capped live Mira lap and one-time loading of the local HoloChat environment. The run stopped on turn 1 before any HoloGov or worker provider call:

- Provider calls: `0`
- Estimated provider spend: `$0.00`
- Trace turns written: `0`
- Failure: Supabase returned `42703` because `holo_chat_sessions.scope_id` does not exist in the connected legacy schema.

Root cause: `ProjectBrain.get_chat_session()` selected the future hybrid-scope column even while `HOLOCHAT_HYBRID_SCOPES_ENABLED=0`. The local repair now selects only `session_id, capsule_id` in legacy mode and adds `scope_id` only after hybrid scopes are explicitly enabled. Regression coverage proves both schema paths without credentials or network calls.

The hybrid-scope migration was not applied. That first paid lap was not retried until Taylor separately authorized the second run recorded below.

## Authorized Live Launch Lap

Taylor separately authorized one second capped live lap after the legacy-schema repair. Run `mira-launch-20260714-145916` completed all eight adaptive turns:

| Live requirement | Observed result | Status |
| --- | --- | --- |
| Worker rotation | OpenAI, xAI, OpenAI, xAI, OpenAI, xAI, OpenAI, xAI | PASS |
| Worker models | OpenAI `gpt-5.5`; xAI `grok-4.3` | PASS |
| HoloGov | One MiniMax `MiniMax-M2.7-highspeed` call before every worker; no retries or failovers | PASS |
| HoloBrain | Synthetic capsule created, state persisted every turn, and rolling-summary mode activated when history was bounded | PASS |
| Recursive continuity | Origin topic parked on turn 3, resurfaced on turn 5, preserved through turn 8, and prior worker overreach repaired | PASS |
| Visible release | All eight responses admitted without constitutional tone repair | PASS |
| Pressure score | `14/14`, all dimensions exercised | PASS |
| Cost | `$0.459275` estimated total: `$0.143898` HoloGov and `$0.315377` workers; `$0.057409` estimated average per turn; no unknown-cost turns | PASS |
| Cost ceiling | Stayed below the configured `$0.75` ceiling | PASS |

At turn 8 the deliberately constrained test reported `YELLOW / CONTEXT_PRESSURE`: 14 raw messages, 6 bounded messages, and 8 omitted messages. This was the intended rolling-summary pressure condition, not a control-plane failure. HoloGov retained a 15-item chronological ledger, an 841-token rolling summary, the active and superseded topic lanes, and six selected prior episodes.

Across the lap, HoloGov consumed 166,588 input tokens and 18,310 output tokens. Its mean pre-worker latency was about 47.4 seconds. This proves the rich control step is real and economical relative to frontier workers, but it also identifies latency and long-run HoloGov input growth as the next optimization targets.

The process originally exited `2` because adaptive runs keep the preplanned `messages` list empty and the final audit incorrectly compared eight summaries with `len(messages) == 0`. The harness now audits against `total_turns`; a regression test locks that behavior. The saved trace independently contains eight turn events with exact alternation and no structural failures, so no additional provider run was made.

## Not Yet Proven

The candidate is not deploy-ready until one explicitly authorized live launch lap proves:

1. MiniMax Anthropic-compatible transport and `MiniMax-M2.7-highspeed` packet validity.
2. Real GPT-5.5/Grok-4.3 worker compatibility and alternating route telemetry.
3. Real HoloBrain capsule retrieval and persistence against the intended Supabase project.
4. Subjective continuity, insight, warmth, challenge, and non-scolding behavior over eight adaptive turns.
5. Observed cost remains inside the configured `$0.75` test ceiling.

The exact single-run command is maintained in `docs/holochat/HOLOCHAT_EXPERIMENTS.md`. Do not repeat a failed lap to improve a score; diagnose locally first.

## Scoped Exclusion

`tests/test_brain.py` currently reports 10 failures, 15 passes, and 4 skips. The failing cases cover the HoloVerify vendor-profile path: vendor-domain retrieval, ALLOW/ESCALATE counters, and highest-risk history. They do not exercise HoloChat capsules, HoloChat memory stewardship, conversation episodes, worker context projection, or session authorization. No HoloVerify files were changed under this HoloChat task.

This exclusion does not convert those failures into a pass. It records why they are outside this launch candidate and must remain owned by the HoloVerify workstream.

## Release Decision

Current decision: `PASS_LIVE_LAP_AND_NO_PROVIDER_GATE_PENDING_RELEASE_ACTIONS`.

After a passing live lap: review the trace and transcript, confirm no private Gov data was exposed, rerun the no-provider gate, then commit and deploy intentionally.
