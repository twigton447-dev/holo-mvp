# HoloChat Architecture and the HoloVerify Gate

## The Whole System in One View

Holo is a system, not a single model or a single chat window. HoloChat is the
human-facing intelligence and continuity surface. Its architecture includes
identity, scope, memory, orchestration, workers, tools, and deterministic
runtime controls.

HoloVerify is deliberately **not inside that architecture**. It sits at the
gate. HoloVerify independently tests a bounded candidate, transfer, patch, or
claim before the system is allowed to treat it as verified. HoloAudit,
HoloArchitecture, HoloMiner, and HoloAutopsy support that independent gate by
making its evidence, repair laws, classifications, and receipts inspectable.

```text
Person + authorized Personal or Enterprise scope
  -> HoloChat: conversation, memory, planning, and proactive help
  -> deterministic kernel: identity, scope, tool, and release enforcement
  -> HoloGov: private conversation and memory stewardship
  -> visible worker: the answer the person sees

At the outside edge of the architecture, for consequential decisions,
boundary transfers, architecture changes, or benchmarked behavior:
  HoloChat candidate + explicitly exported evidence packet
  -> HoloVerify gate: independent source and action-boundary evaluation
  -> HoloAudit: independent receipt and claim-boundary review
  -> PASS to the separately authorized next boundary,
     or BLOCK / ESCALATE / no-claim
```

HoloChat makes Holo useful in the moment. HoloVerify prevents a good-looking
answer, patch, transfer, or test result from crossing a consequential gate as
if it already possessed warranted authority.

## What HoloChat Is

HoloChat is a governed, persistent intelligence system. It is not meant to be
a generic chatbot with a long transcript. Its job is to help a person see what
is true, make better decisions, preserve agency and dignity, and keep useful
continuity across threads, projects, and changing circumstances.

The user experiences one Holo. Under the surface, HoloChat separates durable
memory, conversation navigation, model work, deterministic safety controls,
and cross-boundary governance. This separation matters because a system that
remembers a person must be useful without becoming intrusive, overconfident, or
careless with private information.

The central product promise is not "one model that remembers everything." It
is recursive intelligence under governed context: the live conversation stays
primary; durable memory supplies the right background when it is relevant; and
the system maintains enough structure to resume work without making the user
repeat their life or their project every time.

## The User Experience

HoloChat should feel like a capable, continuous partner rather than a sequence
of isolated chats. It should be able to:

- remember selected user-confirmed facts, preferences, active projects,
  boundaries, and decisions within the correct scope;
- understand a current thread in the context of prior work without dumping a
  wall of stale history into the answer;
- recognize that a person may be carrying multiple live topics at once;
- return to a parked topic without pretending it is new;
- distinguish a settled decision from an unresolved question or a working
  hypothesis;
- surface the information, timing, and next action that are useful now;
- be warm and supportive without becoming falsely intimate, flattering, or
  psychologically overconfident;
- say when it does not have enough evidence instead of inventing a personal
  biography, work fact, or history.

HoloChat is designed to carry a coherent picture of a user's situation, not to
turn that person into a fixed narrative. Memory is a map for judgment, not a
verdict about identity.

## The Core Architecture

HoloChat has five distinct roles.

```text
Authenticated person and selected scope
  -> deterministic kernel
  -> HoloGov control layer
  -> selected HoloBrain context + ordered thread record
  -> visible worker response
  -> kernel release gate
  -> HoloGov maintenance and selective durable-memory admission
```

### 1. The Capsule, Principal, and Scope

A **principal** is the authenticated person. A **capsule** is that person's
durable HoloChat identity container. A **scope** is the specific information
space Holo may enter for a turn.

The important rule is that a device is not the authority. Identity and scope
are enforced server-side. Logging in on another phone or browser must not give
one person access to another person's threads, memory, or context. A durable
request must resolve to the exact authenticated capsule, an active principal
mapping, and an authorized scope.

The target relationship is:

```text
Principal -> Personal scope
Principal -> tenant membership -> Enterprise scope
```

A new login must never silently borrow an ambiguous legacy capsule. If account
recovery or consolidation is needed, it must use an exact, metadata-backed,
auditable match and stop on ambiguity. It is not a free-form merge.

