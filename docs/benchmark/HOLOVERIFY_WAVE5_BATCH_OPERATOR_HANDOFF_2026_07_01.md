# HoloVerify Wave5 Batch Operator Handoff

Status: `PASS`
Generated from head: `9608e662148bed1a6c59c0bc1f0286d93ad19346`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`
Preflight: `docs/benchmark/HOLOVERIFY_WAVE5_BATCH_EXECUTION_PREFLIGHT_2026_07_01.json`

## Scope

- No providers were called by this handoff.
- No judges were called by this handoff.
- Wave5 remains split into 28 independent 5-pair batches.
- Each approved batch is 10 packets and 50 Holo provider calls.
- Do not run the full 280-packet bank as one live job.

## Next Batch

- Batch: `WAVE5_MEDX_HOLO_BATCH_001`
- Family: `HV-MEDX-REP-2026-07-01`
- Pairs: `5`
- Packets: `10`
- Expected provider calls if approved: `50`
- Approval packet SHA: `57aa1ae0dc035b2c5769d29aa1f2eb14ca8a4e9ef1027fecc2ad234abab1cb24`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 57aa1ae0dc035b2c5769d29aa1f2eb14ca8a4e9ef1027fecc2ad234abab1cb24 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_001 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Operator Rules

- Run only one Wave5 batch at a time.
- Use the exact approval statement and approval packet SHA for that batch.
- Do not run solo or judges during Wave5 Holo batch execution.
- Do not edit frozen packets or prompts.
- If a batch fails, preserve the invalid run and stop for autopsy before continuing.
- Do not treat future unrun batches as evidence.

## Batch Queue

| # | Batch | Family | Pairs | Packets | Calls | Approval SHA |
| --- | --- | --- | --- | --- | --- | --- |
| `1` | `WAVE5_MEDX_HOLO_BATCH_001` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `57aa1ae0dc035b2c5769d29aa1f2eb14ca8a4e9ef1027fecc2ad234abab1cb24` |
| `2` | `WAVE5_MEDX_HOLO_BATCH_002` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `bdb43e3867f0664aeb89a769c432e21bb848e17e28ecd373e7370ac6dd43d1b1` |
| `3` | `WAVE5_MEDX_HOLO_BATCH_003` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `31c5643fa527ca8a721ee7848ca01e13d90313463239d7616c4f266ee4dee1f8` |
| `4` | `WAVE5_MEDX_HOLO_BATCH_004` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `6f713a7de3d08aa5c1d92e8c4918273e80534d368b0b8184086e61e23a344431` |
| `5` | `WAVE5_TRES_HOLO_BATCH_001` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `a1e7f8e017b83e9281a9b8fc03aa68fcf3d08dde32a609f6ab899932f53940c5` |
| `6` | `WAVE5_TRES_HOLO_BATCH_002` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `016b592f806c803faeb26d1f71fdaa45500ac12bf39b083d255f8c8fa76d6c0d` |
| `7` | `WAVE5_TRES_HOLO_BATCH_003` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `d4fd39911ed8c635f9b278c64eef575dee8d5aad84160ecc79570aba8ee38a8c` |
| `8` | `WAVE5_TRES_HOLO_BATCH_004` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `6168eb3221408da059d52c4d2c5e36416b73c117aaff82c634bb1aa507f6b069` |
| `9` | `WAVE5_LREG_HOLO_BATCH_001` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `b64c1a38438584afcab09eb7dc2c2756afb53a9b908348f8ed54141597210361` |
| `10` | `WAVE5_LREG_HOLO_BATCH_002` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `e8578c24140b9755cd496c1c119bd900830d7eeaab9ee12c4e97a3443ee9175e` |
| `11` | `WAVE5_LREG_HOLO_BATCH_003` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `850a33b654ef2fec0c1b42eb008fa5b006830d6ba5da3c532dd53e9cfd62adc9` |
| `12` | `WAVE5_LREG_HOLO_BATCH_004` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `845c2bebc264f34e5a417b4c3eb49f054a9ab3f272009901cea6cd6e7e1c2d4a` |
| `13` | `WAVE5_CLAD_HOLO_BATCH_001` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `8eddf10b59dafc47c3a6ba06fc8fdd76f83bb19034a9602d6d36afabf33c5133` |
| `14` | `WAVE5_CLAD_HOLO_BATCH_002` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `296e109e792a5f89beee103eb7cc25749981dd0e0c0bd50b0d36ec46ee62bb9f` |
| `15` | `WAVE5_CLAD_HOLO_BATCH_003` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `8c30987e032fe31d69e2eb1849dda5fa2f4f27e3eafd96534fed6cd396597454` |
| `16` | `WAVE5_CLAD_HOLO_BATCH_004` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `101d29ceb98f396d8f49bb5f5593b2d3e89426638c21391a14bfe295cf875d2b` |
| `17` | `WAVE5_SECO_HOLO_BATCH_001` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `7e290524efd6c408eeff0a3886f8c399c344cf5dd1a24ef2c08ec21ab3285a3b` |
| `18` | `WAVE5_SECO_HOLO_BATCH_002` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `bea3d98b10a83f3faaae2b07313d04be88df09aeffa55720e6fa16f635de1a63` |
| `19` | `WAVE5_SECO_HOLO_BATCH_003` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `37f6222e4438b9d434b78ce4e599c6adf729cb1c01283aaa8b8b2d51aaae6e10` |
| `20` | `WAVE5_SECO_HOLO_BATCH_004` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `1fb3c492423abecf1678efc4495fa6936789aa7b5d4cb6b27f33b56c4af8f8d3` |
| `21` | `WAVE5_PSRC_HOLO_BATCH_001` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `431a08641f34c7758dfe37147b5cdd0a20568871915977f9b6d4b169d741582e` |
| `22` | `WAVE5_PSRC_HOLO_BATCH_002` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `16af8f89d318abb1d05cc6f3bafc51329fe8de5ea9a83376fa6a3e4038d8626a` |
| `23` | `WAVE5_PSRC_HOLO_BATCH_003` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `8eee65c6e7db577ff260f35edf44f51fc35dcf523a3397c2009a1b259d450735` |
| `24` | `WAVE5_PSRC_HOLO_BATCH_004` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `f1f227286990bd1dc62f35ec1557fdb140eebb581b9c75ac7e23f7a52f6ef8c6` |
| `25` | `WAVE5_OTSF_HOLO_BATCH_001` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `61e0230f017a3d117391a1fde7788f4f1f6d79f35fc585ecd74f4a1892ece97e` |
| `26` | `WAVE5_OTSF_HOLO_BATCH_002` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `e8e576af96a6e796397ac7844a10fa0f5ffaa426bb370626de7d36b00921aad7` |
| `27` | `WAVE5_OTSF_HOLO_BATCH_003` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `c4fc1679b5236ca87ad1ff8c49235463dce760dc00725df51e3db1a404f7ce9d` |
| `28` | `WAVE5_OTSF_HOLO_BATCH_004` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `9ca91cb95565da0361b4505b013f4e4597bfaf63059a27f6d8ba5c48be48eb43` |

## Evidence Boundary

This handoff is not benchmark evidence. A batch becomes evidence only after a clean live run, lock validation, no-leakage audit, and readiness assertions pass for that specific batch.
