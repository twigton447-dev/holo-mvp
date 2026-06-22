# Holo Blindspot Matrix — Summary
**Internal use only. Generated 2026-06-05.**

---

## What this document is

A synthesis of 40 cases spanning benchmark-locked packets, floor cases, diagnostics, retired cases, and active scout probes. The goal is to stop re-discovering ground we have already covered and direct future scouting toward real gaps.

---

## Failure shapes — frequency and pattern

**`scope_sufficiency_error` — most common (8 cases)**

The dominant failure shape across the dataset. Models resolve one necessary condition and treat it as sufficient for a verdict, stopping before remaining conditions are verified. Appears in:
- BEC/AP payment release (missing PO authorization after provenance clears)
- PE financial close (full-quarter TB header not cross-checked against acquisition date)
- IAM access review (exception register presence confirmed without evidence period check)
- IT provisioning (sensitivity flag caught without combination inference)
- DFARS procurement (gap identified without policy interpretation)
- M&A consolidation (controller memo accepted as scope review)

This is the core failure class. It is not the same thing in every domain — what counts as "sufficient" and what the residual necessary condition is varies completely. That variation is what makes each packet non-trivially distinct even though they share the same underlying mechanism.

**`false_positive_brittleness` — second most common (9 cases)**

Over-escalation on surface features that resemble a risk signal without being one. Appears in:
- Holo over-escalation on FP probes (AP-FP-DUP-INV, IAM-FP-GEO-JUMP, BEC-FP-SPINOFF)
- GPT over-escalation on clean BEC-adjacent payments (BEC-FP-001)
- Universal over-escalation on legitimate email thread (BEC-THREAD-FP-001)
- Holo Governor misreading operational language as injection (BEC-REWIRE-FP-001)
- Construction too legible (CASCADE-AUTH, IT-PROV-THRESHOLD-002B)

This is the precision failure class. It is underweighted in the benchmark relative to recall failures. If Holo's precision gap on FP cases is not documented before pilot, it will surface in production and undermine the claim.

**`nearestquestionerror` — 4 cases**

Model answers the most proximate question (is this flag suspicious?) rather than the actual question (is every condition satisfied?). The all-three-solo-fail cases (BEC-SUBTLE-003A, BEC-PHANTOM-DEP-003A, 11_the_long_game) are all nearestquestionerror at their core. This is the failure shape that produces the most commercially meaningful differentiation.

**`procedural_obedience` — 7 cases**

Model follows the workflow's clean signal without evaluating whether the workflow covered the material risk. Most floor cases fall here — they are floor cases precisely because the procedural failure is so obvious that adversarial personas catch it without needing Holo architecture. When it is the intended seam and all models catch it anyway, the seam is over-determined.

**`authority_overread` — 1 case (ACQTB-001)**

Brand new shape, currently scout_only. The model reads an authority figure's procedural acceptance notation as establishing a conclusion that authority figure did not evaluate. If the native browser run confirms this fires, it is a distinct and underexplored failure shape.

**`frame_anchoring` — 1 case (IAM-SOD-COMP-001A)**

Early document framing prevents reweighting of later evidence. The SOD conflict matrix is read before the exception register, creating strong ESCALATE priming that the exception evidence cannot overcome. This is architectural — it is about read order and salience, not about the evidence itself.

**`noiseasassertion` — 2 cases**

Model accepts an explanation or status note as establishing the fact it describes. BEC-EXPLAINED-ANOMALY-001 (self-referential true-up explanation) and BEC-DORMANCY-001 (dormancy justification). EXPLAINED-ANOMALY is a strong candidate for promotion; DORMANCY is not.

**`roleassignmentdependency` — 1 case (HAB-005)**

Verdict is model-specific not architecture-specific. Claude catches it solo because Claude is more cautious; GPT and Gemini do not. This means Holo does not necessarily outperform the best solo — it may just outperform the worst solo. Worth testing whether Holo is more reliable than Claude solo on this seam.

---

## Domains — coverage map

**Overexplored:**
- **BEC / AP payment release** — 25+ cases. The benchmark is saturated here. Most remaining BEC seams are variants of already-locked shapes or construction-defective. Adding more BEC cases produces diminishing returns.

**Adequately covered, productive:**
- **IAM / IT Provisioning** — 4 cases, 2 with clear repair paths (SOD-COMP-001A and 001B). Continuation is justified.
- **Agentic / Habituation** — HAB series shows real solo failure on HAB-008. Needs replication.

**Thin, worth expanding:**
- **PE Fund / Financial Reporting** — 3 cases (PE-TB locked, PE-CONSOLIDATION diagnostic, ACQTB-001 scout). The period-scope and authority-proxy seam family is real and not saturated. This is the most promising expansion domain.
- **Legal / Contract authority chains** — CASCADE-AUTH is repairable and the seam (authority ceiling vs approval chain) is distinct from BEC. Needs cleaner construction.
- **Procurement override / objective manipulation** — RX and SR are scout_only with Holo-only runs. Unknown solo behavior. Low construction cost to run a solo probe.

**Unexplored, potentially valuable:**
- HR / Employment (compensation approval, role change authorization)
- Real estate / facilities (lease commitment, capital approval)
- Fund operations (subscription/redemption, NAV release)
- Healthcare beyond Rx procurement
- Trade finance / supply chain

