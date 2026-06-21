# D2 Oil & Gas / Middle East JV Accounting Source Packet

Status: frozen source packet. No browsing. Use only this packet and the task brief.

## Case Facts

- **facts_are_case_scenario_not_external_sources**: true
- **company_profile**: "A fictional U.S.-linked public energy company holds a 35% equity-method interest in a Middle East oil and gas joint venture through a non-operated affiliate."
- **decision_time**: "Audit committee, CFO, legal, treasury, and regional operations must decide this week whether normal JV accounting/economic treatment can continue or whether controls, accounting judgments, disclosures, and cash movement should change."
- **current_jv_exposure**: ["JV carrying amount on the parent balance sheet: $480 million.", "Parent share of pending JV distribution: $26.25 million, based on a $75 million gross distribution approved locally but not yet remitted.", "Gross JV local cash balance reported by operator: $120 million equivalent; parent share at 35% is $42 million before withholding, bank charges, or FX/repatriation effects.", "Gross production averaged 42,000 boe/day last quarter; current operator flash report says 38,600 boe/day, or about 92% of prior-quarter average.", "One regional service contractor on the JV vendor list has incomplete beneficial-ownership refresh; no SDN match is documented in the packet, but screening is not complete."]
- **geopolitical_and_cash_pressure**: ["Regional shipping disruption has delayed two cargo liftings by 18 days and increased demurrage estimates, but cargoes are not cancelled in the packet.", "Local bank has delayed USD conversion/repatriation for the approved distribution pending compliance documentation.", "Operations says pausing all JV spending could reduce production below 80% within 30 days; legal says distribution release should wait for sanctions/export-control sign-off.", "Investor relations expects questions about Middle East exposure on the next earnings call."]
- **not_provided**: ["No complete JOA or PSA clause text is provided.", "No legal opinion that sanctions prohibit the JV, distribution, bank, cargo, contractor, or commodity flow.", "No completed export-control classification for U.S.-origin equipment or technical services.", "No independent reserve-engineering update after the disruption.", "No recoverable-amount calculation, discount-rate update, or board-approved impairment conclusion.", "No confirmation that the pending distribution is legally trapped or permanently unrecoverable."]
- **illustrative_calculations_to_check**: ["Parent share of the $75 million pending distribution is $26.25 million.", "Parent share of $120 million gross local JV cash is $42 million before withholding, bank charges, and FX/repatriation effects.", "A 9% FX/repatriation haircut on $42 million would be $3.78 million; this sensitivity does not prove realized loss.", "Production drop from 42,000 to 38,600 boe/day is 3,400 boe/day, or about 8.1%; parent 35% share of the gross drop is about 1,190 boe/day.", "A 12% impairment sensitivity on the $480 million carrying amount equals $57.6 million, but impairment requires a recoverable-amount analysis and cannot be concluded from this sensitivity alone.", "FRED Brent data in this packet show a drop from $97.46 on 2026-06-08 to $84.36 on 2026-06-15, a decline of about 13.4%; this is market context, not JV-specific realized price."]

## Claim Boundaries

- Do not claim a sanctions breach unless the packet gives a prohibited party, blocked transaction, legal opinion, or completed screening result.
- Do not claim export-control violation unless equipment, technology, service, destination, end use, and license status are established.
- Do not claim automatic impairment from regional disruption, oil-price volatility, or delayed cash repatriation alone.
- Do not treat FX/repatriation friction as realized cash loss or permanent trapping unless supported by evidence.
- Do not invent JOA, PSA, concession, covenant, reserve, tax, royalty, or partner-default terms absent from the packet.
- Do not give legal, accounting, audit, tax, sanctions, export-control, investment, or trading advice; write an internal decision brief under uncertainty.

## Frozen Sources

### S1_OFAC_COMPLIANCE_FRAMEWORK_2019: A Framework for OFAC Compliance Commitments
- Publisher: U.S. Department of the Treasury, Office of Foreign Assets Control
- Date: 2019-05-02
- URL/Citation: https://ofac.treasury.gov/media/16331/download?inline
- Source type: authoritative_sanctions_compliance_source
- Strength classification: strong
- Source hash: 36e259af744b17ef8a5fe30dee272cb9949c655a25f436ce29cd1e5afcde0dca

Excerpt:
OFAC says it administers and enforces U.S. economic and trade sanctions programs and strongly encourages organizations subject to U.S. jurisdiction, and foreign entities doing business in or with the United States or U.S.-origin goods or services, to use a risk-based sanctions compliance program. The framework names five essential components: management commitment, risk assessment, internal controls, testing and auditing, and training. It also says risk assessment should consider customers, supply chain, intermediaries, counterparties, products and services, and geographic locations.

Limitations:
Authoritative sanctions-compliance framework, but it is not a legal opinion on this fictional JV and does not identify any case-specific prohibited party or blocked transaction.

