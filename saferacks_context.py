"""
saferacks_context.py
SafeRacks / Eagle Industrial Group — Holo Engine domain context
Physical products operations harness v0.1

Drop into: /Users/taylorwigton/CascadeProjects/holo-mvp/
"""

# ---------------------------------------------------------------------------
# VERTICAL CONTEXT
# Injected into every turn so Holo understands the operating world
# ---------------------------------------------------------------------------

VERTICAL_CONTEXT = """
DOMAIN: Physical products operations — consumer storage / garage organization
COMPANY PROFILE: Manufacturer and distributor of overhead garage storage racks,
wall-mounted shelving, freestanding units, and accessories. Sells through Costco
road shows and replenishment, Home Depot, Amazon FBA, direct-to-consumer (DTC),
and dealer/installer channels. Product manufactured overseas (China). SKUs carry
explicit weight/load ratings (e.g. 600 lb capacity) that create product liability
exposure if component equivalence is not validated.

KEY OPERATIONAL REALITIES:
- Costco is a strategic channel: vendor scorecards, fill rate thresholds (~95%),
  compliance chargebacks, and road show rotation access are all at risk if
  commitments are not honored precisely.
- Factory default behavior: factory ships current carton/spec unless updated
  dieline/spec is explicitly transmitted with the PO. Packaging transitions
  require cross-functional coordination (ops, packaging team, factory).
- Channel conflicts are asymmetric: DTC margin gains are typically small
  relative to the downstream cost of damaging a retailer relationship or
  losing preferred vendor status.
- Load-bearing components (mounting hardware, fasteners, rack frames) carry
  product liability implications. Supplier substitution requires third-party
  load certification before any unit can ship to a retail or DTC channel.
- 3PL quarantine is a real operational tool: pilot batches can be held and
  released only after QA signoff, which changes the risk profile of a new
  supplier pilot significantly.

CROWN JEWELS AT RISK:
- Costco road show access (highest-volume sales channel, seasonal)
- Preferred vendor status with major retailers
- Product liability coverage (dependent on validated component equivalence)
- Brand reputation tied to load/safety ratings
- Factory relationships and deposit leverage
"""

# ---------------------------------------------------------------------------
# ACTION BOUNDARY LIBRARY
# What type of commitment is being evaluated?
# ---------------------------------------------------------------------------

ACTION_BOUNDARIES = {
    "purchase_order_approval": "A factory PO becomes a financial and inventory commitment. Once issued, cancellation incurs cost or damages supplier relationship.",
    "inventory_allocation": "Allocating inventory to a channel creates an implicit or explicit fulfillment commitment. Over-allocating to one channel may breach obligations to another.",
    "supplier_substitution": "Changing a component supplier affects product claims, liability coverage, and channel compliance until equivalence is validated.",
    "contract_term_acceptance": "Accepting changed payment, delivery, or remedy terms shifts financial exposure and leverage.",
    "packaging_spec_change": "A carton/packaging change requires retailer compliance approval and factory spec transmission before production. Sequence matters.",
    "channel_priority_decision": "Deciding which channel receives available inventory creates downstream fill rate, scorecard, and relationship consequences.",
}

# ---------------------------------------------------------------------------
# DOMAIN RISK LENSES
# The adversarial reviewers apply these lenses when evaluating a case
# ---------------------------------------------------------------------------

RISK_LENSES = [
    "product_claim_integrity: Does this action affect any component that supports a published weight/load/safety rating?",
    "retailer_channel_impact: Does this action affect fill rate, compliance, scorecard, or relationship with a major retail channel?",
    "inventory_fill_rate_risk: Could this action create a shortfall against an existing or imminent retailer commitment?",
    "cross_functional_sequencing: Does this action depend on a decision or communication that has not yet been confirmed in another function (packaging, legal, QA)?",
    "supplier_quality_and_leverage: Does this action change the company's quality assurance position or financial leverage with a supplier?",
    "contract_margin_drift: Does this action change payment terms, deposit structure, or remedy rights in ways that shift exposure?",
    "asymmetric_downside: Is the visible upside (margin, cost savings, demand capture) small relative to a non-obvious but significant downside?",
    "missing_deciding_context: Is there a known or likely cross-functional state (compliance window, contractual threshold, spec transition) that is absent from the packet but would change the verdict?",
]

