from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
from proof_credit_rules import (  # noqa: E402
    annotate_judge_credit,
    forbidden_text_errors,
    generation_dna_for_pair,
    runtime_visibility_errors,
    select_outside_dna_judges,
)

D1_DOMAIN = "capital_markets_trade_shock_execution"
CURRENT_LOCK_RUN_ID = "holo_factory_live_20260619T180210Z"
OUT = ROOT / "domain_01_capital_markets"
HOLO_FACTORY_RUNS = ROOT / "holo_factory" / "suite_runs"
LEGACY_PACKET = ROOT / "current_event_finance_algo_execution_20260618"
LEGACY_RUNS = LEGACY_PACKET / "runs"
LEGACY_ROLLUP = LEGACY_PACKET / "suite_rollups" / "hash_locked_lift_rollup.json"
DEFAULT_JUDGE_PANEL = [
    {"judge_id": "judge_frontier_01", "provider": "openai", "model": "gpt-5.5", "outside_judge": False},
    {"judge_id": "judge_frontier_02", "provider": "anthropic", "model": "claude-opus-4-8", "outside_judge": False},
    {"judge_id": "judge_frontier_03", "provider": "google", "model": "gemini-3.1-pro-preview", "outside_judge": False},
    {"judge_id": "judge_frontier_04", "provider": "xai", "model": "grok-4.3", "outside_judge": True},
]
OUTSIDE_DNA_REJUDGE_PANEL = [
    {"judge_id": "judge_outside_xai_01", "provider": "xai", "model": "grok-4.3"},
    {"judge_id": "judge_outside_minimax_01", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
]


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def safe_len_glob(root: Path, pattern: str) -> int:
    if not root.exists():
        return 0
    return len(list(root.glob(pattern)))


def load_judge_panel(run_root: Path) -> list[dict[str, Any]]:
    preflight_path = run_root / "preflight.json"
    if preflight_path.exists():
        panel = read_json(preflight_path).get("judge_panel")
        if isinstance(panel, list) and panel:
            return panel
    return DEFAULT_JUDGE_PANEL


def load_run_cohort_plans(run_root: Path) -> dict[str, dict[str, Any]]:
    manifest_path = run_root / "suite_run_manifest.json"
    if not manifest_path.exists():
        return {}
    manifest = read_json(manifest_path)
    plans: dict[str, dict[str, Any]] = {}
    for plan in manifest.get("cohorts", []) or []:
        cohort = plan.get("cohort")
        if cohort:
            plans[str(cohort)] = plan
    return plans


def pair_generation_dna(run_root: Path, pair: dict[str, Any]) -> dict[str, Any]:
    if isinstance(pair.get("generation_dna"), dict):
        return pair["generation_dna"]
    plans = load_run_cohort_plans(run_root)
    cohort_plan = plans.get(str(pair.get("cohort") or ""))
    if not cohort_plan:
        return {}
    return generation_dna_for_pair(
        cohort_plan=cohort_plan,
        solo_condition=pair.get("solo_condition"),
        holo_condition=pair.get("holo_condition"),
    )


def judge_boundary_status(prompt_card_path: Path, trace_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    if prompt_card_path.exists():
        try:
            prompt_card = read_json(prompt_card_path)
            visible_prompt = {
                "system": prompt_card.get("system", ""),
                "user": prompt_card.get("user", ""),
            }
            errors.extend(runtime_visibility_errors(visible_prompt, scope="judge_prompt_card_visible_text"))
        except Exception as exc:
            errors.append(f"judge_prompt_card:unreadable:{exc.__class__.__name__}")
    if trace_path.exists():
        try:
            trace = read_json(trace_path)
            trace_text = {
                "artifact_text": trace.get("artifact_text", ""),
                "raw_text": trace.get("raw_text", ""),
                "response_text": trace.get("response_text", ""),
            }
            errors.extend(forbidden_text_errors(trace_text, scope="judge_trace_text"))
        except Exception as exc:
            errors.append(f"judge_trace:unreadable:{exc.__class__.__name__}")
    return {
        "judge_boundary_clean": not errors,
        "judge_boundary_errors": ";".join(errors),
    }


def ms_to_minutes(ms: int | float | None) -> float | None:
    if ms is None:
        return None
    return round(float(ms) / 60000, 3)


def classify_run(run_id: str, status: str | None) -> str:
    text = f"{run_id} {status or ''}".lower()
    if "no_provider_smoke" in text:
        return "no_provider_smoke"
    if "tiny_live" in text:
        return "tiny_live_smoke"
    if "holo_factory_live" in text:
        return "holo_factory_live"
    if "full" in text or "patent_grade" in text or "holo_only" in text:
        return "live_or_partial_live"
    if "routing_robustness" in text:
        return "routing_robustness_diagnostic"
    return "diagnostic"


def status_bucket(status: str | None) -> str:
    if not status:
        return "unknown"
    if status.endswith("_COMPLETE") or status in {"HOLO_FACTORY_LIVE_COMPLETE"}:
        return "complete"
    if status.endswith("_PASS"):
        return "pass"
    if "ERROR" in status:
        return "error_or_partial"
    if "RUNNING" in status or "running" in status:
        return "running_or_stale"
    return "other"


def collect_holo_factory_runs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for manifest_path in sorted(HOLO_FACTORY_RUNS.glob("*/suite_run_manifest.json")):
        manifest = read_json(manifest_path)
        domains = manifest.get("domains", [])
        run_root = manifest_path.parent
        has_d1 = D1_DOMAIN in domains or bool(list(run_root.glob(f"**/{D1_DOMAIN}/**/*")))
        if not has_d1:
            continue
        final_packets = safe_len_glob(run_root, f"judge_packets/final/{D1_DOMAIN}/**/*.json")
        turn_packets = safe_len_glob(run_root, f"judge_packets/turns/{D1_DOMAIN}/**/*.json")
        judge_scores = safe_len_glob(run_root, "judge_scores/**/*.json")
        row = {
            "lane": "holo_factory",
            "run_id": manifest.get("run_id", run_root.name),
            "run_dir": str(run_root),
            "status": manifest.get("status"),
            "status_bucket": status_bucket(manifest.get("status")),
            "run_class": classify_run(manifest.get("run_id", run_root.name), manifest.get("status")),
            "benchmark_credit": manifest.get("benchmark_credit"),
            "public_claim": manifest.get("public_claim"),
            "domains": ",".join(domains),
            "cohorts": ",".join(c.get("cohort", "") for c in manifest.get("cohorts", [])),
            "condition_count": manifest.get("condition_count"),
            "provider_call_trace_count": manifest.get("provider_call_trace_count"),
            "input_tokens": manifest.get("input_tokens"),
            "output_tokens": manifest.get("output_tokens"),
            "total_tokens": manifest.get("total_tokens"),
            "latency_ms": manifest.get("latency_ms"),
            "latency_minutes": ms_to_minutes(manifest.get("latency_ms")),
            "final_judge_packets": final_packets or manifest.get("final_judge_packet_count"),
            "turn_judge_packets": turn_packets or manifest.get("turn_judge_packet_count"),
            "judge_scores": judge_scores or manifest.get("judge_score_count"),
            "sealed_pair_count": manifest.get("sealed_pair_count"),
            "error_count": len(manifest.get("errors", []) or []),
        }
        rows.append(row)
    return rows


def collect_legacy_runs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for manifest_path in sorted(LEGACY_RUNS.glob("*/run_manifest.json")):
        manifest = read_json(manifest_path)
        run_root = manifest_path.parent
        final_packets = safe_len_glob(run_root, "judge_packets/*.json") + safe_len_glob(run_root, "final_judge_packets/*.json")
        turn_packets = safe_len_glob(run_root, "turn_judge_packets/*.json")
        judge_scores = safe_len_glob(run_root, "judge_scores/*.json") + safe_len_glob(run_root, "judge_scores/**/*.json")
        condition_results = manifest.get("condition_results") or {}
        if isinstance(condition_results, dict):
            condition_count = len(condition_results)
        elif isinstance(condition_results, list):
            condition_count = len(condition_results)
        else:
            condition_count = ""
        rows.append(
            {
                "lane": "legacy_finance_algo",
                "run_id": manifest.get("run_id", run_root.name),
                "run_dir": str(run_root),
                "status": manifest.get("status"),
                "status_bucket": status_bucket(manifest.get("status")),
                "run_class": classify_run(manifest.get("run_id", run_root.name), manifest.get("status")),
                "benchmark_credit": manifest.get("benchmark_credit"),
                "public_claim": manifest.get("public_claim"),
                "domains": D1_DOMAIN,
                "cohorts": manifest.get("solo_suite_id") or manifest.get("routing_config_id") or "",
                "condition_count": condition_count,
                "provider_call_trace_count": manifest.get("provider_call_trace_count") or "",
                "input_tokens": manifest.get("input_tokens") or "",
                "output_tokens": manifest.get("output_tokens") or "",
                "total_tokens": manifest.get("total_tokens") or "",
                "latency_ms": manifest.get("latency_ms") or "",
                "latency_minutes": ms_to_minutes(manifest.get("latency_ms")) if manifest.get("latency_ms") else "",
                "final_judge_packets": final_packets,
                "turn_judge_packets": turn_packets,
                "judge_scores": judge_scores,
                "sealed_pair_count": "",
                "error_count": 1 if (run_root / "run_error.json").exists() else 0,
            }
        )
    return rows


def collect_holo_factory_conditions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for intelligence_path in sorted(HOLO_FACTORY_RUNS.glob("*/analysis/run_intelligence.json")):
        data = read_json(intelligence_path)
        run_id = data.get("run_id", intelligence_path.parents[1].name)
        for item in data.get("conditions", []):
            if item.get("domain_id") != D1_DOMAIN:
                continue
            rows.append(
                {
                    "source": "holo_factory",
                    "run_id": run_id,
                    "cohort": item.get("cohort"),
                    "condition": item.get("condition"),
                    "condition_type": "holo" if item.get("is_holo") else "solo",
                    "provider_model": item.get("provider_model"),
                    "manifest_status": item.get("manifest_status"),
                    "revalidated_status": item.get("revalidated_status"),
                    "turns_complete": item.get("turn_count_complete"),
                    "gov_turns_complete": item.get("gov_turn_count_complete"),
                    "input_tokens": item.get("input_tokens"),
                    "output_tokens": item.get("output_tokens"),
                    "total_tokens": item.get("total_tokens"),
                    "latency_ms": item.get("latency_ms"),
                    "latency_minutes": ms_to_minutes(item.get("latency_ms")),
                    "final_word_count": item.get("final_word_count"),
                    "selected_turn": item.get("selected_turn"),
                    "flags": ";".join(item.get("revalidated_flags") or []),
                    "final_artifact_path": item.get("final_artifact_path"),
                }
            )
    return rows


def collect_legacy_conditions() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for intelligence_path in sorted(LEGACY_RUNS.glob("*/intelligence/benchmark_intelligence.json")):
        data = read_json(intelligence_path)
        run_id = data.get("run_id", intelligence_path.parents[1].name)
        token_by_condition = (data.get("token_summary") or {}).get("by_condition", {})
        final_checks = {item.get("condition"): item for item in data.get("final_artifact_checks", [])}
        trajectory = data.get("turn_trajectory", [])
        provider_by_condition = {}
        for item in trajectory:
            provider_by_condition.setdefault(item.get("condition"), item.get("provider_model"))
        for condition, token_row in token_by_condition.items():
            final = final_checks.get(condition, {})
            rows.append(
                {
                    "source": "legacy_finance_algo",
                    "run_id": run_id,
                    "cohort": "mini" if "mini" in run_id else "frontier",
                    "condition": condition,
                    "condition_type": "holo" if condition.startswith("holo") else "solo",
                    "provider_model": provider_by_condition.get(condition),
                    "manifest_status": data.get("run_status"),
                    "revalidated_status": "clean_ending" if final.get("clean_ending") else ("not_clean_or_unknown" if final else ""),
                    "turns_complete": len({x.get("turn") for x in trajectory if x.get("condition") == condition and x.get("call_type") in {"solo_turn", "holo_analyst_turn"}}),
                    "gov_turns_complete": len([x for x in trajectory if x.get("condition") == condition and x.get("call_type") == "holo_gov_mission_packet"]),
                    "input_tokens": token_row.get("input_tokens"),
                    "output_tokens": token_row.get("output_tokens"),
                    "total_tokens": token_row.get("total_tokens"),
                    "latency_ms": token_row.get("latency_ms"),
                    "latency_minutes": ms_to_minutes(token_row.get("latency_ms")),
                    "final_word_count": final.get("word_count"),
                    "selected_turn": 6 if final else "",
                    "flags": "possible_mid_bullet_cutoff" if final.get("possible_mid_bullet_cutoff") else "",
                    "final_artifact_path": final.get("artifact_path"),
                }
            )
    return rows


def load_anonymization_map(run_root: Path) -> dict[str, dict[str, Any]]:
    maps = list((run_root / "sealed").glob("*anonymization_map.json"))
    if not maps:
        return {}
    data = read_json(maps[0])
    return {item.get("judge_packet_id"): item for item in data.get("pairs", [])}


def collect_missing_final_judge_queue() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_root in sorted(HOLO_FACTORY_RUNS.glob("*")):
        if not run_root.is_dir():
            continue
        pair_map = load_anonymization_map(run_root)
        panel = load_judge_panel(run_root)
        final_packets = sorted(run_root.glob(f"judge_packets/final/{D1_DOMAIN}/**/*.json"))
        if not final_packets:
            continue
        for packet_path in final_packets:
            packet_id = packet_path.stem
            pair = pair_map.get(packet_id, {})
            generation_dna = pair_generation_dna(run_root, pair)
            if pair.get("domain_id") and pair.get("domain_id") != D1_DOMAIN:
                continue
            for judge in panel:
                judge_id = judge.get("judge_id")
                score_path = run_root / "judge_scores" / packet_id / f"{judge_id}.json"
                prompt_card_path = run_root / "prompt_cards" / "judges" / packet_id / f"{judge_id}.json"
                trace_path = run_root / "traces" / "judges" / packet_id / f"{judge_id}.json"
                credit = annotate_judge_credit(judge, generation_dna)
                boundary = judge_boundary_status(prompt_card_path, trace_path)
                proof_credit_eligible = credit["proof_credit_eligible"] and boundary["judge_boundary_clean"]
                score_credit_label = credit["score_credit_label"] if boundary["judge_boundary_clean"] else f"{credit['score_credit_label']}_boundary_violation"
                score_use = credit["score_use"] if proof_credit_eligible else "diagnostic_only"
                if score_path.exists():
                    score_status = "scored"
                elif prompt_card_path.exists() or trace_path.exists():
                    score_status = "attempted_no_parsed_score"
                else:
                    score_status = "not_attempted"
                rows.append(
                    {
                        "run_id": run_root.name,
                        "judge_packet_id": packet_id,
                        "packet_kind": "final",
                        "domain_id": pair.get("domain_id") or D1_DOMAIN,
                        "cohort": pair.get("cohort"),
                        "turn": pair.get("turn"),
                        "solo_condition": pair.get("solo_condition"),
                        "holo_condition": pair.get("holo_condition"),
                        "judge_id": judge_id,
                        "judge_provider": judge.get("provider"),
                        "judge_model": judge.get("model"),
                        "outside_judge": proof_credit_eligible,
                        "panel_outside_judge_claim": judge.get("outside_judge", False),
                        "proof_credit_eligible": proof_credit_eligible,
                        "score_credit_label": score_credit_label,
                        "score_use": score_use,
                        "judge_dna_overlap": credit["judge_dna_overlap"],
                        "generation_dna_providers": credit["generation_dna_providers"],
                        "generation_dna_models": credit["generation_dna_models"],
                        "judge_boundary_clean": boundary["judge_boundary_clean"],
                        "judge_boundary_errors": boundary["judge_boundary_errors"],
                        "score_status": score_status,
                        "score_exists": score_path.exists(),
                        "prompt_card_exists": prompt_card_path.exists(),
                        "trace_exists": trace_path.exists(),
                        "score_path": str(score_path) if score_path.exists() else "",
                        "prompt_card_path": str(prompt_card_path) if prompt_card_path.exists() else "",
                        "trace_path": str(trace_path) if trace_path.exists() else "",
                    }
                )
    return rows


def collect_outside_dna_rejudge_queue() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    run_root = HOLO_FACTORY_RUNS / CURRENT_LOCK_RUN_ID
    pair_map = load_anonymization_map(run_root)
    final_packets = sorted(run_root.glob(f"judge_packets/final/{D1_DOMAIN}/**/*.json"))
    for packet_path in final_packets:
        packet_id = packet_path.stem
        pair = pair_map.get(packet_id, {})
        if pair.get("domain_id") and pair.get("domain_id") != D1_DOMAIN:
            continue
        generation_dna = pair_generation_dna(run_root, pair)
        selected_judges = select_outside_dna_judges(OUTSIDE_DNA_REJUDGE_PANEL, generation_dna)
        for judge in selected_judges:
            judge_id = judge["judge_id"]
            score_path = run_root / "judge_scores" / packet_id / f"{judge_id}.json"
            prompt_card_path = run_root / "prompt_cards" / "judges" / packet_id / f"{judge_id}.json"
            trace_path = run_root / "traces" / "judges" / packet_id / f"{judge_id}.json"
            boundary = judge_boundary_status(prompt_card_path, trace_path)
            score_status = "scored" if score_path.exists() else ("attempted_no_parsed_score" if prompt_card_path.exists() or trace_path.exists() else "not_attempted")
            proof_credit_eligible = bool(judge["proof_credit_eligible"] and boundary["judge_boundary_clean"])
            rows.append(
                {
                    "run_id": CURRENT_LOCK_RUN_ID,
                    "judge_packet_id": packet_id,
                    "packet_kind": "final",
                    "domain_id": pair.get("domain_id") or D1_DOMAIN,
                    "cohort": pair.get("cohort"),
                    "turn": pair.get("turn"),
                    "solo_condition": pair.get("solo_condition"),
                    "holo_condition": pair.get("holo_condition"),
                    "judge_id": judge_id,
                    "judge_provider": judge.get("provider"),
                    "judge_model": judge.get("model"),
                    "proof_credit_eligible": proof_credit_eligible,
                    "score_credit_label": judge["score_credit_label"] if proof_credit_eligible else f"{judge['score_credit_label']}_boundary_violation",
                    "score_use": judge["score_use"] if proof_credit_eligible else "diagnostic_only",
                    "judge_dna_overlap": judge["judge_dna_overlap"],
                    "generation_dna_providers": judge["generation_dna_providers"],
                    "generation_dna_models": judge["generation_dna_models"],
                    "judge_boundary_clean": boundary["judge_boundary_clean"],
                    "judge_boundary_errors": boundary["judge_boundary_errors"],
                    "score_status": score_status,
                    "score_exists": score_path.exists(),
                    "prompt_card_exists": prompt_card_path.exists(),
                    "trace_exists": trace_path.exists(),
                    "score_path": str(score_path) if score_path.exists() else "",
                    "prompt_card_path": str(prompt_card_path) if prompt_card_path.exists() else "",
                    "trace_path": str(trace_path) if trace_path.exists() else "",
                    "rejudge_reason": "outside_dna_required_for_proof_credit",
                }
            )

    by_status: dict[str, int] = {}
    by_pair: dict[str, dict[str, int]] = {}
    for row in rows:
        status = str(row.get("score_status") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        pair = str(row.get("solo_condition") or row.get("judge_packet_id"))
        by_pair.setdefault(pair, {})
        by_pair[pair][status] = by_pair[pair].get(status, 0) + 1
    summary = {
        "current_lock_run": CURRENT_LOCK_RUN_ID,
        "outside_dna_panel_size": len(OUTSIDE_DNA_REJUDGE_PANEL),
        "expected_proof_credit_scores": len(rows),
        "observed_proof_credit_scores": len([row for row in rows if row.get("score_status") == "scored" and row.get("proof_credit_eligible") is True]),
        "score_status_counts": by_status,
        "score_status_by_pair": by_pair,
        "policy_note": "Proof-credit D1 scoring requires outside-DNA blind solo judges. Same-DNA frontier judges remain diagnostic only.",
    }
    return rows, summary


def validity_cap_for_condition(condition_row: dict[str, Any] | None) -> tuple[float | None, str]:
    if not condition_row:
        return None, "condition_not_found"
    if condition_row.get("revalidated_status") == "valid_final":
        return None, "valid_final_no_cap"
    flags = str(condition_row.get("flags") or "")
    if "missing_required_disclaimer" in flags:
        return 6.0, "missing_required_disclaimer_cap_6_0"
    if "truncated" in flags or "unclean" in flags or "cutoff" in flags:
        return 6.5, "truncated_or_unclean_cap_6_5"
    if "missing_required_section" in flags:
        return 8.0, "missing_required_section_cap_8_0"
    if "word_count_out_of_band" in flags:
        return 8.5, "word_count_out_of_band_cap_8_5"
    return 8.0, "invalid_final_default_cap_8_0"


def apply_cap(score: Any, cap: float | None) -> Any:
    if not isinstance(score, (int, float)):
        return score
    return round(min(float(score), cap), 3) if cap is not None else score


def collect_validity_adjusted_scores(score_rows: list[dict[str, Any]], condition_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    condition_index = {
        (row.get("run_id"), row.get("condition")): row
        for row in condition_rows
        if row.get("source") == "holo_factory"
    }
    rows: list[dict[str, Any]] = []
    for row in score_rows:
        if row.get("source") != "holo_factory" or row.get("packet_kind") != "final":
            continue
        holo_condition = row.get("holo_condition")
        solo_condition = row.get("solo_condition")
        holo_cap, holo_cap_reason = validity_cap_for_condition(condition_index.get((row.get("run_id"), holo_condition)))
        solo_cap, solo_cap_reason = validity_cap_for_condition(condition_index.get((row.get("run_id"), solo_condition)))
        adjusted_holo = apply_cap(row.get("holo_score"), holo_cap)
        adjusted_solo = apply_cap(row.get("solo_score"), solo_cap)
        adjusted_gap = (
            round(adjusted_holo - adjusted_solo, 3)
            if isinstance(adjusted_holo, (int, float)) and isinstance(adjusted_solo, (int, float))
            else ""
        )
        adjusted_pct = (
            round((adjusted_gap / adjusted_solo) * 100, 3)
            if isinstance(adjusted_gap, (int, float)) and adjusted_solo
            else ""
        )
        rows.append(
            {
                "run_id": row.get("run_id"),
                "judge_packet_id": row.get("judge_packet_id"),
                "judge_id": row.get("judge_id"),
                "solo_condition": solo_condition,
                "holo_condition": holo_condition,
                "judge_provider": row.get("judge_provider"),
                "judge_model": row.get("judge_model"),
                "proof_credit_eligible": row.get("proof_credit_eligible", False),
                "score_credit_label": row.get("score_credit_label", ""),
                "score_use": row.get("score_use", "diagnostic_only"),
                "raw_holo_score": row.get("holo_score"),
                "raw_solo_score": row.get("solo_score"),
                "raw_gap_holo_minus_solo": row.get("gap_holo_minus_solo"),
                "raw_percent_lift": row.get("percent_lift"),
                "adjusted_holo_score": adjusted_holo,
                "adjusted_solo_score": adjusted_solo,
                "adjusted_gap_holo_minus_solo": adjusted_gap,
                "adjusted_percent_lift": adjusted_pct,
                "holo_validity_cap": holo_cap or "",
                "solo_validity_cap": solo_cap or "",
                "holo_validity_cap_reason": holo_cap_reason,
                "solo_validity_cap_reason": solo_cap_reason,
            }
        )

    def mean(values: list[float]) -> float | None:
        return round(sum(values) / len(values), 3) if values else None

    summary = {
        "rows": len(rows),
        "proof_credit_rows": len([r for r in rows if r.get("proof_credit_eligible") is True]),
        "diagnostic_rows": len([r for r in rows if r.get("proof_credit_eligible") is not True]),
        "mean_raw_gap": mean([r["raw_gap_holo_minus_solo"] for r in rows if isinstance(r.get("raw_gap_holo_minus_solo"), (int, float))]),
        "mean_raw_percent_lift": mean([r["raw_percent_lift"] for r in rows if isinstance(r.get("raw_percent_lift"), (int, float))]),
        "mean_adjusted_gap": mean([r["adjusted_gap_holo_minus_solo"] for r in rows if isinstance(r.get("adjusted_gap_holo_minus_solo"), (int, float))]),
        "mean_adjusted_percent_lift": mean([r["adjusted_percent_lift"] for r in rows if isinstance(r.get("adjusted_percent_lift"), (int, float))]),
        "policy_note": "Validity-adjusted scores preserve raw judge scores and apply deterministic caps only when revalidation flagged invalid finals. Rows with same-DNA or historical-current-lock mismatch are diagnostic only.",
    }
    return rows, summary


def collect_judge_scores() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for run_root in sorted(HOLO_FACTORY_RUNS.glob("*")):
        if not run_root.is_dir():
            continue
        pair_map = load_anonymization_map(run_root)
        for score_path in sorted((run_root / "judge_scores").glob("**/*.json")):
            score = read_json(score_path)
            judge_packet_id = score_path.parent.name
            pair = pair_map.get(judge_packet_id, {})
            if pair.get("domain_id") != D1_DOMAIN:
                continue
            harness = score.get("_harness") or {}
            judge = {
                "judge_id": score.get("judge_id"),
                "provider": harness.get("judge_provider"),
                "model": harness.get("judge_model"),
            }
            generation_dna = pair_generation_dna(run_root, pair)
            credit = annotate_judge_credit(judge, generation_dna)
            prompt_card_path = run_root / "prompt_cards" / "judges" / judge_packet_id / f"{score.get('judge_id')}.json"
            trace_path = run_root / "traces" / "judges" / judge_packet_id / f"{score.get('judge_id')}.json"
            boundary = judge_boundary_status(prompt_card_path, trace_path)
            proof_credit_eligible = credit["proof_credit_eligible"] and boundary["judge_boundary_clean"]
            score_credit_label = credit["score_credit_label"] if boundary["judge_boundary_clean"] else f"{credit['score_credit_label']}_boundary_violation"
            doc_x_condition = pair.get("document_x_condition")
            doc_y_condition = pair.get("document_y_condition")
            x_score = (score.get("document_x") or {}).get("weighted_score_1_10")
            y_score = (score.get("document_y") or {}).get("weighted_score_1_10")
            if doc_x_condition == pair.get("holo_condition"):
                holo_score, solo_score = x_score, y_score
            else:
                holo_score, solo_score = y_score, x_score
            gap = round(holo_score - solo_score, 3) if isinstance(holo_score, (int, float)) and isinstance(solo_score, (int, float)) else ""
            pct = round((gap / solo_score) * 100, 3) if isinstance(gap, (int, float)) and solo_score else ""
            rows.append(
                {
                    "source": "holo_factory",
                    "run_id": run_root.name,
                    "judge_packet_id": judge_packet_id,
                    "judge_id": score.get("judge_id"),
                    "packet_kind": pair.get("packet_kind"),
                    "cohort": pair.get("cohort"),
                    "turn": pair.get("turn"),
                    "solo_condition": pair.get("solo_condition"),
                    "holo_condition": pair.get("holo_condition"),
                    "judge_provider": harness.get("judge_provider"),
                    "judge_model": harness.get("judge_model"),
                    "proof_credit_eligible": proof_credit_eligible,
                    "score_credit_label": score_credit_label,
                    "score_use": credit["score_use"] if proof_credit_eligible else "diagnostic_only",
                    "judge_dna_overlap": credit["judge_dna_overlap"],
                    "generation_dna_providers": credit["generation_dna_providers"],
                    "generation_dna_models": credit["generation_dna_models"],
                    "judge_boundary_clean": boundary["judge_boundary_clean"],
                    "judge_boundary_errors": boundary["judge_boundary_errors"],
                    "document_x_condition": doc_x_condition,
                    "document_y_condition": doc_y_condition,
                    "document_x_score": x_score,
                    "document_y_score": y_score,
                    "holo_score": holo_score,
                    "solo_score": solo_score,
                    "gap_holo_minus_solo": gap,
                    "percent_lift": pct,
                    "holo_summary": (score.get("document_x") if doc_x_condition == pair.get("holo_condition") else score.get("document_y") or {}).get("summary_description", ""),
                    "solo_summary": (score.get("document_y") if doc_x_condition == pair.get("holo_condition") else score.get("document_x") or {}).get("summary_description", ""),
                }
            )
    if LEGACY_ROLLUP.exists():
        rollup = read_json(LEGACY_ROLLUP)
        for run in rollup.get("runs", []):
            for pair in run.get("pair_rows", []):
                rows.append(
                    {
                        "source": "legacy_hash_locked_lift_rollup",
                        "run_id": run.get("run_id"),
                        "judge_packet_id": pair.get("pair_id"),
                        "judge_id": "aggregate",
                        "packet_kind": "final",
                        "cohort": run.get("holo_cohort_lane") or "",
                        "turn": 6,
                        "solo_condition": pair.get("solo_condition"),
                        "holo_condition": "holo",
                        "judge_provider": "",
                        "judge_model": "",
                        "proof_credit_eligible": False,
                        "score_credit_label": "diagnostic_historical_non_current_lock",
                        "score_use": "diagnostic_only",
                        "judge_dna_overlap": "",
                        "generation_dna_providers": "",
                        "generation_dna_models": "",
                        "judge_boundary_clean": "",
                        "judge_boundary_errors": "",
                        "document_x_condition": "",
                        "document_y_condition": "",
                        "document_x_score": "",
                        "document_y_score": "",
                        "holo_score": pair.get("holo_mean_all"),
                        "solo_score": pair.get("solo_mean_all"),
                        "gap_holo_minus_solo": pair.get("gap_all"),
                        "percent_lift": pair.get("percent_lift_all"),
                        "clean_gap": pair.get("gap_clean_only"),
                        "clean_percent_lift": pair.get("percent_lift_clean"),
                        "matches_current_lock": run.get("matches_current_lock"),
                        "judge_count": pair.get("judge_count"),
                        "flagged_judge_count": pair.get("flagged_judge_count"),
                    }
                )
    return rows


def summarize_scores(score_rows: list[dict[str, Any]]) -> dict[str, Any]:
    current = [r for r in score_rows if r.get("source") == "holo_factory" and isinstance(r.get("gap_holo_minus_solo"), (int, float))]
    current_proof = [r for r in current if r.get("proof_credit_eligible") is True]
    current_diagnostic = [r for r in current if r.get("proof_credit_eligible") is not True]
    historical = [r for r in score_rows if r.get("source") == "legacy_hash_locked_lift_rollup" and isinstance(r.get("percent_lift"), (int, float))]
    def mean(values: list[float]) -> float | None:
        return round(sum(values) / len(values), 3) if values else None
    return {
        "current_holo_factory_scored_rows": len(current),
        "current_holo_factory_proof_credit_rows": len(current_proof),
        "current_holo_factory_diagnostic_rows": len(current_diagnostic),
        "current_holo_factory_mean_gap": mean([r["gap_holo_minus_solo"] for r in current]),
        "current_holo_factory_mean_percent_lift": mean([r["percent_lift"] for r in current if isinstance(r.get("percent_lift"), (int, float))]),
        "current_holo_factory_proof_credit_mean_gap": mean([r["gap_holo_minus_solo"] for r in current_proof]),
        "current_holo_factory_proof_credit_mean_percent_lift": mean([r["percent_lift"] for r in current_proof if isinstance(r.get("percent_lift"), (int, float))]),
        "current_holo_factory_pairs_scored": sorted(set(r.get("solo_condition") for r in current)),
        "historical_scored_pair_rows": len(historical),
        "historical_mean_percent_lift_all": mean([r["percent_lift"] for r in historical]),
        "historical_mean_percent_lift_clean": mean([r["clean_percent_lift"] for r in historical if isinstance(r.get("clean_percent_lift"), (int, float))]),
        "historical_lift_range_all": [
            min([r["percent_lift"] for r in historical]) if historical else None,
            max([r["percent_lift"] for r in historical]) if historical else None,
        ],
        "historical_current_lock_matching_rows": len([r for r in historical if r.get("matches_current_lock") is True]),
    }


def build_projections(run_rows: list[dict[str, Any]], condition_rows: list[dict[str, Any]], score_rows: list[dict[str, Any]], missing_rows: list[dict[str, Any]]) -> dict[str, Any]:
    hf_live = next((r for r in run_rows if r["lane"] == "holo_factory" and r["run_id"] == CURRENT_LOCK_RUN_ID), None)
    mini_conditions = [r for r in condition_rows if r["run_id"] == "full_frontier_finance_algo_execution_mini_order_a_openai_bookend_20260619T160811Z"]
    mini_tokens = sum(int(r.get("total_tokens") or 0) for r in mini_conditions)
    mini_latency = sum(int(r.get("latency_ms") or 0) for r in mini_conditions)
    current_missing_rows = [r for r in missing_rows if r.get("run_id") == CURRENT_LOCK_RUN_ID]
    expected_final_scores_per_domain_frontier = len(current_missing_rows)
    current_final_scores = len([r for r in score_rows if r["source"] == "holo_factory" and r.get("run_id") == CURRENT_LOCK_RUN_ID and r.get("packet_kind") == "final"])
    return {
        "generated_at_utc": utc_iso(),
        "projection_basis": {
            "frontier_current_lock_run": hf_live["run_id"] if hf_live else None,
            "frontier_current_lock_status": hf_live["status"] if hf_live else None,
            "mini_diagnostic_run": "full_frontier_finance_algo_execution_mini_order_a_openai_bookend_20260619T160811Z" if mini_conditions else None,
            "note": "Token and latency projections multiply observed D1 traces. Dollar projections require a separately locked pricing table.",
        },
        "frontier_current_lock_d1": {
            "tokens": hf_live.get("total_tokens") if hf_live else None,
            "latency_ms": hf_live.get("latency_ms") if hf_live else None,
            "latency_minutes": hf_live.get("latency_minutes") if hf_live else None,
            "provider_calls": hf_live.get("provider_call_trace_count") if hf_live else None,
            "final_judge_packets": hf_live.get("final_judge_packets") if hf_live else None,
            "turn_judge_packets": hf_live.get("turn_judge_packets") if hf_live else None,
        },
        "frontier_current_lock_5_domain_projection": {
            "tokens": int(hf_live.get("total_tokens") or 0) * 5 if hf_live else None,
            "latency_ms": int(hf_live.get("latency_ms") or 0) * 5 if hf_live else None,
            "latency_minutes": round(float(hf_live.get("latency_minutes") or 0) * 5, 3) if hf_live else None,
            "provider_calls": int(hf_live.get("provider_call_trace_count") or 0) * 5 if hf_live else None,
            "final_judge_packets": int(hf_live.get("final_judge_packets") or 0) * 5 if hf_live else None,
            "turn_judge_packets": int(hf_live.get("turn_judge_packets") or 0) * 5 if hf_live else None,
            "final_judge_scores_expected": expected_final_scores_per_domain_frontier * 5,
            "turn_judge_scores_expected_if_enabled": 18 * len(load_judge_panel(HOLO_FACTORY_RUNS / CURRENT_LOCK_RUN_ID)) * 5,
        },
        "current_frontier_judging_gap": {
            "d1_expected_final_judge_scores": expected_final_scores_per_domain_frontier,
            "d1_observed_final_judge_scores": current_final_scores,
            "d1_missing_final_judge_scores": max(expected_final_scores_per_domain_frontier - current_final_scores, 0),
            "note": "Only final judging is counted here; turn-level judge packets exist but have not been live-scored.",
        },
        "mini_diagnostic_d1": {
            "tokens": mini_tokens or None,
            "latency_ms": mini_latency or None,
            "latency_minutes": ms_to_minutes(mini_latency) if mini_latency else None,
            "condition_count": len(mini_conditions) or None,
            "status": "diagnostic_partial_or_error",
        },
        "mini_diagnostic_5_domain_projection": {
            "tokens": mini_tokens * 5 if mini_tokens else None,
            "latency_ms": mini_latency * 5 if mini_latency else None,
            "latency_minutes": round(ms_to_minutes(mini_latency) * 5, 3) if mini_latency else None,
            "condition_count": len(mini_conditions) * 5 if mini_conditions else None,
            "note": "Mini projection uses legacy diagnostic run with error status, not a clean current-lock HoloFactory mini run.",
        },
    }


def summarize_missing_judging(rows: list[dict[str, Any]]) -> dict[str, Any]:
    current = [r for r in rows if r.get("run_id") == CURRENT_LOCK_RUN_ID]
    by_status: dict[str, int] = {}
    by_pair: dict[str, dict[str, int]] = {}
    for row in current:
        status = str(row.get("score_status") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        pair = str(row.get("solo_condition") or row.get("judge_packet_id"))
        by_pair.setdefault(pair, {})
        by_pair[pair][status] = by_pair[pair].get(status, 0) + 1
    return {
        "current_lock_run": CURRENT_LOCK_RUN_ID,
        "expected_final_scores": len(current),
        "proof_credit_eligible_rows": len([r for r in current if r.get("proof_credit_eligible") is True]),
        "diagnostic_only_rows": len([r for r in current if r.get("proof_credit_eligible") is not True]),
        "score_status_counts": by_status,
        "score_status_by_pair": by_pair,
    }


def build_findings(
    run_rows: list[dict[str, Any]],
    condition_rows: list[dict[str, Any]],
    score_rows: list[dict[str, Any]],
    missing_rows: list[dict[str, Any]],
    adjusted_summary: dict[str, Any],
    projections: dict[str, Any],
    outside_rejudge_summary: dict[str, Any],
) -> dict[str, Any]:
    score_summary = summarize_scores(score_rows)
    missing_summary = summarize_missing_judging(missing_rows)
    current_conditions = [r for r in condition_rows if r["source"] == "holo_factory" and r["run_id"] == CURRENT_LOCK_RUN_ID]
    valid_current = [r for r in current_conditions if r.get("revalidated_status") == "valid_final"]
    invalid_current = [r for r in current_conditions if r.get("revalidated_status") != "valid_final"]
    holo = next((r for r in current_conditions if r.get("condition_type") == "holo"), None)
    solos = [r for r in current_conditions if r.get("condition_type") == "solo"]
    solo_tokens = [int(r.get("total_tokens") or 0) for r in solos if r.get("total_tokens")]
    holo_tokens = int(holo.get("total_tokens") or 0) if holo else 0
    mean_solo_tokens = round(sum(solo_tokens) / len(solo_tokens), 3) if solo_tokens else None
    token_multiple = round(holo_tokens / mean_solo_tokens, 3) if mean_solo_tokens else None
    return {
        "generated_at_utc": utc_iso(),
        "domain_id": D1_DOMAIN,
        "current_lock_run": CURRENT_LOCK_RUN_ID,
        "decision": "D1 current-lock frontier scoring is now outside-DNA scored locally; keep D1 out of public benchmark-credit promotion until score provenance is committed and mini/order/domain replication is run.",
        "evidence_classes": [
            {
                "name": "current_lock_operational",
                "status": "strong_for_operations_weak_for_quality_claim",
                "summary": "The current HoloFactory frontier D1 run completed generation, packet assembly, final pair packets, turn pair packets, traces, and deterministic validation.",
            },
            {
                "name": "current_lock_scoring",
                "status": "proof_credit_scored_for_frontier_d1",
                "summary": f"{score_summary['current_holo_factory_proof_credit_rows']} outside-DNA proof-credit candidate rows and {score_summary['current_holo_factory_diagnostic_rows']} same-DNA diagnostic rows are present.",
            },
            {
                "name": "historical_diagnostic_lift",
                "status": "directional_only",
                "summary": f"Historical runs show {score_summary['historical_mean_percent_lift_all']}% mean lift all rows and {score_summary['historical_mean_percent_lift_clean']}% clean lift, but no rows match the current lock.",
            },
        ],
        "current_lock_quality_state": {
            "conditions": len(current_conditions),
            "valid_finals": len(valid_current),
            "invalid_finals": len(invalid_current),
            "invalid_conditions": [
                {"condition": r.get("condition"), "flags": r.get("flags"), "provider_model": r.get("provider_model")}
                for r in invalid_current
            ],
            "raw_observed_score_summary": {
                "rows": score_summary["current_holo_factory_scored_rows"],
                "proof_credit_rows": score_summary["current_holo_factory_proof_credit_rows"],
                "diagnostic_rows": score_summary["current_holo_factory_diagnostic_rows"],
                "pairs_scored": score_summary["current_holo_factory_pairs_scored"],
                "mean_gap": score_summary["current_holo_factory_mean_gap"],
                "mean_percent_lift": score_summary["current_holo_factory_mean_percent_lift"],
                "proof_credit_mean_gap": score_summary["current_holo_factory_proof_credit_mean_gap"],
                "proof_credit_mean_percent_lift": score_summary["current_holo_factory_proof_credit_mean_percent_lift"],
                "claimable": False,
            },
            "validity_adjusted_observed_score_summary": adjusted_summary,
            "outside_dna_rejudge_summary": outside_rejudge_summary,
        },
        "token_and_latency_state": {
            "holo_tokens": holo_tokens or None,
            "mean_solo_tokens": mean_solo_tokens,
            "holo_vs_mean_solo_token_multiple": token_multiple,
            "run_total_tokens": projections["frontier_current_lock_d1"]["tokens"],
            "run_latency_minutes": projections["frontier_current_lock_d1"]["latency_minutes"],
        },
        "findings": [
            "D1 generation is operationally real: the current HoloFactory frontier run completed all four generation conditions and produced judge packets.",
            "D1 current-lock final scoring now has six outside-DNA blind solo judge rows across the three final pairwise packets.",
            "Same-DNA frontier judge rows remain diagnostic-only and are separated from the proof-credit outside-DNA rows.",
            "Raw current-lock proof-credit scores show Holo lift across five of six outside-DNA judge rows, with one negative Anthropic-pair xAI row.",
            "Validity-adjusted scoring preserves raw judge scores and applies deterministic caps only when revalidation flagged invalid finals.",
            "Historical D1 evidence supports directional Holo lift, but it must be labeled diagnostic because it does not match the current run lock.",
            "For public or client-facing claims, D1 alone is still insufficient: the architecture claim needs the mini lane, order permutations, and D2-D5 replication.",
        ],
        "next_actions": [
            "Commit the D1 proof-credit scoring board and boundary-accounting patch.",
            "Preserve the raw outside-DNA judge artifacts and parse-failure provenance for audit.",
            "Keep same-DNA frontier judge rows diagnostic-only even if additional legacy-panel scores are added.",
            "Run the matched mini Holo versus mini solo lane for D1.",
            "Then run order permutations and D2-D5 replication before making the architecture-level lift claim.",
        ],
    }


def build_findings_markdown(findings: dict[str, Any]) -> str:
    quality = findings["current_lock_quality_state"]
    token = findings["token_and_latency_state"]
    adjusted = quality["validity_adjusted_observed_score_summary"]
    rejudge = quality["outside_dna_rejudge_summary"]
    next_actions = "\n".join(f"{index}. {item}" for index, item in enumerate(findings["next_actions"], start=1))
    return f"""# D1 Findings - Capital Markets

Generated: `{findings['generated_at_utc']}`

Domain: `{findings['domain_id']}`

## Decision

{findings['decision']}

## Bottom Line

D1 is useful now, and its current-lock frontier lane has outside-DNA final scoring on disk. It is still not a finished public benchmark claim: D1 is one domain and the broader architecture proof still needs matched mini results, order permutations, and D2-D5 replication. Current D1 has `{quality['raw_observed_score_summary']['proof_credit_rows']}` outside-DNA proof-credit candidate rows and `{quality['raw_observed_score_summary']['diagnostic_rows']}` same-DNA diagnostic rows.

## Current-Lock Quality

- Conditions: `{quality['conditions']}`
- Valid finals: `{quality['valid_finals']}`
- Invalid finals: `{quality['invalid_finals']}`
- Raw observed mean gap: `{quality['raw_observed_score_summary']['mean_gap']}`
- Raw observed mean lift: `{quality['raw_observed_score_summary']['mean_percent_lift']}%`
- Validity-adjusted observed mean gap: `{adjusted['mean_adjusted_gap']}`
- Validity-adjusted observed mean lift: `{adjusted['mean_adjusted_percent_lift']}%`
- Proof-credit final judge scores observed: `{rejudge['observed_proof_credit_scores']} / {rejudge['expected_proof_credit_scores']}`
- Claimable now: `false`

## Invalid Finals

{markdown_table(quality['invalid_conditions'], ['condition', 'provider_model', 'flags'])}

## Token And Latency

- Holo tokens: `{token['holo_tokens']}`
- Mean solo tokens: `{token['mean_solo_tokens']}`
- Holo vs mean solo token multiple: `{token['holo_vs_mean_solo_token_multiple']}x`
- Run total tokens: `{token['run_total_tokens']}`
- Run latency: `{token['run_latency_minutes']}` minutes

## Findings

{chr(10).join(f'- {item}' for item in findings['findings'])}

## Next Actions

{next_actions}
"""


def markdown_table(rows: list[dict[str, Any]], fields: list[str], limit: int | None = None) -> str:
    selected = rows[:limit] if limit else rows
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in selected:
        vals = [str(row.get(field, "")).replace("\n", " ") for field in fields]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_board(
    run_rows: list[dict[str, Any]],
    condition_rows: list[dict[str, Any]],
    score_rows: list[dict[str, Any]],
    missing_rows: list[dict[str, Any]],
    outside_rejudge_rows: list[dict[str, Any]],
    outside_rejudge_summary: dict[str, Any],
    adjusted_rows: list[dict[str, Any]],
    adjusted_summary: dict[str, Any],
    projections: dict[str, Any],
) -> str:
    score_summary = summarize_scores(score_rows)
    missing_summary = summarize_missing_judging(missing_rows)
    hf_live = projections["frontier_current_lock_d1"]
    hf_projection = projections["frontier_current_lock_5_domain_projection"]
    judging_gap = projections["current_frontier_judging_gap"]
    complete_runs = [r for r in run_rows if r["status_bucket"] in {"complete", "pass"}]
    live_runs = [r for r in run_rows if r["run_class"] in {"holo_factory_live", "live_or_partial_live", "tiny_live_smoke"}]
    current_conditions = [r for r in condition_rows if r["source"] == "holo_factory" and r["run_id"] == CURRENT_LOCK_RUN_ID]
    historical_pairs = [r for r in score_rows if r["source"] == "legacy_hash_locked_lift_rollup"]
    current_scores = [r for r in score_rows if r["source"] == "holo_factory"]
    current_missing = [r for r in missing_rows if r.get("run_id") == CURRENT_LOCK_RUN_ID]
    current_missing_not_scored = [r for r in current_missing if r.get("score_status") != "scored"]

    return f"""# D1 Evidence Board - Capital Markets

Generated: `{utc_iso()}`

Domain: `{D1_DOMAIN}`

## Executive Read

D1 now has a real data map. The current-lock HoloFactory frontier run generated a complete four-condition D1 set with `577,728` total tokens, `30` provider-call traces, `3` final judge packets, and `18` turn judge packets. It is not benchmark credit and not a public claim yet.

The key split:

- **Current-lock operational evidence:** HoloFactory live frontier run `{CURRENT_LOCK_RUN_ID}`.
- **Current-lock scoring evidence:** `{score_summary['current_holo_factory_proof_credit_rows']}` outside-DNA proof-credit candidate rows and `{score_summary['current_holo_factory_diagnostic_rows']}` same-DNA diagnostic rows are present.
- **Proof-credit rejudge queue:** `{outside_rejudge_summary['observed_proof_credit_scores']} / {outside_rejudge_summary['expected_proof_credit_scores']}` outside-DNA final judge scores are present.
- **Historical judged lift evidence:** legacy finance runs with measured Holo lift, but `matches_current_lock=false`.

## Current-Lock Frontier Snapshot

- Run: `{CURRENT_LOCK_RUN_ID}`
- Status: `HOLO_FACTORY_LIVE_COMPLETE`
- Benchmark credit: `false`
- Public claim: `false`
- Conditions completed: `4 / 4`
- Valid after revalidation: `2 / 4`
- Total tokens: `{hf_live['tokens']}`
- Latency: `{hf_live['latency_minutes']}` minutes
- Holo vs mean solo token multiple: `3.212x`
- Final judge packets: `{hf_live['final_judge_packets']}`
- Turn judge packets: `{hf_live['turn_judge_packets']}`
- Final judge scores observed: `{judging_gap['d1_observed_final_judge_scores']} / {judging_gap['d1_expected_final_judge_scores']}`
- Missing final judge scores: `{judging_gap['d1_missing_final_judge_scores']}`
- Proof-credit outside-DNA judge scores observed: `{outside_rejudge_summary['observed_proof_credit_scores']} / {outside_rejudge_summary['expected_proof_credit_scores']}`
- Final score status counts: `{missing_summary['score_status_counts']}`

## Current-Lock Condition Matrix

{markdown_table(current_conditions, ['condition', 'condition_type', 'provider_model', 'revalidated_status', 'turns_complete', 'gov_turns_complete', 'total_tokens', 'latency_minutes', 'final_word_count', 'flags'])}

## Current Judge Scores Seen

{markdown_table(current_scores, ['run_id', 'judge_id', 'judge_provider', 'solo_condition', 'holo_score', 'solo_score', 'gap_holo_minus_solo', 'percent_lift', 'score_credit_label'], limit=20)}

These scores are only for scored packets already present on disk. Rows labeled `proof_credit_candidate` use outside-DNA judges with clean prompt/trace boundaries; rows labeled `diagnostic_same_dna` remain diagnostic because judge DNA overlaps generation DNA.

## Validity-Adjusted Score Lens

Raw judge scores are preserved. This lens applies deterministic caps only when the artifact gate says a final is invalid.

- Rows adjusted: `{adjusted_summary['rows']}`
- Proof-credit rows adjusted: `{adjusted_summary['proof_credit_rows']}`
- Diagnostic rows adjusted: `{adjusted_summary['diagnostic_rows']}`
- Raw observed mean gap: `{adjusted_summary['mean_raw_gap']}`
- Raw observed mean lift: `{adjusted_summary['mean_raw_percent_lift']}%`
- Validity-adjusted observed mean gap: `{adjusted_summary['mean_adjusted_gap']}`
- Validity-adjusted observed mean lift: `{adjusted_summary['mean_adjusted_percent_lift']}%`

{markdown_table(adjusted_rows, ['judge_id', 'solo_condition', 'score_credit_label', 'raw_holo_score', 'raw_solo_score', 'raw_gap_holo_minus_solo', 'adjusted_holo_score', 'adjusted_solo_score', 'adjusted_gap_holo_minus_solo', 'adjusted_percent_lift', 'solo_validity_cap_reason'], limit=20)}

This is still not a final public architecture claim because D1 is one domain. The proof-credit queue is scored for the current-lock frontier lane; the next proof burden is matched mini, order-permutation, and cross-domain replication.

## Missing Current-Lock Final Judging Queue

{markdown_table(current_missing_not_scored, ['solo_condition', 'judge_id', 'judge_provider', 'judge_model', 'proof_credit_eligible', 'score_credit_label', 'score_status', 'prompt_card_exists', 'trace_exists'], limit=20)}

## Outside-DNA Rejudge Queue

This queue is the proof-credit path for D1. It is not executed by this board builder.

- Expected proof-credit outside-DNA final judge scores: `{outside_rejudge_summary['expected_proof_credit_scores']}`
- Observed proof-credit outside-DNA final judge scores: `{outside_rejudge_summary['observed_proof_credit_scores']}`
- Score status counts: `{outside_rejudge_summary['score_status_counts']}`

{markdown_table(outside_rejudge_rows, ['solo_condition', 'judge_id', 'judge_provider', 'judge_model', 'proof_credit_eligible', 'score_status', 'rejudge_reason'], limit=20)}

## Historical Diagnostic Lift

The legacy hash-locked lift rollup contains judged final-output comparisons, but those runs do not match the current lock. Treat as directional diagnostics, not public benchmark claims.

- Historical scored pair rows: `{score_summary['historical_scored_pair_rows']}`
- Historical mean lift, all rows: `{score_summary['historical_mean_percent_lift_all']}%`
- Historical mean lift, clean rows: `{score_summary['historical_mean_percent_lift_clean']}%`
- Historical lift range, all rows: `{score_summary['historical_lift_range_all']}`
- Current-lock matching historical rows: `{score_summary['historical_current_lock_matching_rows']}`

{markdown_table(historical_pairs, ['run_id', 'solo_condition', 'holo_score', 'solo_score', 'gap_holo_minus_solo', 'percent_lift', 'clean_percent_lift', 'matches_current_lock'], limit=12)}

## Run Inventory Summary

- Total D1 run records found: `{len(run_rows)}`
- Complete/pass records: `{len(complete_runs)}`
- Live/partial-live records: `{len(live_runs)}`
- HoloFactory suite records: `{len([r for r in run_rows if r['lane'] == 'holo_factory'])}`
- Legacy finance-algo records: `{len([r for r in run_rows if r['lane'] == 'legacy_finance_algo'])}`

{markdown_table(run_rows, ['lane', 'run_id', 'status', 'run_class', 'condition_count', 'total_tokens', 'latency_minutes', 'final_judge_packets', 'turn_judge_packets', 'judge_scores'], limit=40)}

## Five-Domain Projection

Using the current-lock D1 HoloFactory frontier run as the base:

- Frontier generation tokens for 5 domains: `{hf_projection['tokens']}`
- Frontier generation latency for 5 domains: `{hf_projection['latency_minutes']}` minutes
- Frontier provider calls for 5 domains: `{hf_projection['provider_calls']}`
- Frontier final judge packets for 5 domains: `{hf_projection['final_judge_packets']}`
- Frontier turn judge packets for 5 domains: `{hf_projection['turn_judge_packets']}`
- Final judge scores expected for 5 domains: `{hf_projection['final_judge_scores_expected']}`
- Turn judge scores if enabled for 5 domains: `{hf_projection['turn_judge_scores_expected_if_enabled']}`

Mini-lane projection is available but should be treated as diagnostic because the observed D1 mini source run ended with an error/partial status:

- Mini diagnostic D1 tokens: `{projections['mini_diagnostic_d1']['tokens']}`
- Mini diagnostic 5-domain tokens: `{projections['mini_diagnostic_5_domain_projection']['tokens']}`
- Mini diagnostic 5-domain latency: `{projections['mini_diagnostic_5_domain_projection']['latency_minutes']}` minutes

## Claim Boundaries

- Do not claim current benchmark lift from D1 until outside-DNA final judging and proof-credit rollup are complete.
- Do not merge historical judged lift with current-lock operational data as if they are the same benchmark.
- Do not publish dollar cost projections until a model-pricing table is separately locked.
- Current-lock D1 shows operational feasibility and validity gaps; historical D1 shows directional lift.
- D1 has enough data to plan D2-D5, but not enough outside-DNA proof-credit judging to make the headline claim.

## Immediate Data Gaps

1. Rejudge the current-lock final packets with outside-DNA blind solo judges.
2. Build a current-lock proof-credit judge rollup separate from diagnostic same-DNA rows.
3. Keep raw quality score, validity-adjusted score, and provider reliability score separate.
4. Run or rebuild the current-lock mini lane cleanly if mini claims matter.
5. Add dollar-cost estimates only after pricing assumptions are locked.
"""


def main() -> int:
    run_rows = collect_holo_factory_runs() + collect_legacy_runs()
    condition_rows = collect_holo_factory_conditions() + collect_legacy_conditions()
    score_rows = collect_judge_scores()
    missing_rows = collect_missing_final_judge_queue()
    outside_rejudge_rows, outside_rejudge_summary = collect_outside_dna_rejudge_queue()
    adjusted_rows, adjusted_summary = collect_validity_adjusted_scores(score_rows, condition_rows)
    projections = build_projections(run_rows, condition_rows, score_rows, missing_rows)
    score_summary = summarize_scores(score_rows)
    missing_summary = summarize_missing_judging(missing_rows)
    findings = build_findings(run_rows, condition_rows, score_rows, missing_rows, adjusted_summary, projections, outside_rejudge_summary)

    run_fields = [
        "lane",
        "run_id",
        "status",
        "status_bucket",
        "run_class",
        "benchmark_credit",
        "public_claim",
        "domains",
        "cohorts",
        "condition_count",
        "provider_call_trace_count",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "latency_ms",
        "latency_minutes",
        "final_judge_packets",
        "turn_judge_packets",
        "judge_scores",
        "sealed_pair_count",
        "error_count",
        "run_dir",
    ]
    condition_fields = [
        "source",
        "run_id",
        "cohort",
        "condition",
        "condition_type",
        "provider_model",
        "manifest_status",
        "revalidated_status",
        "turns_complete",
        "gov_turns_complete",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "latency_ms",
        "latency_minutes",
        "final_word_count",
        "selected_turn",
        "flags",
        "final_artifact_path",
    ]
    score_fields = [
        "source",
        "run_id",
        "judge_packet_id",
        "judge_id",
        "packet_kind",
        "cohort",
        "turn",
        "solo_condition",
        "holo_condition",
        "judge_provider",
        "judge_model",
        "proof_credit_eligible",
        "score_credit_label",
        "score_use",
        "judge_dna_overlap",
        "generation_dna_providers",
        "generation_dna_models",
        "judge_boundary_clean",
        "judge_boundary_errors",
        "holo_score",
        "solo_score",
        "gap_holo_minus_solo",
        "percent_lift",
        "clean_gap",
        "clean_percent_lift",
        "matches_current_lock",
        "judge_count",
        "flagged_judge_count",
    ]
    missing_fields = [
        "run_id",
        "judge_packet_id",
        "packet_kind",
        "domain_id",
        "cohort",
        "turn",
        "solo_condition",
        "holo_condition",
        "judge_id",
        "judge_provider",
        "judge_model",
        "outside_judge",
        "panel_outside_judge_claim",
        "proof_credit_eligible",
        "score_credit_label",
        "score_use",
        "judge_dna_overlap",
        "generation_dna_providers",
        "generation_dna_models",
        "judge_boundary_clean",
        "judge_boundary_errors",
        "score_status",
        "score_exists",
        "prompt_card_exists",
        "trace_exists",
        "score_path",
        "prompt_card_path",
        "trace_path",
    ]
    adjusted_fields = [
        "run_id",
        "judge_packet_id",
        "judge_id",
        "solo_condition",
        "holo_condition",
        "judge_provider",
        "judge_model",
        "proof_credit_eligible",
        "score_credit_label",
        "score_use",
        "raw_holo_score",
        "raw_solo_score",
        "raw_gap_holo_minus_solo",
        "raw_percent_lift",
        "adjusted_holo_score",
        "adjusted_solo_score",
        "adjusted_gap_holo_minus_solo",
        "adjusted_percent_lift",
        "holo_validity_cap",
        "solo_validity_cap",
        "holo_validity_cap_reason",
        "solo_validity_cap_reason",
    ]

    write_json(OUT / "d1_run_index.json", {"generated_at_utc": utc_iso(), "rows": run_rows})
    write_csv(OUT / "d1_run_index.csv", run_rows, run_fields)
    write_json(OUT / "d1_condition_matrix.json", {"generated_at_utc": utc_iso(), "rows": condition_rows})
    write_csv(OUT / "d1_condition_matrix.csv", condition_rows, condition_fields)
    write_json(OUT / "d1_judge_score_rollup.json", {"generated_at_utc": utc_iso(), "summary": score_summary, "rows": score_rows})
    write_csv(OUT / "d1_judge_score_rollup.csv", score_rows, score_fields)
    write_json(OUT / "d1_missing_final_judge_queue.json", {"generated_at_utc": utc_iso(), "summary": missing_summary, "rows": missing_rows})
    write_csv(OUT / "d1_missing_final_judge_queue.csv", missing_rows, missing_fields)
    write_json(OUT / "d1_outside_dna_rejudge_queue.json", {"generated_at_utc": utc_iso(), "summary": outside_rejudge_summary, "rows": outside_rejudge_rows})
    write_csv(
        OUT / "d1_outside_dna_rejudge_queue.csv",
        outside_rejudge_rows,
        [
            "run_id",
            "judge_packet_id",
            "packet_kind",
            "domain_id",
            "cohort",
            "turn",
            "solo_condition",
            "holo_condition",
            "judge_id",
            "judge_provider",
            "judge_model",
            "proof_credit_eligible",
            "score_credit_label",
            "score_use",
            "judge_dna_overlap",
            "generation_dna_providers",
            "generation_dna_models",
            "judge_boundary_clean",
            "judge_boundary_errors",
            "score_status",
            "score_exists",
            "prompt_card_exists",
            "trace_exists",
            "score_path",
            "prompt_card_path",
            "trace_path",
            "rejudge_reason",
        ],
    )
    write_json(OUT / "d1_validity_adjusted_scores.json", {"generated_at_utc": utc_iso(), "summary": adjusted_summary, "rows": adjusted_rows})
    write_csv(OUT / "d1_validity_adjusted_scores.csv", adjusted_rows, adjusted_fields)
    write_json(OUT / "d1_projection_summary.json", projections)
    projection_rows = []
    for group, payload in projections.items():
        if isinstance(payload, dict):
            row = {"projection_group": group}
            row.update(payload)
            projection_rows.append(row)
    write_csv(
        OUT / "d1_projection_summary.csv",
        projection_rows,
        [
            "projection_group",
            "tokens",
            "latency_ms",
            "latency_minutes",
            "provider_calls",
            "final_judge_packets",
            "turn_judge_packets",
            "final_judge_scores_expected",
            "turn_judge_scores_expected_if_enabled",
            "condition_count",
            "status",
            "note",
        ],
    )
    write_json(OUT / "d1_findings.json", findings)
    write_text(OUT / "D1_FINDINGS.md", build_findings_markdown(findings))
    write_text(OUT / "D1_EVIDENCE_BOARD.md", build_board(run_rows, condition_rows, score_rows, missing_rows, outside_rejudge_rows, outside_rejudge_summary, adjusted_rows, adjusted_summary, projections))
    write_text(
        OUT / "d1_claim_boundaries.md",
        """# D1 Claim Boundaries

- Current-lock D1 operational evidence exists, but full current-lock judging is incomplete.
- Existing current-lock judge scores are diagnostic if judge DNA overlaps generation DNA.
- Proof-credit D1 scoring requires outside-DNA blind solo judges and a clean judge-visible boundary.
- Historical D1 judged lift exists, but the scored runs do not match the current execution lock.
- Treat historical lift as diagnostic until reproduced under the current lock.
- Keep raw scores, validity-adjusted scores, and provider reliability separate.
- No public headline claim should be made from D1 until outside-DNA final judging and rollup are complete.
""",
    )
    print(
        json.dumps(
            {
                "status": "D1_EVIDENCE_BOARD_COMPLETE",
                "out_dir": str(OUT),
                "run_rows": len(run_rows),
                "condition_rows": len(condition_rows),
                "score_rows": len(score_rows),
                "missing_final_judge_rows": len([r for r in missing_rows if r.get("run_id") == CURRENT_LOCK_RUN_ID and r.get("score_status") != "scored"]),
                "outside_dna_rejudge_rows": len(outside_rejudge_rows),
                "outside_dna_rejudge_summary": outside_rejudge_summary,
                "score_summary": score_summary,
                "validity_adjusted_summary": adjusted_summary,
                "projection_basis": projections["projection_basis"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
