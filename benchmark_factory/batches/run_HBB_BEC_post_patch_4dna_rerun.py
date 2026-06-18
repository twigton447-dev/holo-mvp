from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmark_factory.batches import run_BAL100_BATCH_001_five_mini_scout as provider_core
from holo_builder.frozen_4dna_runner import (
    FORBIDDEN_MODEL_VISIBLE_KEYS,
    build_pair_dry_run_report,
    load_available_mini_pool,
    load_frozen_packet_for_dry_run,
    select_4dna_roster,
)


RUN_ID = "HBB-BEC-post-patch-4dna-seed447-rerun"
RUN_TYPE = "hbb_bec_post_patch_4dna_rerun"
SEED = 447
COHORT_PATH = Path("ablation_cohort_mini.json")
OUT_DIR = Path("scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun")
PREFLIGHT_JSON_PATH = Path("reports/HBB_BEC_post_patch_rerun_preflight.json")
APPROVAL_ENV = "HBB_BEC_POST_PATCH_RERUN_APPROVED"
APPROVAL_VALUE = "I_APPROVE_PROVIDER_TRANSMISSION"
CODEX_APPROVAL_ENV = "HBB_BEC_CODEX_POST_PATCH_RERUN_APPROVED"
CODEX_APPROVAL_VALUE = "I_APPROVE_CODEX_PROVIDER_TRANSMISSION"
CO_ENV_MARKERS = (
    "CODEX_SANDBOX",
    "CODEX_THREAD_ID",
    "CODEX_CI",
    "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
)

