# D3 Insurance / Reinsurance Catastrophe Risk Source Packet

Status: frozen source packet. No browsing. Use only this packet and the task brief.

## Case Facts

- **facts_are_case_scenario_not_external_sources**: true
- **company_profile**: "A fictional regional property insurer writes homeowners and small-commercial property policies in hurricane, severe-convective-storm, wildfire-smoke, and flood-adjacent counties."
- **decision_time**: "Executive leadership, actuarial, reinsurance, claims, legal, product, investor relations, and state-regulatory affairs must decide before a July 1 catastrophe reinsurance renewal deadline."
- **current_portfolio_and_renewal_pressure**: ["Coastal and inland-catastrophe-exposed book: 125,000 policies and $42 billion total insured value.", "Last 12 months gross catastrophe claims: $410 million; ceded recoveries booked to date: $235 million; retained net catastrophe loss: $175 million before any late coverage disputes or development.", "Expiring treaty: $650 million excess of $150 million per occurrence, with reinstatement protection subject to aggregate terms not fully quoted in this packet.", "Renewal quote received: $500 million excess of $250 million at $92 million annual premium, versus $78 million expiring annual premium.", "Internal surplus at start of renewal decision: $1.10 billion.", "Board risk appetite says modeled retained loss from a 1-in-100 event should not exceed 30% of surplus without board risk-committee approval.", "Product team says a full actuarial rate need points to an 18% average rate increase; state-facing affordability plan currently assumes no more than 8% average customer increase this year.", "Claims/legal teams report open disputes over whether some flood-driven losses fall outside homeowners coverage and whether annual aggregate terms limit recovery after multiple events."]
- **not_provided**: ["No full treaty wording or binding quote is provided.", "No final actuarial indication memorandum is provided.", "No state DOI approval or disapproval is provided.", "No final reserve opinion, statutory filing, or auditor conclusion is provided.", "No portfolio-level model output by ZIP, peril, or construction class is provided.", "No legal coverage opinion on the flood/exclusion or aggregate-limit disputes is provided.", "No evidence that the insurer is insolvent or that reinsurance capacity is unavailable at any price."]
- **illustrative_calculations_to_check**: ["Expiring retained loss on an $800 million gross occurrence is $150 million if the $650 million xs $150 million layer pays fully and no exclusion/aggregate dispute applies.", "Renewal retained loss on the same $800 million gross occurrence is $300 million: $250 million retention plus $50 million above the $500 million layer limit.", "The renewal structure increases retained loss on that event by $150 million versus expiring terms.", "$300 million retained loss equals 27.3% of $1.10 billion surplus, below but close to the 30% board risk appetite trigger of $330 million.", "If an additional $80 million is retained because of exclusion or aggregate-limit dispute, retained loss becomes $380 million, or 34.5% of surplus, above the 30% trigger.", "Renewal premium increase from $78 million to $92 million is $14 million, or about 17.9%.", "The gap between an 18% indicated customer rate need and an 8% affordability plan is 10 percentage points; on a $540 million annual written-premium base, that gap is $54 million of annual premium adequacy pressure before mix and approval effects."]

## Claim Boundaries

- Do not treat broad catastrophe statistics as proof of this insurers portfolio loss.
- Do not treat reinsurance market hardening as automatic insolvency or capacity failure.
- Do not treat flood, earthquake, aggregate, or excluded-peril disputes as resolved without policy/treaty wording and legal review.
- Do not flatten economic loss, insured loss, reinsured loss, and retained net loss.
- Do not invent state DOI action, final actuarial rate indication, reserve opinion, RBC result, treaty wording, or binding reinsurance quote.
- Do not give legal, actuarial, reserving, rating, investment, or regulatory advice; write an internal decision brief under uncertainty.

## Frozen Sources

