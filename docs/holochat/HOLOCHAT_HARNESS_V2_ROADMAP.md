# HoloChat Harness V2 Roadmap

Status: implementation roadmap
Updated: 2026-07-14

## Product Position

HoloChat should provide the normal capabilities users expect from a modern chat application while preserving its architectural advantage: HoloGov maintains continuity, evidence, scope, and state while rotating worker models provide independent reasoning perspectives.

The product is strongest for long-running personal reasoning, project continuity, evidence-grounded research, sensitive decisions, and hybrid personal/enterprise work where identity can travel but data must not.

## Provider Web Search Study

Official provider documentation reviewed on 2026-07-14:

- OpenAI Responses API: hosted `web_search`, inline URL citations, complete source lists, domain filters, configurable search context, live/cached access control, and longer research token budgets.
- Google Gemini: hosted `google_search` grounding, automatic query generation, URL citation annotations, and combined built-in/custom tools.
- xAI: hosted `web_search`, citations, domain allow/exclude filters, image search, and Responses API compatibility.
- DeepSeek: tool calling is documented, but no hosted web-search tool is documented. HoloChat should supply its own search function for DeepSeek workers.
- Tavily: remains a useful provider-neutral retrieval backend and fallback, but must sit behind the same typed search contract as provider-native search.

HoloChat must not copy a consumer chatbot's private search implementation. It can use the public provider APIs and reproduce the durable pattern: search planning, retrieval, source normalization, evidence selection, synthesis, citations, and release admission.

## Search Architecture

The canonical flow is:

`User turn -> HoloGov SearchPlan -> SearchAdapter -> RetrievalBundle -> EvidenceSelection -> Worker -> CitationAdmission -> Visible release`

HoloGov owns whether search is needed, the source policy, allowed domains, risk class, budget, and selected evidence. Search providers retrieve evidence; they do not become Gov authority.

Required adapter interface:

- `TavilySearchAdapter`
- `OpenAIWebSearchAdapter`
- `XAIWebSearchAdapter`
- `GeminiGroundingAdapter`
- `CustomFunctionSearchAdapter` for DeepSeek and other providers

Every adapter returns the same typed outcome: provider, status, queries, candidates, canonical URLs, source keys, passages, citations, latency, tool-call count, and error category. Retrieved text is always untrusted data.

## Model Experiment Program

Three cost/intelligence lanes are used for evaluation, not silently applied to production:

- Economy: inexpensive workers for routine turns and high-volume regression runs.
- Balanced: strong general models for normal conversation and mixed workloads.
- Frontier: maximum capability for high-stakes, emotionally complex, deeply technical, or adversarial turns.

Each lane tests the same A/B/C/D conditions:

- A: rotating-worker baseline with pre-worker HoloGov control disabled.
- B: the legacy clipped-history path with the current control plane.
- C: the current HoloGov control packet with bounded ordered history.
- D: the current HoloGov packet plus selective context, episodes, and reseed behavior.

Worker homogeneity and DNA diversity are separate experiment dimensions. Do
not infer them from the A/B/C/D context condition; the manifest's exact worker
model sequence is authoritative.

All runs record exact model IDs, HoloGov model, input/output/cached/reasoning tokens, latency, search calls, estimated cost, context receipt, memory selections, failover, visible repair, and rubric scores. Pricing is versioned and estimates are never presented as billed cost.

Primary quality measures:

- factuality and citation support
- continuity and memory precision
- insight and blind-spot discovery
- empathy without flattery or false intimacy
- useful challenge without scolding
- hallucination and overclaim rate
- drift across turns and worker handoffs
- cost and latency per useful turn

## Portable Identity, Fixed Data Scope

The portable object is the principal identity, not an unrestricted capsule containing every datum.

`Principal -> Personal scope`

`Principal -> Tenant membership -> Enterprise scope`

Every request must resolve a server-side access context containing principal, active scope, scope kind, tenant, workspace, membership, roles, authorization version, and session. The client may request a scope; it may not authorize itself.

Hard invariants:

1. Every session, message, memory, artifact, consolidation, integration, and evidence record belongs to one immutable scope.
2. Personal data is not injected into enterprise context by default.
3. Tenant data never appears in personal context or another tenant.
4. Cross-scope transfer is explicit, minimal, consented, and audited.
5. Personal-to-enterprise transfer creates a tenant-owned derivative.
6. Enterprise-to-personal export is denied unless enterprise policy explicitly permits a sanitized derivative.
7. HoloGov sees only records admitted by the resolved scope and classification policy.
8. Database row-level security is defense in depth; application authorization remains mandatory.

## Delivery Order

1. Repair current session ownership checks before loading any chat history.
2. Land dry-run-first experiment manifests and cost accounting.
3. Replace search string/side-channel transport with a typed provider-neutral search result.
4. Add claim-level citation support checks and source-quality policy.
5. Introduce principals, tenants, memberships, scopes, and audited transfers.
6. Run continuous Mira and synthetic-enterprise isolation evaluations before enabling hybrid scope switching.

## Rollout Gates

Two features remain disabled until the reviewed Supabase migration is applied:

- `HOLOCHAT_HYBRID_SCOPES_ENABLED=1` enables server-resolved personal and enterprise scopes.
- `HOLOCHAT_MEMORY_STEWARD_ENABLED=1` enables atomic delta checkpoints, durable correction/revocation handling, restart watermark recovery, and the pre-autocompact acknowledgement gate.

Enable them together only after migration preflight, rollback review, synthetic cross-tenant isolation tests, and a six-turn memory checkpoint run succeed in the target environment. No client-supplied scope identifier is authority.
