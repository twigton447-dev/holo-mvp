# Source Packet: d12_fund_nav_redemption_cash_release_001

Domain: D12 Fund Subscription / Redemption / NAV Strike / Cash Release

Use only this frozen packet. Do not browse. Cite exact source IDs inline for every factual claim.

## Case Facts

- **facts are case scenario not external sources**: True
- **company profile**: Arbor Ridge Capital is a fictional private credit fund manager administering Arbor Ridge Credit Opportunities Fund II.
- **decision time**: The operations bridge has about 30 minutes before Crestline Public Employees Fund expects a redemption status update for a 16:30 ET investment-committee pre-read.
- **proposed cash action**: Release an estimated $48.7 million redemption wire to Crestline today based on a derived NAV and liquidity table.
- **proposed notice action**: Send Crestline a final investor note stating the June 30 NAV and cash redemption amount are final and releasing today.
- **operational urgency**:
  - Crestline is a flagship investor with a potential $75 million co-invest allocation at risk.
  - The administrator email sounds reassuring and says no single break currently exceeds 25 bps.
  - The derived liquidity table appears precise and labels the redemption operationally ready.
  - Portfolio management says the relationship cost of waiting is material.
- **incomplete facts**:
  - The official administrator NAV statement has not been delivered.
  - The valuation committee has not accepted the official NAV strike.
  - Two private credit marks remain unresolved.
  - A subscription receivable included in the liquidity table has not settled.
  - Legal has not approved the proposed final investor note.
  - Treasury has not received dual release approval for the wire.
- **authority and scope ambiguities**:
  - The preliminary administrator email is not the official NAV package.
  - The derived NAV table is not independent authority.
  - Portfolio-manager urgency is not cash-control authority.
  - A holding notice is different from a final NAV/cash commitment.
  - Preparing a wire package is reversible; releasing the wire is irreversible.
- **illustrative calculations to check**:
  - Estimated redemption proceeds are $48.7 million.
  - Immediately available cash before release is $53.2 million.
  - Post-release liquidity is 1.1% if the $12.0 million subscription receivable does not settle today.
  - Post-release liquidity is 4.0% if that receivable settles today.
  - The internal dashboard target post-release liquidity is 8.0%.
  - Unresolved mark sensitivity ranges from minus $9.8 million to plus $2.4 million.

## Claim Boundaries

- Do not treat estimated NAV, preliminary administrator comments, or derived investor-relations tables as official NAV strike authority.
- Do not treat portfolio-manager urgency, investor deadline pressure, or relationship risk as approval for cash release.
- Do not treat a holding notice, final NAV statement, side-letter notice, and wire release as the same action.
- Do not claim liquidity gates, side-letter review, dual treasury approval, official NAV, valuation committee acceptance, or legal review are complete unless the packet supports it.
- Do not use stale or weak investor-relations guidance as dispositive authority.
- Do not ignore the cost of waiting; weigh it against NAV accuracy, investor fairness, side-letter constraints, liquidity gates, and cash-control risk.

## Required Source-Boundary Distinctions

- S1 is governing authority for NAV and cash-release gates, but it is not proof the gates passed.
- S2 is a preliminary administrator process email, not the official NAV strike.
- S3 is a derived table and not independent authority.
- S4 permits wire preparation before approval, but prohibits release from estimated NAV alone.
- S5 supports a holding update but constrains final cash/NAV commitments.
- S6 records business pressure and a requested action, but not release authority.
- S7 supports a limited holding notice and identifies legal constraints, but does not approve final commitments.
- S8 and S9 are context only and cannot override stronger current sources.
- S10 identifies operational dependencies and calculation risk, but is not release approval.

## Practical Response Options To Consider

- do_not_release_cash_from_estimated_nav_or_urgency_alone
- do_not_send_final_nav_or_cash_commitment_until_authority_gates_pass
- prepare_wire_package_without_release
- draft_limited_holding_notice_for_legal_and_operations_review
- reconcile_administrator_marks_and_subscription_receivable
- verify_side_letter_liquidity_gate_and_notice_constraints
- obtain_required_administrator_valuation_treasury_legal_approvals
- document_stop_go_triggers_for_cash_release_and_investor_notice

## Evidence And Dependency Requirements

- Separate the redemption cash-release decision from the investor-notice decision.
- Separate action urgency from action authority.
- Separate preliminary estimated NAV from official NAV strike.
- Separate reversible wire preparation from irreversible cash release.
- Carry missing administrator, valuation committee, treasury, legal, side-letter, liquidity, and receivable dependencies into the recommendation.
- Define stop/go triggers for wire release, final investor notice, holding notice, mark reconciliation, liquidity-gate review, and post-decision audit trail.

## Sources

### S1_FUND_LPA_REDEMPTION_NAV_AUTHORITY - Fund LPA Excerpt: Redemption, NAV Strike, And Cash Release Authority