### 2. The Deterministic Kernel

The kernel is the system's hard-law layer. It is not the part that tries to be
creative or insightful. It enforces the things that cannot be left to model
judgment:

- authentication and active-capsule checks;
- exact capsule, session, and API-key ownership;
- Personal and Enterprise scope authorization;
- tenant membership enforcement for Enterprise work;
- incognito behavior;
- tool and connector boundaries;
- secret and private-prompt redaction;
- provider eligibility and safe failure handling;
- streaming admission and terminal error behavior;
- memory-write and state-shape validation;
- telemetry and regression-testable invariants.

The kernel should fail closed. If the system cannot prove that a request belongs
to an active authorized capsule and scope, it should deny the request rather
than guess.

### 3. HoloBrain: The Durable Library

HoloBrain is the durable memory substrate. It is a library, not a speaking
agent and not an unrestricted profile dump.

Within an authorized scope, it can hold selected durable material such as:

- user-confirmed facts and preferences;
- active projects and project state;
- decisions, constraints, and unresolved questions;
- boundaries and communication preferences;
- prior insights and relevant artifacts by reference;
- rolling thread summaries and state briefs;
- life-context entries that were deliberately admitted;
- topic lanes, saved sessions, and maintenance metadata.

It should not become an attic full of every sentence a user has ever written.
Meaningful memory is admitted, ranked, consolidated, revised, archived, or
forgotten deliberately. The system should reject noise, preserve provenance,
and support correction when the user changes their mind or corrects a prior
fact.

Every durable interpretation needs an epistemic status. A useful framework is:

| Status | Meaning |
| --- | --- |
| `FACT` | Confirmed external reality or user-confirmed stable detail |
| `SELF_DESCRIPTION` | How the user describes themselves or their situation |
| `PATTERN` | A repeated observation supported across contexts |
| `HYPOTHESIS` | A tentative interpretation, held loosely |
| `CONTRADICTION` | A meaningful tension requiring care or revision |
| `EXPIRED` | A prior interpretation no longer valid |

Holo must not turn a hypothesis into a fact, or a useful old story into a
permanent explanation of a person.

### 4. HoloGov: The Conversation and Memory Steward

HoloGov is the private control layer. It does not speak directly to the user.
It organizes the conversation so the visible responder can be intelligent
without being lost.

HoloGov is responsible for:

- reading the ordered conversation and current message;
- maintaining topic lanes and their status: active, parked, resolved, or
  superseded;
- preserving chronology, source provenance, corrections, uncertainty, and
  contradictions;
- selecting relevant HoloBrain material under a context budget;
- maintaining a rolling state brief;
- tracking settled decisions, active tensions, and unanswered questions;
- proposing memory admission, rejection, consolidation, pruning, or
  clarification;
- preparing a typed private turn plan for the visible worker;
- authorizing tools and searches only when appropriate;
- maintaining internal context health when a thread becomes long.

HoloGov does not get to invent a psychological theory about a user, write an
unreviewed portrait as truth, or become the visible voice of Holo. It prepares
the conditions for a good answer; the worker still has to reason from the
actual conversation and admitted evidence.

### 5. Visible Workers

Visible workers are the model calls that write the reply the user sees. They
receive the current message, a substantial ordered record of the conversation,
selected relevant durable context, and HoloGov's bounded control plan.

Workers may rotate so different model strengths and blind spots can contribute,
but the user should experience one coherent Holo personality and one set of
governing principles. A worker is not permitted to browse the entire HoloBrain
or mutate canonical state directly. Its output is work product, not automatic
truth or automatic memory.

### 6. Internal Release Controls and the External HoloVerify Gate

Before a response, memory change, cross-boundary signal, or other sensitive
action leaves HoloChat, the deterministic kernel applies internal structural,
identity, scope, and tool controls. These runtime controls are part of the
HoloChat architecture. They are not HoloVerify.

When a candidate reaches a consequential boundary, HoloChat can export only
the explicitly authorized candidate and evidence packet to HoloVerify.
HoloVerify sits outside the architecture and independently determines whether
the packet closes the declared source and action boundary. HoloAudit records
the governed receipt needed to explain what passed, was blocked, or escalated
without logging unnecessary private content.

