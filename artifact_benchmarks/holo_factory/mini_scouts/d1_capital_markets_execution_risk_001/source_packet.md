# D1 Capital Markets / Execution Risk Source Packet

Status: frozen source packet. No browsing. Use only this packet and the task brief.

## Case Facts

- **facts_are_case_scenario_not_external_sources**: true
- **company_profile**: "A fictional U.S. investment-grade industrial issuer is deciding whether to launch a financing during a sudden market-volatility and liquidity shock."
- **decision_time**: "Leadership meeting at 08:00 ET tomorrow; banks say a same-day launch is feasible but pricing is moving quickly."
- **proposed_action**: "Issue up to $900 million of 3-year senior unsecured notes to prefund commercial-paper maturities and a near-term debt maturity."
- **near_term_obligations**: ["Commercial paper maturities of $650 million over the next 10 business days.", "A $300 million senior note maturity in 70 days.", "A $35 million supplier and payroll liquidity need inside the same 10-business-day window."]
- **liquidity_position**: ["Current cash and immediately available investments: $620 million.", "Minimum board liquidity floor: $300 million.", "Committed revolver availability: $500 million, but a draw above $250 million must be escalated to the board and disclosed to rating-agency coverage teams under the company treasury policy."]
- **banker_market_color**: ["Syndicate desk indicates the bond market is open but expects a 20-35 bp new-issue concession if launched immediately.", "Desk estimates delaying 48-72 hours may save the concession if volatility fades, but there is no firm underwrite and order-book depth is not committed.", "Treasury desk can hedge benchmark-rate risk but hedge execution requires board authorization and does not eliminate credit-spread or order-book risk."]
- **not_provided**: ["No committed underwrite or guaranteed investor order book.", "No board approval yet for derivatives hedging.", "No evidence that the company can roll all commercial paper if money-market buyers shorten tenor.", "No issuer-specific rating-agency statement, covenant waiver, or investor feedback letter."]
- **illustrative_calculations_to_check**: ["If only 60% of the $650 million CP maturities roll, $260 million must be paid from liquidity; $620 million cash minus $260 million CP cash use minus $35 million operating need leaves $325 million, only $25 million above the board liquidity floor.", "If only 50% rolls, cash after CP paydown and the $35 million operating need is $260 million, which is $40 million below the board liquidity floor before revolver use.", "A 35 bp new-issue concession on $900 million equals $3.15 million of incremental annual interest cost, or $9.45 million over three years before tax effects and discounting."]

## Claim Boundaries

- Do not claim that any public indicator proves the fictional issuers bond deal will clear.
- Do not claim that VIX alone determines bond-market access or new-issue concession.
- Do not treat high-yield OAS as the issuers investment-grade spread.
- Do not treat historical 2020 emergency stress as current 2026 market condition.
- Do not invent issuer rating, covenant text, hedge authorization, investor orders, or committed underwriting.
- Do not give investment, legal, accounting, or trading advice; write an internal decision brief under uncertainty.

## Frozen Sources

### S1_FED_FSR_2026_OVERVIEW_VULNERABILITIES: Financial Stability Report - May 2026: Overview
- Publisher: Board of Governors of the Federal Reserve System
- Date: 2026-05-28
- URL/Citation: https://www.federalreserve.gov/publications/2026-may-financial-stability-report-overview.htm
- Source type: authoritative_market_and_financial_stability_source
- Strength classification: strong
- Source hash: 37c4e45ee04cab4fad327024612569a338818585637efa63af0c5325cde9d6ef

Excerpt:
The Federal Reserve May 2026 overview says its financial-stability assessment covers valuation pressures, business and household borrowing, financial-sector leverage, and funding risks. It states market conditions and data are as of April 23, 2026. It reports elevated asset-valuation pressures, low corporate bond spreads by longer-run standards, higher Treasury term premiums amid volatility, moderate funding risks, and salient risks including geopolitical risks, oil shock, private credit, persistent inflation, and AI-related risks.

Limitations:
Authoritative macro-financial context, but not issuer-specific and not a commitment that any market is open for this company at executable size.

### S2_FED_FSR_2026_MARKET_LIQUIDITY_AND_SPREADS: Financial Stability Report - May 2026: Asset Valuations
- Publisher: Board of Governors of the Federal Reserve System
- Date: 2026-05-28
- URL/Citation: https://www.federalreserve.gov/publications/2026-may-financial-stability-report-asset-valuations.htm
- Source type: authoritative_execution_risk_and_liquidity_source
- Strength classification: strong
- Source hash: a2121967f82a893170f1d12a786e0bd4d9618a6bf99df44462d57f2a1271bb9c

