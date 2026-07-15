# HoloChat Source Of Truth

Status: canonical product and architecture doctrine for HoloChat.

Owner: HoloOps / HoloArchitecture / HoloChat QA.

Last updated: 2026-07-14.

Current release label: HoloChat 3.2.

This document defines what HoloChat is, how it should work, and which runtime role is responsible for what. Product behavior, prompts, HoloGov packets, HoloBrain memory policy, tests, and future implementation work should align to this document unless HoloOps explicitly supersedes it.

## Core Claim

HoloChat is a governed conversation runtime, not a normal chatbot.

The user experiences one coherent Holo presence. Behind that presence, rotating DNA workers recursively learn from the ordered conversation and from the work of the workers before them. HoloGov is the continuous controller that keeps this evolving record navigable, correctly scoped, and moving in a straight line even when the human conversation wanders.

The product promise is not that a single model remembers everything. The product promise is recursive intelligence under governed context: workers add insight; HoloGov preserves structure, provenance, and direction.

## Two-Plane Context Architecture

HoloChat operates on two context planes that must never be confused:

1. **Ordered recursive record.** The user turns, prior worker answers, supplied documents, corrections, evidence, and changes of mind in the order they happened. This is primary conversational evidence. It contains the layering that lets each new DNA worker learn from the workers before it.
2. **HoloGov control ledger.** A compact, typed map of active, parked, resurfaced, resolved, and superseded lanes; prior worker contributions; settled decisions; contradictions; open questions; provenance; context gaps; and the next worker assignment. It steers the record. It does not replace it.

HoloBrain is a third, secondary source: durable cross-thread memory and user-owned context. It can enrich the live conversation, but it must not displace the evolving thread or cause HoloChat to overfit old beliefs about the user.

Relevant older material enters a turn as a bounded **episode registry**. Every selected episode must carry a stable ID, source type, source ID, summary, relevance signal, token estimate, selection reason, and provenance. Retrieval rank is a navigation aid, not truth authority.

## Topic Lane Lifecycle

HoloChat has no single permanent topic and no single useful beginning. HoloGov therefore maintains a durable topic registry inside the private canonical working context.

HoloGov should create a new topic lane only when the conversation materially shifts in subject, project, question, or objective. It must not create a new lane for every message or rhetorical variation.

Each topic lane carries:

- stable topic ID
- concise subject and factual summary
- status: `active`, `parked`, `resolved`, or `superseded`
- origin turn
- most recent relevant turn
- supporting source-turn IDs
- importance
- resurface count
- parking, resolution, or supersession reason when applicable

When attention moves, HoloGov parks the prior lane instead of deleting it. When the user returns, HoloGov resurfaces the same stable lane and restores its origin, prior worker contributions, unresolved questions, and relevant evidence. A slightly different name must not create a duplicate topic when the semantic lane is the same.

The HoloGov model proposes topic creation and transitions. The deterministic kernel reconciles those proposals against the prior registry so provider omission, renaming, or malformed fields cannot silently erase topic history.

## Operating Objective

HoloChat has one goal:

Serve the user's best interests by helping them see what is true, choose what is wise and actionable, preserve agency and dignity, and move forward with more clarity than they had before the turn.

Truth outranks performance. Warmth is the delivery system for truth. HoloChat must never become scolding, gotcha-driven, cold, sterile, bureaucratic, falsely intimate, manipulative, or flattering at the expense of honesty.

This is universal product law for every user. Named feedback users may appear in tests or user-owned memory fixtures, but never as universal HoloChat law.

## Primary Roles

### HoloBrain

HoloBrain is the durable memory substrate.

It stores selected capsule memory, user portrait, durable preferences, active projects, prior insights, boundaries, artifacts, rolling summaries, state briefs, unresolved arcs, and memory lifecycle metadata.

HoloBrain does not speak. HoloBrain does not decide. HoloBrain is the library.

### HoloGov

HoloGov is the continuous operator and ultimate librarian of HoloBrain.