The point is independence: a model, tool, connector, controller, or internal
governor should not be able to approve its own work by producing a clever
summary. HoloVerify cannot select HoloChat workers, steer HoloGov, browse
HoloBrain, mutate memory, rewrite a candidate during adjudication, or execute
the external action. A HoloVerify pass only opens the next separately
authorized gate; it does not itself perform the action.

## How a Normal HoloChat Turn Works

1. The user sends a message in an authorized Personal or Enterprise space.
2. The kernel validates identity, active capsule, scope, session ownership,
   policy, and relevant tool boundaries.
3. HoloGov reads the current message, the ordered thread, and the previous
   control state.
4. HoloGov selects only the useful, authorized memory episodes and artifact
   references from HoloBrain.
5. HoloGov updates its control ledger: topic lanes, decisions, constraints,
   open questions, corrections, and what the next answer must accomplish.
6. A visible worker receives the actual conversation plus a bounded private
   plan and produces a response.
7. The kernel releases, repairs, or blocks the output according to hard rules.
8. HoloGov absorbs the admitted turn, and only then proposes any durable-memory
   maintenance.

The thread is the primary evidence. Memory is secondary enrichment. Holo should
not let an old portrait override what the user is telling it now.

## Continuity Across Threads

Long threads do not have to become unintelligent merely because they approach a
context window. HoloChat maintains a compact structured state object that can
preserve:

- the current goal;
- latest-input summary;
- critical constraints;
- rolling summary;
- settled decisions;
- artifact references;
- required tools;
- a baton pass for the next thread or worker;
- audit hashes and warnings about missing or contradictory state.

When a new signed-in thread starts, the system can privately reseed it with
authorized compact continuity. Full artifacts are referenced rather than copied
blindly into every prompt. Secret-like values are redacted from the reseed
material. Normal user-facing answers should not expose hidden prompt text,
tokens, keys, private implementation metadata, or raw provider payloads.

## HoloTopics and Conversation Shape

The conversation is not a flat scroll. HoloGov keeps topic lanes so Holo can
handle several real life or work arcs at once. A lane should be created only
when the subject, project, or objective materially changes. It should not make
a new lane for every rhetorical variation.

A good HoloTopics interface can make active topics visible and expandable:

- each topic has a clear headline and a useful explanatory subhead;
- expanding a topic reveals more context and pushes later content down rather
  than covering it;
- a parked topic can be resumed with its earlier decisions and questions;
- a resolved topic stays historically legible without cluttering the current
  workspace.

For a personal workspace, this allows Holo to connect a school transition,
family planning, health logistics, travel, finance, or a difficult conversation
without pretending every topic is the same kind of task.

## HoloPersonal

HoloPersonal is the user's private scope. It is where Holo can build a fuller
picture of a person's life when the user has chosen to share or connect that
information. It may include family context, private plans, preferences, health
constraints, relationships, personal finances, travel, private messages, or
other high-sensitivity material only under explicit consent and the applicable
retention policy.

HoloPersonal should help with the practical and emotional shape of life:

- what is happening now;
- what is about to collide on the calendar;
- which commitments need protecting or reducing;
- how to approach a conversation compassionately and realistically;
- what information the user has already shared or decided;
- when a win deserves celebration or a loss calls for steadiness;
- what to surface proactively because it is timely and relevant.

This does not mean it should perform therapy, make medical or legal decisions,
or treat an inferred story as certain. In high-stakes domains, Holo must clearly
separate facts, interpretations, constraints, and next questions.

## HoloEnterprise

HoloEnterprise is a separate, tenant-authorized work scope. Its purpose is to
help a person perform professionally while respecting organizational
confidentiality, role obligations, access controls, and the difference between
useful work context and private life.

Within an authorized Enterprise scope, Holo can work with sensitive
organization information that the tenant has made available: project briefs,
board preparation, customer or client material, operational plans, internal
documents, regulated workflows, work calendars, and role-specific decisions.
That information remains inside the Enterprise scope. It is not a source for
Personal Holo by default.

Enterprise access is based on verified tenant membership and an authorized
Enterprise scope, not on a user's personal device or their use of HoloPersonal.
An individual can have a Personal scope and one or more Enterprise scopes, but
they are different spaces with different data and different entitlements.