### S1_NOAA_NCEI_BILLION_DOLLAR_DISASTERS_2026: Billion-Dollar Weather and Climate Disasters
- Publisher: NOAA National Centers for Environmental Information
- Date: March 2026 release page accessed 2026-06-21
- URL/Citation: https://www.ncei.noaa.gov/access/billions/
- Source type: authoritative_catastrophe_loss_source
- Strength classification: strong
- Source hash: dfb67c291197e5ba8c244f6385efc6b16875dad96c376171c2e4e7500c881665

Excerpt:
NOAA NCEI hosts the U.S. Billion-Dollar Weather and Climate Disasters dataset and provides the official citation: NOAA National Centers for Environmental Information (NCEI) U.S. Billion-Dollar Weather and Climate Disasters (2025), DOI 10.25921/stkw-7w73. The public page identifies the March U.S. release dated April 8, 2026 and frames the dataset as a climate monitoring resource for high-cost U.S. weather and climate disasters.

Limitations:
Authoritative catastrophe-loss archive, but it is broad public catastrophe history. It does not prove this insurers portfolio loss, coverage response, reinsurance recovery, or reserve adequacy.

### S2_FT_HOWDEN_GUY_CARPENTER_REINSURANCE_2025: Reinsurance costs fall as sector deploys record capital
- Publisher: Financial Times, reporting Howden and Guy Carpenter market data
- Date: 2025-01-02
- URL/Citation: https://www.ft.com/content/279e0473-5b23-46d7-96f9-1a43aade23e6
- Source type: reinsurance_market_capacity_source
- Strength classification: contradictory_or_complicating
- Source hash: 87c597c9b20f6d37e79cfa3b5e200d28e6b60e22985375f824af0257c67969d8

Excerpt:
The FT reported Howden research that property catastrophe reinsurance costs fell 8% globally at January 1 renewals as reinsurers deployed record capital. Dedicated reinsurance capital reportedly finished 2024 at a record $463 billion, up 10% year over year, with catastrophe bond issuance at $17.7 billion and alternative capital about $116 billion. The same article says risks had not abated: insured property catastrophe losses reached an estimated $136 billion in 2024, primary insurers retained more smaller-peril losses, and heavily affected regions faced increases of up to 30% for some reinsurance coverage.

Limitations:
Useful reinsurance market context but secondary reporting, not a binding quote for the fictional insurer. It complicates any claim that capacity is simply unavailable or simply cheap.

### S3_FEMA_NFIP_COVERAGE_EXCLUSIONS_2026: What you need to know about buying flood insurance
- Publisher: FEMA National Flood Insurance Program / FloodSmart.gov
- Date: Accessed 2026-06-21
- URL/Citation: https://www.floodsmart.gov/get-insured/buy-a-policy
- Source type: coverage_exclusion_and_limit_source
- Strength classification: strong
- Source hash: 952f978b88d1a7cf73dd0b6b85c5e60226211de33d6aa6abcf84b5d73c18f5e9

Excerpt:
FloodSmart says most homeowners and renters insurance does not cover flood damage. It says NFIP offers flood policies for homeowners, renters, and businesses. Homeowner building policies cover up to $250,000 of flood damage and contents policies cover up to $100,000; commercial flood insurance provides building and contents coverage up to $500,000 each. The page also says NFIP policy rates are unique to location and needs, and that building and contents coverage are typically purchased separately and have separate deductibles.

Limitations:
Authoritative for NFIP consumer coverage concepts and flood coverage boundaries, but not this insurers policy wording, reinsurance treaty terms, or claims legal outcome.

### S4_NAIC_HOMEOWNERS_INSURANCE_2025: Insurance Topics: Homeowners Insurance
- Publisher: National Association of Insurance Commissioners
- Date: Last updated 2025-10-25
- URL/Citation: https://content.naic.org/insurance-topics/homeowners-insurance
- Source type: insurance_affordability_availability_and_coverage_source
- Strength classification: strong
- Source hash: 10a1d91cbc42c2c7a86f02a62f053518ae558014715d9223b109ee2c8d234465

