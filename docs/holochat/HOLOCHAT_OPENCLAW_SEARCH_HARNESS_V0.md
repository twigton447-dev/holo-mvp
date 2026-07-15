# HoloChat OpenClaw Search Harness V0

## Status

Implemented as an opt-in transport adapter. Disabled by default. This document
does not authorize a gateway deployment, provider call, or production change.

## Purpose

OpenClaw may serve as HoloChat's **search harness**, not as HoloGov and not as
a general-purpose agent runtime. It can centralize provider-specific web
search transports while HoloChat keeps the product authority:

- HoloGov decides whether a turn requires current evidence.
- HoloGov assigns the query, risk class, source-domain policy, and evidence
  budget.
- The harness retrieves structured source records only.
- HoloChat's evidence gate admits or rejects those records before a visible
  worker receives them.
- The worker synthesizes admitted evidence; it never controls the harness.

The visible worker rotation is independent of the search backend. A Grok turn
may use a source retrieved through OpenClaw or direct OpenAI search, and an
OpenAI worker may do the same. Search selection is HoloGov-controlled rather
than tied to whichever worker happens to be speaking.

## Required Gateway Boundary

Do **not** configure HoloChat with an ordinary OpenClaw gateway. A normal
gateway bearer token is an operator credential and can expose more capability
than HoloChat needs.

Before enabling this adapter, operate a dedicated private gateway with all of
the following properties:

1. A separate deployment, OS account, token, and network boundary from any
   operator or development gateway.
2. Only the read-only `web_search` tool exposed. Browser control, shell/exec,
   files, email, messaging, connectors, and every action tool must be denied.
3. A private address by default. The adapter refuses remote hosts unless an
   operator explicitly overrides that denial; the override is not approved for
   beta use.
4. Structured result records containing at least a URL plus title or excerpt.
   Plain prose from the gateway is rejected rather than treated as evidence.
5. Gateway-side request, provider, token, and latency telemetry that can be
   joined to HoloChat's redacted search trace without recording raw user
   content in ordinary application logs.

HoloChat calls only `POST /tools/invoke` with `tool: web_search`. It sends a
bounded query and result count. It does not send user profile data, HoloBrain
content, worker prompts, or a capability list to the gateway.

## Configuration

The adapter remains unavailable unless every relevant value is set:

```text
HOLOCHAT_SEARCH_PROVIDERS=openclaw,openai
HOLOCHAT_OPENCLAW_SEARCH_ENABLED=true
HOLOCHAT_OPENCLAW_SEARCH_DEDICATED_GATEWAY=true
HOLOCHAT_OPENCLAW_GATEWAY_URL=http://127.0.0.1:18789
HOLOCHAT_OPENCLAW_GATEWAY_TOKEN=<dedicated-search-only-token>
```

`HOLOCHAT_OPENCLAW_ALLOW_REMOTE_GATEWAY` must remain `false`. A future remote
gateway requires a separate security review and a narrow identity-aware proxy;
it is not a beta configuration shortcut.

When OpenClaw is absent or intentionally disabled, its slot is skipped without
a provider request. Direct OpenAI hosted search is the controlled fallback.

## Cost and Latency Defaults

The current direct-hosted fallback is deliberately bounded:

- one configured provider attempt per authorized search;
- three hosted web tool calls at most;
- 1,200 maximum retrieval/reasoning output tokens;
- low retrieval reasoning effort;
- 10--60 second per-backend timeout.

Those defaults protect against the repeated-search pattern that drove the prior
high-cost OpenAI usage. An operator must deliberately raise any cap, and every
OpenClaw provider route needs equivalent gateway-side limits before activation.

## Evidence and Safety Rules

The harness is a transport, not an evidence authority. HoloChat still:

- applies domain allow/deny rules after retrieval;
- rejects malformed or unsupported source records;
- labels title-and-link-only records as citations, not proof for a factual
  claim;
- passes only admitted evidence to the visible worker;
- logs the provider, outcome, source IDs, bundle hash, and fallback outcome;
- tells the user that a current check was unavailable when no evidence was
  admitted instead of claiming a search occurred.

For clinical trials and other high-stakes current facts, HoloGov's domain policy
is authoritative even if a search provider returns a broader result set.

## Activation Checklist

1. Create a dedicated search-only OpenClaw gateway and separate token.
2. Confirm a deny-by-default tool policy with only `web_search` enabled.
3. Run the injected no-provider adapter tests.
4. Run one cost-capped canary query against the isolated gateway.
5. Inspect the redacted HoloChat trace and gateway telemetry together.
6. Confirm no unadmitted source can appear in the visible answer.
7. Enable it for a small internal cohort before general beta traffic.