HoloGov is the only runtime role authorized to enter, query, organize, update, prune, archive, or manage HoloBrain. HoloGov and HoloBrain are a team: HoloBrain holds the library; HoloGov knows where to go, what to retrieve, what to ignore, what to consolidate, and what to hand to the next worker.

HoloGov never speaks directly to the user. HoloGov acts through state, typed packets, private instructions, release decisions, memory admissions, tool/search authorizations, and post-turn maintenance.

HoloGov is responsible for:

- reading the ordered record from oldest to newest within the available window
- mapping active, parked, resurfaced, resolved, and superseded topic lanes
- recording what each prior DNA worker added, challenged, or left unresolved
- maintaining an iterative factual rolling ledger without erasing origins
- maintaining only explicit, relevant user portrait facts
- preserving chronology, provenance, corrections, uncertainty, and contradictions
- selecting origins, relevant older evidence, and recent turns under real context pressure
- deciding what should be preserved, repaired, rejected, clarified, or retrieved
- authorizing search and tools
- admitting or rejecting memory writes
- maintaining internal context health and compaction state without forcing normal conversations to end
- preparing the worker's GovTurnPlan
- checking whether visible output obeys tone, truth, and safety law
- stewarding HoloBrain so it does not become stale, noisy, or cluttered

HoloGov is not the creative mind of the visible answer. It must not pre-solve the user's problem, draft the response, diagnose the person, invent a psychological theory, or make itself the source of insight. Its excellence is visible in the conditions it creates for the worker.

### Visible Workers

Visible workers are the models that speak to the user.

They are brilliant strangers walking into the room each turn. They receive substantial ordered conversation plus HoloGov's control ledger. They inspect the actual record, learn from prior DNA contributions, test weak assumptions, and add a new layer. They do not browse HoloBrain directly and do not mutate canonical control state.

The worker's job is to ingest both the recursive record and HoloGov's beautifully organized control document, then produce the best possible visible response: warm, precise, useful, insightful, stylish, and bounded.

Worker rotation exists to preserve adversarial variation and blindspot coverage. OpenAI and xAI workers should bring different instincts, not different product personalities. The user should feel one Holo.

### Kernel

The deterministic runtime kernel enforces hard law.

The kernel is responsible for provider eligibility, model failover, release gates, secret redaction, capsule boundaries, incognito rules, raw-thought suppression, streaming release admission, tool execution boundaries, telemetry, and testable invariants.

HoloGov guides and curates. The kernel enforces.

## Canonical Runtime Loop

The optimal HoloChat turn works like this:

1. User sends a message.
2. Kernel checks identity, capsule, incognito, tool boundaries, and runtime policy.
3. HoloGov reads prior control state, the ordered conversation, and the current message.
4. HoloGov retrieves relevant secondary HoloBrain material when authorized and useful.
5. HoloGov updates the existing control ledger: lanes, contributions, facts, decisions, conflicts, provenance, gaps, and assignment.
6. HoloGov builds exactly one typed GovTurnPlan immediately before the visible worker call.
7. Worker receives substantial ordered conversation, the current message, selected supporting context, and the GovTurnPlan.
8. Worker recursively builds on prior work and writes the visible answer.
9. Kernel release gates repair or block violations before anything is shown.
10. HoloGov's next turn absorbs the admitted user/worker exchange into the ledger.
11. HoloGov decides what, if anything, deserves durable HoloBrain admission or maintenance.

HoloChat conversations have no architectural end. People wander, pause, introduce new material, and return to old subjects. Context pressure is managed internally through origin/relevance/recency selection, retrieval, and iterative compaction. A fresh-thread prompt is an exceptional opt-in escape hatch, not normal intelligence management.

## GovTurnPlan

The GovTurnPlan is the worker's private control chart for the turn.

It should make a large recursive record easy to navigate, not become a smaller substitute for that record. It exists because the worker is a stranger entering the room.

Minimum GovTurnPlan control-packet fields:

- `gov_role`
- `worker_context_contract`
- `holobrain_operator`
- `holobrain_scope`
- `memory_stewardship`
- `conversation_phase`
- `topic_registry`
- `topic_events`
- `active_threads`
- `parked_threads`
- `resolved_threads`
- `resurfaced_threads`
- `worker_contributions`
- `user_portrait`
- `current_state_of_affairs`
- `chronological_ledger`
- `rolling_summary`
- `narrative_arc`
- `active_tension`
- `settled_decisions`
- `unresolved_questions`
- `contradictions`
- `context_manifest`
- `preserve`
- `reject`
- `worker_assignment`
- `next_worker_directive`
- `context_pressure`

The packet should tell the worker:

- which conversation lanes are active, parked, or resurfacing
- what prior workers contributed and whether it still stands
- who this user explicitly says they are where relevant to this turn
- what is happening now
- where the conversation has been going
- what tension is unresolved
- what must be preserved
- what must not be repeated or inferred
- what tone law applies
- what tool/search/memory boundaries apply
- what the next answer must accomplish

Raw advisor text, raw thought metadata, raw private memory, and provider output are not authority unless admitted into typed fields.

## HoloBrain Stewardship

HoloBrain must not become an attic.

HoloGov should act as librarian, curator, archivist, editor, guide, and protector. The memory system should be a living library: indexed, consolidated, versioned, weighted, and periodically cleaned.

Every memory should eventually carry lifecycle metadata:

- `candidate`
- `active`
- `confirmed`
- `inferred`
- `stale`
- `archived`
- `contradicted`
- `forgotten`

HoloGov should perform memory stewardship after meaningful turns, after long threads, when thread health degrades, when contradictions appear, when a user corrects memory, when a project ends, and on scheduled maintenance.

HoloGov memory actions:

- Admit meaningful memory.
- Reject noise and transient emotion.
- Consolidate repeated fragments into clean state.
- Rank by relevance, confidence, sensitivity, recency, and user confirmation.
- Archive low-current-value material without deleting it prematurely.
- Prune duplicate, stale, contradicted, or no-longer-useful records.
- Forget/delete when the user requests it and the kernel authorizes the operation.

The worker should never be given the whole HoloBrain library. It should receive the right shelf from HoloBrain, while still receiving as much of the ordered live conversation as the context window can usefully support.

## Rolling Summary

The rolling summary is one component of canonical control state. It is not a replacement for the ordered conversation.

It should be iterative. HoloGov should not rewrite the user's story from scratch each turn. It should massage, correct, compress, and extend the state brief as the conversation evolves.

The rolling summary should preserve:

- current goal
- user portrait deltas
- active projects
- current emotional/strategic tension
- settled decisions
- unresolved questions
- boundaries and preferences
- best prior insight
- risks and blocked moves
- recent source IDs or artifact references when relevant
- what the next worker must not lose

Every worker call must also produce a private `WorkerContextReceipt`. The receipt records raw, selected, and omitted history counts; selected history hashes; selected episode IDs and token estimates; admitted evidence source IDs; Gov packet token estimate; total estimated worker input; and a stable receipt hash. It is operator telemetry, never normal user-facing content.

The complete HoloGov ledger remains private canonical state. The worker receives a bounded projection of that ledger, not repeated operator bookkeeping or full prior responses already present in ordered history. The projection prioritizes current state, iterative summary, active tension, user portrait, anchors, active and relevant parked lanes, selected HoloBrain episodes/evidence, standing contribution summaries, and the current assignment. The default worker-facing HoloGov narrative-packet ceiling is 4.5k estimated tokens; raw conversation and admitted evidence must retain room to remain primary.

When raw history is bounded, the summary and lane ledger become more important, but selection must still preserve origins, relevant older evidence, and recent turns. Thread length should not determine HoloChat intelligence. HoloGov's navigation and the worker's access to recursive evidence should.

## Current Provider Policy

Current intended HoloChat policy:

- HoloGov: fixed private MiniMax `MiniMax-M2.7-highspeed` proposal compiler.
- Visible workers: rotate OpenAI `gpt-5.5` and xAI `grok-4.3`.
- HoloGov output is never visible authority. The deterministic kernel admits, repairs, or rejects its typed control packet before a worker receives it.
- Canonical HoloChat permits exactly one paid HoloGov call per visible turn. If the MiniMax packet is malformed, incomplete, truncated, or unavailable, the deterministic kernel uses its local canonical-state fallback and marks control degraded. It never makes a hidden second provider call.

### Cost Policy

Frontier intelligence remains the visible quality target. MiniMax occupies one locked, private HoloGov-only
seat because conversation accounting and state compilation consume substantial recurring tokens. It is not
part of worker rotation and cannot speak to the user. Canonical operation always uses the frontier worker tier,
one HoloGov provider call, and HoloGov control compilation. Economy workers, multi-call legacy Gov behavior,
or disabled control compilation require both explicit noncanonical experiment gates.
- No mini models in visible normal operation.
- MiniMax is not in visible rotation.
- HoloGov provider fallback is local, explicit, and logged; visible worker failover remains a separate provider-failure path.

Provider output is work product. HoloGov and the kernel decide what becomes admitted state or visible output.

## Token Budget Doctrine

Both HoloGov and the worker need serious context, for different reasons. HoloGov spends tokens organizing and steering; the worker spends tokens absorbing the recursive record and producing insight. Starving either role breaks HoloChat in a different way.

Recommended starting budgets:

- HoloGov normal-turn input target: 16k-32k tokens.
- HoloGov high-stakes or long-context input target: 48k-80k tokens when provider limits and cost allow.
- HoloGov output target for GovTurnPlan: 1.5k-3.5k tokens.
- HoloGov output hard cap for GovTurnPlan: around 5k tokens unless explicitly running a deep maintenance pass.
- Worker input target: 16k-32k tokens for established conversations when available.
- Worker high-context input target: 48k-80k tokens when documents, long arcs, or recursive prior work genuinely require it and provider limits permit.
- Rolling summary target: 2k-4k tokens.
- Expanded rolling summary cap: 6k-8k tokens for long-running high-value threads.
- User portrait active packet target: 1k-2k tokens.
- HoloBrain candidate retrieval pool for HoloGov: large enough to inspect meaningfully, but ranked before worker admission.

Allocate context from observed value, not arbitrary turn-count thresholds. Measure:

- HoloGov selected context tokens
- HoloGov dropped context tokens
- HoloBrain retrieval source and version
- rolling summary tokens
- user portrait tokens
- GovTurnPlan tokens
- worker prompt tokens
- omitted history count
- memory blocks included/dropped
- model/provider per turn
- release repair reason
- whether the answer preserved and advanced prior worker contributions
- which origin, relevant-middle, and recent messages reached the worker
- whether a resurfaced lane recovered its original evidence

## Tone And Style Law

HoloChat must never scold, prosecute, shame, corner, humiliate, patronize, become sterile, or use gotcha framing.

Warmth does not mean agreement. Directness does not mean cruelty. Challenge must feel like a capable ally helping the user see clearly, not a judge trying to win.

Visible answers should feel alive, useful, and well-shaped:

- short paragraphs
- selective bolding
- bullets when they help momentum
- no walls of text when the user needs scanability
- no fake intimacy
- no bureaucratic safety theater
- no memory performance
- no hidden-system exposition unless requested

The user should feel protected, understood, and sharpened.

## Web, Tools, And External Action

HoloGov authorizes tools. Workers do not independently decide to use tools.

Web search is part of HoloChat because lack of current information weakens the product. It must follow the same law:

- HoloGov decides whether search is needed.
- Kernel executes or blocks.
- Search results become a typed evidence bundle with a query hash, provider, retrieval time, stable bundle hash, and bounded source records.
- HoloGov admits relevant findings into the packet.
- Each admitted source receives a turn-scoped source ID such as `[S1]`, plus URL, domain, title, bounded snippet, retrieval time, and content hash.
- Worker cites web-derived claims with admitted source IDs and never invents IDs.
- The deterministic citation audit reports valid, missing, or invented source IDs for normal and streaming turns.
- Search snippets remain untrusted evidence and never become instructions or Gov authority.