### S2_BIS_EXPORT_CONTROL_CONTEXT_2026: Bureau of Industry and Security Homepage / Export Control Resources
- Publisher: U.S. Department of Commerce, Bureau of Industry and Security
- Date: Accessed 2026-06-21
- URL/Citation: https://www.bis.gov/
- Source type: export_control_context_source
- Strength classification: useful_normal
- Source hash: 4c5f99a86790d476fde2ae2c2478a1ff0146effcefcb3b5cea49da4c9ecc198e

Excerpt:
BIS describes its mission as advancing U.S. national security, foreign policy, and economic objectives through an effective export-control and treaty-compliance system. Its homepage links to Export Administration Regulations, classification, country guidance, the Consolidated Screening List, licensing, end-use and end-user controls, and Export Compliance Programs.

Limitations:
Useful for export-control workflow context only. It does not classify any specific equipment, software, service, technical data, destination, or counterparty in the fictional JV.

### S3_EIA_STEO_JUNE_2026_HORMUZ_DISRUPTION: Short-Term Energy Outlook - June 2026
- Publisher: U.S. Energy Information Administration
- Date: 2026-06-09
- URL/Citation: https://www.eia.gov/outlooks/steo/
- Source type: authoritative_energy_market_geopolitical_disruption_source
- Strength classification: strong
- Source hash: 0088d61fbc814e69fa8d328378d57d17a92111712713378fe2a34d1d0bc8e6e4

Excerpt:
EIA June 2026 STEO says its forecast assumes the Strait of Hormuz remains effectively closed in the near term, oil shipments through the strait resume in 3Q26, and ramp-up to pre-conflict traffic likely takes several months. EIA says very limited shipping traffic through the strait caused Middle East producers to reduce crude oil production by more than 11 million barrels per day in May compared with pre-conflict levels, creating large global inventory draws.

Limitations:
Authoritative market disruption context, but it does not identify this fictional JV, its country, its cargo route, its contract rights, or any legal prohibition.

### S4_IFRS_IAS28_EQUITY_METHOD_JV: IAS 28 Investments in Associates and Joint Ventures
- Publisher: IFRS Foundation
- Date: Standard page issued 2026
- URL/Citation: https://www.ifrs.org/issued-standards/list-of-standards/ias-28-investments-in-associates-and-joint-ventures/
- Source type: jv_equity_method_accounting_source
- Strength classification: strong
- Source hash: 1aabd5223c630f17efad68458fabf1afd742659011b8a333c4f7c15a0ceb083b

Excerpt:
The IFRS Foundation summary says IAS 28 requires an investor to account for investments in associates using the equity method, and IFRS 11 requires equity-method accounting for investments in joint ventures with limited exceptions. It says an associate is an entity over which the investor has significant influence, while a joint venture is a joint arrangement where parties with joint control have rights to net assets. Under the equity method, the investment is initially recognized at cost, then adjusted for the investors share of subsequent profit or loss, and distributions received reduce the carrying amount.

Limitations:
Authoritative IFRS summary for equity-method mechanics, but the packet does not state whether the fictional parent reports under IFRS or U.S. GAAP and does not provide full JOA/PSA or control analysis.

### S5_IFRS_IAS36_IMPAIRMENT_BOUNDARY: IAS 36 Impairment of Assets
- Publisher: IFRS Foundation
- Date: Standard page issued 2026
- URL/Citation: https://www.ifrs.org/issued-standards/list-of-standards/ias-36-impairment-of-assets/
- Source type: oil_gas_accounting_impairment_boundary_source
- Strength classification: contradictory_or_complicating
- Source hash: fa0176b5f58f6ea5585c214db843b1740f057da997a94069e0ece5dc43d899aa

Excerpt:
The IFRS Foundation summary says IAS 36s core principle is that an asset must not be carried above the highest amount recoverable through use or sale. If carrying amount exceeds recoverable amount, the asset is impaired and must be reduced to recoverable amount. For assets other than goodwill and certain intangibles, recoverable amount is assessed when there is an indication that the asset may be impaired. Recoverable amount is the higher of fair value less costs to sell and value in use.

Limitations:
This source creates a boundary against automatic impairment. It does not provide the fictional JVs recoverable amount, discount rate, reserve update, fair value, or value-in-use model.

### S6_IFRS_IAS21_FX_AND_LACK_OF_EXCHANGEABILITY: IAS 21 The Effects of Changes in Foreign Exchange Rates
- Publisher: IFRS Foundation
- Date: Standard page issued 2026
- URL/Citation: https://www.ifrs.org/issued-standards/list-of-standards/ias-21-the-effects-of-changes-in-foreign-exchange-rates/
- Source type: fx_currency_translation_and_repatriation_risk_source
- Strength classification: useful_normal
- Source hash: 46f43310e74eec12ce1e2c431e89ad8006aa0414b110a787f46abaf85303e95e

Excerpt:
The IFRS Foundation summary says IAS 21 prescribes how to account for foreign currency transactions, translate financial statements of a foreign operation into the entitys functional currency, and translate financial statements into a presentation currency. It identifies the principal issues as which exchange rates to use and how to report exchange-rate effects. The page also notes 2023 amendments on lack of exchangeability, requiring a consistent approach to assessing whether a currency is exchangeable and, if not, determining the exchange rate and disclosures.