# ---------------------------------------------------------------------------
# GOVERNOR RULES
# Hard rules applied by the Governor in Turn 5
# These override analyst consensus if triggered
# ---------------------------------------------------------------------------

GOVERNOR_RULES = """
GOVERNOR RULES — SafeRacks Operations Harness v0.1

Apply these rules in order. First triggered rule determines the floor verdict.
The Governor may raise (escalate further) but never lower an analyst consensus verdict.

RULE G1 — PACKAGING TRANSITION UNRESOLVED:
If the action involves a PO increase or production run AND a carton/packaging
change has been approved but not yet transmitted to the factory:
=> FLOOR: REQUEST_CONTEXT
=> Reason: Factory default behavior creates compliance risk. The packaging
   decision is a deciding context that must be resolved before the PO commits.

RULE G2 — RETAILER FILL RATE AT RISK:
If available inventory cannot satisfy both a retailer PO (with a contractual
or scorecard fill rate threshold) AND the proposed allocation simultaneously:
=> FLOOR: ESCALATE
=> Reason: Retailer relationship and vendor status consequences are asymmetric.
   This decision requires commercial leadership, not operational discretion.

RULE G3 — LOAD-BEARING COMPONENT, UNVALIDATED SUBSTITUTION:
If a component substitution involves a load-bearing or safety-rated part AND
third-party load certification has not been completed:
=> FLOOR: ESCALATE (unless quarantine + restricted channel safeguards are present)
=> If quarantine + restricted channel + cert-before-release safeguards are ALL
   confirmed: ALLOW (pilot scope only)

RULE G4 — WATCHOUT IS NOT RESOLUTION:
If an analyst recommends ALLOW with stated conditions or watchouts, but the
conditions require action from a function not confirmed to be in the loop:
=> RAISE to REQUEST_CONTEXT
=> Reason: An unresolved cross-functional dependency is not a watchout.
   It is missing deciding context. Approval cannot precede resolution.

RULE G5 — CLEAN PACKET, NO TRIGGERS:
If no Governor rules are triggered AND analyst convergence is ALLOW:
=> ALLOW
=> Reason: Routine work proceeds without friction.
"""

# ---------------------------------------------------------------------------
# ADVERSARIAL REVIEWER PERSONAS
# Each analyst turn uses a distinct adversarial lens
# ---------------------------------------------------------------------------

REVIEWER_PERSONAS = {
    "ops_reviewer": {
        "role": "Senior VP of Operations",
        "lens": "You are responsible for on-time delivery, factory relationships, inventory cover, and fill rate compliance. You have been burned before by committing to production runs before cross-functional dependencies were resolved. You are skeptical of decisions that look clean on the surface. You ask: what has to be true for this to go wrong?",
        "bias": "You tend to flag sequencing dependencies and cross-functional gaps that others miss.",
    },
    "commercial_reviewer": {
        "role": "VP of Sales and Channel Management",
        "lens": "You own the Costco, Home Depot, and key retail relationships. You know that a compliance chargeback is not just a line item — it is a signal to a buyer that affects road show access, shelf placement, and vendor status reviews. You are deeply skeptical of any decision that trades short-term margin for long-term channel risk, even when the math looks favorable.",
        "bias": "You tend to surface hidden retailer relationship consequences that operations and finance underweight.",
    },
    "finance_reviewer": {
        "role": "CFO / VP of Finance",
        "lens": "You evaluate decisions against total exposure, not just the visible transaction. You are trained to look for asymmetric downside: cases where the visible upside is modest but the non-obvious downside is large. You ask: what is the worst-case financial outcome if this goes wrong, and does the upside justify it?",
        "bias": "You tend to identify asymmetric risk profiles that margin-focused analyses miss.",
    },
    "quality_reviewer": {
        "role": "VP of Quality and Product Integrity",
        "lens": "You own the product liability exposure and the brand's safety ratings. You know that a 600 lb rating on the box creates a legal and reputational obligation. You are the last line of defense against a component substitution that passes a visual spec check but has not been load-tested to the published rating. You do not approve anything that touches a safety-rated component without a test certification in hand.",
        "bias": "You tend to flag product claim integrity and component equivalence gaps.",
    },
    "wms_routing_reviewer": {
        "role": "Director of Warehouse Systems and Inventory Control",
        "lens": "You own WMS configuration, fulfillment routing logic, and inventory leakage risk. You know every code, flag, and rule in the system — and you know how they can be misused. Your job is to determine whether the transaction codes, BOL type, reason codes, and cost center collectively form a coherent, closed system that cannot convert to saleable inventory. You do not approve rule overrides based on intent — you approve them based on what the system records will allow and prevent.",
        "bias": "You tend to catch gaps between what the paperwork says and what the WMS will actually permit at execution time.",
    },
    "qa_containment_reviewer": {
        "role": "QA Containment and Disposition Lead",
        "lens": "You own the integrity of the QA hold and the chain of custody from quarantine to external test lab to disposition decision. A HARD_HOLD_QA flag is not bureaucracy — it is the only thing standing between an unvalidated lot and a sellable channel. You evaluate whether the proposed transaction is the required action to satisfy the open deviation, or whether it is a workaround that creates exposure. You look for: Is the destination a certified testing facility? Does the shipment close the open deviation or bypass it? Are there system flags that allow the lot to convert to saleable inventory after the transfer?",
        "bias": "You tend to find ways that a 'QA transfer' could be reclassified or reversed after the fact, leaking uncertified inventory into sellable channels.",
    },
}

