# Wave 2 3-Family Solo Triage External Execution Handoff

Purpose: run solo one-shot triage for the three Wave 2 frozen families outside Codex, because Codex cannot export frozen benchmark packet/prompt content to external providers.

## Scope

- Families:
  - `HV-HRWF-REP-2026-07-01` — HR / payroll / workforce controls
  - `HV-DPRV-REP-2026-07-01` — Data privacy / customer data release controls
  - `HV-FINC-REP-2026-07-01` — Finance close / revenue / expense recognition controls
- Frozen packet bank: `holoverify_replication_packet_freeze_3families_wave2_2026-07-01`
- Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
- Packet freeze commit: `c03114ed`
- Packets per family: 40
- Pairs per family: 20
- Expected solo provider calls per family: 120
- Expected solo provider calls for all three families: 360
- Gov calls: 0
- Holo calls: 0
- Judge calls: 0
- No packet edits
- No prompt edits
- No model substitution

## Solo Roster

- `xai/grok-3-mini`
- `openai/gpt-5.4-mini`
- `minimax/MiniMax-M2.5-highspeed`

Required env vars:

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`

Do not paste provider keys into chat.

## Local Preflight Status

Codex no-provider preflight passed for each individual family and for all three families together.

All-family preflight shape:

- Status: `PASS`
- Packets: 120
- Pairs: 60
- Truth balance: 60 ALLOW / 60 ESCALATE
- Expected provider calls: 360
- Expected Gov calls: 0
- Expected Holo calls: 0
- Expected judge calls: 0
- OpenAI model: `gpt-5.4-mini`
- `gpt-4o-mini` absent from triage roster
- Prompt leakage rows: none

## Run Order

Run Workforce first. After it completes and is inspected, run Data Privacy. After Data Privacy completes and is inspected, run Finance.

## Workforce Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py \
  --run-live \
  --family HV-HRWF-REP-2026-07-01 \
  --batch-label wave2_workforce_solo_triage
```

## Data Privacy Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py \
  --run-live \
  --family HV-DPRV-REP-2026-07-01 \
  --batch-label wave2_data_privacy_solo_triage
```

## Finance Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py \
  --run-live \
  --family HV-FINC-REP-2026-07-01 \
  --batch-label wave2_finance_close_solo_triage
```

## Expected Output Paths

```text
docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_workforce_solo_triage/run_*/
docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_data_privacy_solo_triage/run_*/
docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_finance_close_solo_triage/run_*/
```

Each completed run should contain:

- `SOLO_TRIAGE_PREFLIGHT.json`
- `SOLO_TRIAGE_TRACE.jsonl`
- `solo_triage_results.json`
- `solo_triage_summary.md`
- `SOLO_TRIAGE_LOCK_MANIFEST.json`
- `SOLO_TRIAGE_LOCK_VALIDATION.json`
- `prompts/*.prompt.txt`

## Pass Conditions Per Family

- Provider calls: 120 / 120
- Provider failures: none
- Gov calls: 0
- Holo calls: 0
- Judge calls: 0
- Packet identity matches Wave 2 freeze
- Prompt leakage rows: none
- Active models exactly match the solo roster above

## Fail Conditions

- Provider failure
- Model substitution
- Packet hash mismatch
- Prompt hash mismatch
- Gov/Holo/judge call present
- Prompt leakage hit
- `openai/gpt-4o-mini` used

