from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['README.md','ARTIFACT_BENCHMARK_MANDATE.md','RUNBOOK.md','CHECKLIST.md','GEMINI_25_PRO_BLOCKED_NOTE.md','registry/artifact_benchmark_registry.json','harness/common.py','harness/validate_instance.py','harness/generate_stub_run.py','harness/build_pairwise_packets.py','harness/judge_harness.py','harness/tiny_live_smoke.py']
def main() -> int:
    missing = [rel for rel in REQUIRED if not (ROOT / rel).exists()]
    if missing:
        print('ARTIFACT_BENCHMARK_STRUCTURE_VALIDATE_FAIL')
        for rel in missing: print(f'missing={rel}')
        return 1
    for path in ROOT.rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8'))
    mandate = (ROOT / 'ARTIFACT_BENCHMARK_MANDATE.md').read_text(encoding='utf-8')
    for term in ['ARTIFACT_BENCHMARK_MANDATE_V1','Gov mission packet','loop_uplift','holo_advantage','Diagnostic POC not benchmark credit']:
        if term not in mandate:
            print('ARTIFACT_BENCHMARK_STRUCTURE_VALIDATE_FAIL')
            print(f'missing_mandate_term={term}')
            return 1
    print('ARTIFACT_BENCHMARK_STRUCTURE_VALIDATE_PASS')
    print('mandate=ARTIFACT_BENCHMARK_MANDATE_V1 live_calls=0')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
