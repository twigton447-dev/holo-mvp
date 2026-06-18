from __future__ import annotations
import argparse
from pathlib import Path
from common import read_json
ROOT = Path(__file__).resolve().parents[1]
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('instance_dir', type=Path); args = parser.parse_args(); instance = args.instance_dir
    registry = read_json(ROOT / 'registry' / 'artifact_benchmark_registry.json')
    missing = [rel for rel in registry['required_instance_files'] if not (instance / rel).exists()]
    if missing:
        print('ARTIFACT_BENCHMARK_INSTANCE_VALIDATE_FAIL')
        for rel in missing: print(f'missing={rel}')
        return 1
    manifest = read_json(instance / 'benchmark_manifest.json'); rubric = read_json(instance / 'prompts' / 'scoring_rubric_8criteria.json')
    if manifest.get('live_calls_allowed') is not False or manifest.get('turn_budget') != 6 or manifest.get('judge_count') != 3 or len(rubric.get('criteria', [])) != 8:
        print('ARTIFACT_BENCHMARK_INSTANCE_VALIDATE_FAIL'); return 1
    print('ARTIFACT_BENCHMARK_INSTANCE_VALIDATE_PASS')
    print(f"instance={instance} domains={len(manifest['domains'])} turn_budget={manifest['turn_budget']} judges={manifest['judge_count']} live_calls=0")
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
