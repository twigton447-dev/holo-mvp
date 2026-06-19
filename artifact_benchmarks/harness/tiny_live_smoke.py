from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from artifact_validity import gov_artifact_validity_gate, require_valid_artifact
PROVIDER_ENV = {'openai': 'OPENAI_API_KEY', 'anthropic': 'ANTHROPIC_API_KEY', 'google': 'GOOGLE_API_KEY', 'xai': 'XAI_API_KEY', 'minimax': 'MINIMAX_API_KEY'}
SOLO = {'solo_openai': 'openai', 'solo_anthropic': 'anthropic', 'solo_google': 'google'}
HOLO_ANALYSTS = ['openai', 'anthropic', 'google', 'openai', 'anthropic', 'google']
HOLO_GOVS = [None, 'google', 'openai', 'anthropic', 'google', 'openai']
THIRD_PROVIDERS = ('google', 'xai', 'minimax')
def load(path: Path) -> Any: return json.loads(path.read_text(encoding='utf-8'))
def write(path: Path, payload: Any) -> None: path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, indent=2, sort_keys=False) + '\n', encoding='utf-8')
def sha(text: str) -> str: return hashlib.sha256(text.encode('utf-8')).hexdigest()
def preflight(providers: list[str] | None = None) -> dict[str, str]:
    selected = providers or ['openai', 'anthropic', 'google']
    return {PROVIDER_ENV[provider]: ('PRESENT' if os.getenv(PROVIDER_ENV[provider]) else 'MISSING') for provider in selected}
def redact(value: object) -> str: return re.sub(r'sk-[A-Za-z0-9_-]+', 'sk-REDACTED', str(value))[:500]
def third_provider(value: str) -> str:
    if value not in THIRD_PROVIDERS: raise ValueError(f'unsupported_third_provider={value}')
    return value