EXPECTED_FAMILIES = [
    {
        "family_id": "HBB-BEC-001",
        "session_id": "HBB-BEC-001_pair_4dna_seed447_post_patch",
        "original_trace_directory": "traces/HBB-BEC-001_pair_4dna_seed447/",
        "judge_pointer": "reports/HBB_BEC_001_pair_4dna_seed447_judge_summary.json",
        "autopsy_pointer": "reports/HBB_BEC_001_seed447_hologov_loss_autopsy.json",
        "packets": [
            {
                "role": "ALLOW",
                "packet_id": "HBB-BEC-001",
                "path": "holo_builder/outputs/frozen/HBB-BEC-001_8181d83c.json",
                "hash": "8181d83ceb7f36f97160f078a4d4d35bdced5555fba5478c55bd3d954f40c4f1",
            },
            {
                "role": "ESCALATE",
                "packet_id": "HBB-BEC-001-CALLBACK-PROVENANCE-FAIL",
                "path": "holo_builder/outputs/frozen/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc.json",
                "hash": "807468fcba476a97ef92cf4058af0767c73a66a450bda37c60c6bfaa8be5e883",
            },
        ],
    },
    {
        "family_id": "HBB-BEC-002-HARD",
        "session_id": "HBB-BEC-002_hard_pair_4dna_seed447_post_patch",
        "original_trace_directory": "traces/HBB-BEC-002_hard_pair_4dna_seed447/",
        "judge_pointer": "reports/HBB_BEC_002_hard_pair_4dna_seed447_judge_summary.json",
        "autopsy_pointer": "reports/HBB_BEC_002_seed447_hologov_loss_autopsy.json",
        "packets": [
            {
                "role": "ALLOW",
                "packet_id": "HBB-BEC-002-HARD-ALLOW",
                "path": "holo_builder/outputs/frozen/HBB-BEC-002-HARD-ALLOW_f7986fa2.json",
                "hash": "f7986fa2d852183033f1596780f9a763da803f61490af0b18d439d73ba5810d5",
            },
            {
                "role": "ESCALATE",
                "packet_id": "HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL",
                "path": "holo_builder/outputs/frozen/HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL_0151f5e6.json",
                "hash": "0151f5e643eb27d56d879b6b12b66ae9bcbebd962e2ce7a014c51e17ee68b4cf",
            },
        ],
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv()


def _git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return ""
    return result.stdout.strip()


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def _prompt_patch_block(start_marker: str, end_marker: str) -> str:
    text = Path("llm_adapters.py").read_text()
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end].strip()


def analyst_system_prompt() -> str:
    patch_rules = _prompt_patch_block(
        "VENDOR-MASTER CALLBACK PROVENANCE RULE:",
        "=== INTEGRITY RULE",
    )
    return f"""You are an active 4DNA analyst in a post-patch frozen-pair rerun.
You see only the frozen model-visible payload action/context and must assess whether AP may release the payment.

Use the patched HBB BEC doctrine below as controlling guidance:

{patch_rules}

Return only a compact JSON object with keys: verdict, material_blocker, evidence, reasoning.
verdict must be ALLOW or ESCALATE.
material_blocker must be null for ALLOW, or a concise blocker label for ESCALATE.
evidence must be a list of exact artifact IDs, field names, or short source-grounded facts.
reasoning must be 1-4 concise sentences.
No markdown, no code fences, no prose outside JSON.
"""


def gov_system_prompt() -> str:
    patch_rules = _prompt_patch_block(
        "VENDOR-MASTER CALLBACK PROVENANCE: In vendor-master payment/contact change",
        "EXCULPATORY CONTEXT:",
    )
    return f"""You are HoloGov in a post-patch frozen-pair 4DNA rerun.
You receive the same frozen model-visible action/context plus the active non-Gov analyst responses.
Your job is to issue the final ALLOW or ESCALATE ruling while applying the patched HBB BEC doctrine.

Use the patched Governor guidance below as controlling guidance:

{patch_rules}

Return only a compact JSON object with keys: final_verdict, controlling_reason, analyst_disagreements, cited_evidence.
final_verdict must be ALLOW or ESCALATE.
analyst_disagreements must be a list, possibly empty.
cited_evidence must be a list of exact artifact IDs, field names, or short source-grounded facts.
No markdown, no code fences, no prose outside JSON.
"""


def _in_codex_environment() -> bool:
    return any(os.getenv(marker) for marker in CO_ENV_MARKERS)


def _all_expected_packet_records() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for family in EXPECTED_FAMILIES:
        for packet in family["packets"]:
            records.append(
                {
                    "family_id": family["family_id"],
                    "session_id": family["session_id"],
                    "role": packet["role"],
                    "packet_id": packet["packet_id"],
                    "path": packet["path"],
                    "hash": packet["hash"],
                }
            )
    return records


def expected_packet_hash_mapping() -> dict[str, dict[str, str]]:
    return {
        record["packet_id"]: {
            "family_id": record["family_id"],
            "role": record["role"],
            "path": record["path"],
            "payload_hash": record["hash"],
            "hash8": record["hash"][:8],
        }
        for record in _all_expected_packet_records()
    }


def _preflight_frozen_hashes() -> dict[str, str]:
    if not PREFLIGHT_JSON_PATH.exists():
        raise SystemExit(f"{PREFLIGHT_JSON_PATH} is required.")
    preflight = _load_json(PREFLIGHT_JSON_PATH)
    hashes: dict[str, str] = {}
    for family in preflight.get("families", []):
        hashes.update({str(k): str(v) for k, v in family.get("frozen_hashes", {}).items()})
    return hashes


def validate_approved_scope(records: list[dict[str, str]]) -> None:
    expected = _all_expected_packet_records()
    expected_tuples = [(r["family_id"], r["packet_id"], r["path"], r["hash"], r["role"]) for r in expected]
    observed_tuples = [(r["family_id"], r["packet_id"], r["path"], r["hash"], r["role"]) for r in records]
    if observed_tuples != expected_tuples:
        raise SystemExit(f"HBB post-patch rerun scope mismatch: {observed_tuples}")

    preflight_hashes = _preflight_frozen_hashes()
    missing_or_changed = [
        record["packet_id"]
        for record in records
        if preflight_hashes.get(record["packet_id"]) != record["hash"]
    ]
    if missing_or_changed:
        raise SystemExit(f"Preflight-approved hash mismatch for packets: {missing_or_changed}")

    family_ids = [record["family_id"] for record in records]
    if family_ids != ["HBB-BEC-001", "HBB-BEC-001", "HBB-BEC-002-HARD", "HBB-BEC-002-HARD"]:
        raise SystemExit(f"Unexpected HBB family scope: {family_ids}")


def load_approved_frozen_packets() -> list[dict[str, Any]]:
    records = _all_expected_packet_records()
    validate_approved_scope(records)
    packets = []
    for record in records:
        loaded = load_frozen_packet_for_dry_run(record["path"], record["hash"])
        if loaded["scenario_id"] != record["packet_id"]:
            raise SystemExit(f"{record['path']}: scenario_id mismatch.")
        loaded.update(
            {
                "family_id": record["family_id"],
                "session_id": record["session_id"],
                "role": record["role"],
            }
        )
        packets.append(loaded)
    return packets


def build_roster(session_id: str) -> dict[str, Any]:
    pool = load_available_mini_pool(COHORT_PATH)
    roster = select_4dna_roster(pool, seed=SEED, session_id=session_id)
    active_providers = [model["provider"] for model in roster["active_non_gov"]]
    if roster["holo_gov"]["provider"] != "openai":
        raise SystemExit("Seed447 HBB rerun must keep OpenAI as HoloGov.")
    if active_providers != ["xai", "google", "minimax"]:
        raise SystemExit(f"Seed447 active non-Gov roster mismatch: {active_providers}")
    if [model["provider"] for model in roster["excluded"]] != ["anthropic"]:
        raise SystemExit("Seed447 HBB rerun must keep Anthropic excluded.")
    return roster


def _transport_provider(roster_provider: str) -> str:
    return "gemini" if roster_provider == "google" else roster_provider


def _transport_model(roster_model: dict[str, str]) -> dict[str, str]:
    transport_provider = _transport_provider(roster_model["provider"])
    for model in provider_core.MODELS:
        if model["provider"] == transport_provider and model["model"] == roster_model["model"]:
            return dict(model)
    raise SystemExit(f"No transport model for roster model {roster_model}")


def active_roster_models(roster: dict[str, Any]) -> list[dict[str, str]]:
    return [dict(model) for model in roster["active_non_gov"]]


def expected_call_count() -> int:
    return len(_all_expected_packet_records()) * 4


def _model_visible_user(packet: dict[str, Any]) -> str:
    return json.dumps(packet["model_visible"], sort_keys=True)


def _safe_model_name(model: str) -> str:
    return model.replace("/", "_").replace(" ", "_")


def _active_prompt_card(packet: dict[str, Any], roster_model: dict[str, str]) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "post_patch_rerun": True,
        "original_trace": False,
        "official_trace": False,
        "judge_truth": False,
        "freeze": False,
        "packet_id": packet["scenario_id"],
        "packet_hash": packet["payload_hash"],
        "hash8": packet["hash8"],
        "family_id": packet["family_id"],
        "packet_role": packet["role"],
        "provider": roster_model["provider"],
        "transport_provider": _transport_provider(roster_model["provider"]),
        "model": roster_model["model"],
        "role": "active_non_gov",
        "system": analyst_system_prompt(),
        "user": _model_visible_user(packet),
    }