No external action should bypass HoloGov and kernel authorization.

## Evaluation Doctrine

HoloChat should be tested like a governed runtime, not like a single prompt.

Required no-provider tests:

- GovTurnPlan required fields.
- HoloGov-only HoloBrain authority.
- Worker prompt receives the HoloGov control packet and ordered recursive record.
- Ordered transcript and prior worker outputs reach the worker as primary recursive evidence.
- HoloGov control state steers the transcript without replacing it.
- Topic lanes can park and resurface without losing their origins.
- Material topic shifts create stable lanes; rhetorical variation does not.
- Provider renaming cannot duplicate a returning lane or erase its origin.
- Prior worker contributions are preserved, challenged, superseded, or advanced explicitly.
- Rolling summary appears when history is bounded.
- Relevant older episodes outrank recent irrelevant material and preserve provenance.
- WorkerContextReceipt matches the history, episodes, evidence, and Gov packet actually handed to the worker.
- Web evidence rejects unsafe URLs, uses stable source IDs and hashes, and reports missing or invented citations.
- Streaming and non-streaming turns expose the same context receipt and citation audit.
- HoloBrain memory is grounding, not accusation.
- No scolding/gotcha/cold/sterile release.
- Streaming does not leak unadmitted output.
- Thought metadata is admitted or suppressed.
- Mini models do not enter normal rotation.

Required live/runtime tests:

- 8-turn Mira identity-pressure run.
- 20-turn long-context rolling-summary run.
- HoloBrain retrieval and pruning simulation.
- Worker rotation stability: OpenAI then xAI then OpenAI.
- Same user, same arc, different worker.
- False-memory trap.
- Privacy seduction trap.
- Dependency pressure trap.
- Sensitive medical/financial boundary trap.
- Relationship rupture and repair.
- Best prior insight preservation.
- Eight-turn recursive-context track: establish evidence, record a worker gain, detour, introduce new evidence, resurface the original lane, resist contradiction pressure, compound prior work, and audit the control ledger.

Compare against a solo GPT baseline and score the transcript with the same checks. HoloChat should win on continuity, false-memory boundaries, agency preservation, and final-arc preservation. If solo GPT matches HoloChat, HoloGov packet depth or HoloBrain retrieval is not doing enough work yet.

Mira should remain synthetic and adaptive. The test user should react to what HoloChat actually says, not follow a fully scripted transcript. That is how identity-level failure appears.

### Operator Track Lap

After sourcing the local provider and test-HoloBrain environment, run:

```bash
RUN_ID="mira-recursive-$(date +%Y%m%d-%H%M%S)"

PYTHONDONTWRITEBYTECODE=1 .venv312/bin/python scripts/holochat_live_smoke.py \
  --adaptive-script mira_recursive_context \
  --turns 8 \
  --with-supabase \
  --ensure-test-capsule \
  --capsule-id "hc-${RUN_ID}" \
  --capsule-email "${RUN_ID}@holo.test" \
  --capsule-name "Mira Recursive Track" \
  --seed-synthetic-persona \
  --live-dashboard \
  --trace-jsonl "/tmp/${RUN_ID}.jsonl" \
  --transcript-md "/tmp/${RUN_ID}.md" \
  --govtrace-md "/tmp/${RUN_ID}-gov.md" \
  --trace-private-gov
```

The private Gov trace is an operator artifact and may contain synthetic HoloBrain and transcript context. It must not be exposed in the normal user interface or published.

Run two controls with the same scenario:

- `--disable-gov-control` isolates the value of HoloGov's compiled control ledger while keeping ordered history.
- `--legacy-clipped-history` recreates the old small history window and measures the value of recursive worker context.

Compare the three transcripts on origin recall, resurfaced-lane recovery, prior-worker contribution preservation, contradiction discipline, non-repetition, useful new insight, warmth, and false-certainty resistance. The governed full-context run should win for observable reasons in the trace, not because a judge was told which architecture produced it.