## HoloVerify: The Independent Gate Outside the Architecture

HoloVerify is the independent evidence gate for consequential judgment. It is
adjacent to HoloChat, not a component within HoloChat's reasoning, memory, or
orchestration architecture. It asks a different question from HoloChat.

HoloChat asks: "What would be useful, true, and humane for this person right
now?"

HoloVerify asks: "Does the supplied source evidence close this exact action
boundary, and do we have enough independent evidence to claim that a behavior
or repair works beyond one packet?"

HoloVerify is not a conversational personality, a memory system, a worker, an
internal governor, or a blanket permission to take action. It is a controlled
gate for evaluating a submitted claim against frozen evidence and explicit
rules. Its default safety answer is `ESCALATE` whenever the exact boundary
remains open.

This separation is a security and epistemic property, not a diagramming
preference. The system being evaluated cannot silently alter the gate, choose
which failures count, or grant itself a pass. HoloVerify sees only the bounded
packet deliberately presented at the gate. It receives no ambient right to
read Personal memory, Enterprise records, connector data, or unrelated thread
history.

### Why It Exists

Language models can produce a plausible answer that is nonetheless wrong in a
way that matters. They can:

- treat an adjacent document as the authority for the exact action at hand;
- infer a missing approval from urgency, status, or a persuasive narrative;
- confuse a plan, draft, communication, or prior event with permission to act;
- accept a patch that fixes a visible example but breaks an unseen sibling;
- reduce a false-positive rate by relabeling or weakening the test rather than
  improving the underlying evidence boundary;
- turn a small successful rerun into a broad claim about a model, architecture,
  provider, or production safety.

HoloVerify exists to keep those failures legible. It forces the system to name
the requested action, the controlling source, the required authority, timing,
scope, dependencies, citations, and the exact reason an action is allowed or
must escalate.

### The Source-Bound Packet

The basic unit of HoloVerify is a frozen packet. A packet is not merely a
prompt. It is a bounded decision environment containing, as applicable:

- an exact action boundary: what may be done now, by whom, and under what
  conditions;
- source records and stable source identifiers;
- a policy or governing rule;
- a rubric for `ALLOW` and `ESCALATE`;
- declared risks, traps, and known failure targets;
- expected label(s) and adjudication rules;
- packet manifest, hashes, and lock information;
- model and route constraints for a controlled run.

The required question is deliberately narrow. For example: not "Is this
project generally healthy?" but "May the legal operator execute this filing
now, given these current records?" The packet must prove the exact authority,
currentness, scope, and dependency chain. Plausibility is not enough.

An `ALLOW` means the packet's exact action boundary is closed under the
declared policy. It does not execute the real-world action. An `ESCALATE`
means a material boundary is still open, unclear, missing, stale, mismatched,
or outside the system's authority. It is often the correct and valuable answer.

### The Gate Evaluation Runtime

For benchmark and hardening work, the HoloVerify gate can use a controlled
evaluation route rather than trusting a single raw answer. This evaluation
runtime belongs to the gate protocol; it is not the HoloChat production
reasoning loop. In a representative multi-worker evaluation, bounded workers
and governors proceed through a fixed sequence such as:

```text
W1 -> G1 -> W2 -> G2 -> W3
```

Workers examine the frozen packet and return a structured answer contract.
Governance stages reconcile state, preserve the action boundary, and prevent
unadmitted free-form reasoning from becoming authority. Deterministic checks
then validate required fields, exact citation IDs, allowed values, word bounds,
timing, scope, dependency, source-boundary rules, and known traps.

The exact route, models, selectors, runtime locks, and expected call plan are
recorded before a controlled evaluation. This prevents quiet substitutions or
post-hoc ambiguity about what actually ran.

### Evidence Custody

For a provider-backed evaluation, HoloVerify treats execution itself as
evidence that must be bound to a trace. A completed run may include:

- the canonical call plan;
- runtime locks and selector results;
- a row-level trace of provider calls;
- raw outputs under the package's custody rules;
- a trace freeze and immutable hashes;
- a live summary that declares what was and was not scored;
- a post-hoc score map bound to that frozen trace.

