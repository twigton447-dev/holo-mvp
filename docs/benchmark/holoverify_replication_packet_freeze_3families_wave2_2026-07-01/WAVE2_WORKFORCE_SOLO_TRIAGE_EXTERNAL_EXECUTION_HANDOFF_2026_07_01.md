# Wave 2 Workforce Solo Triage External Execution Handoff

Purpose: run the Wave 2 Workforce solo one-shot triage outside Codex in an authorized local shell, because Codex cannot export frozen benchmark packet/prompt content to external providers.

## Scope

- Family: `HV-HRWF-REP-2026-07-01`
- Domain: HR / payroll / workforce controls
- Packets: 40
- Pairs: 20
- Expected provider calls: 120
- Gov calls: 0
- Holo calls: 0
- Judge calls: 0
- No packet edits
- No prompt edits
- No model substitution

## Lineage

- Wave 2 packet freeze commit: `c03114ed`
- Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
- Runner: `docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py`

## Required Provider Environment

The local shell must have:

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`

Do not paste provider keys into chat.

## Exact Preflight Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
python3 -m py_compile docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py
python3 -B docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py \
  --preflight \
  --family HV-HRWF-REP-2026-07-01 \
  --batch-label wave2_workforce_solo_triage
```

Preflight must show:

- `status`: `PASS`
- `expected_provider_calls`: `120`
- `expected_gov_calls`: `0`
- `expected_holo_calls`: `0`
- `expected_judge_calls`: `0`
- `openai_w2_is_gpt_5_4_mini`: `true`
- `no_gpt_4o_mini_in_triage_roster`: `true`

## Exact Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_replication_3family_wave2_solo_triage_2026_07_01.py \
  --run-live \
  --family HV-HRWF-REP-2026-07-01 \
  --batch-label wave2_workforce_solo_triage
```

## Expected Output Location

The run should create:

```text
docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/solo_triage_3mini/wave2_workforce_solo_triage/run_YYYYMMDDTHHMMSSZ/
```

Expected files:

- `SOLO_TRIAGE_PREFLIGHT.json`
- `SOLO_TRIAGE_TRACE.jsonl`
- `solo_triage_results.json`
- `solo_triage_summary.md`
- `SOLO_TRIAGE_LOCK_MANIFEST.json`
- `SOLO_TRIAGE_LOCK_VALIDATION.json`
- `prompts/*.prompt.txt`

## Pass Conditions

- Provider calls: 120 / 120
- Provider failures: none
- Gov calls: 0
- Holo calls: 0
- Judge calls: 0
- Family: only `HV-HRWF-REP-2026-07-01`
- Packet identity matches frozen Wave 2 bank
- Prompt leakage rows: none
- Active models:
  - `xai/grok-3-mini`
  - `openai/gpt-5.4-mini`
  - `minimax/MiniMax-M2.5-highspeed`

## Fail Conditions

- Any provider failure
- Any model substitution
- Any packet or prompt hash mismatch
- Any Gov/Holo/judge call
- Any prompt leakage hit
- Any run using `openai/gpt-4o-mini`

