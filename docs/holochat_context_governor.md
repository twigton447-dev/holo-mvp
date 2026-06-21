# HoloChat Context Governor

Status: implementation note for the HoloChat continuity layer.

HoloChat now maintains a durable, structured HoloChat State Object for continuity across long threads and fresh threads. The layer is deterministic and local: it does not call providers, it does not adjudicate irreversible actions, and it does not turn HoloChat into HoloBuild.

## Scope

HoloChat remains the workspace and continuity surface for strategy, evidence, drafts, project memory, artifacts, and handoff packets. HoloBuild remains the governed artifact and refinement factory.

The Context Governor layer in HoloChat owns working continuity only:

- rolling conversation and project summary
- critical constraints
- settled decisions
- artifact references
- required tools
- baton pass for the next assistant/thread
- audit hashes and trust warnings

## State Object

The canonical state object exposes these doctrine fields:

- `USER_GOAL`
- `LATEST_INPUT_SUMMARY`
- `CRITICAL_CONSTRAINTS`
- `ROLLING_SUMMARY`
- `SETTLED_DECISIONS`
- `ARTIFACTS_REGISTRY`
- `REQUIRED_TOOLS`
- `BATON_PASS`

`STATE_AUDIT` records trust status, missing required fields, reseed size warnings, artifact reference warnings, contradiction warnings, and hashes for the state, rolling summary, baton pass, artifact registry, and reseed payload.

## Runtime Flow

After meaningful HoloChat turns, the runtime updates the state object from the latest user input, assistant response summary, current Gov arc state, saved artifact references, required tools, thread health, and context budget pressure.

When a thread approaches budget pressure, the same state object becomes the compact continuity target. It preserves working continuity rather than routine logs.

When a new signed-in HoloChat thread starts, the runtime reads the latest durable state from capsule context and injects a private auto-reseed block into the system prompt. Normal user-visible replies do not expose this block unless explicitly requested.

Artifacts are tracked by reference. The registry stores identifiers such as artifact ID, path, hash, title, type, and status where available. Full artifact content is not blindly copied into every reseed.

## Privacy Boundary

The durable state is stored under a private underscore-prefixed capsule context key and is excluded from normal working-memory prompt blocks. Reseed output is redacted for secret-like key, token, password, authorization, and bearer patterns.

The runtime reports inspectable metadata and hashes in Engine data, while keeping provider internals, secrets, environment values, and private implementation metadata out of normal chat responses.