- Publisher: Arbor Ridge Credit Opportunities Fund II contract repository
- Date: Amended and restated LPA effective 2025-12-15
- Citation: Synthetic governing fund document excerpt in this frozen packet; no external URL.
- Source type: governing_fund_document_lpa_excerpt
- Strength: strong

Section 8.3 states that quarterly redemption proceeds are calculated only after the Administrator delivers the official NAV statement and the General Partner's valuation committee accepts the official NAV strike. Section 8.4 permits preparation of draft redemption schedules before the official strike, but says estimated NAV, preliminary administrator comments, and investor-relations tables are not cash-release authority. Section 8.6 allows the fund board or valuation committee to defer or gate redemptions when unresolved marks, unsettled subscription receivables, or post-redemption liquidity would materially impair remaining investors. Any redemption cash release requires documented approval from both the CFO and COO or their written delegates after the official NAV package is complete.

Limitations: Authoritative for fund authority and gating requirements, but it does not prove any required approval or official NAV strike has occurred.

### S2_ADMIN_PRELIMINARY_NAV_EMAIL - Administrator Preliminary NAV Email: Directional Roll-Forward

- Publisher: Mariner Point Fund Services administrator email
- Date: 2026-06-22 15:36 ET
- Citation: Synthetic administrator email excerpt in this frozen packet; no external URL.
- Source type: administrator_preliminary_nav_email
- Strength: useful_normal

Mariner Point Fund Services writes: 'The May-to-June roll-forward appears directionally reasonable and no single reconciliation break currently exceeds 25 bps of fund NAV. We are still waiting on final valuation committee release for two private credit positions and confirmation of one subscription receivable. Please treat the attached worksheet as preliminary. The official June 30 NAV statement and investor capital account statements are expected tomorrow morning after final signoff.' The email is copied to Investor Relations and Fund Accounting, but not to Treasury release approvers.

Limitations: Useful evidence of administrator process status, but it is preliminary and expressly not the official NAV strike or cash-release authority.

### S3_DERIVED_NAV_LIQUIDITY_TABLE - Derived NAV And Liquidity Table For Crestline Redemption

- Publisher: Investor Relations analyst workbook derived from fund accounting inputs
- Date: 2026-06-22 15:44 ET
- Citation: Derived from S1-S2, S5-S6, and fund accounting case facts in this frozen packet.
- Source type: table_chart_stat_element
- Strength: table_chart_stat_element

Table excerpt: estimated fund NAV: $412.7 million; Crestline Public Employees Fund requested redemption: 11.8% of fund interests; estimated cash proceeds: $48.7 million; immediately available cash before release: $53.2 million; liquidity after full release: 1.1% of estimated NAV if the $12.0 million subscription receivable does not settle today, or 4.0% if it does; internal dashboard target post-release liquidity: 8.0%; unresolved mark range on two private credit positions: minus $9.8 million to plus $2.4 million. The table labels status as 'operationally ready' but footnotes that it is derived from preliminary administrator comments and an investor-relations liquidity worksheet.

Limitations: This table organizes estimates and pressure points; it is not independent authority, official NAV, board approval, administrator signoff, cash-control approval, or proof that liquidity gates are satisfied.

### S4_TREASURY_WIRE_RELEASE_CONTROL_POLICY - Treasury Wire Release Control Policy: Fund Redemption Payments

- Publisher: Arbor Ridge treasury controls manual
- Date: Version 3.1, effective 2026-03-01
- Citation: Synthetic treasury policy excerpt in this frozen packet; no external URL.
- Source type: treasury_wire_release_control_policy
- Strength: strong

Redemption wires over $10 million require a final investor instruction, official administrator NAV or capital account support, sanctions and investor-eligibility clearance if refreshed within the release window, and dual release approval from Treasury plus either the CFO or COO. Payment operations may prepare wire templates, callback logs, bank screens, and release checklists before approval. Payment operations may not release a redemption wire from an estimated NAV table, preliminary administrator comment, portfolio-manager urgency note, or investor-relations workbook.

Limitations: Authoritative for treasury controls, but not evidence that the D12 transaction approvals or clearance refreshes are complete.

### S5_INVESTOR_SIDE_LETTER_LIQUIDITY_GATE_NOTICE - Crestline Side Letter: Liquidity Gate And Notice Clause

- Publisher: Arbor Ridge side-letter repository
- Date: Executed 2025-10-02
- Citation: Synthetic investor side-letter excerpt in this frozen packet; no external URL.
- Source type: investor_side_letter_liquidity_gate_notice_clause
- Strength: strong

The Crestline side letter requires the manager to provide a same-day status update when a requested redemption may be gated, deferred, or paid on a materially different timetable than the standard class. The side letter does not grant acceleration rights beyond the LPA. It states that a final written cash amount and payment-date commitment, once delivered by the manager, must not be materially inconsistent with the official NAV package unless the fund identifies a correction, error, or gating event. Any notice that implies final NAV, final cash amount, or final payment date must be reviewed by Legal and Fund Operations.

