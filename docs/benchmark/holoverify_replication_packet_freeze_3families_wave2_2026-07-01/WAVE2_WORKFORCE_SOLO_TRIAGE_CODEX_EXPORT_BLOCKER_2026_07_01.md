# Wave 2 Workforce Solo Triage Codex Export Blocker

Classification: `WAVE2_WORKFORCE_SOLO_TRIAGE_CODEX_EXPORT_BLOCKED_NO_PROVIDER_CALLS`

Codex prepared the Wave 2 Workforce solo triage lane and ran local no-provider validation, but the live provider run was blocked by tenant policy before any frozen benchmark packet or prompt content was exported to external providers.

This is not a benchmark result and not a model failure.

## Scope

- Family: `HV-HRWF-REP-2026-07-01`
- Domain: HR / payroll / workforce controls
- Frozen packet bank: `holoverify_replication_packet_freeze_3families_wave2_2026-07-01`
- Freeze root: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`
- Packets selected: 40
- Pairs selected: 20
- Truth balance: 20 ALLOW / 20 ESCALATE
- Expected solo provider calls: 120
- Gov calls: 0
- Holo calls: 0
- Judge calls: 0

## Local Validation Completed

- `py_compile`: PASS
- Workforce preflight: PASS
- Packet hashes: PASS
- Prompt hashes: PASS
- Prompt leakage rows: none
- Gov/state/baton/artifact/final-selector context in solo lane: none
- Active solo roster:
  - `xai/grok-3-mini`
  - `openai/gpt-5.4-mini`
  - `minimax/MiniMax-M2.5-highspeed`

## Blocker

Codex attempted to start the approved live Workforce solo triage command. The execution environment rejected the action because it would export private frozen benchmark packet/prompt data from the workspace to external providers.

Provider calls made from Codex: `0`

No Holo, solo, Gov, or judge live result was created in Codex.

## Next Valid Move

Run the external execution handoff from an authorized local shell/environment where sending the frozen Workforce prompts to the configured providers is permitted.