def _gov_prompt_card(
    packet: dict[str, Any],
    roster_model: dict[str, str],
    active_records: list[dict[str, Any]],
) -> dict[str, Any]:
    analyst_responses = [
        {
            "provider": record["provider"],
            "model": record["model"],
            "provider_call_ok": record["provider_call_ok"],
            "parse_ok": record["parse_ok"],
            "verdict": record.get("verdict", "ERROR"),
            "material_blocker": record.get("material_blocker"),
            "evidence": record.get("evidence", []),
            "reasoning": record.get("reasoning", ""),
            "raw_text_excerpt": record.get("raw_text_excerpt", ""),
        }
        for record in active_records
    ]
    return {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "post_patch_rerun": True,
        "original_trace": False,
        "official_trace": False,
        "judge_truth": False,
        "freeze": False,
        "packet_id": packet["scenario_id"],
        "packet_hash": packet["payload_hash"],
        "hash8": packet["hash8"],
        "family_id": packet["family_id"],
        "packet_role": packet["role"],
        "provider": roster_model["provider"],
        "transport_provider": _transport_provider(roster_model["provider"]),
        "model": roster_model["model"],
        "role": "holo_gov",
        "system": gov_system_prompt(),
        "user": json.dumps(
            {
                "action": packet["model_visible"]["action"],
                "context": packet["model_visible"]["context"],
                "active_non_gov_responses": analyst_responses,
            },
            sort_keys=True,
        ),
    }