## Implementation Priorities

### Context And Evidence Harness V1

The local V1 implementation establishes:

- HoloState schema `holochat_state_v1.0` with user portrait, topic registry, episode registry, evidence ledger, and worker context receipt.
- capsule-scoped episode retrieval from prior HoloBrain session consolidations, merged with current-thread episodes and ranked under a token budget.
- one admitted evidence ledger shared by HoloGov and the visible worker.
- source IDs and safe source links for the user-facing web-check surface without exposing private engine data.
- citation audit and context receipts for both normal and buffered streaming turns.
- private HoloGov plans, HoloBrain projections, context receipts, and cost telemetry withheld from normal API/SSE clients unless an explicit local operator flag is enabled.
- backward loading of legacy `holochat_state_v0.1` records with empty V1 registries.

V1 does not make retrieved memory or search text authoritative. HoloGov curates it, the deterministic kernel records admission and citation integrity, and the visible worker remains responsible for synthesis.

### Harness V2 Program

The active V2 program is defined in `docs/holochat/HOLOCHAT_HARNESS_V2_ROADMAP.md` and `docs/holochat/HOLOCHAT_EXPERIMENTS.md`.

- Web retrieval crosses a provider-neutral structured boundary with explicit outcomes; Tavily is the first adapter, not a permanent architectural dependency.
- Source bibliographies are disclosure only. They do not satisfy inline citation or claim-support admission.
- Economy, balanced, and frontier test lanes are explicit experiment policies and never silently change production routing.
- Portable identity is separated from data authority. Personal and enterprise records remain in immutable scopes, with deny-by-default cross-scope access and audited derivative transfers.
- Session ownership must be proven before any durable or in-memory history is restored.

### Continuous Memory Steward

HoloChat has two different memory rhythms and they must never be collapsed into one:

- Per-turn HoloGov state keeps the current conversation coherent for the next worker.
- Durable Memory Steward checkpoints consolidate only the new transcript delta into HoloBrain.

A checkpoint is required after 6–8 user turns, 10k–15k new input tokens, a meaningful topic transition, a correction, revocation, commitment, major decision, thread open/fork with unconsolidated history, idle with a delta, or immediately before autocompact. Every checkpoint carries a transcript watermark and hash, exact provenance, typed proposals, and deterministic admit/reject/quarantine decisions.

The persistence law is strict:

1. HoloGov may propose memory; it cannot silently write it.
2. HoloBrain commits the checkpoint, admitted entries, supersessions, revocations, and quarantined candidates atomically under one immutable scope.
3. The watermark advances only after a successful persistence acknowledgement.
4. A failed or unresolved urgent checkpoint remains pending and blocks autocompact.
5. Retries use the same idempotency key and may not duplicate memory.
6. Corrections supersede named prior memory; forget requests create durable tombstones.
7. Restart recovery restores the acknowledged watermark and the ordered transcript before processing another turn.

Rolling state, durable consolidation, the user portrait, and the raw transcript are separate records with separate jobs. The rolling state is not durable truth; a summary is not a substitute for the ordered transcript; and a portrait may not overwrite event history.

Near-term priorities:

1. Make HoloGov naming consistent in prompts, docs, telemetry, and packets.
2. Complete the typed control ledger described above.
3. Keep rolling summary iterative while preserving substantial ordered history for workers.
4. Add HoloBrain memory lifecycle metadata.
5. Extend the checkpointed Memory Steward with reviewed pruning and archival policy; consolidation, contradiction handling, supersession, forgetting, and restart recovery are implemented behind a feature flag.
6. Add token telemetry for HoloGov and worker packets separately.
7. Build dashboard views for internal testing only; do not expose engine internals to normal users.
8. Run repeated Mira track tests and compare drift over time.

The north star: every worker enters as a stranger, can see how the whole conversation became what it is, and adds an exceptional new layer because HoloGov prepared the room without doing the worker's thinking.
