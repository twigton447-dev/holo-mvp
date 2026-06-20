# D4 Source Packet: AP / Procurement / Vendor Risk

Packet ID: `d4_ap_procurement_vendor_risk_001`
Frozen at: `2026-06-20T22:55:45Z`

Contestants may not browse. Use only these frozen excerpts and the task brief.

## S1_FBI_IC3_2024_BEC_LOSSES: 2024 Internet Crime Report

- Publisher: Federal Bureau of Investigation Internet Crime Complaint Center (IC3)
- Date: 2025-04-23
- URL/Citation: https://www.ic3.gov/AnnualReport/Reports/2024_IC3Report.pdf
- Source type: authoritative_fraud_bec_quantitative
- Strength classification: strong
- Recency status: current_authoritative_report
- Source hash: `328e28961226439896d464b98de5858e85d4f65ee25cdad8bef2560611632194`

Excerpt: The 2024 IC3 report records 859,532 complaints and reported losses of $16.6 billion. It lists Business Email Compromise as 21,442 complaints and $2,770,151,146 in reported losses, and states IC3 Recovery Asset Team activity often involves BEC-related Financial Fraud Kill Chain requests.

Limitations: IC3 data reflects reported complaints and losses; it is not proof that any specific vendor request is fraudulent, and underreporting or categorization limits can affect interpretation.

Use note: Use to frame BEC/payment-redirection risk and quantify general exposure. Do not treat general BEC prevalence as evidence that this specific supplier request is fraudulent.

## S2_NACHA_WEB_DEBIT_ACCOUNT_VALIDATION_2021: Supplementing Fraud Detection Standards for WEB Debits

- Publisher: Nacha
- Date: 2021-03-19
- URL/Citation: https://www.nacha.org/rules/supplementing-fraud-detection-standards-web-debits
- Source type: ach_payment_control_rule_guidance
- Strength classification: useful_normal
- Recency status: older_rule_guidance_still_relevant_to_account_validation_concepts
- Source hash: `6bc88d91702aa9827bcab684077cf5b0a86a613af89e1a7407ef765777db365e`

Excerpt: Nacha says the WEB Debit Account Validation Rule made account validation explicit as part of a commercially reasonable fraud-detection system for first use of an account number or account-number changes. The FAQ notes the minimum standard validates that an account is open and can accept ACH entries, not necessarily account ownership; more rigorous validation may be appropriate depending on risk.

Limitations: This specific rule is for WEB debit entries, not every corporate payable or wire transfer. It supports account-validation logic, but does not by itself define the full control path for this crisis payment.

Use note: Use to reason about account-change validation and limits. Do not claim it automatically proves a supplier bank-account change is safe or unsafe.

## S3_OFAC_COMPLIANCE_FRAMEWORK_2019: A Framework for OFAC Compliance Commitments

- Publisher: U.S. Department of the Treasury Office of Foreign Assets Control
- Date: 2019-05-02
- URL/Citation: https://ofac.treasury.gov/media/16331/download?inline
- Source type: sanctions_restricted_party_compliance_framework
- Strength classification: strong
- Recency status: authoritative_framework_older_but_currently_cited
- Source hash: `3824a86e8b230b9b1f1fedd0b91e5c105c64d948156dcc1b818b0c22bb7c94be`

Excerpt: OFAC encourages a risk-based sanctions compliance program with five essential components: management commitment, risk assessment, internal controls, testing and auditing, and training. The framework says risk assessments should consider customers, supply chain, intermediaries, counterparties, products/services, and geographic locations, while internal controls should identify, interdict, escalate, report, and keep records for potentially prohibited activity.

Limitations: This framework is general sanctions-compliance guidance. It does not identify the vendor in this packet as sanctioned and does not replace actual restricted-party screening.

Use note: Use to require sanctions/restricted-party screening and escalation before payment release. Do not infer a sanctions hit absent evidence.

## S4_NIST_C_SCRM_800_161R1_UPD1: Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations, NIST SP 800-161r1-upd1

- Publisher: National Institute of Standards and Technology
- Date: 2024-11-01 update to May 2022 publication
- URL/Citation: https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final
- Source type: procurement_vendor_supply_chain_risk_guidance
- Strength classification: strong
- Recency status: current_authoritative_update
- Source hash: `bc4202ef00a8f7db9765e0c9dae0a9bfa5e0147f16b5326e652da53ee07db0c9`

Excerpt: NIST describes supply-chain risks from malicious functionality, counterfeit products, vulnerabilities, and poor development or manufacturing practices. It frames reduced visibility into how acquired products and services are developed, integrated, deployed, and assured as a core supply-chain risk, and provides guidance for identifying, assessing, and mitigating C-SCRM risks throughout the organization.

Limitations: NIST C-SCRM is broader than AP payment release; it supports vendor/procurement risk analysis but does not answer whether this invoice should be paid today.

Use note: Use to evaluate supplier criticality, vendor assurance, and procurement risk. Do not turn it into a generic cybersecurity essay.

## S5_GAO_FRAUD_RISK_FRAMEWORK_2015: A Framework for Managing Fraud Risks in Federal Programs

- Publisher: U.S. Government Accountability Office
- Date: 2015-07-28
- URL/Citation: https://www.gao.gov/products/gao-15-593sp
- Source type: fraud_internal_control_framework_stale_tempting
- Strength classification: stale_tempting
- Recency status: older_authoritative_context_not_current_payment_rule
- Source hash: `d2679c0873280ee3f06af57cda95afb6510d0125de68fb3a71da39eeaf911d5b`

Excerpt: GAO describes a fraud-risk framework with components to commit, assess, design and implement, and evaluate and adapt. It emphasizes preventive control activities, fraud-risk assessment, response planning, monitoring, and feedback.