Excerpt:
The Fed says low liquidity can amplify asset-price volatility and create larger price moves after shocks. Treasury market liquidity initially deteriorated during March stress and then recovered, but the market-depth measure for the most liquid on-the-run 2-year Treasury note remained near the first quartile of its historical distribution. The same section reports that corporate bond spreads remained low by historical standards, while corporate bond market liquidity remained robust through March and in line with recent years.

Limitations:
This is system-level evidence. It supports caution about execution risk but does not prove current order-book depth for a specific issuer or bond maturity.

### S3_FRED_VIXCLS_20260617: CBOE Volatility Index: VIX (VIXCLS)
- Publisher: Federal Reserve Bank of St. Louis FRED / Chicago Board Options Exchange
- Date: Updated 2026-06-18; observation 2026-06-17
- URL/Citation: https://fred.stlouisfed.org/series/VIXCLS
- Source type: current_volatility_indicator
- Strength classification: useful_normal
- Source hash: b0df364bc4f268833c829e0afd8e4b5836f3a4536cdabf45cfb544af34a8c406

Excerpt:
FRED reports VIXCLS at 18.44 on 2026-06-17, with recent observations of 19.44 on June 11, 17.68 on June 12, 16.20 on June 15, and 16.41 on June 16. FRED notes VIX measures near-term volatility expectations conveyed by stock index option prices.

Limitations:
VIX is an equity-volatility indicator. It is useful stress context but does not directly price this companys bond issue, CP rollover capacity, or credit-spread concession.

### S4_FRED_HY_OAS_20260617: ICE BofA US High Yield Index Option-Adjusted Spread (BAMLH0A0HYM2)
- Publisher: Federal Reserve Bank of St. Louis FRED / ICE Data Indices
- Date: Updated 2026-06-18; observation 2026-06-17
- URL/Citation: https://fred.stlouisfed.org/series/BAMLH0A0HYM2
- Source type: current_credit_spread_indicator
- Strength classification: useful_normal
- Source hash: 559f7c4bb8964535d9d63fb43df959cc42a0a130f6399b6882514cba000fd9ce

Excerpt:
FRED reports the ICE BofA U.S. High Yield option-adjusted spread at 2.63 percent on 2026-06-17, after 2.78 on June 11, 2.71 on June 12, 2.66 on June 15, and 2.71 on June 16. The series is a daily high-yield spread measure, not an investment-grade issuer-specific spread.

Limitations:
High-yield OAS can indicate broad credit risk appetite, but the fictional issuer is investment grade; this indicator alone cannot determine fair new-issue concession.

### S5_FED_COMMERCIAL_PAPER_20260618: Commercial Paper Rates and Outstanding Summary
- Publisher: Board of Governors of the Federal Reserve System
- Date: 2026-06-18; data as of 2026-06-17
- URL/Citation: https://www.federalreserve.gov/releases/cp/
- Source type: current_short_term_funding_market_source
- Strength classification: strong
- Source hash: d60db3e878bb889c366d7432558f6a2e9b3a80d734d562150c2127a931387a21

Excerpt:
The Fed commercial paper release says data are derived from Depository Trust & Clearing Corporation data. For June 17, 2026, AA nonfinancial CP rates include 1-day 3.65, 15-day 3.74, 30-day 3.70, 60-day 3.65, and 90-day 3.67 percent. A2/P2 nonfinancial rates include 1-day 3.83, 7-day 3.90, 15-day 3.96, 30-day 4.02, and 60-day 3.99 percent. Seasonally adjusted total commercial paper outstanding was $1,400.5 billion on June 17.

Limitations:
This shows market rates/outstandings, not this companys exact rollover success probability or tenor access.

### S6_SIFMA_CORPORATE_BOND_STATISTICS_20251001: US Corporate Bonds Statistics
- Publisher: Securities Industry and Financial Markets Association (SIFMA)
- Date: 2025-10-01
- URL/Citation: https://www.sifma.org/resources/research/statistics/us-corporate-bonds-statistics/
- Source type: corporate_financing_and_market_capacity_source
- Strength classification: contradictory_or_complicating
- Source hash: 8b135991b82b39057a659e493d83883c6fcc0f2d951bd3d538a0f1db58a27edf

Excerpt:
SIFMA says it tracks issuance, trading, and outstanding data for the U.S. corporate bond market. Its October 2025 page reports year-to-date issuance through end-September of $1,736.6 billion, up 5.9 percent year over year; average daily trading of $58.8 billion, up 12.6 percent year over year; and $11.4 trillion outstanding as of 2025 Q2.

Limitations:
Useful evidence that corporate bond markets can be large and active, but it is not live order-book evidence for the decision date and may tempt overconfidence that issuance capacity equals attractive pricing.