Excerpt:
NAIC says homeowners insurance is essential for many consumers because the home is often their most valuable asset; it protects the structure and personal belongings, provides liability coverage, and often serves as the primary rebuilding funds after a total loss. It notes most mortgage lenders require homeowners coverage. NAIC also explains that flood insurance and earthquake insurance are separate policies or add-ons, policies pay for covered perils up to policy limits, and policyholders pay deductibles before insurers share in losses beyond the deductible.

Limitations:
Authoritative consumer/regulatory context, but not a rate filing, DOI approval, affordability finding, or this insurers policy-specific coverage conclusion.

### S5_NAIC_RISK_BASED_CAPITAL_2025: Insurance Topics: Risk-Based Capital
- Publisher: National Association of Insurance Commissioners
- Date: Last updated 2025-10-02
- URL/Citation: https://content.naic.org/insurance-topics/risk-based-capital
- Source type: reserve_capital_and_regulatory_intervention_source
- Strength classification: strong
- Source hash: 388aebc34bb51c13039db3cefb449d3e624fdfd5f85c4c24569998ccaa931055

Excerpt:
NAIC says regulators are charged with ensuring insurance companies can fulfill obligations to policyholders, and risk-based capital is a statutory minimum capital level based on company size and inherent riskiness of assets and operations. It says RBC is intended as a regulatory standard, not necessarily the full capital needed to meet company objectives, and identifies potentially weakly capitalized companies. The page says RBC calculations enable timely regulatory intervention, but RBC is not designed as a stand-alone solvency tool. It also notes P/C RBC formulas consider underwriting risk and other risks, and regulators have graduated intervention levels tied to capital sufficiency.

Limitations:
Authoritative capital/regulatory framework, but not this insurers RBC calculation, statutory surplus filing, reserve opinion, or solvency determination.

### S6_GAO_NFIP_REFORM_2017_STALE: Flood Insurance: Comprehensive Reform Could Improve Solvency and Enhance Resilience
- Publisher: U.S. Government Accountability Office
- Date: 2017-04-27; matter status noted as of 2026 on GAO page
- URL/Citation: https://www.gao.gov/products/gao-17-425
- Source type: stale_flood_insurance_affordability_and_resilience_source
- Strength classification: stale_tempting
- Source hash: b036e19b4d9a048ccc06f3c3af0ae376baea6976605230772b285a8c731c393f

Excerpt:
GAO found that comprehensive NFIP reform would need to balance competing goals such as keeping flood insurance affordable while keeping the program fiscally solvent. GAO said raising rates to reflect full risk can create affordability issues and reduce participation, while affordability assistance could help consumers buy insurance and support mitigation. GAO also said consumer participation can be affected by misperceived flood risk and overestimation of federal assistance after disaster.

Limitations:
Valuable but stale and specific to NFIP public-policy reform, not this private insurers current catastrophe treaty, rate filing, or coverage dispute.

### S7_GUARDIAN_HOMEOWNERS_INSURANCE_COSTS_2025: US homeowners in disaster-prone states face soaring insurance costs
- Publisher: The Guardian
- Date: 2025-01-22
- URL/Citation: https://www.theguardian.com/environment/2025/jan/22/us-homeowners-insurance-costs-climate-crisis
- Source type: weak_or_limited_market_context_source
- Strength classification: weak_or_limited
- Source hash: 1b68f3b371450050e0bcd34288a846b12adef9c1f1902eff130fe1bcbb169cc7

Excerpt:
The Guardian reported on U.S. Treasury data showing homeowners in high climate-risk ZIP codes faced steep insurance premium pressure. It reported that people in the top 20% riskiest places for climate-related perils paid on average 82% more than those in the lowest-risk ZIP codes and discussed insurer withdrawal or pausing in high-risk states such as Florida and California.

Limitations:
Useful affordability context but journalistic and not decisive. It is not a rate approval, statutory filing, portfolio model, or binding evidence about this fictional insurers customers.