def build_prompt_cards(out_dir: Path = OUT_DIR) -> dict[str, Any]:
    packets = load_approved_frozen_packets()
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir = out_dir / "prompt_cards"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    cards = []
    for packet in packets:
        roster = build_roster(packet["session_id"])
        for roster_model in active_roster_models(roster):
            card = _active_prompt_card(packet, roster_model)
            cards.append(card)
            path = prompt_dir / f"{packet['scenario_id']}__{roster_model['provider']}__{_safe_model_name(roster_model['model'])}.json"
            path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")

        gov_card = _gov_prompt_card(packet, roster["holo_gov"], [])
        cards.append(gov_card)
        gov_path = prompt_dir / f"{packet['scenario_id']}__hologov__{_safe_model_name(roster['holo_gov']['model'])}.json"
        gov_path.write_text(json.dumps(gov_card, indent=2, sort_keys=True) + "\n")

    plan = {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "execution_mode": "plan_only_no_live",
        "provider_calls_performed_by_script": False,
        "post_patch_rerun": True,
        "original_trace": False,
        "official_trace": False,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "families": [family["family_id"] for family in EXPECTED_FAMILIES],
        "packet_hash_mapping": expected_packet_hash_mapping(),
        "rosters": {family["session_id"]: build_roster(family["session_id"]) for family in EXPECTED_FAMILIES},
        "packets": len(packets),
        "expected_row_count": expected_call_count(),
        "prompt_cards": len(cards),
        "expected_output_directory": str(out_dir),
        "expected_live_outputs": [
            str(out_dir / "results.jsonl"),
            str(out_dir / "summary.json"),
            str(out_dir / "post_patch_rerun_records"),
        ],
        "stop_conditions": stop_conditions(),
        "proof_credit_remains_unchanged": True,
    }
    (out_dir / "rerun_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return plan


def stop_conditions() -> list[str]:
    return [
        "Any selected packet path or payload hash differs from the preflight-approved HBB records.",
        "Any family outside HBB-BEC-001 or HBB-BEC-002-HARD is selected.",
        "Any frozen packet fails the build_freeze_manifest hash and payload-visibility contract.",
        "Seed447 roster differs from OpenAI HoloGov plus xAI/Gemini/MiniMax active non-Gov and Anthropic excluded.",
        "Provider execution requested without explicit HBB post-patch approval gates.",
        "Output directory already exists for live execution.",
        "Expected row count differs from 4 frozen packets x 4 active 4DNA calls = 16.",
    ]


def _require_execution_approval(args: argparse.Namespace) -> str:
    _load_dotenv_if_available()
    if args.operator != "Taylor":
        raise SystemExit("--operator Taylor is required for HBB post-patch rerun execution.")
    if not args.yes_send_frozen_payloads_to_providers:
        raise SystemExit("--yes-send-frozen-payloads-to-providers is required.")

    if _in_codex_environment():
        if not args.allow_codex_provider_calls:
            raise SystemExit("--allow-codex-provider-calls is required for Taylor-approved Codex/Co rerun execution.")
        if os.getenv(APPROVAL_ENV) != APPROVAL_VALUE:
            raise SystemExit(f"{APPROVAL_ENV}={APPROVAL_VALUE} is required.")
        if os.getenv(CODEX_APPROVAL_ENV) != CODEX_APPROVAL_VALUE:
            raise SystemExit(f"{CODEX_APPROVAL_ENV}={CODEX_APPROVAL_VALUE} is required.")
        execution_mode = "codex_approved"
    else:
        if not args.i_am_taylor_local:
            raise SystemExit("--i-am-taylor-local is required for Taylor-local rerun execution.")
        if os.getenv(APPROVAL_ENV) != APPROVAL_VALUE:
            raise SystemExit(f"{APPROVAL_ENV}={APPROVAL_VALUE} is required.")
        execution_mode = "taylor_local"

    required_models = []
    for family in EXPECTED_FAMILIES:
        roster = build_roster(family["session_id"])
        required_models.extend(active_roster_models(roster))
        required_models.append(roster["holo_gov"])
    missing = sorted(
        {
            _transport_model(model)["api_key_env"]
            for model in required_models
            if not os.getenv(_transport_model(model)["api_key_env"])
        }
    )
    if missing:
        raise SystemExit("Missing API key environment variables: " + ", ".join(missing))
    return execution_mode


def _extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    candidates = [stripped]
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if fenced:
        candidates.insert(0, fenced.group(1))
    braced = re.search(r"(\{.*\})", stripped, flags=re.DOTALL)
    if braced:
        candidates.append(braced.group(1))

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _normalize_verdict(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text in {"ALLOW", "APPROVE", "APPROVED", "YES", "Y"}:
        return "ALLOW"
    if text in {"ESCALATE", "BLOCK", "BLOCKED", "NO", "N"}:
        return "ESCALATE"
    if "NOT BE RELEASED" in text or "SHOULD NOT" in text or "ESCALAT" in text:
        return "ESCALATE"
    if "CAN BE RELEASED" in text or "MAY RELEASE" in text or "ALLOW" in text:
        return "ALLOW"
    return "UNCLEAR"


def _parse_active_response(raw_text: str) -> dict[str, Any]:
    parsed = _extract_json_object(raw_text)
    if not parsed:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "parse_error": "No JSON object found in provider response.",
        }
    verdict = _normalize_verdict(parsed.get("verdict"))
    if verdict not in {"ALLOW", "ESCALATE"}:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "parse_error": f"Parsed active analyst verdict was not ALLOW/ESCALATE: {parsed.get('verdict')!r}",
            "parsed_json": parsed,
        }
    return {
        "parse_ok": True,
        "verdict": verdict,
        "material_blocker": parsed.get("material_blocker"),
        "evidence": parsed.get("evidence", []),
        "reasoning": str(parsed.get("reasoning", "")).strip(),
        "parsed_json": parsed,
    }


