#!/usr/bin/env python3
"""Run or preflight solo one-shot triage over the frozen 3-family bank.

This is intentionally not a Holo run:
- no Gov
- no state brief
- no baton
- no artifact registry
- no final selector
- no judges
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_2026-06-29"
RUN_ROOT = FREEZE_ROOT / "solo_triage_3mini"
EXPECTED_FREEZE_ROOT_HASH = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
OPENAI_WEAK_MODEL_KEY = "openai_weak"
OPENAI_WEAK_MODEL_ID = "gpt-4o-mini"
EXPECTED_FAMILIES = {
    "HV-AP-REP-2026-06-29": "AP / procurement / vendor-master controls",
    "HV-ACOM-REP-2026-06-29": "Agentic commerce / order execution controls",
    "HV-ITAC-REP-2026-06-29": "IT access / permission change controls",
}
MODEL_KEYS = ("xai", OPENAI_WEAK_MODEL_KEY, "minimax")

FORBIDDEN_PROMPT_TERMS = (
    "packet_truth",
    "target_bucket",
    "target_sibling",
    "deterministic_answer_key_for_local_audit_only",
    "required_verdict",
    "verdict_basis",
    "local_audit_predicate",
    "answer key",
    "expected verdict",
    "hologov",
    "gov_baton",
    "latest_gov_baton",
    "state_brief",
    "artifact_registry",
    "best_artifact_registry",
    "blindspot_atlas",
    "final_selector",
)


def load_ap_runner_module():
    path = BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py"
    spec = importlib.util.spec_from_file_location("ap_runner_for_3family_solo_triage", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.configure_openai_w2_runner()
    module.RUNNER.MODEL_CONFIGS[OPENAI_WEAK_MODEL_KEY] = {
        "provider": "openai",
        "model": OPENAI_WEAK_MODEL_ID,
        "dna": "openai",
        "api_key_env": "OPENAI_API_KEY",
        "kind": "openai_responses",
    }
    return module


AP = load_ap_runner_module()
RUNNER = AP.RUNNER


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def read_freeze_records() -> list[dict[str, Any]]:
    freeze = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    if freeze.get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError(f"freeze_root_hash_mismatch:{freeze.get('freeze_root_hash')}")

    index = load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")
    packet_manifest = load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    packet_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}

    records = []
    for row in sorted(index, key=lambda item: (item["family_id"], item["pair_id"], item["sibling_id"])):
        packet_hash = packet_by_id[row["packet_id"]]
        prompt_hash = prompt_by_id[row["packet_id"]]
        packet_path = FREEZE_ROOT / packet_hash["packet_path"]
        prompt_path = FREEZE_ROOT / prompt_hash["prompt_path"]
        payload_path = FREEZE_ROOT / packet_hash["model_visible_payload_path"]
        if sha256_file(packet_path) != packet_hash["packet_sha256"]:
            raise RuntimeError(f"packet_hash_mismatch:{row['packet_id']}")
        if sha256_file(prompt_path) != prompt_hash["prompt_sha256"]:
            raise RuntimeError(f"prompt_hash_mismatch:{row['packet_id']}")
        if sha256_file(payload_path) != packet_hash["model_visible_payload_file_sha256"]:
            raise RuntimeError(f"model_visible_payload_hash_mismatch:{row['packet_id']}")
        packet = load_json(packet_path)
        answer_key = packet["deterministic_answer_key_for_local_audit_only"]
        records.append(
            {
                **row,
                "packet_path": str(packet_path.relative_to(BENCHMARK_ROOT)),
                "prompt_path": str(prompt_path.relative_to(BENCHMARK_ROOT)),
                "model_visible_payload_path": str(payload_path.relative_to(BENCHMARK_ROOT)),
                "packet_file_sha256": packet_hash["packet_sha256"],
                "prompt_file_sha256": prompt_hash["prompt_sha256"],
                "model_visible_payload_file_sha256": packet_hash["model_visible_payload_file_sha256"],
                "packet": packet,
                "required_verdict_for_local_audit_only": answer_key["required_verdict"],
                "required_source_ids_for_local_audit_only": answer_key["required_source_ids"],
                "allowed_source_ids_for_local_audit_only": answer_key["allowed_source_ids"],
            }
        )
    validate_records(records)
    return records


def validate_records(records: list[dict[str, Any]]) -> None:
    if len(records) != 120:
        raise RuntimeError(f"expected_120_records_got:{len(records)}")
    family_counts = Counter(row["family_id"] for row in records)
    if set(family_counts) != set(EXPECTED_FAMILIES):
        raise RuntimeError(f"family_set_mismatch:{sorted(family_counts)}")
    for family_id in EXPECTED_FAMILIES:
        family_rows = [row for row in records if row["family_id"] == family_id]
        if len(family_rows) != 40:
            raise RuntimeError(f"family_packet_count_mismatch:{family_id}:{len(family_rows)}")
        if len({row["pair_id"] for row in family_rows}) != 20:
            raise RuntimeError(f"family_pair_count_mismatch:{family_id}")
        truths = Counter(row["packet_truth"] for row in family_rows)
        if truths != {"ALLOW": 20, "ESCALATE": 20}:
            raise RuntimeError(f"family_truth_balance_mismatch:{family_id}:{truths}")
        buckets = Counter(row["target_bucket"] for row in family_rows if row["target_sibling"])
        if buckets != {"hard_allow": 10, "hard_escalate": 10}:
            raise RuntimeError(f"family_target_balance_mismatch:{family_id}:{buckets}")


def prompt_leakage_hits(prompt_text: str) -> list[str]:
    lower = prompt_text.lower()
    return [term for term in FORBIDDEN_PROMPT_TERMS if term.lower() in lower]


def filter_records(
    records: list[dict[str, Any]],
    family_ids: list[str] | None = None,
    pair_limit: int | None = None,
    packet_limit: int | None = None,
) -> list[dict[str, Any]]:
    selected = records
    if family_ids:
        unknown = sorted(set(family_ids) - set(EXPECTED_FAMILIES))
        if unknown:
            raise RuntimeError(f"unknown_family_ids:{unknown}")
        selected = [row for row in selected if row["family_id"] in set(family_ids)]
    if pair_limit is not None:
        if pair_limit < 1:
            raise RuntimeError("pair_limit_must_be_positive")
        ordered_pairs = []
        seen_pairs = set()
        for row in selected:
            if row["pair_id"] not in seen_pairs:
                seen_pairs.add(row["pair_id"])
                ordered_pairs.append(row["pair_id"])
        keep_pairs = set(ordered_pairs[:pair_limit])
        selected = [row for row in selected if row["pair_id"] in keep_pairs]
    if packet_limit is not None:
        if packet_limit < 1:
            raise RuntimeError("packet_limit_must_be_positive")
        selected = selected[:packet_limit]
    return selected


def build_call_plan(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for model_key in MODEL_KEYS:
        for record in records:
            sort_key = sha256_text(EXPECTED_FREEZE_ROOT_HASH + "::" + model_key + "::" + record["packet_id"])
            plan.append({"sort_key": sort_key, "model_key": model_key, "record": record})
    return sorted(plan, key=lambda item: item["sort_key"])


def model_roster() -> list[dict[str, Any]]:
    return [
        {
            "model_key": key,
            "provider": RUNNER.MODEL_CONFIGS[key]["provider"],
            "model": RUNNER.MODEL_CONFIGS[key]["model"],
            "dna": RUNNER.MODEL_CONFIGS[key]["dna"],
        }
        for key in MODEL_KEYS
    ]


def preflight_report(
    family_ids: list[str] | None = None,
    pair_limit: int | None = None,
    packet_limit: int | None = None,
    batch_label: str = "all_families",
) -> dict[str, Any]:
    all_records = read_freeze_records()
    records = filter_records(all_records, family_ids=family_ids, pair_limit=pair_limit, packet_limit=packet_limit)
    if not records:
        raise RuntimeError("no_records_selected")
    call_plan = build_call_plan(records)
    family_counts = Counter(row["family_id"] for row in records)
    truth_counts = Counter(row["packet_truth"] for row in records)
    leakage_rows = []
    for record in records:
        prompt_text = (BENCHMARK_ROOT / record["prompt_path"]).read_text()
        if sha256_text(prompt_text) != record["prompt_file_sha256"]:
            raise RuntimeError(f"prompt_hash_recheck_mismatch:{record['packet_id']}")
        hits = prompt_leakage_hits(prompt_text)
        if hits:
            leakage_rows.append({"packet_id": record["packet_id"], "hits": hits})
    checks = {
        "freeze_root_matches": True,
        "families_selected": bool(family_counts),
        "packets_selected": bool(records),
        "pairs_selected": bool({row["pair_id"] for row in records}),
        "truths_selected": bool(truth_counts),
        "model_count": len(MODEL_KEYS) == 3,
        "expected_provider_calls": len(call_plan) == len(records) * len(MODEL_KEYS),
        "openai_weak_is_gpt_4o_mini": RUNNER.MODEL_CONFIGS[OPENAI_WEAK_MODEL_KEY]["model"] == OPENAI_WEAK_MODEL_ID,
        "no_gemini_in_triage_roster": all("gemini" not in RUNNER.MODEL_CONFIGS[key]["model"].lower() for key in MODEL_KEYS),
        "no_gov_calls_configured": True,
        "no_holo_state_configured": True,
        "no_judge_calls_configured": True,
        "prompt_leakage": not leakage_rows,
        "provider_calls": True,
        "judge_calls": True,
    }
    return {
        "classification": "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_PREFLIGHT",
        "batch_label": batch_label,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "selection": {
            "family_ids": family_ids or sorted(EXPECTED_FAMILIES),
            "pair_limit": pair_limit,
            "packet_limit": packet_limit,
        },
        "families": dict(family_counts),
        "truth_counts": dict(truth_counts),
        "pair_count": len({row["pair_id"] for row in records}),
        "packet_count": len(records),
        "model_roster": model_roster(),
        "expected_provider_calls": len(call_plan),
        "expected_gov_calls": 0,
        "expected_holo_calls": 0,
        "expected_judge_calls": 0,
        "checks": checks,
        "prompt_leakage_rows": leakage_rows,
        "provider_calls_made_by_preflight": 0,
        "judge_calls_made_by_preflight": 0,
    }


def parse_solo_text(text: str) -> tuple[bool, dict[str, Any] | None, str | None]:
    try:
        parsed = json.loads((text or "").strip())
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}"
    return isinstance(parsed, dict), parsed if isinstance(parsed, dict) else None, None if isinstance(parsed, dict) else "not_json_object"


def normalize_source_ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).replace("doc_id:", "").strip() for item in value if str(item).strip()]


def solo_gate(parsed: dict[str, Any] | None, record: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    required_keys = {"verdict", "binding_reason", "source_ids", "open_dependencies", "action_boundary"}
    if not isinstance(parsed, dict):
        return {"passed": False, "failures": ["parse_failed"], "artifact_verdict": None}
    extra = sorted(set(parsed) - required_keys)
    missing = sorted(required_keys - set(parsed))
    if missing:
        failures.append("missing_keys:" + ",".join(missing))
    if extra:
        failures.append("extra_keys:" + ",".join(extra))
    verdict = parsed.get("verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("invalid_verdict")
    if verdict != record["required_verdict_for_local_audit_only"]:
        failures.append("verdict_mismatch")
    if not str(parsed.get("binding_reason") or "").strip():
        failures.append("missing_binding_reason")
    if parsed.get("action_boundary") != record["packet"]["action_boundary"]:
        failures.append("action_boundary_mismatch")
    if not isinstance(parsed.get("open_dependencies"), list):
        failures.append("open_dependencies_not_array")
    cited = normalize_source_ids(parsed.get("source_ids"))
    allowed = set(record["allowed_source_ids_for_local_audit_only"])
    required = set(record["required_source_ids_for_local_audit_only"])
    if not cited:
        failures.append("missing_source_ids")
    invented = sorted(set(cited) - allowed)
    if invented:
        failures.append("invented_source_ids:" + ",".join(invented))
    missing_required = sorted(required - set(cited))
    if missing_required:
        failures.append("missing_required_source_ids:" + ",".join(missing_required))
    return {
        "passed": not failures,
        "failures": failures,
        "artifact_verdict": verdict,
        "required_verdict": record["required_verdict_for_local_audit_only"],
        "cited_source_ids": cited,
    }


def solo_label(provider_ok: bool, parse_ok: bool, parsed: dict[str, Any] | None, gate: dict[str, Any]) -> str:
    if not provider_ok:
        return "PROVIDER_FAIL"
    if not parse_ok or not isinstance(parsed, dict):
        return "PARSE_FAIL"
    if "verdict_mismatch" in (gate.get("failures") or []):
        return "WRONG_VERDICT"
    if gate.get("passed"):
        return "KNEW"
    return "STRUCTURAL_OR_EVIDENCE_FAIL"


def run_live(
    family_ids: list[str] | None = None,
    pair_limit: int | None = None,
    packet_limit: int | None = None,
    batch_label: str = "all_families",
) -> int:
    all_records = read_freeze_records()
    records = filter_records(all_records, family_ids=family_ids, pair_limit=pair_limit, packet_limit=packet_limit)
    if not records:
        raise RuntimeError("no_records_selected")
    call_plan = build_call_plan(records)
    for key in MODEL_KEYS:
        env = RUNNER.MODEL_CONFIGS[key]["api_key_env"]
        if not os.getenv(env, "").strip():
            raise RuntimeError(f"{env} missing")
    preflight = preflight_report(family_ids=family_ids, pair_limit=pair_limit, packet_limit=packet_limit, batch_label=batch_label)
    if preflight["status"] != "PASS":
        raise RuntimeError(f"preflight_failed:{preflight['checks']}")

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    safe_label = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in batch_label)
    run_dir = RUN_ROOT / safe_label / run_id
    prompts_dir = run_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=False)
    write_json(run_dir / "SOLO_TRIAGE_PREFLIGHT.json", preflight)
    trace_path = run_dir / "SOLO_TRIAGE_TRACE.jsonl"
    rows: list[dict[str, Any]] = []
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    with trace_path.open("w") as trace:
        for index, item in enumerate(call_plan, 1):
            record = item["record"]
            model_key = item["model_key"]
            config = RUNNER.MODEL_CONFIGS[model_key]
            prompt_text = (BENCHMARK_ROOT / record["prompt_path"]).read_text()
            if sha256_text(prompt_text) != record["prompt_file_sha256"]:
                raise RuntimeError(f"prompt_hash_mismatch_before_call:{record['packet_id']}")
            leakage_hits = prompt_leakage_hits(prompt_text)
            if leakage_hits:
                raise RuntimeError(f"prompt_leakage_before_call:{record['packet_id']}:{leakage_hits}")
            prompt_ref = prompts_dir / f"{index:03d}_{model_key}_{record['packet_id']}.prompt.txt"
            write_text(prompt_ref, prompt_text)
            messages = [{"role": "user", "content": prompt_text}]
            row: dict[str, Any] = {
                "call_index": index,
                "lane": "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE",
                "model_key": model_key,
                "provider": config["provider"],
                "model": config["model"],
                "dna": config["dna"],
                "family_id": record["family_id"],
                "domain": record["domain"],
                "pair_id": record["pair_id"],
                "packet_id": record["packet_id"],
                "sibling_id": record["sibling_id"],
                "target_bucket": record["target_bucket"],
                "target_sibling": record["target_sibling"],
                "packet_truth_for_local_audit_only": record["packet_truth"],
                "required_verdict_for_local_audit_only": record["required_verdict_for_local_audit_only"],
                "prompt_ref": str(prompt_ref.relative_to(run_dir)),
                "frozen_prompt_hash": record["prompt_file_sha256"],
                "provider_prompt_hash": sha256_text(prompt_text),
                "prompt_hash_matches_freeze": True,
                "prompt_leakage_hits": [],
                "gov_context_in_prompt": False,
                "holo_state_in_prompt": False,
                "artifact_registry_in_prompt": False,
                "judge_calls": 0,
            }
            response: dict[str, Any] = {}
            provider_ok = False
            parse_ok = False
            parsed = None
            parse_error = None
            gate = {"passed": False, "failures": ["not_called"], "artifact_verdict": None}
            try:
                response = RUNNER._call_model(config, messages, max_tokens=1400)
                provider_ok = True
                parse_ok, parsed, parse_error = parse_solo_text(response.get("text", ""))
                gate = solo_gate(parsed, record)
            except Exception as exc:
                if isinstance(exc, RUNNER.TransportFailureAfterRetries):
                    response = dict(exc.metadata)
                parse_error = f"{type(exc).__name__}: {exc}"
                row["error"] = parse_error
            row.update(response)
            label = solo_label(provider_ok, parse_ok, parsed, gate)
            row.update(
                {
                    "provider_call_ok": provider_ok,
                    "parse_ok": parse_ok,
                    "parse_error": parse_error,
                    "parsed_json": parsed,
                    "local_verdict": parsed.get("verdict") if isinstance(parsed, dict) else None,
                    "local_verdict_matches_packet_truth": (
                        parsed.get("verdict") == record["packet_truth"] if isinstance(parsed, dict) else False
                    ),
                    "gate_result": gate,
                    "admissible": bool(gate.get("passed")),
                    "solo_label": label,
                }
            )
            for key in totals:
                if isinstance(row.get(key), int):
                    totals[key] += row[key]
            trace.write(json.dumps(row, sort_keys=True) + "\n")
            trace.flush()
            rows.append(row)
            if not provider_ok:
                break
    summary = summarize(run_dir, rows, totals, trace_path, preflight)
    write_json(run_dir / "solo_triage_results.json", summary)
    write_text(run_dir / "solo_triage_summary.md", render_summary(summary))
    write_run_lock(run_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["classification"] == "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_COMPLETE" else 1


def summarize(run_dir: Path, rows: list[dict[str, Any]], totals: dict[str, int], trace_path: Path, preflight: dict[str, Any]) -> dict[str, Any]:
    expected_provider_calls = preflight["expected_provider_calls"]
    by_model = {}
    for key in MODEL_KEYS:
        config = RUNNER.MODEL_CONFIGS[key]
        model_rows = [row for row in rows if row.get("model_key") == key]
        counts = Counter(row.get("solo_label") for row in model_rows)
        by_model[f"{config['provider']}/{config['model']}"] = {
            "calls": len(model_rows),
            "expected_calls": preflight["packet_count"],
            "knew_admissible": counts.get("KNEW", 0),
            "wrong_verdict": counts.get("WRONG_VERDICT", 0),
            "structural_or_evidence_fail": counts.get("STRUCTURAL_OR_EVIDENCE_FAIL", 0),
            "parse_fail": counts.get("PARSE_FAIL", 0),
            "provider_fail": counts.get("PROVIDER_FAIL", 0),
            "verdict_correct": sum(1 for row in model_rows if row.get("local_verdict_matches_packet_truth") is True),
            "tokens": {
                "input_tokens": sum(row.get("input_tokens") or 0 for row in model_rows),
                "output_tokens": sum(row.get("output_tokens") or 0 for row in model_rows),
                "total_tokens": sum(row.get("total_tokens") or 0 for row in model_rows),
            },
        }
    by_family = {}
    for family_id in EXPECTED_FAMILIES:
        family_rows = [row for row in rows if row.get("family_id") == family_id]
        by_family[family_id] = {
            "domain": EXPECTED_FAMILIES[family_id],
            "calls": len(family_rows),
            "expected_calls": preflight["families"].get(family_id, 0) * len(MODEL_KEYS),
            "knew_admissible": sum(1 for row in family_rows if row.get("solo_label") == "KNEW"),
            "not_knew": sum(1 for row in family_rows if row.get("solo_label") != "KNEW"),
            "wrong_verdict": sum(1 for row in family_rows if row.get("solo_label") == "WRONG_VERDICT"),
            "parse_fail": sum(1 for row in family_rows if row.get("solo_label") == "PARSE_FAIL"),
            "provider_fail": sum(1 for row in family_rows if row.get("solo_label") == "PROVIDER_FAIL"),
        }
    pair_rankings = build_pair_rankings(rows)
    provider_failures = [row for row in rows if row.get("provider_call_ok") is not True]
    complete = len(rows) == expected_provider_calls and not provider_failures
    return {
        "classification": "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_COMPLETE" if complete else "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_INVALID_OR_INCOMPLETE",
        "batch_label": preflight["batch_label"],
        "run_dir": str(run_dir),
        "freeze_root": EXPECTED_FREEZE_ROOT_HASH,
        "provider_calls": len(rows),
        "expected_provider_calls": expected_provider_calls,
        "gov_calls": 0,
        "holo_calls": 0,
        "judge_calls": 0,
        "provider_failures": [
            {
                "call_index": row.get("call_index"),
                "family_id": row.get("family_id"),
                "packet_id": row.get("packet_id"),
                "provider": row.get("provider"),
                "model": row.get("model"),
                "error": row.get("error") or row.get("parse_error"),
            }
            for row in provider_failures
        ],
        "preflight": {k: v for k, v in preflight.items() if k != "prompt_leakage_rows"},
        "totals": totals,
        "trace_hash": sha256_file(trace_path),
        "by_model": by_model,
        "by_family": by_family,
        "pair_rankings": pair_rankings,
        "top_holo_targets": [row for row in pair_rankings if row["triage_class"] in {"ALL_SIX_SOLO_COLLAPSE", "STRONG_SOLO_COLLAPSE"}][:20],
    }


def build_pair_rankings(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["pair_id"]].append(row)
    rankings = []
    for pair_id, pair_rows in grouped.items():
        not_knew = sum(1 for row in pair_rows if row.get("solo_label") != "KNEW")
        wrong = sum(1 for row in pair_rows if row.get("solo_label") == "WRONG_VERDICT")
        parse_or_provider = sum(1 for row in pair_rows if row.get("solo_label") in {"PARSE_FAIL", "PROVIDER_FAIL"})
        if len(pair_rows) != 6:
            triage_class = "INVALID_PAIR_TRACE"
        elif not_knew == 6:
            triage_class = "ALL_SIX_SOLO_COLLAPSE"
        elif not_knew >= 4 or wrong >= 3:
            triage_class = "STRONG_SOLO_COLLAPSE"
        elif not_knew:
            triage_class = "MIXED_SEAM"
        else:
            triage_class = "NO_SOLO_SEAM"
        sample = pair_rows[0]
        rankings.append(
            {
                "family_id": sample["family_id"],
                "domain": sample["domain"],
                "pair_id": pair_id,
                "target_bucket": sample["target_bucket"],
                "calls_present": len(pair_rows),
                "not_knew_count": not_knew,
                "wrong_verdict_count": wrong,
                "parse_or_provider_fail_count": parse_or_provider,
                "triage_class": triage_class,
                "packets": sorted({row["packet_id"] for row in pair_rows}),
                "solo_outcomes": [
                    {
                        "packet_id": row["packet_id"],
                        "provider": row["provider"],
                        "model": row["model"],
                        "verdict": row.get("local_verdict"),
                        "label": row.get("solo_label"),
                        "admissible": row.get("admissible"),
                    }
                    for row in sorted(pair_rows, key=lambda item: (item["packet_id"], item["model_key"]))
                ],
            }
        )
    order = {
        "ALL_SIX_SOLO_COLLAPSE": 0,
        "STRONG_SOLO_COLLAPSE": 1,
        "MIXED_SEAM": 2,
        "NO_SOLO_SEAM": 3,
        "INVALID_PAIR_TRACE": 4,
    }
    return sorted(rankings, key=lambda row: (order[row["triage_class"]], -row["not_knew_count"], -row["wrong_verdict_count"], row["pair_id"]))


def render_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify 3-Family Solo Triage",
        "",
        f"Classification: `{summary['classification']}`",
        f"Freeze root: `{summary['freeze_root']}`",
        f"Provider calls: `{summary['provider_calls']}` / `{summary['expected_provider_calls']}`",
        f"Gov calls: `{summary['gov_calls']}`",
        f"Holo calls: `{summary['holo_calls']}`",
        f"Judge calls: `{summary['judge_calls']}`",
        f"Tokens: `{summary['totals']['input_tokens']}` input / `{summary['totals']['output_tokens']}` output / `{summary['totals']['total_tokens']}` total",
        "",
        "## Family Results",
        "",
        "| Family | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Provider Fail |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for family_id, stats in summary["by_family"].items():
        lines.append(
            f"| `{family_id}` | {stats['calls']} / {stats['expected_calls']} | {stats['knew_admissible']} | {stats['not_knew']} | {stats['wrong_verdict']} | {stats['parse_fail']} | {stats['provider_fail']} |"
        )
    lines.extend(
        [
            "",
            "## Model Results",
            "",
            "| Model | Calls | KNEW | Verdict Correct | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model, stats in summary["by_model"].items():
        lines.append(
            f"| `{model}` | {stats['calls']} / {stats['expected_calls']} | {stats['knew_admissible']} | {stats['verdict_correct']} | {stats['wrong_verdict']} | {stats['structural_or_evidence_fail']} | {stats['parse_fail']} | {stats['provider_fail']} |"
        )
    lines.extend(
        [
            "",
            "## Top Holo Targets",
            "",
            "| Class | Family | Pair | Target bucket | Not KNEW | Wrong verdict | Packets |",
            "| --- | --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for row in summary["top_holo_targets"]:
        lines.append(
            f"| `{row['triage_class']}` | `{row['family_id']}` | `{row['pair_id']}` | `{row['target_bucket']}` | {row['not_knew_count']} | {row['wrong_verdict_count']} | `{', '.join(row['packets'])}` |"
        )
    return "\n".join(lines) + "\n"


def locked_files(run_dir: Path) -> list[dict[str, Any]]:
    files = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if path.name in {"SOLO_TRIAGE_LOCK_MANIFEST.json", "SOLO_TRIAGE_LOCK_VALIDATION.json"}:
            continue
        files.append({"relative_path": str(path.relative_to(run_dir)), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return files


def write_run_lock(run_dir: Path, summary: dict[str, Any]) -> None:
    manifest_no_root = {
        "classification": "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_LOCK",
        "status": "PASS" if summary["classification"].endswith("_COMPLETE") else "FAIL",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "freeze_root": summary["freeze_root"],
        "trace_hash": summary["trace_hash"],
        "provider_calls": summary["provider_calls"],
        "expected_provider_calls": summary["expected_provider_calls"],
        "locked_files": locked_files(run_dir),
    }
    root_signature = sha256_text(canonical_json(manifest_no_root))
    manifest = {**manifest_no_root, "root_signature": root_signature}
    write_json(run_dir / "SOLO_TRIAGE_LOCK_MANIFEST.json", manifest)
    validation = validate_run_lock(run_dir)
    write_json(run_dir / "SOLO_TRIAGE_LOCK_VALIDATION.json", validation)


def validate_run_lock(run_dir: Path) -> dict[str, Any]:
    lock = load_json(run_dir / "SOLO_TRIAGE_LOCK_MANIFEST.json")
    for item in lock["locked_files"]:
        if sha256_file(run_dir / item["relative_path"]) != item["sha256"]:
            raise RuntimeError(f"run_lock_hash_mismatch:{item['relative_path']}")
    no_root = dict(lock)
    root = no_root.pop("root_signature")
    recomputed = sha256_text(canonical_json(no_root))
    if root != recomputed:
        raise RuntimeError("run_lock_root_mismatch")
    return {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": root,
        "locked_file_count": len(lock["locked_files"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true", help="Local no-provider preflight only.")
    parser.add_argument("--run-live", action="store_true", help="Run solo triage in an authorized shell.")
    parser.add_argument("--family", action="append", choices=sorted(EXPECTED_FAMILIES), help="Limit to a frozen family. May be repeated.")
    parser.add_argument("--pair-limit", type=int, help="Limit to the first N sibling pairs after family filtering.")
    parser.add_argument("--packet-limit", type=int, help="Limit to the first N packets after family/pair filtering.")
    parser.add_argument("--batch-label", default="all_families", help="Label used in output run path and reports.")
    args = parser.parse_args()
    if args.preflight:
        report = preflight_report(
            family_ids=args.family,
            pair_limit=args.pair_limit,
            packet_limit=args.packet_limit,
            batch_label=args.batch_label,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if args.run_live:
        return run_live(
            family_ids=args.family,
            pair_limit=args.pair_limit,
            packet_limit=args.packet_limit,
            batch_label=args.batch_label,
        )
    parser.error("Use --preflight or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