### S8_ARXIV_CAT_REINSURANCE_CLIMATE_MODEL_2026: Pricing Excess-of-Loss Reinsurance and CAT Bonds under Climate Uncertainty: A Cox Process Framework with Temperature-Dependent Stochastic Intensity
- Publisher: arXiv preprint
- Date: 2026-06-12
- URL/Citation: https://arxiv.org/abs/2606.14830
- Source type: limited_preprint_modeling_source
- Strength classification: useful_normal
- Source hash: 7662e687cbd617f2bb706a455edf56e6e4932d444d7de7968c70479d090d064f

Excerpt:
The arXiv preprint proposes a climate-aware pricing framework for excess-of-loss reinsurance and catastrophe bonds using a Cox process with temperature-dependent stochastic intensity. The abstract says catastrophe losses are not dynamically replicable and emphasizes scenario-based valuation rather than model-independent no-arbitrage bounds. It reports that, in its baseline calibration, the climate-aware model increases excess-of-loss reinsurance premium and lowers CAT bond price relative to a stationary benchmark, and that stationary benchmarks may underestimate economic capital requirements by about 13.7% compared with the climate-aware framework.

Limitations:
Recent preprint and model-specific. It is useful for uncertainty framing but not market consensus, regulatory capital requirement, or direct pricing evidence for this portfolio.

### S9_FEMA_NFIP_REINSURANCE_PROGRAM: National Flood Insurance Program Reinsurance Program
- Publisher: Federal Emergency Management Agency
- Date: Accessed 2026-06-21
- URL/Citation: https://www.fema.gov/flood-insurance/work-with-nfip/reinsurance
- Source type: risk_transfer_and_reinsurance_tool_source
- Strength classification: useful_normal
- Source hash: 76358e95b394e8759156c335f04db53b74fbc969423ff23b1cbdc9deb04443e2

Excerpt:
FEMA describes the NFIP Reinsurance Program as an additional method to fund flood claims after catastrophic flood events. FEMA says reinsurance is insurance purchased by an insurance organization to transfer risk and that NFIP uses both traditional reinsurance and capital markets risk transfer to manage catastrophic flood losses.

Limitations:
Useful risk-transfer concept and public-program example, but not evidence that this fictional insurer can buy the desired private reinsurance terms or transfer every peril.

### S10_DERIVED_D3_DECISION_PRESSURE_TABLE: D3 derived catastrophe renewal and retained-loss pressure table from frozen public sources and case facts
- Publisher: Packet compiler using S2/S3/S4/S5 and case facts
- Date: 2026-06-21
- URL/Citation: Derived from S2_FT_HOWDEN_GUY_CARPENTER_REINSURANCE_2025, S3_FEMA_NFIP_COVERAGE_EXCLUSIONS_2026, S4_NAIC_HOMEOWNERS_INSURANCE_2025, S5_NAIC_RISK_BASED_CAPITAL_2025, and case facts in this packet.
- Source type: table_chart_stat_element
- Strength classification: table_chart_stat_element
- Source hash: b60c26d23ed425bf5ce9d435f81681726b37f85ec56267df7d502cdedf3c6ca8

Excerpt:
Quantitative pressure table: Last 12 months gross catastrophe claims $410 million; ceded recoveries $235 million; retained net catastrophe loss $175 million. Renewal quote premium rises from $78 million to $92 million, a $14 million or about 17.9% increase. Expiring retained loss on an $800 million gross occurrence is $150 million if $650 million xs $150 million pays fully. Renewal retained loss on the same event is $300 million: $250 million retention plus $50 million above the $500 million layer. The renewal structure increases retained event loss by $150 million. $300 million is 27.3% of $1.10 billion surplus; adding $80 million from coverage/aggregate dispute gives $380 million, or 34.5% of surplus, above the internal 30% board trigger. The gap between 18% indicated rate need and 8% affordability plan is 10 percentage points; on $540 million written premium that is $54 million annual adequacy pressure before mix and approval effects.

Limitations:
Decision table only. It is not a treaty quote, actuarial opinion, reserve opinion, regulator approval, solvency finding, or coverage legal conclusion.
