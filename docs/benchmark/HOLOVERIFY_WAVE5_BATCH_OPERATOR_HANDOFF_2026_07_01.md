# HoloVerify Wave5 Batch Operator Handoff

Status: `PASS`
Source preflight repo/runtime: `wave5_runner=a49c0647dd933c59c853bf396d98cafd2410db18b07d9b54e11f3077ffe20b3a:base_runner=9a2d04b9c0aeb453debfbf4182d4b08857343e8844986194237a4cac5807a308`
Operator builder SHA-256: `4be1494ac860a424387002fd75c6e2e344b466bb861790161c6c4a9dee4f9a21`
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
- Approval packet SHA: `4aabf9937d7aa629ed4da512d924b99fdafc8b8a4e437df47e7fd80deff8bbc0`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 4aabf9937d7aa629ed4da512d924b99fdafc8b8a4e437df47e7fd80deff8bbc0 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_001 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
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
| `1` | `WAVE5_MEDX_HOLO_BATCH_001` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `4aabf9937d7aa629ed4da512d924b99fdafc8b8a4e437df47e7fd80deff8bbc0` |
| `2` | `WAVE5_MEDX_HOLO_BATCH_002` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `83b68cbc2c3775ed28d78e4de0045768d17ef9ab3d8de8a6f92cdb295329e0b1` |
| `3` | `WAVE5_MEDX_HOLO_BATCH_003` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `164cbbce07c402e214b36110865ea49217f5d4f30af3defbd0c8ca0d29b9f07b` |
| `4` | `WAVE5_MEDX_HOLO_BATCH_004` | `HV-MEDX-REP-2026-07-01` | `5` | `10` | `50` | `7fb34b48ae48831fb18451b6211a3ef5f420822a24908659139abe5f63e6ac2d` |
| `5` | `WAVE5_TRES_HOLO_BATCH_001` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `c8e214491cdd69ac97ec319928739146718466a54b40c3e6ed86e2ab9fed4fc0` |
| `6` | `WAVE5_TRES_HOLO_BATCH_002` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `453f3d3a322b9a0a340c2e093e9274b12ad0eb373814ac7561abae2313db563e` |
| `7` | `WAVE5_TRES_HOLO_BATCH_003` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff` |
| `8` | `WAVE5_TRES_HOLO_BATCH_004` | `HV-TRES-REP-2026-07-01` | `5` | `10` | `50` | `8e1e796543a36a4334b45a2dd9787ab2087a669901c1a92263bf3157cf52f594` |
| `9` | `WAVE5_LREG_HOLO_BATCH_001` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90` |
| `10` | `WAVE5_LREG_HOLO_BATCH_002` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `53f3c3f4d6d195ac54f57eb17e7f20564a6e1355ec1d05a87ba952615bc2979c` |
| `11` | `WAVE5_LREG_HOLO_BATCH_003` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189` |
| `12` | `WAVE5_LREG_HOLO_BATCH_004` | `HV-LREG-REP-2026-07-01` | `5` | `10` | `50` | `72c594069a80c601b15c3525700a57d22b2953081748d0aecb52596e0e3b9fb5` |
| `13` | `WAVE5_CLAD_HOLO_BATCH_001` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `fe4c710403b9158fccb4ff4611904cec3f687f66c9969a7a3dc730f3d592d307` |
| `14` | `WAVE5_CLAD_HOLO_BATCH_002` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad` |
| `15` | `WAVE5_CLAD_HOLO_BATCH_003` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `9d730b21da1013a3664299342ef1e6e338c2bd0b8c45c7f46ec6cbeb660d10be` |
| `16` | `WAVE5_CLAD_HOLO_BATCH_004` | `HV-CLAD-REP-2026-07-01` | `5` | `10` | `50` | `cdac66ca9081ca18cdef03b914db281e5ff71633f33970acc042688419479f5d` |
| `17` | `WAVE5_SECO_HOLO_BATCH_001` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `578a0f03efb8c741e24ea89b6621a6e27f409dc3b0d5ce344141555032a9632a` |
| `18` | `WAVE5_SECO_HOLO_BATCH_002` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `398bd98cc7b9892c8272fea8627886122c25ca573ac5eb1ab80cd330af0f1657` |
| `19` | `WAVE5_SECO_HOLO_BATCH_003` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `279e58a9a6f76420bea21e307083a5c65f36867a0a7a96c157a6c50d2136ee04` |
| `20` | `WAVE5_SECO_HOLO_BATCH_004` | `HV-SECO-REP-2026-07-01` | `5` | `10` | `50` | `78b8cc0be4c9b6933e7328ef795e859c5a7a153b1ed472ecdee6eb9458c3bce8` |
| `21` | `WAVE5_PSRC_HOLO_BATCH_001` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `923a2f8c218f1ca503dc74d3d7f896bec100d7bdacec5d317b1f9207a7c2bca8` |
| `22` | `WAVE5_PSRC_HOLO_BATCH_002` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `2f4862937b1cd633d98f828667e44b3771c812a5ff786640a3c5f3e378c03a7e` |
| `23` | `WAVE5_PSRC_HOLO_BATCH_003` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `5fbc27082b0f6315fd91f9282566dccdd907f70720f490533f7682d6cb1c7ab2` |
| `24` | `WAVE5_PSRC_HOLO_BATCH_004` | `HV-PSRC-REP-2026-07-01` | `5` | `10` | `50` | `b79a323256eeb7ffa971e3d73d9d7816f80a9bd0e8687cefed782a1ff31743fe` |
| `25` | `WAVE5_OTSF_HOLO_BATCH_001` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `260a9fbaeee1d6461c21ce04ad3f5e35011a9763a338812f5cce9a704e3fa320` |
| `26` | `WAVE5_OTSF_HOLO_BATCH_002` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `ce195d664177fed19fc531d9ac7a6ad39e6fadfdfe496842cf9069b8f4220b99` |
| `27` | `WAVE5_OTSF_HOLO_BATCH_003` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `d271ce89608d8beada106c7596457c95174978c3c2e147e242ce40b3db363291` |
| `28` | `WAVE5_OTSF_HOLO_BATCH_004` | `HV-OTSF-REP-2026-07-01` | `5` | `10` | `50` | `a2f793112787096e9b39f2559527962b938a9e5fa529acf1b497d2851cd6f794` |

## Evidence Boundary

This handoff is not benchmark evidence. A batch becomes evidence only after a clean live run, lock validation, no-leakage audit, and readiness assertions pass for that specific batch.