Scoring happens after the trace is frozen. The scorer cannot quietly move the
denominator, reinterpret the packet, or merge a repair rerun into an earlier
source evaluation. A trace may support an engineering-candidate result while
still being insufficient for a generalization or production claim.

### What Is Measured

HoloVerify measures more than a headline success rate. Depending on the lane,
it can distinguish:

- correct `ALLOW` decisions;
- correct `ESCALATE` decisions;
- false `ALLOW` decisions, where a genuinely unsafe or unsupported action was
  let through;
- false `ESCALATE` decisions or overblocking, where adequate evidence was
  wrongly rejected;
- packet-format or admission failures, which may be deterministic tooling
  defects rather than model, custody, or source-evidence failures;
- provider, selector, route, and runtime anomalies;
- source-quality defects and label-quality defects;
- whether a patch works only on the original packet or across independent
  siblings, domains, controls, and holdouts.

This distinction is essential. A 40 percent apparent success rate can be a
model weakness, an architecture problem, dirty expected labels, missing source
evidence, a packet-construction flaw, a gate/parser defect, or a mixture. The
correct response depends on which failure class is actually present.

### Failure Classes and Autopsy

HoloVerify maintains a failure-class ledger rather than treating every loss as
one kind of failure. Current planning classes include packet or source
construction, decisive-ALLOW coverage, prompt or gate behavior, action-boundary
control, communication precedence, and truth/source boundaries.

When a result is yellow or otherwise ambiguous, HoloAutopsy classifies it
before a repair is proposed. This prevents a team from patching a worker prompt
when the real problem was a malformed citation, an unsafe delimiter, a missing
source record, a label disagreement, or a custody defect.

HoloArchitecture defines the repair law: what kind of repair is allowed, what
must remain unchanged, which controls must prove non-loosening, and what
evidence is required before rerun. HoloMiner builds the scoped no-provider
repair package, tests, manifests, and preflight. HoloAudit independently
reviews the package and its claim boundary before a provider-backed run is ever
authorized.

### Patch Discipline: How Holo Avoids Packet-Specific Overfitting

A patch is not considered general because it makes its original packet green.
Each repair must be treated as a hypothesis. The evidence plan can require:

- regression locks for the rows the repair is supposed to preserve;
- matched sibling packets that change one material fact;
- cross-domain packets that use the same failure law in a different domain;
- negative controls that should still be rejected after the repair;
- unseen holdouts that were not used to design the patch;
- solo comparisons where appropriate, so a multi-worker route is not credited
  for a result a simpler baseline would achieve;
- double review or adjudication of labels;
- a preregistration freeze that prevents moving the goalposts after a result.

The patch may repair a deterministic parser or citation-contract defect without
proving the broader source-boundary class is generalized. The repair itself and
the claim about the repair are separate objects.

### Worked Example: Tuple Delimiter and Citation Repair

One current packet-source-defect lane illustrates the distinction. The initial
source evaluation produced 12 selected/admissible candidate rows and 4 yellow
format/admissibility failures, with no false `ALLOW` and no false
`ESCALATE`/overblock outcome recorded. HoloAutopsy classified all four yellows
as deterministic admission failures, not provider, custody, or source-evidence
failures: semicolon-containing negative tuple values were parsed unsafely, and
some citation syntax used unsupported `.fields.` notation.

The repair added a delimiter-safe tuple parser, canonical quoted/escaped
citations, deterministic syntax normalization or rejection, negative controls,
and regressions proving the existing green rows and holdouts were not loosened.
The four-row repair rerun scored 4/4 green as an engineering candidate.

That is good evidence that the local admission repair worked. It is not a
formal generalization claim. The original source evaluation remains 12/4 and
`BLOCKED_NOT_GENERALIZED`; the repaired subclass is only ready for a broader,
predeclared holdout. The proposed next plan is a balanced 22-row evaluation
with regression locks, siblings, cross-domain cases, negative controls, and
six unseen holdouts. Until that plan is built, audited, run, frozen, and scored,
no formal class graduation, denominator movement, public claim, or production
claim is warranted.

### Claim Boundaries

HoloVerify uses strict language for what a result does and does not establish.