Limitations: The framework is older and designed for federal programs. It is useful control context but should not override current payment, sanctions, or vendor-screening evidence.

Use note: Use as background for fraud-control discipline. Do not cite it as a current AP payment-rule authority.

## S6_NACHA_COMMON_SCAMS_2025: Watch Out! Common Scams That Can Steal Your Money

- Publisher: Nacha
- Date: 2025-06-12
- URL/Citation: https://www.nacha.org/content/watch-out-common-scams-can-steal-your-money
- Source type: payments_fraud_practitioner_awareness
- Strength classification: useful_normal
- Recency status: recent_practitioner_awareness_source
- Source hash: `959effe3695399cea3123a21f1b9b4694c8de3ab72689c247467ec549d0d87ce`

Excerpt: Nacha warns that phishing messages can impersonate trusted companies, that imposter scams use urgency to pressure payment, and that deepfake scams can imitate a familiar boss or person. It advises checking addresses carefully and double-checking urgent requests by calling through a known channel.

Limitations: This is broad scam-awareness guidance, not a corporate AP control standard and not case-specific proof of fraud.

Use note: Use to recognize urgency and impersonation pressure. Do not use it as the sole basis to reject a critical supplier payment.

## S7_GUARDIAN_RED_SEA_MANUFACTURING_DISRUPTION_2024: UK manufacturers hit by Red Sea disruption and rising shipping costs

- Publisher: The Guardian
- Date: 2024-02-01
- URL/Citation: https://www.theguardian.com/business/2024/feb/01/uk-manufacturers-hit-by-red-sea-disruption-and-rising-shipping-costs
- Source type: operational_continuity_complicating_news_source
- Strength classification: contradictory_or_complicating
- Recency status: recent_news_context
- Source hash: `ea3108b86857943ec0112f8341205f28753c0d76d90d701e11e51f23557aa0ca`

Excerpt: The report describes manufacturers facing shipping delays and higher costs from Red Sea disruption, with supply-chain difficulties pressuring production and purchasing decisions.

Limitations: This is news context, not evidence about the specific vendor or payment request. It supports operational pressure, not bypassing fraud/sanctions controls.

Use note: Use to explain why delay has real costs. Do not treat continuity pressure as automatic approval authority.

## S8_TECHRADAR_AI_INVOICE_FRAUD_2026: How AI is changing the fight against invoice fraud

- Publisher: TechRadar Pro
- Date: 2026-06-12
- URL/Citation: https://www.techradar.com/pro/how-ai-is-changing-the-fight-against-invoice-fraud
- Source type: weak_limited_secondary_explainer
- Strength classification: weak_or_limited
- Recency status: current_secondary_vendor_adjacent_article
- Source hash: `995bce85bc61665e82deb3058097361c25e9e4ec31c88495b74fc9f52a9aa76a`

Excerpt: The article says invoice fraud can involve subtle anomalies such as changed bank details or unusual timing, and argues that disconnected/manual controls may miss patterns while speed matters after payment initiation.

Limitations: This is a secondary technology/business article, not an authority, rule, audit standard, or case-specific proof. It should not carry the decision.

Use note: Use only as a weak prompt about modern invoice-fraud patterns. Stronger authority must come from FBI, Nacha, OFAC, NIST, and GAO sources.

## S9_DERIVED_D4_DECISION_PRESSURE_TABLE: Decision Pressure Table: Urgent Supplier Payment, Account-Change, and Vendor-Risk Controls

- Publisher: Packet author derived from frozen public-source excerpts
- Date: 2026-06-20
- URL/Citation: Derived table inside frozen packet; not an independent public source.
- Source type: packet_derived_table_chart_stat_element
- Strength classification: table_chart_stat_element
- Recency status: derived_from_current_packet_sources
- Source hash: `e1f09b4c4e76b359721b61178291c1c7887aaf3971bf02d8fcc68ed5e8f99658`

Excerpt: Derived from S1-S8: BEC losses show major background exposure; Nacha/OFAC/NIST/GAO support control steps; Red Sea/news context supports continuity pressure; weak TechRadar source only supports awareness of invoice-fraud patterns.

Limitations: This table is an interpretation aid built from the frozen sources. It is not an independent fact source and should not be cited as external authority.

Use note: Use to compare evidence pressure, but verify the underlying source IDs and do not let the table replace source-specific reasoning.

| Decision issue | Supporting source IDs | What it supports | What it does not support |
|---|---|---|---|
| Payment-redirection/BEC background risk | S1_FBI_IC3_2024_BEC_LOSSES | BEC is a high-loss reported cyber-enabled fraud category; 2024 BEC reported losses were about $2.77B. | Does not prove this supplier request is fraudulent. |
| Account-change control | S2_NACHA_WEB_DEBIT_ACCOUNT_VALIDATION_2021, S6_NACHA_COMMON_SCAMS_2025 | Account changes and urgent requests warrant independent validation and known-channel confirmation. | Does not prove account ownership or approve a payment by itself. |
| Sanctions/vendor screening | S3_OFAC_COMPLIANCE_FRAMEWORK_2019 | Risk-based sanctions compliance, internal controls, escalation, and records are relevant before release. | Does not identify a sanctions hit unless actual screening evidence exists. |
| Supplier/procurement continuity | S4_NIST_C_SCRM_800_161R1_UPD1, S7_GUARDIAN_RED_SEA_MANUFACTURING_DISRUPTION_2024 | Supplier disruption can create real operational consequences, so delay has costs. | Does not justify overriding fraud, sanctions, or bank-change controls. |
| Weak/limited modern fraud context | S8_TECHRADAR_AI_INVOICE_FRAUD_2026 | Modern invoice fraud can be subtle and time-sensitive. | Does not establish a control standard or case-specific finding. |