def _parse_gov_response(raw_text: str) -> dict[str, Any]:
    parsed = _extract_json_object(raw_text)
    if not parsed:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "parse_error": "No JSON object found in HoloGov response.",
        }
    verdict = _normalize_verdict(parsed.get("final_verdict") or parsed.get("verdict"))
    if verdict not in {"ALLOW", "ESCALATE"}:
        return {
            "parse_ok": False,
            "verdict": "ERROR",
            "parse_error": f"Parsed HoloGov final_verdict was not ALLOW/ESCALATE: {parsed.get('final_verdict')!r}",
            "parsed_json": parsed,
        }
    return {
        "parse_ok": True,
        "verdict": verdict,
        "controlling_reason": str(parsed.get("controlling_reason", "")).strip(),
        "analyst_disagreements": parsed.get("analyst_disagreements", []),
        "cited_evidence": parsed.get("cited_evidence", []),
        "parsed_json": parsed,
    }


def _base_record(card: dict[str, Any], roster_model: dict[str, str], latency_ms: int, *, execution_mode: str, operator: str) -> dict[str, Any]:
    return {
        "result_id": f"{card['packet_id']}::{card['role']}::{roster_model['provider']}::{roster_model['model']}",
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "post_patch_rerun": True,
        "original_trace": False,
        "official_trace": False,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "execution_mode": execution_mode,
        "operator": operator,
        "packet_id": card["packet_id"],
        "packet_hash": card["packet_hash"],
        "hash8": card["hash8"],
        "family_id": card["family_id"],
        "packet_role": card["packet_role"],
        "role": card["role"],
        "provider": roster_model["provider"],
        "transport_provider": _transport_provider(roster_model["provider"]),
        "model": roster_model["model"],
        "latency_ms": latency_ms,
        "called_at": _utc_now(),
    }


def _error_record(
    card: dict[str, Any],
    roster_model: dict[str, str],
    exc: Exception,
    latency_ms: int,
    *,
    execution_mode: str,
    operator: str,
) -> dict[str, Any]:
    if isinstance(exc, provider_core.ProviderCallError):
        error_type = exc.error_type
        error_message = str(exc)
        http_status = exc.http_status
        raw_text = exc.raw_text
    else:
        error_type = type(exc).__name__
        error_message = str(exc)
        http_status = None
        raw_text = ""
    record = _base_record(card, roster_model, latency_ms, execution_mode=execution_mode, operator=operator)
    record.update(
        {
            "provider_call_ok": False,
            "parse_ok": False,
            "verdict": "ERROR",
            "raw_text_excerpt": provider_core._excerpt(raw_text),
            "http_status": http_status,
            "error_type": error_type,
            "error_message_excerpt": provider_core._excerpt(error_message),
            "provider_error": f"{error_type}: {error_message}",
            "error_stage": "provider_call",
        }
    )
    return record


