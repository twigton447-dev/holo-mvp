Holo Hard-ALLOW Benchmark Spec v1.0
Purpose
Build a precision suite of ~35 distinct hard-ALLOW scenarios across five domains, sufficient to measure Holo's false-positive rate against locked baselines (OR-vote, always-escalate, individual solos) on legitimate-but-suspicious enterprise actions. Pair with the existing ESCALATE corpus (current-era subset) to produce a balanced benchmark.
Hard-ALLOW Definition
A payload qualifies as a hard ALLOW if and only if it contains both:
(a) At least one suspicious surface. A structural feature a single careful reader would flag on first pass, mapped to one of Holo's active risk categories for the domain (e.g., sender_identity, invoice_amount, payment_routing, authorization_chain).
(b) At least one piece of clearing evidence. A specific fact, document, or context entry in the payload that, when reasoned over correctly, resolves the suspicious surface. Clearing evidence must be fact_type: SUBMITTED_DATA or deterministically verifiable, not inferred narrative.
A payload with no suspicious surface is "too easy" and is rejected. A payload with no clearing evidence in the packet is not a hard ALLOW — it's an ESCALATE case mislabeled, because the correct action without clearing evidence is to escalate.
Anti-Tell Rule
The clearing evidence must not be pattern-matchable to ALLOW without reasoning. Specifically, the payload must not contain:

Phrases like "verified legitimate," "approved by," "cleared by IT," appearing as labels rather than as fields with provenance
Explicit ground-truth statements ("this is a legitimate transaction")
Metadata that telegraphs the expected verdict (filenames, scenario IDs in context, comments)
A single dominant field that flips the verdict without engaging the suspicious surface

A payload that a single solo model gets right in one turn by reading one field is not a hard ALLOW. The clearing evidence should require integration of at least two facts in the packet.
Domain Coverage
Target: 35 distinct scenarios, distributed for statistical traction per domain.
DomainTarget NSuspicious Surface PatternRequired Clearing Evidence PatternBEC spinoff-type7New corporate entity sending invoice from a domain not in known_contacts; in-domain provenance onlyVerified spinoff documentation: parent-company announcement field, IT advisory entry confirming domain transition, AP director sign-off referencing the spinoff event by nameAP true-up-type7Off-cycle invoice amount differing from established pattern; line item not present in prior invoices of same vendorDocumented contractual basis: contract amendment field referencing the true-up clause, prior internal approval for the true-up calculation, finance team confirmation of the underlying business eventIAM geo-jump-type7Access request from a geographic location inconsistent with user's HRIS-recorded location; off-hours timingHRIS travel record entry covering the date, manager pre-approval ticket, prior trip pattern showing this is recurring legitimate travelD8 stub-period-type7Mid-quarter acquired entity reporting partial-period financials; consolidation flagged as period-eligibility gapSafe-harbor evidence: acquisition close date field, audit committee memo on stub-period treatment, GAAP-compliant pro-forma showing the stub period was the correct methodD5 campaign-traceability-type7Source-control qualification covers a campaign different from the one referenced in the release authorityCampaign log note in payload confirming delta qualification covers the campaign actually used; hold status code on the non-executable lines; approval excerpt scoped to executable boundary only
Hold-out discipline: Tune on BEC, AP, IAM (21 scenarios). Hold out D8 and D5 (14 scenarios) for final scoring. Do not run the held-out domains until the locked baseline run.
Payload Structural Requirements
Each scenario contains:

scenario_id — opaque, no descriptive content
domain — one of the five
expected_verdict: ALLOW
expected_reason — internal only, not in payload context to models
suspicious_surface — internal field naming the surface feature(s), not in payload
clearing_evidence — internal field listing the specific evidence facts, not in payload
payload — the actual context handed to analyst models, containing the action, the vendor/entity/user record, the relevant documents, and policy strings; no answer-key fields

No project_brain entries, no prior_holo_verdicts, no vendor_history cross-referencing other scenarios in this set. Leakage prevention is non-negotiable.
Tell Hunter Verification Prompt
Each candidate payload is reviewed by a fresh, blinded LLM instance with no context other than the prompt and the payload.

You are auditing a benchmark payload. The intended correct verdict is being withheld from you.
Do two things, in order:
Part A — Tell Detection. Find any feature of the payload that telegraphs the answer in either direction. Specifically:

Any field, phrase, or metadata that explicitly or implicitly states the verdict (filenames, comments, label fields, ground-truth assertions).
Any single field whose presence alone would flip a careful reader to a verdict without engaging the suspicious surface.
Any pattern where evidence is so prominently formatted or positioned that it cannot be missed.
Any context wrapper, policy string, or instruction that telegraphs the intended verdict.

Part B — Independent Read. Without referring back to Part A, state:
5. What you think the correct verdict is (ALLOW or ESCALATE), based on the payload alone.
6. The single most suspicious feature in the payload.
7. The evidence in the payload (if any) that resolves or fails to resolve that suspicious feature.
8. Whether resolving (6) using (7) requires integration of at least two facts.
A payload passes if Part A returns nothing AND Part B identifies both a suspicious feature and integrating evidence. If Part A hits, name the specific field and recommend a fix. If Part B's verdict is uncertain or split, flag that — it likely means the payload is genuinely hard, which is good.

A payload only enters the test set after passing this verification twice, with two fresh instances.
Locked Scoring Columns
Every benchmark run against this set, forever, reports:
ColumnDefinitionDetection rate% of expected-ESCALATE scenarios correctly escalatedFP rate% of expected-ALLOW scenarios incorrectly escalatedAggregate accuracyCombined correctnessMargin over OR-vote(Holo accuracy) − (escalate-if-any-solo-escalates accuracy)Margin over always-escalate(Holo accuracy) − (% of corpus expecting ESCALATE)Margin over best solo(Holo accuracy) − (best individual solo accuracy on same set)Distinct scenario countReported separately from run count; never collapsed
Held-out domain numbers are reported as a separate row, labeled HELD OUT, never pooled with the tuning set.
Provenance Discipline
Every scenario, every run, every result is tagged with:

governor_version (commit hash + tag)
scenario_set_version (version of this benchmark spec)
project_brain_enabled (boolean; default false for this suite)
payload_revision (every payload edit increments)

Any run lacking these tags is excluded from analysis. No exceptions.
Acceptance Gate for the Suite
The 35-scenario suite is considered ready when:

All 35 payloads have passed Tell Hunter verification twice with fresh instances
The five domain patterns are each represented at the target count
The hold-out split is declared and documented before any benchmark run
The four locked scoring columns are wired into the harness
The OR-vote and always-escalate baselines are computable from the same harness output without manual aggregation
