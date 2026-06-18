from __future__ import annotations
import argparse
from pathlib import Path
from common import CRITERIA, read_json, weighted_score, write_json
def blank_score(cid: str) -> dict:
    return {'criterion_id': cid, 'score_1_5': None, 'score_1_10': None, 'notes': ''}
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('instance_dir', type=Path); parser.add_argument('--run-id', default='stub_no_live_001'); parser.add_argument('--create-blank-forms', action='store_true'); args = parser.parse_args(); root = args.instance_dir / 'runs' / args.run_id
    if args.create_blank_forms:
        count = 0
        for packet_path in sorted((root / 'judge_packets').glob('*.json')):
            packet = read_json(packet_path)
            for number in range(1, 4):
                form = {'judge_id': f'judge_{number:02d}', 'judge_packet_id': packet['judge_packet_id'], 'domain_id': packet['domain_id'], 'scores': {'document_x': {cid: blank_score(cid) for cid in CRITERIA}, 'document_y': {cid: blank_score(cid) for cid in CRITERIA}}, 'qualitative_feedback': {'document_x': '', 'document_y': '', 'comparative_notes': ''}, 'validation_flags': []}
                write_json(root / 'judge_scores' / f"{packet['judge_packet_id']}_judge_{number:02d}.json", form); count += 1
        print('ARTIFACT_BENCHMARK_JUDGE_FORMS_CREATED'); print(f'run_id={args.run_id} forms={count}'); return 0
    complete = []; incomplete = []; flags = []; rubric = read_json(args.instance_dir / 'prompts' / 'scoring_rubric_8criteria.json')
    for form_path in sorted((root / 'judge_scores').glob('*.json')):
        form = read_json(form_path)
        try:
            for doc_key in ['document_x', 'document_y']:
                for cid in CRITERIA:
                    s5 = form['scores'][doc_key][cid]['score_1_5']; s10 = form['scores'][doc_key][cid]['score_1_10']
                    if s5 is None or s10 is None: raise ValueError(f'{doc_key}.{cid} missing score')
                    if not (1 <= float(s5) <= 5 and 1 <= float(s10) <= 10): raise ValueError(f'{doc_key}.{cid} out of range')
            complete.append({'form': form_path.name, 'document_x_weighted': weighted_score(form['scores']['document_x'], rubric), 'document_y_weighted': weighted_score(form['scores']['document_y'], rubric)})
        except Exception as exc:
            incomplete.append({'form': form_path.name, 'reason': str(exc)})
    write_json(root / 'judge_score_summary.json', {'complete': complete, 'incomplete': incomplete, 'flags': flags}); print('ARTIFACT_BENCHMARK_JUDGE_FORMS_VALIDATED'); print(f'complete={len(complete)} incomplete={len(incomplete)} flags={len(flags)}'); return 0
if __name__ == '__main__':
    raise SystemExit(main())