def solo_map(third: str) -> dict[str, str]: return {'solo_openai': 'openai', 'solo_anthropic': 'anthropic', f'solo_{third}': third}
def condition_list(third: str) -> list[str]: return [*solo_map(third).keys(), 'holo_3substrate_gov']
def holo_analysts(third: str) -> list[str]: return ['openai', 'anthropic', third, 'openai', 'anthropic', third]
def holo_govs(third: str) -> list[str | None]: return [None, third, 'openai', 'anthropic', third, 'openai']
def model_lineup(third: str, google_model: str, xai_model: str, minimax_model: str) -> dict[str, str]:
    models = {'openai': os.getenv('OPENAI_MODEL', 'gpt-5.4'), 'anthropic': os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')}
    if third == 'google': models['google'] = google_model
    elif third == 'xai': models['xai'] = xai_model
    else: models['minimax'] = minimax_model
    return models
def role(prompts: dict[str, Any], turn: int) -> dict[str, Any]: return next(item for item in prompts['turns'] if int(item['turn']) == turn)
def artifact_kind(turn: int) -> str: return 'critique' if turn in (2, 4) else ('final' if turn == 6 else 'draft')
def best(outputs: list[dict[str, str]]) -> str:
    for item in reversed(outputs):
        if item['kind'] in ('draft', 'final'): return item['text']
    return ''
def latest_critique(outputs: list[dict[str, str]]) -> str:
    for item in reversed(outputs):
        if item['kind'] == 'critique': return item['text']
    return ''
def history(outputs: list[dict[str, str]], max_chars: int = 8500) -> str:
    text = '\n\n---\n\n'.join(f"Turn {item['turn']} {item['role']} {item['kind']}\n{item['text'][:1600]}" for item in outputs); return text[-max_chars:]
def system_prompt(context: dict[str, Any], max_words: int) -> str: return f"Diagnostic artifact benchmark. Use only provided context. Do not invent facts. Output Markdown only. Keep under about {max_words} words. Domain: {context['domain_label']}."
def turn_prompt(context: dict[str, Any], role_item: dict[str, Any], turn: int, outputs: list[dict[str, str]], mission: str | None) -> str:
    final = 'FINAL TURN: produce the best possible final artifact, not another critique.\n' if turn == 6 else ''
    mission_block = f'GOVERNOR MISSION PACKET:\n{mission}\n' if mission else ''
    return f"""BRIEF:
{context['brief']}

DELIVERABLE:
{json.dumps(context['deliverable'], indent=2)}

SOURCE CONTEXT:
{json.dumps(context['source_context'], indent=2)}

GROUNDING RULE:
{context['grounding_rule']}

TURN {turn} OF 6
ROLE: {role_item['role']}
INSTRUCTION: {role_item['instruction']}
{final}{mission_block}
CURRENT BEST DRAFT:
{best(outputs) or '[none]'}

LATEST CRITIQUE:
{latest_critique(outputs) or '[none]'}

HISTORY:
{history(outputs) or '[none]'}

Execute this turn now."""
def gov_prompt(context: dict[str, Any], gov: dict[str, Any], role_item: dict[str, Any], turn: int, outputs: list[dict[str, str]]) -> str:
    fields = '\n'.join('- ' + field for field in gov['mission_packet_required_fields'])
    final = 'This mission is for Turn 6, the final document. Pressure synthesis.\n' if turn == 6 else ''
    validity = json.dumps(gov.get('artifact_validity_doctrine', {}), indent=2)
    repair_ledger = json.dumps(gov.get('repair_ledger_doctrine', {}), indent=2)
    hidden_probes = json.dumps(gov.get('hidden_failure_probe_bank', []), indent=2)
    winning_rule = gov.get('winning_feature_feedback_rule', '')
    return f"""You are HoloGov. Create a focused mission packet for the next model. Do not write the artifact and do not judge the benchmark.

Required fields:
{fields}
{final}
ARTIFACT VALIDITY DOCTRINE:
{validity}

REPAIR LEDGER DOCTRINE:
{repair_ledger}

MANDATORY HIDDEN-FAILURE PROBES:
{hidden_probes}

WINNING FEATURE PRESERVATION RULE:
{winning_rule}

BRIEF:
{context['brief']}

SOURCE CONTEXT:
{json.dumps(context['source_context'], indent=2)}

NEXT TURN {turn} OF 6
NEXT ROLE: {role_item['role']}
NEXT INSTRUCTION: {role_item['instruction']}

CURRENT BEST:
{best(outputs) or '[none]'}

LATEST CRITIQUE:
{latest_critique(outputs) or '[none]'}

HISTORY:
{history(outputs) or '[none]'}"""
def google_text(response: Any) -> str:
    text = getattr(response, 'text', None) or ''
    if text.strip(): return text
    parts = []
    try:
        for part in response.candidates[0].content.parts:
            if getattr(part, 'text', ''): parts.append(part.text)
    except Exception: pass
    return ''.join(parts)
def call_provider(provider: str, model: str, system: str, user: str, temperature: float, max_tokens: int) -> dict[str, Any]:
    start = time.time()
    if provider == 'openai':
        from openai import OpenAI
        response = OpenAI(api_key=os.getenv('OPENAI_API_KEY')).chat.completions.create(model=model, temperature=temperature, max_completion_tokens=max_tokens, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]); text = response.choices[0].message.content or ''; usage = response.usage; in_tok = usage.prompt_tokens if usage else 0; out_tok = usage.completion_tokens if usage else 0
    elif provider == 'anthropic':
        import anthropic
        response = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')).messages.create(model=model, temperature=temperature, max_tokens=max_tokens, system=system, messages=[{'role': 'user', 'content': user}]); text = response.content[0].text if response.content else ''; in_tok = response.usage.input_tokens; out_tok = response.usage.output_tokens
    elif provider == 'google':
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'), http_options={'timeout': 60000}); response = client.models.generate_content(model=model, contents=f"{system}\n\n---\n\n{user}", config=types.GenerateContentConfig(temperature=temperature, max_output_tokens=max_tokens)); text = google_text(response); usage = getattr(response, 'usage_metadata', None); in_tok = getattr(usage, 'prompt_token_count', 0) if usage else 0; out_tok = getattr(usage, 'candidates_token_count', 0) if usage else 0
    elif provider in ('xai', 'minimax'):
        from openai import OpenAI
        base_url = 'https://api.x.ai/v1' if provider == 'xai' else os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.io/v1')
        response = OpenAI(api_key=os.getenv(PROVIDER_ENV[provider]), base_url=base_url).chat.completions.create(model=model, temperature=temperature, max_tokens=max_tokens, messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]); text = response.choices[0].message.content or ''; usage = response.usage; in_tok = usage.prompt_tokens if usage else 0; out_tok = usage.completion_tokens if usage else 0
    else:
        raise ValueError(f'unsupported_provider={provider}')
    if not (text or '').strip(): raise RuntimeError(f'empty_visible_text provider={provider} model={model}')
    return {'text': text, 'input_tokens': int(in_tok or 0), 'output_tokens': int(out_tok or 0), 'latency_ms': int((time.time() - start) * 1000)}