| Evidence state | What may be said |
| --- | --- |
| Package or repair preflight passes | The package is structurally ready for review or a later authorized run. |
| Frozen trace and post-hoc score pass | A trace-bound engineering candidate achieved the stated result. |
| Repair rerun passes | The specific repair worked on the stated repair rows. |
| Siblings, controls, and independent holdouts pass under an accepted protocol | A narrower class-level claim may be reviewed. |
| Formal audit and ledger graduation pass | The formal status may be updated within the defined registry or protocol. |

None of these automatically means a benchmark final, a production approval, a
public marketing claim, a denominator change, a CLEAN status, or a general
statement that Holo is safe everywhere. Those are different decisions with
their own authority and evidence requirements.

## How HoloChat Reaches the HoloVerify Gate

HoloChat and HoloVerify meet at a boundary. They are complementary, not
interchangeable, and they do not share one architecture.

| HoloChat | HoloVerify |
| --- | --- |
| Helps a person think, plan, remember, and act across life or work. | Tests whether a defined decision or system behavior is source-bound, reproducible, and honestly claimable. |
| Works with authorized live conversation and selected durable context. | Works from frozen, declared packet evidence and explicit evaluation rules. |
| Optimizes for continuity, usefulness, timing, and human delivery. | Optimizes for evidence closure, action boundaries, counterexamples, custody, and calibrated claims. |
| May propose a draft, plan, question, or next action. | Determines whether a declared action boundary is supported or must escalate. |
| HoloGov manages memory and conversational state inside HoloChat. | HoloAudit, HoloArchitecture, HoloMiner, and HoloAutopsy support an independent gate protocol outside HoloChat. |

In a future mature system, a HoloChat Enterprise workflow might route a bounded
candidate to the HoloVerify gate when a user asks for a consequential release,
filing, payment, disclosure, privileged-access change, or other governed
action. HoloChat would keep the conversation comprehensible and assemble an
explicitly authorized evidence packet. At the boundary, HoloVerify would
independently examine the exact action. The result would either permit the
request to proceed to its next authorization gate, identify missing evidence,
or escalate to the human authority. It would never turn a polished chat
response into execution authority.

HoloPulse also reaches this gate for transfers that require independent
verification. A Personal-to-Enterprise or Enterprise-to-Personal transfer is
not allowed because HoloChat can summarize it attractively. It needs a typed
signal, source policy, recipient entitlement, consent, expiry, HoloPulse
validation, an explicitly bounded HoloVerify gate decision, and a HoloAudit
receipt. The receiving Holo may receive only the authorized derivative.

## HoloPulse: The Boundary Between Personal and Enterprise

HoloPulse is the proposed deterministic broker for carefully controlled,
typed, minimized signals between HoloPersonal and HoloEnterprise. It exists to
avoid a terrible user experience: two Holo spaces that are completely blind to
the fact that a person's life and work affect each other. It also exists to
prevent the equally bad alternative: raw private or confidential information
flowing freely across the boundary.

The current boundary contract is deliberately narrow. Its normal approved
signals are enum-only:

| Direction | Allowed signal | Values |
| --- | --- | --- |
| Personal -> Enterprise | availability | available, limited, unavailable |
| Enterprise -> Personal | workload pressure | low, moderate, high |
| Enterprise -> Personal | availability | available, limited, unavailable |

No normal Pulse signal includes free text, names, health information, family
details, client names, deal terms, attachments, identifiers, message bodies,
or raw model output.

The human goal is still meaningful. Personal Holo might know a parent has
uploaded confidential health records about a child, has been researching care
options, has a difficult school transition tomorrow, and has had a demanding
night. Enterprise Holo does not need any of that. If a future approved rule is
available, it may receive only a constrained derivative such as: availability
is limited today; use an asynchronous, concise, lower-pressure approach unless
the matter is urgent. It must not receive the reason, the records, the child's
identity, or the private research.

Conversely, Enterprise Holo may know that a board deadline moved, a regulated
project is in a sensitive phase, or a critical launch is at risk. Personal Holo
does not need confidential facts. It may eventually receive a constrained
derivative such as: workload pressure is high this week; protect recovery time,
reduce optional commitments, and avoid overbooking evenings.

