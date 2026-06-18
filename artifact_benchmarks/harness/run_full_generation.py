from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tiny_live_smoke import THIRD_PROVIDERS, backup_run, condition_list, holo_analysts, holo_govs, load, model_lineup, preflight, redact, run_condition, solo_map, third_provider, write


def expected_calls(turn_limit: int) -> int:
    return (3 * turn_limit) + turn_limit + max(0, turn_limit - 1)


def totals(calls: list[dict[str, Any]]) -> dict[str, int]:
    return {
        'call_count': len(calls),
        'total_input_tokens': sum(int(item.get('input_tokens', 0)) for item in calls),
        'total_output_tokens': sum(int(item.get('output_tokens', 0)) for item in calls),
        'total_latency_ms': sum(int(item.get('latency_ms', 0)) for item in calls),
    }


def write_manifest(root: Path, payload: dict[str, Any]) -> None:
    write(root / 'run_manifest.json', payload)


def validate_artifacts(calls: list[dict[str, Any]]) -> None:
    for call in calls:
        if call.get('call_type') != 'analyst_turn':
            continue
        path = Path(call['artifact_path'])
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f'post_run_artifact_missing_or_empty path={path}')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('instance_dir', type=Path)
    parser.add_argument('--domains', nargs='*')
    parser.add_argument('--run-id')
    parser.add_argument('--turn-limit', type=int)
    parser.add_argument('--max-words', type=int)
    parser.add_argument('--max-output-tokens', type=int, default=2600)
    parser.add_argument('--gov-max-output-tokens', type=int, default=1400)
    parser.add_argument('--temperature', type=float, default=0.2)
    parser.add_argument('--third-provider', choices=THIRD_PROVIDERS, default='xai')
    parser.add_argument('--google-model', default='gemini-2.5-flash-lite')
    parser.add_argument('--xai-model', default=os.getenv('XAI_FAST_MODEL', os.getenv('XAI_MODEL', 'grok-3-mini')))
    parser.add_argument('--minimax-model', default=os.getenv('MINIMAX_MODEL', 'MiniMax-Text-01'))
    parser.add_argument('--allow-live-poc', action='store_true')
    parser.add_argument('--preflight', action='store_true')
    args = parser.parse_args()

    third = third_provider(args.third_provider)
    env = preflight(['openai', 'anthropic', third])
    if args.preflight:
        print(json.dumps({'provider_env': env, 'python': sys.version.split()[0], 'third_provider': third, 'third_model': {'google': args.google_model, 'xai': args.xai_model, 'minimax': args.minimax_model}[third]}, indent=2, sort_keys=True))
        return 0 if all(value == 'PRESENT' for value in env.values()) else 2

    if sys.version_info < (3, 11):
        print(json.dumps({'error': 'python_3_11_required', 'python': sys.version.split()[0]}))
        return 2
    if not all(value == 'PRESENT' for value in env.values()):
        print(json.dumps({'error': 'missing_provider_env', 'provider_env': env}, indent=2, sort_keys=True))
        return 2
    if not args.allow_live_poc:
        print(json.dumps({'error': 'allow_live_poc_required', 'reason': 'manifest POC keeps live_calls_allowed=false by default'}, indent=2, sort_keys=True))
        return 2

    instance = args.instance_dir.resolve()
    manifest = load(instance / 'benchmark_manifest.json')
    roles = load(instance / 'prompts' / 'role_prompts.json')
    gov = load(instance / 'prompts' / 'gov_orchestration_prompt.json')

    domains = args.domains or list(manifest['domains'])
    turn_limit = int(args.turn_limit or manifest['turn_budget'])
    max_words = int(args.max_words or manifest['word_count_target']['max'])
    analysts = holo_analysts(third)
    govs = holo_govs(third)
    solos = solo_map(third)
    conditions = condition_list(third)
    if turn_limit > len(analysts):
        print(json.dumps({'error': 'turn_limit_exceeds_holo_sequence', 'turn_limit': turn_limit, 'max_supported': len(analysts)}, indent=2, sort_keys=True))
        return 2
    unknown = [domain for domain in domains if domain not in manifest['domains']]
    if unknown:
        print(json.dumps({'error': 'unknown_domains', 'domains': unknown}, indent=2, sort_keys=True))
        return 2

    rid = args.run_id or 'poc_full_generation_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    root = instance / 'runs' / rid
    root.mkdir(parents=True, exist_ok=True)
    backup_path = str(instance.parents[0] / 'backups' / rid)
    started = datetime.now(timezone.utc).isoformat()
    models = model_lineup(third, args.google_model, args.xai_model, args.minimax_model)

    completed_domains: list[str] = []
    failed_domains: list[dict[str, str]] = []
    all_calls: list[dict[str, Any]] = []
    domain_results: list[dict[str, Any]] = []
    expected_total = expected_calls(turn_limit) * len(domains)

    def manifest_payload(status: str) -> dict[str, Any]:
        aggregate = totals(all_calls)
        return {
            'run_id': rid,
            'benchmark_id': manifest['benchmark_id'],
            'status': status,
            'benchmark_credit': False,
            'public_claim': False,
            'approval_mode': 'live_poc_generation_explicitly_allowed',
            'domains_requested': domains,
            'completed_domains': completed_domains,
            'failed_domains': failed_domains,
            'turn_limit': turn_limit,
            'conditions': conditions,
            'third_provider': third,
            'started_at_utc': started,
            'updated_at_utc': datetime.now(timezone.utc).isoformat(),
            'provider_env': env,
            'model_lineup': models,
            'holo_analyst_sequence': analysts[:turn_limit],
            'holo_governor_sequence': govs[:turn_limit],
            'expected_call_count': expected_total,
            'call_count': aggregate['call_count'],
            'total_input_tokens': aggregate['total_input_tokens'],
            'total_output_tokens': aggregate['total_output_tokens'],
            'total_latency_ms': aggregate['total_latency_ms'],
            'max_words': max_words,
            'max_output_tokens': args.max_output_tokens,
            'gov_max_output_tokens': args.gov_max_output_tokens,
            'domain_results': domain_results,
            'backup_path': backup_path,
            'notes': 'POC full generation only. Not locked benchmark credit and not a public claim until judge packets, scoring, and anonymization are complete.',
        }

    try:
        write_manifest(root, manifest_payload('poc_full_generation_running'))
        for domain_id in domains:
            context = load(instance / 'contexts' / f'{domain_id}.json')
            domain_started = datetime.now(timezone.utc).isoformat()
            results = [
                run_condition(root, context, roles, gov, models, condition, turn_limit, max_words, args.temperature, args.max_output_tokens, args.gov_max_output_tokens, solos, analysts, govs)
                for condition in conditions
            ]
            calls = [call for result in results for call in result['calls']]
            expected_domain = expected_calls(turn_limit)
            if len(calls) != expected_domain:
                raise RuntimeError(f'call_count_mismatch domain={domain_id} expected={expected_domain} observed={len(calls)}')
            validate_artifacts(calls)
            all_calls.extend(calls)
            completed_domains.append(domain_id)
            domain_summary = {
                'domain_id': domain_id,
                'status': 'complete',
                'started_at_utc': domain_started,
                'completed_at_utc': datetime.now(timezone.utc).isoformat(),
                'expected_call_count': expected_domain,
                **totals(calls),
                'condition_results': results,
            }
            domain_results.append(domain_summary)
            write(root / 'domain_manifests' / f'{domain_id}.json', domain_summary)
            write_manifest(root, manifest_payload('poc_full_generation_running'))
            backup_run(instance, rid, root)

        final_payload = manifest_payload('poc_full_generation_complete')
        final_payload['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        if final_payload['call_count'] != expected_total:
            raise RuntimeError(f'total_call_count_mismatch expected={expected_total} observed={final_payload["call_count"]}')
        write_manifest(root, final_payload)
        backup_run(instance, rid, root)
        print(json.dumps({'status': 'ARTIFACT_POC_FULL_GENERATION_PASS', 'run_id': rid, 'domains_completed': completed_domains, 'call_count': final_payload['call_count'], 'expected_call_count': expected_total, 'total_input_tokens': final_payload['total_input_tokens'], 'total_output_tokens': final_payload['total_output_tokens'], 'total_latency_ms': final_payload['total_latency_ms'], 'run_manifest': str(root / 'run_manifest.json'), 'backup_path': backup_path}, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        failed_domains.append({'domain_id': domains[len(completed_domains)] if len(completed_domains) < len(domains) else 'unknown', 'error_type': type(exc).__name__, 'error_message_excerpt': redact(exc)})
        error = {'status': 'poc_full_generation_error', 'error_type': type(exc).__name__, 'error_message_excerpt': redact(exc), 'completed_domains': completed_domains, 'benchmark_credit': False, 'public_claim': False}
        write(root / 'run_error.json', error)
        write_manifest(root, manifest_payload('poc_full_generation_incomplete'))
        backup_run(instance, rid, root)
        print(json.dumps({'status': 'ARTIFACT_POC_FULL_GENERATION_ERROR', 'run_id': rid, 'completed_domains': completed_domains, 'error_type': error['error_type'], 'error_message_excerpt': error['error_message_excerpt'], 'run_error': str(root / 'run_error.json'), 'backup_path': backup_path}, indent=2, sort_keys=True))
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