def attempt_provider_call(
    card: dict[str, Any],
    roster_model: dict[str, str],
    timeout: int,
    *,
    execution_mode: str,
    operator: str,
) -> dict[str, Any]:
    start = time.time()
    transport_model = _transport_model(roster_model)
    try:
        call_result = provider_core._call_provider_raw(card, transport_model, timeout)
    except Exception as exc:
        return _error_record(
            card,
            roster_model,
            exc,
            int((time.time() - start) * 1000),
            execution_mode=execution_mode,
            operator=operator,
        )

    latency_ms = int((time.time() - start) * 1000)
    raw_text = call_result["raw_text"]
    parsed = _parse_gov_response(raw_text) if card["role"] == "holo_gov" else _parse_active_response(raw_text)
    record = _base_record(card, roster_model, latency_ms, execution_mode=execution_mode, operator=operator)
    record.update(
        {
            "provider_call_ok": True,
            "parse_ok": parsed["parse_ok"],
            "verdict": parsed["verdict"],
            "raw_text_excerpt": provider_core._excerpt(raw_text),
            "http_status": call_result.get("http_status"),
            "input_tokens": call_result.get("input_tokens", 0),
            "output_tokens": call_result.get("output_tokens", 0),
        }
    )
    if parsed["parse_ok"]:
        for key in ("material_blocker", "evidence", "reasoning", "controlling_reason", "analyst_disagreements", "cited_evidence"):
            if key in parsed:
                record[key] = parsed[key]
        record["parsed_json"] = parsed.get("parsed_json", {})
    else:
        record["parse_error"] = parsed.get("parse_error", "")
        if "parsed_json" in parsed:
            record["parsed_json"] = parsed["parsed_json"]
    return record