def run_condition(root: Path, context: dict[str, Any], roles: dict[str, Any], gov: dict[str, Any], models: dict[str, str], condition: str, turn_limit: int, max_words: int, temperature: float, max_output_tokens: int = 1500, gov_max_output_tokens: int = 1000, solo_providers: dict[str, str] | None = None, holo_analyst_sequence: list[str] | None = None, holo_gov_sequence: list[str | None] | None = None) -> dict[str, Any]:
    outputs = []; calls = []; domain = context['domain_id']
    final_validity_report = None
    solo_providers = solo_providers or SOLO; holo_analyst_sequence = holo_analyst_sequence or HOLO_ANALYSTS; holo_gov_sequence = holo_gov_sequence or HOLO_GOVS
    for turn in range(1, turn_limit + 1):
        role_item = role(roles, turn); mission = None; gov_trace = None
        if condition == 'holo_3substrate_gov':
            analyst = holo_analyst_sequence[turn - 1]; gov_provider = holo_gov_sequence[turn - 1]
            if gov_provider:
                gs = 'You are HoloGov. Produce only the next mission packet.'; gu = gov_prompt(context, gov, role_item, turn, outputs); gr = call_provider(gov_provider, models[gov_provider], gs, gu, 0.1, gov_max_output_tokens); mission = gr['text']; mp = root / 'mission_packets' / domain / condition / f'turn_{turn}_mission.md'; mp.parent.mkdir(parents=True, exist_ok=True); mp.write_text(mission, encoding='utf-8'); gov_trace = {'call_type': 'governor_mission_packet', 'turn': turn, 'provider': gov_provider, 'model': models[gov_provider], 'input_tokens': gr['input_tokens'], 'output_tokens': gr['output_tokens'], 'latency_ms': gr['latency_ms'], 'system_sha256': sha(gs), 'user_sha256': sha(gu), 'output_sha256': sha(mission), 'mission_path': str(mp)}; write(root / 'traces' / domain / condition / f'gov_turn_{turn}.json', gov_trace); calls.append(gov_trace)
        else: analyst = solo_providers[condition]
        sp = system_prompt(context, max_words); up = turn_prompt(context, role_item, turn, outputs, mission); result = call_provider(analyst, models[analyst], sp, up, temperature, max_output_tokens); kind = artifact_kind(turn); ap = root / 'artifacts' / domain / condition / f'turn_{turn}.md'; ap.parent.mkdir(parents=True, exist_ok=True); ap.write_text(result['text'], encoding='utf-8')
        if ap.stat().st_size <= 0: raise RuntimeError(f'artifact_write_failed path={ap}')
        validity_report = None
        if kind == 'final':
            validity_report = gov_artifact_validity_gate(ap, context=context, fallback_max_words=max_words)
            require_valid_artifact(validity_report)
            final_validity_report = validity_report
        trace = {'call_type': 'analyst_turn', 'condition': condition, 'domain_id': domain, 'turn': turn, 'turn_limit': turn_limit, 'role': role_item['role'], 'artifact_kind': kind, 'provider': analyst, 'model': models[analyst], 'input_tokens': result['input_tokens'], 'output_tokens': result['output_tokens'], 'latency_ms': result['latency_ms'], 'system_sha256': sha(sp), 'user_sha256': sha(up), 'output_sha256': sha(result['text']), 'artifact_path': str(ap), 'governor_trace': gov_trace, 'artifact_validity_report': validity_report}; write(root / 'traces' / domain / condition / f'turn_{turn}.json', trace); calls.append(trace); outputs.append({'turn': turn, 'role': role_item['role'], 'kind': kind, 'text': result['text']})
    return {'condition': condition, 'turns_completed': turn_limit, 'calls': calls, 'final_artifact_path': str(root / 'artifacts' / domain / condition / f'turn_{turn_limit}.md'), 'final_artifact_validity_report': final_validity_report}
def backup_run(instance: Path, run_id: str, run_root: Path) -> str:
    backup = instance.parents[0] / 'backups' / run_id
    if backup.exists(): shutil.rmtree(backup)
    shutil.copytree(run_root, backup); return str(backup)