### S7_FED_FSR_2026_FUNDING_RISKS: Financial Stability Report - May 2026: Funding Risks
- Publisher: Board of Governors of the Federal Reserve System
- Date: 2026-05-28
- URL/Citation: https://www.federalreserve.gov/publications/2026-may-financial-stability-report-funding-risks.htm
- Source type: authoritative_funding_and_liquidity_risk_source
- Strength classification: strong
- Source hash: 4db7287ef9cbe62c702b4964f3ba40124c080ab53c5fef05b5861c3ddedbc41e

Excerpt:
The Fed reports funding risks were roughly in line with historical norms, while cash-management vehicles continued to grow and some bond and loan mutual funds remained exposed to liquidity-transformation risk because they allow daily redemptions while holding assets that might become illiquid in stress. It also lists commercial paper at $1,368 billion among selected runnable money-like liabilities in Table 4.1.

Limitations:
This is macro funding-risk context. It does not prove the fictional issuer can or cannot roll CP; artifacts must connect it cautiously to the case facts.

### S8_FED_FSR_2020_STALE_STRESS_ANALOGY: Financial Stability Report - May 2020: Overview
- Publisher: Board of Governors of the Federal Reserve System
- Date: 2020-05-15; page updated 2022-06-16
- URL/Citation: https://www.federalreserve.gov/publications/2020-may-financial-stability-report-overview.htm
- Source type: stale_market_stress_analogy
- Strength classification: stale_tempting
- Source hash: 653d903d41cf705a30506b238a473fe4d391df0a2e50e4e1725808ade62ab6d3

Excerpt:
The Fed May 2020 overview describes severe pandemic stress: impaired credit flow, rapid investor movement toward cash, strains in Treasury and agency MBS markets, short-term funding pressure, CP rollover stress, and emergency Federal Reserve facilities that stabilized key funding markets. It says CP stress forced some businesses to issue CP on a near-daily basis with no guarantee investors would accept it.

Limitations:
Important historical stress analogy, but it is stale and describes an emergency facility environment. It must not be treated as evidence that 2026 markets are in the same condition or that emergency backstops are available.

### S9_FRED_BLOG_IRAN_MARKET_RESPONSE_20260430: How markets have responded to military action against Iran
- Publisher: Federal Reserve Bank of St. Louis FRED Blog
- Date: 2026-04-30
- URL/Citation: https://fredblog.stlouisfed.org/2026/04/how-markets-have-responded-to-military-action-against-iran/
- Source type: contextual_market_commentary
- Strength classification: weak_or_limited
- Source hash: 916fb9a41d5ceea89124174e5593132ea65c8b0d52bf01c6e28c6ce1b09e4fb7

Excerpt:
The FRED Blog discusses 2026 geopolitical events and tracks Brent, WTI, and VIX. It says VIX measures 30-day-ahead S&P 500 volatility and is often considered a fear measure. It interprets joint oil-price and VIX movement in early March 2026 as consistent with broad market pressures, and says persistence of oil-price gaps depends on market adjustment over time.

Limitations:
Contextual explanatory blog, not a capital-markets execution mandate, issuance window signal, or issuer-specific funding analysis. It should not carry the recommendation.

### S10_DERIVED_D1_DECISION_PRESSURE_TABLE: D1 derived market and liquidity pressure table from frozen public indicators and case facts
- Publisher: Packet compiler using S3/S4/S5 and case facts
- Date: 2026-06-21
- URL/Citation: Derived from S3_FRED_VIXCLS_20260617, S4_FRED_HY_OAS_20260617, S5_FED_COMMERCIAL_PAPER_20260618, and case facts in this packet.
- Source type: table_chart_stat_element
- Strength classification: table_chart_stat_element
- Source hash: 555d260a734280e0a65e1f8440feb1b154629606cd3335ead43bb46eb745e260

Excerpt:
Quantitative pressure table: VIX 18.44 on 2026-06-17; high-yield OAS 2.63 percent on 2026-06-17; AA nonfinancial 30-day CP 3.70 percent on June 17; A2/P2 nonfinancial 30-day CP 4.02 percent on June 17; CP rollover stress case: 60 percent rollover leaves $325 million liquidity after $260 million CP cash use and $35 million operating need, only $25 million above the board floor; 50 percent rollover leaves $260 million, $40 million below the floor; 35 bp concession on $900 million equals $3.15 million annual incremental interest and $9.45 million over three years before tax effects and discounting.

Limitations:
This is a frozen decision table for interpretation, not a live quote, underwriter commitment, or forecast. Artifacts must show the arithmetic and not convert it into a certainty claim.
