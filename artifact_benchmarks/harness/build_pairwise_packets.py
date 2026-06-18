from __future__ import annotations
import argparse, hashlib
from pathlib import Path
from common import read_json, write_json
def flip(run_id: str, domain_id: str) -> bool:
    return int(hashlib.sha256(f'{run_id}:{domain_id}'.encode('utf-8')).hexdigest()[:2], 16) % 2 == 0
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('instance_dir', type=Path); parser.add_argument('--run-id', default='stub_no_live_001'); parser.add_argument('--solo-condition', default='solo_openai'); parser.add_argument('--holo-condition', default='holo_3substrate_gov'); args = parser.parse_args()
    instance = args.instance_dir; manifest = read_json(instance / 'benchmark_manifest.json'); rubric = read_json(instance / 'prompts' / 'scoring_rubric_8criteria.json'); root = instance / 'runs' / args.run_id; sealed = {'run_id': args.run_id, 'pairs': []}
    for domain_id in manifest['domains']:
        context = read_json(instance / 'contexts' / f'{domain_id}.json'); solo = (root / 'artifacts' / domain_id / args.solo_condition / 'turn_6.md').read_text(encoding='utf-8'); holo = (root / 'artifacts' / domain_id / args.holo_condition / 'turn_6.md').read_text(encoding='utf-8')
        use_flip = flip(args.run_id, domain_id); doc_x, doc_y = (holo, solo) if use_flip else (solo, holo); map_x, map_y = (args.holo_condition, args.solo_condition) if use_flip else (args.solo_condition, args.holo_condition); packet_id = f'{args.run_id}_{domain_id}_pairwise_001'
        packet = {'judge_packet_id': packet_id, 'blind': True, 'domain_id': domain_id, 'run_id': args.run_id, 'brief': context['brief'], 'context_pack': context, 'rubric': rubric, 'documents': {'document_x': {'anonymous_id': 'X', 'text': doc_x}, 'document_y': {'anonymous_id': 'Y', 'text': doc_y}}}
        write_json(root / 'judge_packets' / f'{packet_id}.json', packet); sealed['pairs'].append({'domain_id': domain_id, 'judge_packet_id': packet_id, 'document_x_condition': map_x, 'document_y_condition': map_y})
    write_json(instance / 'sealed' / f'{args.run_id}_anonymization_map.json', sealed); print('ARTIFACT_BENCHMARK_PAIRWISE_PACKETS_CREATED'); print(f"run_id={args.run_id} packets={len(manifest['domains'])} blind=true"); return 0
if __name__ == '__main__':
    raise SystemExit(main())
