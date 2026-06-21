# D1 Capital Markets / Execution Risk Mini Scout Packet

Packet ID: `d1_capital_markets_execution_risk_001`

This folder contains a frozen no-provider source packet for the D1 capital-markets execution-risk crisis task.

Scope:
- Packet creation only.
- Real public sources plus packet case facts.
- No live artifact generation.
- No HoloBuild run.
- No solo run.
- No judging or scoring.
- No unblinding.
- No provider calls.

Primary model-visible files:
- `task_brief.md`
- `source_packet.md`
- `source_packet.json`

Validation:

```bash
python3 -B artifact_benchmarks/holo_factory/mini_scouts/d1_capital_markets_execution_risk_001/validate_packet_no_provider.py
```