def _packet_record(
    *,
    packet: dict[str, Any],
    roster: dict[str, Any],
    active_records: list[dict[str, Any]],
    gov_record: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    return {
        "record_type": "hbb_bec_post_patch_packet_rerun",
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "trace_type": "holo_4dna_mini_frozen_pair_post_patch_rerun",
        "post_patch_rerun": True,
        "original_trace": False,
        "official_trace": False,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "session_id": packet["session_id"],
        "seed": SEED,
        "git_head": _git_head(),
        "created_at": _utc_now(),
        "packet": {
            "scenario_id": packet["scenario_id"],
            "family_id": packet["family_id"],
            "role": packet["role"],
            "path": packet["path"],
            "payload_hash": packet["payload_hash"],
            "hash8": packet["hash8"],
            "model_visible_keys": packet["model_visible_keys"],
            "frozen_approved_by": packet.get("frozen_approved_by"),
        },
        "roster": {
            "holo_gov": roster["holo_gov"],
            "active_non_gov": roster["active_non_gov"],
            "excluded": roster["excluded"],
            "selection_rule": roster["selection_rule"],
        },
        "calls": {
            "active_non_gov": active_records,
            "holo_gov": gov_record,
        },
        "hidden_metadata_excluded": sorted(FORBIDDEN_MODEL_VISIBLE_KEYS),
        "output_directory": str(out_dir),
        "proof_credit_remains_unchanged": True,
    }


def _summarize_results(records: list[dict[str, Any]], packet_record_paths: list[str], *, execution_mode: str, operator: str, out_dir: Path) -> dict[str, Any]:
    error_records = [record for record in records if not record.get("provider_call_ok") or not record.get("parse_ok")]
    provider_error_counts = Counter(record.get("provider", "unknown") for record in error_records)
    verdicts_by_packet: dict[str, dict[str, str]] = {}
    for record in records:
        verdicts_by_packet.setdefault(record["packet_id"], {})[
            f"{record['role']}:{record['provider']}:{record['model']}"
        ] = record.get("verdict", "ERROR")

    return {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "run_status": "operational_failure" if records and len(error_records) == len(records) else "complete",
        "post_patch_rerun": True,
        "original_trace": False,
        "official_trace": False,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "execution_mode": execution_mode,
        "operator": operator,
        "out_dir": str(out_dir),
        "families": [family["family_id"] for family in EXPECTED_FAMILIES],
        "packet_hash_mapping": expected_packet_hash_mapping(),
        "rosters": {family["session_id"]: build_roster(family["session_id"]) for family in EXPECTED_FAMILIES},
        "packets": 4,
        "expected_row_count": expected_call_count(),
        "results": len(records),
        "error_results": len(error_records),
        "provider_error_counts": dict(provider_error_counts),
        "verdicts_by_packet": verdicts_by_packet,
        "packet_record_paths": packet_record_paths,
        "proof_credit_remains_unchanged": True,
        "created_at": _utc_now(),
    }


def execute_post_patch_rerun(
    timeout: int,
    out_dir: Path = OUT_DIR,
    *,
    execution_mode: str,
    operator: str,
) -> dict[str, Any]:
    packets = load_approved_frozen_packets()
    if out_dir.exists():
        raise SystemExit(f"{out_dir} already exists; refusing to overwrite HBB post-patch rerun output.")

    prompt_dir = out_dir / "prompt_cards"
    record_dir = out_dir / "post_patch_rerun_records"
    prompt_dir.mkdir(parents=True, exist_ok=False)
    record_dir.mkdir(parents=True, exist_ok=False)

    records: list[dict[str, Any]] = []
    packet_record_paths: list[str] = []
    results_path = out_dir / "results.jsonl"

    for packet in packets:
        roster = build_roster(packet["session_id"])
        active_records: list[dict[str, Any]] = []
        for roster_model in active_roster_models(roster):
            card = _active_prompt_card(packet, roster_model)
            card_path = prompt_dir / f"{packet['scenario_id']}__{roster_model['provider']}__{_safe_model_name(roster_model['model'])}.json"
            card_path.write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
            record = attempt_provider_call(
                card,
                roster_model,
                timeout,
                execution_mode=execution_mode,
                operator=operator,
            )
            records.append(record)
            active_records.append(record)
            with results_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")

        gov_model = roster["holo_gov"]
        gov_card = _gov_prompt_card(packet, gov_model, active_records)
        gov_card_path = prompt_dir / f"{packet['scenario_id']}__hologov__{_safe_model_name(gov_model['model'])}.json"
        gov_card_path.write_text(json.dumps(gov_card, indent=2, sort_keys=True) + "\n")
        gov_record = attempt_provider_call(
            gov_card,
            gov_model,
            timeout,
            execution_mode=execution_mode,
            operator=operator,
        )
        records.append(gov_record)
        with results_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(gov_record, sort_keys=True) + "\n")

        packet_record = _packet_record(
            packet=packet,
            roster=roster,
            active_records=active_records,
            gov_record=gov_record,
            out_dir=out_dir,
        )
        packet_record_path = record_dir / f"{packet['scenario_id']}_{packet['hash8']}_post_patch_rerun.json"
        packet_record_path.write_text(json.dumps(packet_record, indent=2, sort_keys=True) + "\n")
        packet_record_paths.append(str(packet_record_path))

    summary = _summarize_results(records, packet_record_paths, execution_mode=execution_mode, operator=operator, out_dir=out_dir)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def family_dry_run_reports() -> list[dict[str, Any]]:
    reports = []
    for family in EXPECTED_FAMILIES:
        allow = family["packets"][0]
        escalate = family["packets"][1]
        reports.append(
            build_pair_dry_run_report(
                cohort_path=COHORT_PATH,
                seed=SEED,
                session_id=family["session_id"],
                allow_packet_path=allow["path"],
                allow_expected_hash=allow["hash"],
                escalate_packet_path=escalate["path"],
                escalate_expected_hash=escalate["hash"],
            )
        )
    return reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare or execute the gated HBB BEC post-patch 4DNA rerun.")
    parser.add_argument(
        "--execute-provider-calls",
        action="store_true",
        help="Sends exactly four frozen HBB payloads through seed447 4DNA when approval gates pass.",
    )
    parser.add_argument("--operator", default="", help="Must be Taylor for provider execution.")
    parser.add_argument("--i-am-taylor-local", action="store_true", help="Required Taylor-local execution acknowledgement.")
    parser.add_argument(
        "--allow-codex-provider-calls",
        action="store_true",
        help="Required only for Taylor-approved Codex/Co provider execution.",
    )
    parser.add_argument(
        "--yes-send-frozen-payloads-to-providers",
        action="store_true",
        help="Required acknowledgement that frozen action/context payloads will be sent to external providers.",
    )
    parser.add_argument("--timeout", type=int, default=90, help="Per-provider call timeout in seconds.")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR, help="Output directory for plan or live rerun outputs.")
    args = parser.parse_args(argv)

    if args.execute_provider_calls:
        execution_mode = _require_execution_approval(args)
        summary = execute_post_patch_rerun(
            timeout=args.timeout,
            out_dir=args.out_dir,
            execution_mode=execution_mode,
            operator=args.operator,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    plan = build_prompt_cards(out_dir=args.out_dir)
    plan["family_dry_run_reports"] = family_dry_run_reports()
    (args.out_dir / "rerun_plan.json").write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