def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('instance_dir', type=Path); parser.add_argument('--domain', default='finance_board_strategy'); parser.add_argument('--run-id'); parser.add_argument('--turn-limit', type=int, default=2); parser.add_argument('--max-words', type=int, default=700); parser.add_argument('--max-output-tokens', type=int, default=1500); parser.add_argument('--gov-max-output-tokens', type=int, default=1000); parser.add_argument('--temperature', type=float, default=0.2); parser.add_argument('--third-provider', choices=THIRD_PROVIDERS, default='google'); parser.add_argument('--google-model', default='gemini-2.5-flash-lite'); parser.add_argument('--xai-model', default=os.getenv('XAI_FAST_MODEL', os.getenv('XAI_MODEL', 'grok-3-mini'))); parser.add_argument('--minimax-model', default=os.getenv('MINIMAX_MODEL', 'MiniMax-Text-01')); parser.add_argument('--preflight', action='store_true'); args = parser.parse_args(); third = third_provider(args.third_provider); env = preflight(['openai', 'anthropic', third])
    if args.preflight:
        print(json.dumps({'provider_env': env, 'python': sys.version.split()[0], 'third_provider': third, 'third_model': {'google': args.google_model, 'xai': args.xai_model, 'minimax': args.minimax_model}[third]}, indent=2, sort_keys=True)); return 0 if all(v == 'PRESENT' for v in env.values()) else 2
    if sys.version_info < (3, 11): print(json.dumps({'error': 'python_3_11_required', 'python': sys.version.split()[0]})); return 2
    if not all(v == 'PRESENT' for v in env.values()): print(json.dumps({'error': 'missing_provider_env', 'provider_env': env}, indent=2, sort_keys=True)); return 2
    instance = args.instance_dir.resolve(); manifest = load(instance / 'benchmark_manifest.json'); context = load(instance / 'contexts' / f'{args.domain}.json'); roles = load(instance / 'prompts' / 'role_prompts.json'); gov = load(instance / 'prompts' / 'gov_orchestration_prompt.json'); rid = args.run_id or 'tiny_live_' + args.domain + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'); root = instance / 'runs' / rid; root.mkdir(parents=True, exist_ok=True); models = model_lineup(third, args.google_model, args.xai_model, args.minimax_model); conditions = condition_list(third); solos = solo_map(third); analysts = holo_analysts(third); govs = holo_govs(third); started = datetime.now(timezone.utc).isoformat()
    try:
        results = [run_condition(root, context, roles, gov, models, c, args.turn_limit, args.max_words, args.temperature, args.max_output_tokens, args.gov_max_output_tokens, solos, analysts, govs) for c in conditions]; calls = [x for r in results for x in r['calls']]; expected = (3 * args.turn_limit) + args.turn_limit + max(0, args.turn_limit - 1)
        if len(calls) != expected: raise RuntimeError(f'call_count_mismatch expected={expected} observed={len(calls)}')
        for call in calls:
            if call.get('call_type') == 'analyst_turn':
                p = Path(call['artifact_path'])
                if not p.exists() or p.stat().st_size <= 0: raise RuntimeError(f'post_run_artifact_missing_or_empty path={p}')
        summary = {'run_id': rid, 'benchmark_id': manifest['benchmark_id'], 'status': 'diagnostic_tiny_live_smoke', 'benchmark_credit': False, 'public_claim': False, 'domain_id': args.domain, 'turn_limit': args.turn_limit, 'conditions': conditions, 'third_provider': third, 'started_at_utc': started, 'completed_at_utc': datetime.now(timezone.utc).isoformat(), 'provider_env': env, 'model_lineup': models, 'holo_analyst_sequence': analysts[:args.turn_limit], 'holo_governor_sequence': govs[:args.turn_limit], 'call_count': len(calls), 'expected_call_count': expected, 'total_input_tokens': sum(int(x.get('input_tokens', 0)) for x in calls), 'total_output_tokens': sum(int(x.get('output_tokens', 0)) for x in calls), 'total_latency_ms': sum(int(x.get('latency_ms', 0)) for x in calls), 'condition_results': results, 'notes': 'Tiny live smoke only. Not benchmark evidence.'}; write(root / 'run_manifest.json', summary); backup = backup_run(instance, rid, root); summary['backup_path'] = backup; write(root / 'run_manifest.json', summary); write(Path(backup) / 'run_manifest.json', summary); print(json.dumps({'status': 'ARTIFACT_TINY_LIVE_SMOKE_PASS', 'run_id': rid, 'call_count': len(calls), 'third_provider': third, 'total_input_tokens': summary['total_input_tokens'], 'total_output_tokens': summary['total_output_tokens'], 'total_latency_ms': summary['total_latency_ms'], 'run_manifest': str(root / 'run_manifest.json'), 'backup_path': backup}, indent=2, sort_keys=True)); return 0
    except Exception as exc:
        error = {'status': 'diagnostic_tiny_live_smoke_error', 'error_type': type(exc).__name__, 'error_message_excerpt': redact(exc), 'benchmark_credit': False, 'public_claim': False}; write(root / 'run_error.json', error); print(json.dumps({'status': 'ARTIFACT_TINY_LIVE_SMOKE_ERROR', 'run_id': rid, 'error_type': error['error_type'], 'error_message_excerpt': error['error_message_excerpt'], 'run_error': str(root / 'run_error.json')}, indent=2, sort_keys=True)); return 3
if __name__ == '__main__': raise SystemExit(main())