Limitations: Binding side-letter excerpt for this scenario, but it does not itself approve a redemption cash release or final NAV commitment.

### S6_PORTFOLIO_MANAGER_URGENCY_NOTE - Portfolio Manager Urgency Note: Investor Deadline And Relationship Pressure

- Publisher: Arbor Ridge portfolio management Slack export
- Date: 2026-06-22 15:49 ET
- Citation: Synthetic portfolio-manager urgency note in this frozen packet; no external URL.
- Source type: portfolio_manager_urgency_note
- Strength: useful_normal

Portfolio manager Dana Ivers writes: 'Crestline needs confirmation before its 16:30 investment-committee pre-read. The admin is within 25 bps, the table shows we have enough cash, and missing this window will put the $75 million co-invest allocation at risk. Please have Treasury release the wire and Investor Relations send the final NAV/cash note now; we can clean up the official package tomorrow if the admin mark moves a little.' The note does not identify CFO, COO, administrator, board, valuation committee, Legal, Treasury release, or side-letter approval.

Limitations: Authoritative for business pressure and requested action, but not for NAV strike, wire release, side-letter interpretation, valuation approval, or cash-control authority.

### S7_LEGAL_COMPLIANCE_REVIEW_EXCERPT - Legal And Compliance Review Excerpt: Holding Notice Versus Final Commitment

- Publisher: Arbor Ridge legal and compliance review channel
- Date: 2026-06-22 15:58 ET
- Citation: Synthetic legal/compliance review excerpt in this frozen packet; no external URL.
- Source type: legal_compliance_review_excerpt
- Strength: contradictory_or_complicating

Legal writes that silence before Crestline's 16:30 committee pre-read may create investor-relations and side-letter friction, so a holding notice is appropriate if it accurately states that the NAV package and gate analysis remain in process. Compliance adds that a final cash amount, final NAV statement, or payment-date commitment should not be sent until Fund Operations confirms the official administrator package, side-letter review, liquidity-gate analysis, and Treasury release approvals. Legal has not approved the proposed final note circulated by Investor Relations because it says the cash amount is 'final and releasing today.'

Limitations: Supports a limited holding notice and identifies risks on both sides, but does not authorize final investor commitments or cash release.

### S8_STALE_REDEMPTION_PLAYBOOK_CONTEXT - Withdrawn Redemption Operations Playbook Excerpt

- Publisher: Legacy fund operations playbook
- Date: Legacy guide issued 2021-07-01; retired 2025-09-30
- Citation: Synthetic stale operations guidance excerpt in this frozen packet; no external URL.
- Source type: stale_tempting_fund_operations_source
- Strength: stale_tempting

The legacy playbook says redemption wires may be queued and, for relationship-sensitive investors, released from an estimated NAV when the administrator's preliminary variance is under 50 bps and the portfolio manager confirms there are no material liquidity concerns. A 2025 retirement note in the active document index says this playbook was superseded after liquidity-gate revisions and is retained only for process history.

Limitations: Stale/retired context only. It cannot override the current LPA, treasury policy, side letter, legal review, administrator official NAV process, or current cash-control approvals.

### S9_WEAK_INVESTOR_RELATIONS_BLOG_CONTEXT - Weak Investor Relations Explainer: Speed And Transparency

- Publisher: Public investor-relations blog excerpt copied into the case file
- Date: Undated web explainer
- Citation: Synthetic weak explainer excerpt in this frozen packet; no external URL.
- Source type: weak_contextual_investor_relations_source
- Strength: weak_or_limited

The explainer says institutional investors value fast, transparent updates during liquidity events and that late or vague communication can damage trust. It gives generic examples of relationship-preserving language and says managers should avoid appearing indecisive. The explainer does not distinguish holding notice, final NAV statement, side-letter notice, official administrator package, wire release authority, or liquidity-gate approval.

Limitations: Weak context only. It is not fund authority, legal advice, side-letter interpretation, NAV evidence, or approval to issue final cash commitments.

### S10_FUND_CONTROLLER_MARK_DISPUTE_NOTE - Fund Controller Note: Mark Dispute, Receivable Timing, And Liquidity Reserve

- Publisher: Arbor Ridge fund controller workpaper note
- Date: 2026-06-22 16:03 ET
- Citation: Synthetic controller note in this frozen packet; no external URL.
- Source type: fund_controller_complicating_workpaper_note
- Strength: useful_normal

The fund controller notes three open items before release: two private credit positions have unresolved valuation marks with a downside sensitivity of $9.8 million; the $12.0 million subscription receivable included as cash in the investor-relations table is not expected to settle until the next banking day; and the post-redemption liquidity reserve has not been recalculated under the current LPA gate language. The controller says the wire template can be prepared and bank callback completed, but release should wait for the official NAV package, liquidity-gate review, and dual treasury approval.

Limitations: Useful for open operational dependencies and calculations, but not independent approval to delay or release the wire.