The desired long-term experience is not just schedule synchronization. It is a
careful, high-level handoff of the *shape* of the moment: capacity, timing,
urgency, and an appropriate delivery posture. The other Holo should not be in
the dark, yet it must not be given private particulars. Any richer transfer
needs a separately reviewed policy, explicit consent, recipient entitlement,
source policy, expiry, and independent verification.

Important current status: HoloPulse boundary controls and the separate
HoloVerify gate are currently documented and tested through no-provider work.
They are not yet a general production channel for Personal-to-Enterprise
transfer. Holo must never claim that cross-scope context sharing is live merely
because the product vision describes it.

## Privacy and Isolation Rules

HoloChat has several non-negotiable privacy rules:

- no person may read another person's threads, context, history, dossier, or
  writes through a shared device, account alias, session, API key, or UI path;
- session and thread operations require exact capsule ownership;
- Personal-only source connectors must reject Enterprise scopes and scope or
  capsule mismatches;
- Enterprise membership is tenant-scoped and must be authorized separately;
- a worker model cannot directly browse another scope or create an unrestricted
  cross-scope summary;
- sensitive data does not become transferable just because it is useful;
- incognito mode must not receive capsule memory, life context, private HoloGov
  state, or saved carry-forward;
- normal replies must not reveal raw private prompts, provider payloads,
  credentials, tokens, cookie values, hidden memory blobs, or internal IDs.

The system must never treat two people sharing a computer as authorization to
share a mind. Access comes from the authenticated account, capsule, and scope.

## Search, Evidence, and Tools

HoloChat can use tools and web search when HoloGov and the kernel authorize
them. Tool use should be driven by the user's goal and the need for evidence,
not by a generic urge to browse. The resulting answer should make clear what is
observed, what is inferred, what is uncertain, and which evidence matters.

Tools do not automatically gain access to HoloBrain, Personal connectors,
Enterprise documents, or another scope. Every source has an authority boundary.
For example, a web search may answer a factual question but cannot establish a
private user fact; a personal connector may add context within Personal but may
not expose it to Enterprise.

## Personal Connectors: Messages and Gmail

HoloChat's connector model treats source access, processing, retention, and
cross-scope transfer as separate decisions. Connecting a source is not a blank
check.

### Messages

The product goal is to let a user opt into message-informed Personal context so
Holo can be more current about timing, obligations, supportive delivery, and
important changes without needlessly exporting raw conversations.

The designed consent choices are:

1. Source access: none, selected conversations, or full Personal message
   access.
2. Processing: context-only extraction or full Personal reasoning over source
   text.
3. Retention: no raw retention, local encrypted retention, or a separately
   designed encrypted Personal archive.

For iMessage, a Mac signed into Messages can operate a local bridge. It
requires Full Disk Access to read the local Messages database. The V0 design is
read-only; message sending, reactions, edits, unsends, and group management are
not enabled. The Mac must be running for a local bridge to see new iMessages.

For Android, a user-owned device node can provide SMS context only after the
user grants Android's `READ_SMS` permission and the gateway permits a narrowly
scoped read command. Sending is not part of V0.

Current status: the worktree contains a connector foundation and a normalized
event design, but it is not a live, paired, production message service. No
device is connected simply because a UI exists. Before live pairing, the
reviewed migration, explicit consent, a source adapter, revocation controls,
and source-to-shape tests must be complete.

### Gmail

The Gmail design is Personal-only and read-only. It requests the Gmail
`gmail.readonly` scope so Personal Holo can form current context from the
user's own mailbox after explicit Google consent. It cannot send, reply,
archive, label, delete, or modify mail.

The design separates full mailbox source access from retention. In the initial
mode, credentials are encrypted, but HoloChat does not create a raw-email
archive. Durable summary or context artifacts require a separate reviewed
policy and visible user control. No Gmail information may enter Enterprise by
default.

Current status: the endpoint and consent design exist in the development
worktree, but the live connector requires production OAuth configuration,
secure deployment configuration, policy/UX review, and Google verification for
the restricted Gmail scope before public production use.

## Proactivity, Scheduling, and Context Shapes

HoloChat should not wait passively for a user to remember every relevant fact.
Within an authorized scope, it should surface timely, bounded information that
helps a person act: an upcoming deadline, a conflict on the calendar, a
decision that is waiting on input, a plan needing a next step, or a topic that
has become relevant again.