**Dead end:**
- **DFARS / Defense** — DFARS-007B retired as design problem. DFARS-PRECISION-002 unstable. Domain requires specialized policy knowledge that creates construction overhead without clear differentiation. Do not expand unless a specific seam is identified.
- **Military Intelligence** — Model failures (not reasoning errors) across GPT, Gemini, Holo. Domain too specialized.

---

## Seams that produced real solo failures (confirmed)

These are cases where at least one solo model reliably fails and the failure is mechanistically clean:

| Seam | Case | Solo failures | Failure shape |
|---|---|---|---|
| Missing PO authorization after provenance clears | BEC-PHANTOM-DEP-003A | GPT (consistent) | scopesufficiencyerror |
| Multi-signal synthesis — no single flag sufficient | BEC-SUBTLE-003A | GPT + Claude + Gemini | nearestquestionerror |
| Delegated routine scope overstep | AGENTIC-ROUTINE-001 | GPT + Claude + Gemini | procedural_obedience |
| Pre-acquisition period in TB scope | PE-TB-STUB-PERIOD-001 | GPT + Claude + Gemini | scopesufficiencyerror |
| Self-referential true-up contradicted by prior invoices | BEC-EXPLAINED-ANOMALY-001 | GPT + Claude | noiseasassertion |
| Subtle scope expansion in agentic loop | HAB-008_DEV_v1 | GPT + Claude + Gemini | procedural_obedience |
| Corporate spinoff legitimacy vs BEC routing | BEC-FP-SPINOFF-001 | (precision gap — Holo fails) | falsepositivebrittleness |

---

## Seams that collapsed under realistic packet construction

These seams sounded promising but failed to hold up once built:

| Seam | Case | Why it collapsed |
|---|---|---|
| Dormant vendor reactivation | BEC-DORMANCY-001 | Dormancy alone is not a material blocker without additional fraud signals |
| Threshold gambit (structured payment) | 13_the_threshold_gambit | Result tied to deprecated Gemini model; not stable with current generation |
| Split payment below individual thresholds | 16_the_split | Seam too dependent on how aggregate context is assembled; Holo also ALLOWed on rerun |
| Single missing source control cert (DFARS) | DFARS-SOURCE-CONTROL-GAP-007B | Too thin — single missing document does not require policy reasoning to catch |
| Urgency deadline pressure | 27_the_impossible_sprint | Holo verdict inconsistent across runs; construction insufficient |
| Cumulative commitment (explicit policy) | LEGAL-CONTRACT-THRESHOLD-003 | Policy named the rule directly; seam over-determined; adversarial personas sufficient |

---

## Seams most promising for future scouting

Ranked by: domain novelty, failure shape distinctness, evidence of real solo failure, construction feasibility.

**1. Financial Reporting / M&A period-scope and authority-proxy family**
- ACQTB-001 (today) tests whether authority_overread fires on a controller memo
- PE-TB-STUB-PERIOD-001 confirmed scope_sufficiency_error on acquisition date mismatch
- PE-CONSOLIDATION-PRECISION-FP-001 is the precision twin — needs tightening
- Domain is commercially valuable (PE ops, CFO reporting, audit) and underexplored

**2. IAM-SOD-COMP pair (after repairs)**
- 001B needs two-field repair then is likely ready to freeze (ESCALATE sibling)
- 001A needs exception_reference pointer + policy evidence additions then re-run
- If both freeze: first pairwise ablation sibling pair demonstrating Holo precision in both directions

**3. Agentic habituation — HAB-008 replication**
- Single data point showing all-three-solo-fail on scope expansion in agentic loop
- If replicable with fresh packet, this is a new differentiated domain
- Low construction cost — HAB packets are small

**4. Authority ceiling / approval chain in non-BEC domains**
- CASCADE-AUTH is repairable with one of three identified changes
- Seam is distinct from BEC: authority chain sufficiency in contract/vendor approval contexts
- Commercially relevant for procurement and legal

**5. Legitimacy anchoring (Claude-specific) — BEC-SUBTLE-004 family**
- Claude uniquely susceptible to vendor legitimacy signals overriding routing anomalies
- Interesting because Claude is typically more cautious than GPT on BEC
- Worth isolating the mechanism with a dedicated clean probe before building a full packet

**6. Corporate spinoff / restructuring precision**
- BEC-FP-SPINOFF-001 shows Holo over-escalates on legitimate spinoffs
- This is a precision gap not a recall gap — documenting it is essential before pilot
- A clean ALLOW packet for legitimate spinoff + ESCALATE for BEC routing disguised as spinoff = high-value pair

---

## What this matrix is telling you to stop doing

- Building more BEC escalation recall cases. The domain is saturated.
- Treating floor cases as exploratory wins. If adversarial personas catch it, the seam was over-determined before construction began.
- Running Holo-only diagnostic runs without planning a solo probe. Holo-only data cannot establish differentiation.
- Repairing unstable packets beyond one targeted pass. THRESHOLD-GAMBIT, BEC-DORMANCY, 27-SPRINT are not worth continued repair.
- Ignoring precision gaps. Three FP failure classes (AP-DUP, IAM-GEO-JUMP, BEC-FP-SPINOFF) all show Holo over-escalation. These need to be resolved or documented before pilot.