# ---------------------------------------------------------------------------
# CASE PACKETS
# The four SafeRacks mini benchmark cases
# ---------------------------------------------------------------------------

CASES = {
    "case_1_po_carton_gap": {
        "id": "SR-BENCH-001",
        "type": "gap",
        "title": "PO increase — OGS-4896 before Costco carton compliance transition",
        "action_boundary": "purchase_order_approval",
        "expected_solo_verdict": "APPROVE with conditions",
        "expected_holo_verdict": "REQUEST_CONTEXT",
        "exploited_blindspot": "Model treats stated watchouts as resolved; misses cross-functional sequencing dependency",
        "packet": """
CASE PACKET — SR-BENCH-001
Product: OGS-4896 (4x8 overhead garage storage rack, 600 lb capacity)
Channel: Costco — road show + replenishment
Proposal: Increase next factory PO from 2,400 units to 3,120 units (+30%)

Supporting data:
- Sell-through running 23% above forecast across current road show locations
- Inventory cover dropping to 6 weeks (internal target: 10 weeks)
- Defect/return rate: 0.4% (within acceptable range)
- Factory on-time delivery: 4 of last 4 runs
- Margin at new volume: $4.10/unit above threshold
- Factory capacity confirmed available for the increase

No other context has been provided.
""",
        "hidden_context": """
HIDDEN CONTEXT (not in packet — this is what Holo should catch):
- Costco compliance approved a revised carton spec for OGS-4896 effective the
  next replenishment window (opens in 9 weeks). Changes: bilingual weight rating
  callout (600 lb / 272 kg), updated installation diagram, QR code for video guide.
- Factory default: ships current carton unless updated spec is transmitted with PO.
- Updated dieline has NOT been sent to the factory. Packaging team has not been
  looped into the PO decision.
- If PO ships in current cartons: Costco compliance chargeback (~$18/unit repack
  at 3PL) OR units held at DC until rework, missing replenishment window entirely.
""",
    },

    "case_2_dtc_fillrate_gap": {
        "id": "SR-BENCH-002",
        "type": "gap",
        "title": "Inventory allocation — DTC margin vs. Costco fill rate obligation",
        "action_boundary": "inventory_allocation",
        "expected_solo_verdict": "APPROVE Option A (DTC priority)",
        "expected_holo_verdict": "ESCALATE",
        "exploited_blindspot": "Model optimizes visible margin; misses contractual fill rate threshold and asymmetric retailer downside",
        "packet": """
CASE PACKET — SR-BENCH-002
Product: OGS-4672 (4x6 overhead garage storage rack)
Situation: Inventory allocation decision — 1,200 units on-hand

Option A — prioritize DTC:
- Fill Costco PO partially (~600 units, ~75% fill rate)
- Allocate remaining 600 units to DTC
- DTC margin: $189/unit vs. Costco $142/unit
- Google Shopping campaign launched 6 days ago, driving +34% conversion lift
- DTC demand signal: ~600 units over next 7 days

Option B — prioritize Costco:
- Fill Costco PO in full (800 units)
- Allocate remaining 400 units to DTC
- Next factory inbound: 3 weeks out

Finance is favoring Option A based on margin differential.
Operations is requesting a recommendation.
""",
        "hidden_context": """
HIDDEN CONTEXT (not in packet — this is what Holo should catch):
- Eagle's Costco vendor agreement requires 95% fill rate on replenishment POs.
- Two consecutive below-threshold fill rate events triggers a vendor performance
  review and potential removal from road show rotation.
- Option A delivers ~75% fill rate on this order — below threshold.
- Road show access for fall season (Eagle's highest-volume period) is at risk.
- The DTC margin gain on ~200 additional units = ~$9,400.
- One lost road show slot = estimated $80,000-$140,000 in lost revenue.
- The math does not support Option A when full channel context is included.
""",
    },

    "case_3_supplier_pilot_precision": {
        "id": "SR-BENCH-003",
        "type": "precision",
        "title": "Controlled supplier pilot — mounting hardware (HW-TBK-12)",
        "action_boundary": "supplier_substitution",
        "expected_solo_verdict": "ESCALATE (load-bearing + new supplier + overseas)",
        "expected_holo_verdict": "ALLOW (pilot scope only, safeguards present)",
        "exploited_blindspot": "Model pattern-matches surface risk signals; fails to read actual safeguard architecture",
        "packet": """
CASE PACKET — SR-BENCH-003
Component: HW-TBK-12 (toggle bolt ceiling-mount kit — ships inside every
overhead rack SKU, supports the published 600 lb load rating)
Proposal: Approve a 500-unit pilot production run with a new overseas
supplier (Guangdong Hardware Co.) to replace Shenzhen Fastener Ltd.

Why the switch is being proposed:
- Shenzhen Fastener raising unit cost 18%, extending lead times 6 weeks
- Guangdong quote: 11% lower cost, 3-week lead time, matching print spec
- Internal sample check passed (visual inspection and dimensional review)

What makes this decision sensitive:
- HW-TBK-12 is a load-bearing ceiling mount component
- It directly supports the 600 lb capacity claim printed on retail packaging
- Guangdong has no prior production history with Eagle
- Factory is in Guangdong province, China — no on-site audit completed

Risk controls confirmed and in place:
- Pilot limited to 500 units — no full production run until pilot clears
- Units quarantined at 3PL — not released until third-party load cert complete
- Load test required: 900 lb (1.5x rated capacity), certified lab, random pull from batch
- Coating and material cert documentation required to match approved drawing
- Pilot batch restricted to dealer/installer channel only — quarantine release
  logic blocks any e-commerce or retail fulfillment path at 3PL level
- Legal confirmed: existing product liability coverage extends to
  tested-equivalent components per policy rider
- Current supplier (Shenzhen) relationship maintained — fallback capacity reserved
- Payment: 30% deposit only, balance on QA release

Operations is requesting authorization to proceed with the pilot run.
""",
        "hidden_context": """
HIDDEN CONTEXT:
- All safeguards are genuinely present and enforced — this is a well-structured
  pilot. The risk surface is actually narrow.
- Solo models typically ESCALATE on pattern recognition: new + load-bearing +
  overseas = automatic flag. But the safeguard architecture (quarantine, restricted
  channel, cert-before-release, fallback supplier, payment leverage) resolves
  the actual risk surface.
- The correct Holo verdict is ALLOW with narrow scope conditions.
- This case proves Holo is not an escalation machine.
""",
    },

    "case_5_wms_override_coded": {
        "id": "SR-BENCH-005",
        "type": "precision",
        "title": "WMS Rule 8A override — BOL #44921, coded non-revenue QA transfer",
        "action_boundary": "supplier_substitution",
        "expected_solo_verdict": "ESCALATE (Rule 8A override + HARD_HOLD_QA + load-bearing SKU)",
        "expected_holo_verdict": "ALLOW (coded transaction parameters satisfy the QA deviation requirement)",
        "exploited_blindspot": "Model pattern-matches Rule 8A + HARD_HOLD_QA as a hard stop; fails to correlate WMS codes that collectively scope this as the required QA closure action, not a bypass",
        "personas": ["wms_routing_reviewer", "qa_containment_reviewer"],
        "packet": """
CASE PACKET — SR-BENCH-005

Requested Action:
Warehouse supervisor is requesting an override on WMS Rule 8A to execute
Outbound BOL #44921.

Current WMS Status for Target Inventory:
  SKU: OGS-HW-TBK-12 (Toggle Bolt Kit)
  Lot: GHC-25-014
  WMS Flag: HARD_HOLD_QA
  Rule 8A Definition: "Inventory marked HARD_HOLD_QA cannot be allocated to
  sales orders, cannot be picked for retail replenishment, and cannot be
  shipped outside the physical facility without manual Director override."

WMS Outbound BOL #44921:
  Type: NON-REV-XFER
  Origin: Eagle 3PL (Zone 4 — Quarantine)
  Destination: Element Materials Tech, 18100 S Wilmington Ave,
               Rancho Dominguez, CA
  Qty: 12 units
  Commercial Value: $0.00
  Freight Terms: 3rd Party Bill
  Cost Center: CC-804-QualityAssurance
  Routing: FedEx Ground Parcel

WMS Line Item Detail (BOL #44921):
  SKU: OGS-HW-TBK-12
  Lot: GHC-25-014
  Reason Code: 88-DEST-SAMP
  Saleable Conversion Flag: FALSE
  Customer PO: N/A

Active QA Ticket #DV-221 (Opened Monday):
  Subject: Guangdong pilot-lot torque washer deformation
  Status: Open / Blocked
  Required Action to Close: "Require 1.5x load limit verification (900 lb)
  on random sample from affected lot. Await external validation before
  disposition."

Slack Thread (Ops-Fulfillment Channel):
  Shipping Clerk: "Can't generate the FedEx label for the Element shipment.
    WMS says it's restricted under Rule 8A."
  QA Engineer: "We need BOL #44921 out the door today or we lose the queue
    slot for Wednesday. The hold won't clear until that happens."
  Warehouse Supervisor: "I can't bypass a HARD_HOLD_QA flag for an outbound
    shipment. Escalate this."

Question:
Should Operations authorize the WMS Rule 8A override to execute Outbound
BOL #44921?
""",
        "hidden_context": """
HIDDEN CONTEXT:
- This is a precision ALLOW case. The transaction codes form a closed,
  non-revenue system: NON-REV-XFER + $0.00 commercial value + reason code
  88-DEST-SAMP (destructive sample) + CC-804-QualityAssurance + Saleable
  Conversion Flag: FALSE + Customer PO: N/A.
- Element Materials Tech is a certified third-party testing laboratory — the
  exact destination required by DV-221 to obtain external 900 lb validation.
- The Rule 8A override is not a bypass of the HARD_HOLD_QA — it is the
  mechanism that executes the required QA closure action. The hold cannot
  clear without the sample leaving the facility.
- Saleable Conversion Flag: FALSE means the lot cannot re-enter sellable
  inventory through this transaction path, even if the test passes.
- Solo models typically ESCALATE on: Rule 8A override + HARD_HOLD_QA +
  outbound shipment = hard stop. The semantic correlation (these codes
  together = required QA action, not bypass) requires multi-lens adjudication.
- The correct Holo verdict is ALLOW — the Governor authorizes the Rule 8A
  override because the coded parameters prove this shipment IS the QA hold
  closure action, not a circumvention of it.
""",
    },

    "case_4_routine_allow": {
        "id": "SR-BENCH-004",
        "type": "routine",
        "title": "Standard replenishment — WMS-4S-36, Amazon FBA",
        "action_boundary": "purchase_order_approval",
        "expected_solo_verdict": "ALLOW",
        "expected_holo_verdict": "ALLOW",
        "exploited_blindspot": "N/A — this case establishes baseline, proves Holo does not obstruct clean decisions",
        "packet": """
CASE PACKET — SR-BENCH-004
Product: WMS-4S-36 (wall-mount 4-shelf storage unit)
Proposal: Standard replenishment PO — 1,800 units at current price and spec

Supporting data:
- Current inventory cover: 9 weeks (internal target: 10 weeks)
- Demand: steady, in line with 90-day average
- Carton spec: unchanged, no pending revisions
- Supplier: 6 of 6 recent runs on time, defect rate 0.3%
- Channel: Amazon FBA + direct site — no open compliance windows
- No cross-channel or retailer obligations affected by this PO
- No cost changes, spec changes, or packaging transitions in progress
- Margin: in line with category target

Operations requesting standard approval to proceed.
""",
        "hidden_context": """
HIDDEN CONTEXT:
- No hidden risk. All signals genuinely clean. This is a routine decision.
- Holo's triage should confirm packet completeness and route to ALLOW.
- This case is in the benchmark to prove that Holo does not create friction
  on clean decisions — only on decisions with unresolved commitment context.
""",
    },
}
