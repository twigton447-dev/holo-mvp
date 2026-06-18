from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
from common import read_json, write_json
CONDITIONS = ['solo_openai','solo_anthropic','solo_google','holo_3substrate_gov']
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('instance_dir', type=Path); parser.add_argument('--run-id', default='stub_no_live_001'); args = parser.parse_args()
    instance = args.instance_dir; manifest = read_json(instance / 'benchmark_manifest.json'); root = instance / 'runs' / args.run_id
    write_json(root / 'run_manifest.json', {'run_id': args.run_id, 'status': 'diagnostic_stub', 'live_calls_allowed': False, 'created_at_utc': datetime.now(timezone.utc).isoformat(), 'domains': manifest['domains'], 'conditions': CONDITIONS})
    for domain_id in manifest['domains']:
        for condition in CONDITIONS:
            for turn in [1, 6]:
                path = root / 'artifacts' / domain_id / condition / f'turn_{turn}.md'; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(f'# Stub Artifact\n\nDomain: {domain_id}\nCondition: {condition}\nTurn: {turn}\n', encoding='utf-8')
    print('ARTIFACT_BENCHMARK_STUB_RUN_CREATED'); print(f'run_id={args.run_id} live_calls=0'); return 0
if __name__ == '__main__':
    raise SystemExit(main())