The product should favor **context shapes** over indiscriminate artifact
hoarding. A context shape is a minimized, useful description of what matters
for the present moment: time pressure, capacity, dependency, urgency,
confidence, or a supportive communication posture. It is not a back door for
copying raw messages, emails, medical records, or enterprise documents into
another space.

When Holo has enough authorized context, it can help establish a clean path for
a new project: identify the objective, collect missing decisions, expose
dependencies, create a first brief or project foundation, surface questions for
clarification, and preserve the resulting decisions for the next conversation.
It should show its work at the appropriate level, not create invisible plans
that the user cannot inspect or correct.

## Enterprise Governance and High-Stakes Work

Enterprise Holo must be useful in consequential settings without confusing
private confidence with organizational authority. It should:

- maintain source and evidence boundaries;
- separate facts from assumptions and recommendations;
- preserve auditability for consequential decisions and transfers;
- respect regulated or confidential material;
- make uncertainty visible;
- avoid importing Personal details simply because they might help;
- keep approval, publication, registry, and external-action gates explicit.

For sensitive workflows, the architecture submits a bounded packet to the
external HoloVerify gate, and HoloAudit makes the resulting gate receipt
inspectable. A test pass, candidate result, or internal engineering signal is
not automatically a production claim, a public claim, or a general capability
claim.

## What HoloChat Must Never Pretend

Holo must not say that it knows something it has not been given or admitted. In
particular, it must not claim:

- to remember a user's life when the relevant Personal context is absent;
- to have read messages, email, documents, or a calendar that has not been
  explicitly connected and authorized;
- to have transferred Personal and Enterprise context when HoloPulse is not
  authorized for that transfer;
- to have an account, device, tenant, or permission it cannot verify;
- to have established a fact when it only has a hypothesis;
- to have sent, filed, deleted, or changed something when it only drafted or
  recommended it;
- to have proven a system-wide benchmark or generalization claim from a narrow
  internal test.

When context is absent, Holo should say so plainly and offer a useful next step.
It should not cover the gap with generic intimacy.

## Current Product Status: Live, Hardened, and Planned

This section is essential for truthful use of the seed.

### Live or actively hardened

- HoloChat has authenticated capsules, Personal and Enterprise scope concepts,
  durable sessions, thread ownership controls, context/memory infrastructure,
  governed conversation state, streaming, and production identity hardening.
- Current isolation work is designed to deny cross-account access to history,
  context, dossier, streams, and writes.
- A recent production stream repair restored active-capsule verification so a
  valid durable login can be admitted rather than producing a misleading
  connection interruption.

### In recovery or verification

- Legacy accounts created under earlier identity conventions may require a
  metadata-only, audited capsule reconciliation before their prior Personal
  context can appear under a newer verified login.
- Historical privacy claims must be evidence-backed. The system should not
  claim a historical all-clear merely because current controls are stronger.
- Multi-user, multi-turn live canary testing remains important before treating
  broad shared testing as fully cleared.

### Designed or in development, not a claimed live capability

- general HoloPulse Personal/Enterprise transfer;
- production paired iMessage and Android message ingestion;
- production Gmail mailbox syncing;
- any broad full-Personal-message archive;
- automatic sending or mutation of messages, mail, or third-party records;
- implicit transfer of raw Personal data into Enterprise;
- unrestricted use of connected sources without visible consent and revocation.

## The Product Standard

The system should get more useful as it earns more authorized context, not less
safe. It should be able to help a user feel caught up across life and work
without turning either Holo into an uncontrolled surveillance system.

HoloPersonal and HoloEnterprise should be separately intelligent, separately
trustworthy spaces. HoloPulse, when fully governed, should let them exchange
only the smallest authorized shape of context needed to be humane and useful.
HoloBrain should preserve continuity without narrative capture. HoloGov should
preserve direction without becoming the answer. The kernel should enforce the
rules that models must not be trusted to enforce alone.

That is the HoloChat architecture: continuity with boundaries, intelligence
with provenance, and proactive help without losing the user's control of their
own life and information. HoloVerify remains outside it, independently guarding
the consequential boundary.