Limitations:
Useful for FX and repatriation accounting discipline, but not proof that the fictional local currency is non-exchangeable or that a pending distribution is permanently trapped.

### S7_SEC_MDA_DISCLOSURE_LIQUIDITY_CRITICAL_ESTIMATES: SEC Adopts Amendments to Modernize and Enhance Managements Discussion and Analysis and other Financial Disclosures
- Publisher: U.S. Securities and Exchange Commission
- Date: 2020-11-19
- URL/Citation: https://www.sec.gov/newsroom/press-releases/2020-290
- Source type: disclosure_and_critical_accounting_estimate_source
- Strength classification: strong
- Source hash: 3b876fad791294c14637b407a446a2661bf99402a12b1afeefe25a320b161229

Excerpt:
The SEC release says amended MD&A requirements are intended to enhance focus on material information and let investors view the registrant from managements perspective. It says Item 303 amendments clarify disclosure requirements for liquidity and capital resources, results of operations, critical accounting estimates, obligations in the broader MD&A context, and interim-period discussion.

Limitations:
Disclosure framework context, not a conclusion that this fictional issuer must disclose a specific risk, record an impairment, or alter accounting treatment today.

### S8_IMF_2022_WAR_SANCTIONS_SPILLOVER_STALE_ANALOGY: IMF Staff Statement on the Economic Impact of War in Ukraine
- Publisher: International Monetary Fund
- Date: 2022-03-05
- URL/Citation: https://www.imf.org/en/News/Articles/2022/03/05/pr2261-imf-staff-statement-on-the-economic-impact-of-war-in-ukraine
- Source type: stale_geopolitical_sanctions_spillover_analogy
- Strength classification: stale_tempting
- Source hash: d57de22c747d714ab93205433a66ca913b767973b98b3c0746dbf9bfa7f3639a

Excerpt:
The IMF 2022 statement says war and sanctions can have severe global economic and financial spillovers; energy and commodity prices surged, financial markets were disrupted, and sanctions on banking systems affected cross-border payments. It emphasizes that the outlook was subject to extraordinary uncertainty and that spillover effects needed continuing monitoring.

Limitations:
Stale analogy from a different conflict, region, sanctions regime, and fact pattern. It is useful to frame risk categories but must not be treated as current legal or accounting evidence for this JV.

### S9_FRED_BLOG_IRAN_MARKET_RESPONSE_20260430: How markets have responded to military action against Iran
- Publisher: Federal Reserve Bank of St. Louis FRED Blog
- Date: 2026-04-30
- URL/Citation: https://fredblog.stlouisfed.org/2026/04/how-markets-have-responded-to-military-action-against-iran/
- Source type: contextual_market_commentary
- Strength classification: weak_or_limited
- Source hash: beff0fc582229eef5e8a3ca3a24c5cc6e549384296ddbc8839b77c650a50642d

Excerpt:
The FRED Blog discusses 2026 geopolitical events, oil prices, and VIX as a measure of 30-day-ahead S&P 500 volatility often treated as a fear measure. It frames oil-price and VIX movement as consistent with broad market pressures and notes that persistence of oil-price gaps depends on market adjustment over time.

Limitations:
Helpful context but not an accounting standard, sanctions authority, legal opinion, JV document, reserve report, or company-specific impairment analysis. It should not carry the recommendation.

### S10_DERIVED_D2_DECISION_PRESSURE_TABLE: D2 derived JV accounting and cash-realization pressure table from frozen public sources and case facts
- Publisher: Packet compiler using S3/S4/S5/S6/S7 and case facts
- Date: 2026-06-21
- URL/Citation: Derived from S3_EIA_STEO_JUNE_2026_HORMUZ_DISRUPTION, S4_IFRS_IAS28_EQUITY_METHOD_JV, S5_IFRS_IAS36_IMPAIRMENT_BOUNDARY, S6_IFRS_IAS21_FX_AND_LACK_OF_EXCHANGEABILITY, S7_SEC_MDA_DISCLOSURE_LIQUIDITY_CRITICAL_ESTIMATES, and case facts in this packet.
- Source type: table_chart_stat_element
- Strength classification: table_chart_stat_element
- Source hash: 70925fc6e9821350892c3758af7491d0d2e263fe01f5808cf45483c80c8abcde

Excerpt:
Quantitative pressure table: Parent share of pending $75 million JV distribution equals $26.25 million. Parent share of $120 million gross JV local cash equals $42 million before withholding, bank charges, and FX/repatriation effects. A 9% FX/repatriation haircut on $42 million equals $3.78 million. Production decline from 42,000 to 38,600 boe/day equals 3,400 boe/day or about 8.1%; parent 35% share of the gross decline equals about 1,190 boe/day. A 12% impairment sensitivity on a $480 million carrying amount equals $57.6 million. FRED Brent data in this packet show $97.46 on 2026-06-08 and $84.36 on 2026-06-15, a decline of about 13.4%.

Limitations:
Decision table only. It is not a legal conclusion, sanctions finding, recoverable-amount calculation, reserve report, realized FX loss, or proof of impairment.
