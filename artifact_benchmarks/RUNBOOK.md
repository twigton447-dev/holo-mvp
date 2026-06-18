# Artifact Benchmark Runbook

Validate with `python3 -B artifact_benchmarks/harness/validate_structure.py` and `python3 -B artifact_benchmarks/harness/validate_instance.py artifact_benchmarks/poc_001`.

Tiny live smoke uses Python 3.11. The third substrate is configurable:

- `--third-provider google --google-model gemini-2.5-flash-lite`
- `--third-provider xai --xai-model grok-3-mini`
- `--third-provider minimax --minimax-model MiniMax-Text-01`

For current POC generation, prefer `--third-provider xai` while Gemini 2.5 Pro remains blocked. MiniMax is available as the alternate third substrate if xAI fails smoke or if the experiment calls for that provider family.
