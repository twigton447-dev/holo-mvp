# Ten-Domain HoloBuild Packet Suite Manifest

Created UTC: `2026-06-21T05:18:34Z`

This manifest stores the frozen D1-D10 action-boundary packet suite for later HoloBuild and solo generation. It is packet-readiness only: no providers, no artifacts, no scoring, no judging, and no unblinding are performed by this manifest.

Proof Holo mode: `patent_aligned_v4` only. Legacy Holo modes are diagnostic-only and banned from proof-credit use.

| Domain | Packet | Packet Hash | Lock Hash | Status |
|---|---|---|---|---|
| D1 Capital Markets / Execution Risk | `d1_capital_markets_execution_risk_001` | `18d259d042740ec63b930c664d1537d45bc521a8df9fcfdc446f65c22dfdd7db` | `ca5f45695b7526f6f7650690eb79aec063b951baf3ac48feede135d7f379c5b2` | `frozen_no_provider_packet_ready` |
| D2 Oil & Gas / Middle East JV Accounting | `d2_oil_gas_middle_east_jv_accounting_001` | `c3c8440319093e6764d6dfe583a9339f5ac6008d2a36411cb95337bdb60bd737` | `99f104ea34fbe50278c665b2d46f86cbb5d52b7ed88daea040840bc023645744` | `frozen_no_provider_packet_ready` |
| D3 Insurance / Reinsurance Catastrophe Risk | `d3_insurance_reinsurance_catastrophe_risk_001` | `cb13658cd2332e4f162e4138a2b6d74ae1a237ac6f95d6eae05cdbcd07798b08` | `2283c706639d2b209b7697270b2b07c68401f6ed15dd27f0df6ab5a35a1ddc2a` | `frozen_no_provider_packet_ready` |
| D4 AP / Procurement / Vendor Risk | `d4_ap_procurement_vendor_risk_001` | `f5aaa2a29d19fc7e48f2757791144467ae30494787bfc28a52fb54a55f04aaf9` | `d8f3e39d4d35187f2a81e89ae5ee6b39fb4a033cc66bef729833140a2c272a4c` | `frozen_no_provider_packet_ready` |
| D5 Healthcare / MedTech Evidence Synthesis | `d5_medtech_capacity_strain_001` | `b73292d9d2e4aac5f65a93ae168235d9d581ae17ebaf0a91aa16437018c527aa` | `211a67112f1ce8a37a2d514028ac30d8a798762df0c610679e84b5d538fa19ca` | `frozen_no_provider_packet_ready` |
| D6 PE / Financial Reporting & Consolidation | `d6_pe_financial_reporting_consolidation_001` | `5c792505d76e9288c74013c9bc4fb39fe64fae0bead2aee3e91d73d4f17ff0ad` | `924501a1a4db2e2f7f4aab1877616c113337748e5045b15e7d92ae03d825af3d` | `frozen_no_provider_packet_ready` |
| D7 Agentic Commerce / Autonomous Purchase Approval | `d7_agentic_commerce_purchase_approval_001` | `7ed2bf03fbf4b1c413ba02605c9bf84f2d15e93eb4ef80cbea822b083f181134` | `b91e6babd94c54b0bdc64e2654edb4d5a99387f1d638ab38bf950578036e0124` | `frozen_no_provider_packet_ready` |
| D8 IT Access Provisioning | `d8_it_access_provisioning_001` | `a0f4156ee8614539db7880b36c2098ac959a3846abebcfb6be4bec9745d1868c` | `d97911ee53df9a74a05a0aa6c6f676c673dd1d1879f3061481e3052a6656239a` | `frozen_no_provider_packet_ready` |
| D9 Legal Contract Execution | `d9_legal_contract_execution_001` | `1a2a254d54c13b61bf679d98f56f1172ce21747dbabb557d619124ef6d39afaa` | `6c268fca0043f7439abae36059ef0a85c76873a9cbe7ea21c9d8ad87ef424ba7` | `frozen_no_provider_packet_ready` |
| D10 Infrastructure / Configuration Change | `d10_infrastructure_configuration_change_001` | `d4c4e6beb777af18061f51b47255422cd8f75fa30dbebce925dd958c759105f1` | `e0509372ce7b8be4290ef5b83c8fb3fd0c9caff20704b8ac2ca6ac39630a3630` | `frozen_no_provider_packet_ready` |

## Safety State

- provider_calls: `0`
- artifact_generation_status: `not_started` for every packet
- scoring_status: `not_started` for every packet
- unblinding_status: `not_started` for every packet
- scoring protocol is external/global, not embedded in packets.

## Tomorrow Commands

Validate the suite:

```bash
python3 -B artifact_benchmarks/holo_factory/validate_holobuild_ten_domain_suite.py
```

Dry-run one packet:

```bash
python3 -B artifact_benchmarks/holo_factory/run_holobuild_mini_scout.py \
  --packet-dir artifact_benchmarks/holo_factory/mini_scouts/d1_capital_markets_execution_risk_001 \
  --condition holo_build_arch \
  --holo-mode patent_aligned_v4 \
  --run-id SMOKE_D1_HOLO \
  --dry-run
```
