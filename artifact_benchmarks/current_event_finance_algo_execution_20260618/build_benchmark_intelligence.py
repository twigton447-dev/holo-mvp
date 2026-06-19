from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


PACKET_DIR = Path(__file__).resolve().parent
RUNS_DIR = PACKET_DIR / "runs"


INSIGHT_THEME_RULES = {
    "bounded_decision_policy": [
        "bounded action",
        "action set",
        "decision policy",
        "constraint ladder",
        "conflict resolution",
        "escalate",
        "pause",
        "reroute",
    ],
    "execution_microstructure_depth": [
        "microstructure",
        "quote fade",
        "queue fade",
        "markout",
        "odd-lot",
        "venue toxicity",
        "spread",
        "lit/dark",
        "clock-skew",
    ],
    "portfolio_funding_integration": [
        "funding",
        "cash",
        "T+1",
        "settlement",
        "repo",
        "collateral",
        "active-risk",
        "portfolio",
        "locate",
    ],
    "audit_control_realism": [
        "audit",
        "kill-switch",
        "FINRA",
        "validation",
        "pre-trade",
        "ledger",
        "control",
        "version",
        "owner",
    ],
    "model_risk_adversarial_insight": [
        "recency",
        "disagreement",
        "adversarial",
        "inference",
        "source_grounding",
        "prompt",
        "simulation",
        "averaging",
    ],
    "source_grounding_accuracy": [
        "source",
        "S1",
        "S2",
        "S3",
        "S4",
        "S5",
        "S6",
        "S7",
        "S8",
        "cites",
        "timestamp",
    ],
    "benchmark_design": [
        "benchmark",
        "VWAP",
        "implementation shortfall",
        "arrival",
        "TWAP",
        "POV",
        "peer",
        "gaming",
    ],
    "client_readiness_completeness": [
        "client",
        "executive",
        "usable",
        "roadmap",
        "truncated",
        "repetition",
        "complete",
        "readability",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def latest_run_dir() -> Path:
    candidates = [
        path
        for path in RUNS_DIR.iterdir()
        if path.is_dir() and (path / "run_manifest.json").exists()
    ]
    if not candidates:
        raise SystemExit(f"No run manifests found under {RUNS_DIR}")
    return max(candidates, key=lambda path: (path / "run_manifest.json").stat().st_mtime)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def clean_ending(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and stripped[-1] in ".!?)]`\"'"


def round_or_none(value: float | None, digits: int = 3) -> float | None:
    return round(value, digits) if value is not None else None


def pct_improvement(holo_mean: float | None, solo_mean: float | None) -> float | None:
    if holo_mean is None or solo_mean in (None, 0):
        return None
    return round(((holo_mean - solo_mean) / solo_mean) * 100, 1)


def score_to_condition(score: dict[str, Any], pair_map: dict[str, Any], condition: str) -> dict[str, Any]:
    if pair_map["document_x_condition"] == condition:
        return score["document_x"]
    if pair_map["document_y_condition"] == condition:
        return score["document_y"]
    raise KeyError(f"{condition} not found in pair map")


def solo_provider_for_condition(condition: str, manifest: dict[str, Any]) -> str | None:
    solo_conditions = manifest.get("solo_conditions") or {}
    provider_model = solo_conditions.get(condition)
    if isinstance(provider_model, str) and ":" in provider_model:
        return provider_model.split(":", 1)[0]
    if condition.startswith("solo_openai"):
        return "openai"
    if condition.startswith("solo_anthropic"):
        return "anthropic"
    if condition.startswith("solo_google"):
        return "google"
    if condition.startswith("solo_xai"):
        return "xai"
    return None


def load_analysis(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "analysis" / "analysis_summary.json"
    return read_json(path) if path.exists() else None


def load_pair_maps(run_dir: Path) -> dict[str, dict[str, Any]]:
    anon_path = run_dir / "sealed" / "anonymization_map.json"
    if not anon_path.exists():
        return {}
    anon = read_json(anon_path)
    return {item["judge_packet_id"]: item for item in anon.get("pairs", [])}


def collect_judge_rows(run_dir: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summary_path = run_dir / "judge_score_summary_all_pairs.json"
    if not summary_path.exists():
        return [], []
    judge_summary = read_json(summary_path)
    pair_maps = load_pair_maps(run_dir)
    judge_rows: list[dict[str, Any]] = []
    criterion_rows: list[dict[str, Any]] = []
    for pair in judge_summary.get("pair_summaries", []):
        pair_id = pair["pair_id"]
        pair_map = pair_maps[pair_id]
        solo_condition = pair["solo_condition"]
        solo_provider = solo_provider_for_condition(solo_condition, manifest)
        for score_path in sorted((run_dir / "judge_scores" / pair_id).glob("*.json")):
            score = read_json(score_path)
            harness = score.get("_harness") or {}
            judge_provider = harness.get("judge_provider")
            primary_included = not (solo_provider and judge_provider == solo_provider)
            holo_doc = score_to_condition(score, pair_map, "holo_frontier_gov")
            solo_doc = score_to_condition(score, pair_map, solo_condition)
            holo_score = float(holo_doc["weighted_score_1_10"])
            solo_score = float(solo_doc["weighted_score_1_10"])
            row = {
                "pair_id": pair_id,
                "solo_condition": solo_condition,
                "judge_id": score.get("judge_id"),
                "judge_provider": judge_provider,
                "judge_model": harness.get("judge_model"),
                "primary_score_included": primary_included,
                "primary_exclusion_reason": "same_provider_as_solo_condition" if not primary_included else "",
                "holo_score": holo_score,
                "solo_score": solo_score,
                "gap_holo_minus_solo": round(holo_score - solo_score, 3),
                "stronger_document": score.get("comparative_verdict", {}).get("stronger_document"),
                "margin_of_difference": score.get("comparative_verdict", {}).get("margin_of_difference"),
                "judge_confidence_1_5": score.get("comparative_verdict", {}).get("judge_confidence_1_5"),
                "validation_flags": score.get("validation_flags") or [],
                "holo_summary": holo_doc.get("summary_description"),
                "solo_summary": solo_doc.get("summary_description"),
                "holo_strengths": holo_doc.get("top_3_strengths") or [],
                "solo_strengths": solo_doc.get("top_3_strengths") or [],
                "holo_weaknesses": holo_doc.get("top_3_weaknesses_or_hidden_failures") or [],
                "solo_weaknesses": solo_doc.get("top_3_weaknesses_or_hidden_failures") or [],
                "holo_unsupported_or_stale_claims": holo_doc.get("unsupported_or_stale_claims") or [],
                "solo_unsupported_or_stale_claims": solo_doc.get("unsupported_or_stale_claims") or [],
                "holo_math_or_benchmark_logic_issues": holo_doc.get("math_or_benchmark_logic_issues") or [],
                "solo_math_or_benchmark_logic_issues": solo_doc.get("math_or_benchmark_logic_issues") or [],
            }
            judge_rows.append(row)
            holo_by_id = {
                item["criterion_id"]: item
                for item in holo_doc.get("criterion_scores", [])
                if isinstance(item, dict) and "criterion_id" in item
            }
            solo_by_id = {
                item["criterion_id"]: item
                for item in solo_doc.get("criterion_scores", [])
                if isinstance(item, dict) and "criterion_id" in item
            }
            for criterion_id in sorted(set(holo_by_id) | set(solo_by_id)):
                h_score = float((holo_by_id.get(criterion_id) or {}).get("score_1_10") or 0)
                s_score = float((solo_by_id.get(criterion_id) or {}).get("score_1_10") or 0)
                criterion_rows.append(
                    {
                        "pair_id": pair_id,
                        "solo_condition": solo_condition,
                        "judge_id": score.get("judge_id"),
                        "judge_provider": judge_provider,
                        "primary_score_included": primary_included,
                        "criterion_id": criterion_id,
                        "holo_score_1_10": h_score,
                        "solo_score_1_10": s_score,
                        "gap_holo_minus_solo": round(h_score - s_score, 3),
                        "holo_notes": (holo_by_id.get(criterion_id) or {}).get("notes", ""),
                        "solo_notes": (solo_by_id.get(criterion_id) or {}).get("notes", ""),
                    }
                )
    return judge_rows, criterion_rows


def collect_traces(run_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((run_dir / "traces").glob("*/*.json")):
        trace = read_json(path)
        rows.append(
            {
                "trace_path": str(path),
                "condition": trace.get("condition"),
                "call_type": trace.get("call_type"),
                "turn": trace.get("turn"),
                "provider": trace.get("provider"),
                "model": trace.get("model"),
                "role": trace.get("role"),
                "input_tokens": int(trace.get("input_tokens") or 0),
                "output_tokens": int(trace.get("output_tokens") or 0),
                "total_tokens": int(trace.get("input_tokens") or 0) + int(trace.get("output_tokens") or 0),
                "latency_ms": int(trace.get("latency_ms") or 0),
                "word_count": trace.get("word_count"),
                "artifact_path": trace.get("artifact_path"),
            }
        )
    return rows


def summarize_trace_tokens(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_condition: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "latency_ms": 0})
    by_call_type: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "latency_ms": 0})
    by_provider: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "latency_ms": 0})
    for row in trace_rows:
        for bucket, key in [(by_condition, row["condition"]), (by_call_type, row["call_type"]), (by_provider, row["provider"])]:
            if not key:
                continue
            bucket[key]["calls"] += 1
            bucket[key]["input_tokens"] += row["input_tokens"]
            bucket[key]["output_tokens"] += row["output_tokens"]
            bucket[key]["total_tokens"] += row["total_tokens"]
            bucket[key]["latency_ms"] += row["latency_ms"]
    return {
        "by_condition": dict(sorted(by_condition.items())),
        "by_call_type": dict(sorted(by_call_type.items())),
        "by_provider": dict(sorted(by_provider.items())),
    }


def turn_trajectory(trace_rows: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    role_by_turn = {
        int(item["turn"]): item.get("role")
        for item in manifest.get("turn_prompt_parity", [])
        if isinstance(item, dict) and item.get("turn")
    }
    rows = []
    for trace in trace_rows:
        call_type = trace.get("call_type") or ""
        if call_type not in {"solo_turn", "holo_analyst_turn", "holo_gov_mission_packet"}:
            continue
        rows.append(
            {
                "condition": trace["condition"],
                "turn": trace["turn"],
                "call_type": call_type,
                "provider_model": f"{trace.get('provider')}:{trace.get('model')}",
                "role": trace.get("role") or role_by_turn.get(int(trace["turn"] or 0)),
                "input_tokens": trace["input_tokens"],
                "output_tokens": trace["output_tokens"],
                "total_tokens": trace["total_tokens"],
                "latency_ms": trace["latency_ms"],
                "word_count": trace.get("word_count"),
            }
        )
    return sorted(rows, key=lambda item: (str(item["condition"]), int(item["turn"] or 0), str(item["call_type"])))


def final_artifact_checks(run_dir: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for condition in manifest.get("conditions", []):
        if condition == "holo_frontier_gov":
            path = run_dir / "artifacts" / condition / "final_selected.md"
            if not path.exists():
                path = run_dir / "artifacts" / condition / "turn_6.md"
        else:
            path = run_dir / "artifacts" / condition / "turn_6.md"
        if not path.exists():
            continue
        text = read_text(path)
        tail = text.strip()[-180:]
        rows.append(
            {
                "condition": condition,
                "artifact_path": str(path),
                "word_count": word_count(text),
                "clean_ending": clean_ending(text),
                "tail_preview": tail,
                "possible_mid_bullet_cutoff": bool(re.search(r"(\n|^)\s*[-*]\s+\S.{0,120}$", text.strip()) and not clean_ending(text)),
            }
        )
    return rows


def mean_gap(rows: list[dict[str, Any]]) -> tuple[float | None, float | None, float | None]:
    if not rows:
        return None, None, None
    holo = mean(float(row["holo_score"]) for row in rows)
    solo = mean(float(row["solo_score"]) for row in rows)
    return round(holo, 3), round(solo, 3), round(holo - solo, 3)


def criterion_gap_summary(criterion_rows: list[dict[str, Any]], *, primary_only: bool) -> list[dict[str, Any]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in criterion_rows:
        if primary_only and not row.get("primary_score_included"):
            continue
        grouped[row["criterion_id"]].append(float(row["gap_holo_minus_solo"]))
    return sorted(
        [
            {"criterion_id": criterion_id, "gap_holo_minus_solo": round(mean(values), 3)}
            for criterion_id, values in grouped.items()
            if values
        ],
        key=lambda item: item["gap_holo_minus_solo"],
        reverse=True,
    )


def chart_rows(judge_rows: list[dict[str, Any]], criterion_rows: list[dict[str, Any]], trace_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    primary_rows = [row for row in judge_rows if row["primary_score_included"]]
    all_holo, all_solo, all_gap = mean_gap(judge_rows)
    primary_holo, primary_solo, primary_gap = mean_gap(primary_rows)
    token_totals = summarize_trace_tokens(trace_rows)["by_condition"]
    return {
        "score_bars": [
            {"series": "all_judges", "label": "Holo", "score": all_holo},
            {"series": "all_judges", "label": "Solo", "score": all_solo},
            {"series": "primary_no_self_dna", "label": "Holo", "score": primary_holo},
            {"series": "primary_no_self_dna", "label": "Solo", "score": primary_solo},
        ],
        "gap_bars": [
            {"series": "all_judges", "gap_holo_minus_solo": all_gap},
            {"series": "primary_no_self_dna", "gap_holo_minus_solo": primary_gap},
        ],
        "criterion_gap_bars": criterion_gap_summary(criterion_rows, primary_only=False),
        "primary_criterion_gap_bars": criterion_gap_summary(criterion_rows, primary_only=True),
        "token_bars": [
            {"condition": condition, **values}
            for condition, values in sorted(token_totals.items())
        ],
        "turn_token_lines": turn_trajectory(trace_rows, {}),
    }


def collect_repeated_phrases(rows: list[dict[str, Any]], key: str, limit: int = 10) -> list[str]:
    seen: list[str] = []
    for row in rows:
        values = row.get(key) or []
        if isinstance(values, str):
            values = [values]
        for value in values:
            if value and value not in seen:
                seen.append(str(value))
    return seen[:limit]


def classify_theme(text: str, fallback: str = "general_quality_lift") -> str:
    lowered = text.lower()
    best_theme = fallback
    best_hits = 0
    for theme, keywords in INSIGHT_THEME_RULES.items():
        hits = sum(1 for keyword in keywords if keyword.lower() in lowered)
        if hits > best_hits:
            best_theme = theme
            best_hits = hits
    return best_theme


def compact_note(text: str, limit: int = 260) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def extract_insights(judge_rows: list[dict[str, Any]], criterion_rows: list[dict[str, Any]]) -> dict[str, Any]:
    atoms: list[dict[str, Any]] = []
    theme_values: dict[str, list[float]] = defaultdict(list)
    theme_by_solo: dict[tuple[str, str], list[float]] = defaultdict(list)

    for row in criterion_rows:
        if not row.get("primary_score_included"):
            continue
        gap = float(row.get("gap_holo_minus_solo") or 0)
        if abs(gap) < 0.5:
            continue
        combined_notes = f"{row.get('holo_notes', '')} {row.get('solo_notes', '')}"
        theme = classify_theme(combined_notes or row.get("criterion_id", ""))
        atom = {
            "source_type": "criterion_gap",
            "theme": theme,
            "pair_id": row.get("pair_id"),
            "solo_condition": row.get("solo_condition"),
            "judge_id": row.get("judge_id"),
            "judge_provider": row.get("judge_provider"),
            "criterion_id": row.get("criterion_id"),
            "gap_holo_minus_solo": round(gap, 3),
            "direction": "holo_lift" if gap > 0 else "solo_edge",
            "evidence_note": compact_note(row.get("holo_notes") if gap > 0 else row.get("solo_notes")),
            "contrast_note": compact_note(row.get("solo_notes") if gap > 0 else row.get("holo_notes")),
        }
        atoms.append(atom)
        theme_values[theme].append(gap)
        theme_by_solo[(str(row.get("solo_condition")), theme)].append(gap)

    for row in judge_rows:
        if not row.get("primary_score_included"):
            continue
        for key, direction in [
            ("holo_strengths", "holo_strength"),
            ("solo_weaknesses", "solo_hidden_failure"),
            ("holo_weaknesses", "holo_residual_risk"),
        ]:
            for value in row.get(key) or []:
                text = str(value)
                theme = classify_theme(text)
                atoms.append(
                    {
                        "source_type": key,
                        "theme": theme,
                        "pair_id": row.get("pair_id"),
                        "solo_condition": row.get("solo_condition"),
                        "judge_id": row.get("judge_id"),
                        "judge_provider": row.get("judge_provider"),
                        "criterion_id": "",
                        "gap_holo_minus_solo": row.get("gap_holo_minus_solo"),
                        "direction": direction,
                        "evidence_note": compact_note(text),
                        "contrast_note": "",
                    }
                )

    theme_summary = []
    for theme, values in sorted(theme_values.items(), key=lambda item: mean(item[1]), reverse=True):
        theme_atoms = [atom for atom in atoms if atom["theme"] == theme]
        sample = next((atom["evidence_note"] for atom in theme_atoms if atom.get("evidence_note")), "")
        theme_summary.append(
            {
                "theme": theme,
                "mean_gap_holo_minus_solo": round(mean(values), 3),
                "evidence_count": len(values),
                "atom_count": len(theme_atoms),
                "sample_evidence": sample,
            }
        )

    theme_solo_heatmap = []
    for (solo_condition, theme), values in sorted(theme_by_solo.items()):
        theme_solo_heatmap.append(
            {
                "solo_condition": solo_condition,
                "theme": theme,
                "mean_gap_holo_minus_solo": round(mean(values), 3),
                "evidence_count": len(values),
            }
        )

    lift_drivers = []
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in criterion_rows:
        if row.get("primary_score_included"):
            grouped[str(row["criterion_id"])].append(float(row["gap_holo_minus_solo"]))
    for criterion_id, values in grouped.items():
        lift_drivers.append(
            {
                "criterion_id": criterion_id,
                "theme": classify_theme(criterion_id.replace("_", " ")),
                "mean_gap_holo_minus_solo": round(mean(values), 3),
                "evidence_count": len(values),
            }
        )
    lift_drivers.sort(key=lambda item: item["mean_gap_holo_minus_solo"], reverse=True)

    return {
        "status": "insight_extraction_complete",
        "method": "deterministic_keyword_theme_mapping_over_primary_judge_notes_and_criterion_gaps",
        "theme_summary": theme_summary,
        "theme_solo_heatmap": theme_solo_heatmap,
        "top_lift_drivers": lift_drivers,
        "insight_atoms": atoms,
    }


def build_intelligence(run_dir: Path) -> dict[str, Any]:
    manifest = read_json(run_dir / "run_manifest.json")
    analysis = load_analysis(run_dir)
    judge_rows, criterion_rows = collect_judge_rows(run_dir, manifest)
    trace_rows = collect_traces(run_dir)
    final_checks = final_artifact_checks(run_dir, manifest)
    all_holo, all_solo, all_gap = mean_gap(judge_rows)
    primary_rows = [row for row in judge_rows if row["primary_score_included"]]
    clean_rows = [row for row in judge_rows if not row["validation_flags"]]
    primary_clean_rows = [row for row in primary_rows if not row["validation_flags"]]
    primary_holo, primary_solo, primary_gap = mean_gap(primary_rows)
    primary_clean_holo, primary_clean_solo, primary_clean_gap = mean_gap(primary_clean_rows)

    active_judge_panel = read_json(PACKET_DIR / "judge_panel_frontier_blind.json")
    run_judge_count = len({row["judge_id"] for row in judge_rows})
    current_judge_count = len(active_judge_panel.get("judge_models", []))
    caveats = []
    if manifest.get("benchmark_credit") is not True:
        caveats.append("Run is marked benchmark_credit=false and public_claim=false.")
    if run_judge_count and run_judge_count != current_judge_count:
        caveats.append(
            f"Run has {run_judge_count} judge rows; current harness is configured for {current_judge_count} judges."
        )
    if manifest.get("solo_condition_scope") and len(manifest.get("solo_condition_scope") or []) == 1:
        caveats.append("Run covers one solo condition; full cohort comparison still requires all solo lanes.")
    if any(not item["clean_ending"] for item in final_checks):
        caveats.append("At least one final artifact does not end cleanly.")

    token_summary = summarize_trace_tokens(trace_rows)
    insight_extraction = extract_insights(judge_rows, criterion_rows)
    charts = chart_rows(judge_rows, criterion_rows, trace_rows)
    charts["insight_theme_bars"] = insight_extraction["theme_summary"]
    charts["insight_theme_solo_heatmap"] = insight_extraction["theme_solo_heatmap"]
    charts["lift_driver_bars"] = insight_extraction["top_lift_drivers"]
    intelligence = {
        "status": "benchmark_intelligence_complete",
        "run_id": manifest.get("run_id", run_dir.name),
        "run_status": manifest.get("status"),
        "benchmark_credit": manifest.get("benchmark_credit"),
        "public_claim": manifest.get("public_claim"),
        "routing_config_id": manifest.get("routing_config_id"),
        "holo_governor_model": manifest.get("holo_governor_model"),
        "holo_analyst_rotation": manifest.get("holo_analyst_rotation"),
        "conditions": manifest.get("conditions"),
        "headline": {
            "all_judges": {
                "holo_mean": all_holo,
                "solo_mean": all_solo,
                "gap_holo_minus_solo": all_gap,
                "percent_improvement_over_solo": pct_improvement(all_holo, all_solo),
                "judge_rows": len(judge_rows),
            },
            "primary_no_self_dna": {
                "holo_mean": primary_holo,
                "solo_mean": primary_solo,
                "gap_holo_minus_solo": primary_gap,
                "percent_improvement_over_solo": pct_improvement(primary_holo, primary_solo),
                "judge_rows": len(primary_rows),
            },
            "primary_clean_no_self_dna": {
                "holo_mean": primary_clean_holo,
                "solo_mean": primary_clean_solo,
                "gap_holo_minus_solo": primary_clean_gap,
                "percent_improvement_over_solo": pct_improvement(primary_clean_holo, primary_clean_solo),
                "judge_rows": len(primary_clean_rows),
            },
        },
        "methodology_caveats": caveats,
        "analysis_summary_available": analysis is not None,
        "criterion_gap_summary": {
            "all_judges": criterion_gap_summary(criterion_rows, primary_only=False),
            "primary_no_self_dna": criterion_gap_summary(criterion_rows, primary_only=True),
        },
        "judge_rows": judge_rows,
        "judge_rationale_digest": {
            "holo_strengths": collect_repeated_phrases(judge_rows, "holo_strengths"),
            "solo_strengths": collect_repeated_phrases(judge_rows, "solo_strengths"),
            "holo_weaknesses": collect_repeated_phrases(judge_rows, "holo_weaknesses"),
            "solo_weaknesses_or_hidden_failures": collect_repeated_phrases(judge_rows, "solo_weaknesses"),
            "validation_flags": [
                {"judge_id": row["judge_id"], "flags": row["validation_flags"]}
                for row in judge_rows
                if row["validation_flags"]
            ],
        },
        "insight_extraction": insight_extraction,
        "token_summary": token_summary,
        "turn_trajectory": turn_trajectory(trace_rows, manifest),
        "final_artifact_checks": final_checks,
        "chart_data": charts,
        "source_files": {
            "run_manifest": str(run_dir / "run_manifest.json"),
            "analysis_summary": str(run_dir / "analysis" / "analysis_summary.json"),
            "judge_summary": str(run_dir / "judge_score_summary_all_pairs.json"),
        },
    }
    return intelligence


def fmt(value: Any) -> str:
    return "`null`" if value is None else f"`{value}`"


def md_table(rows: list[list[Any]], headers: list[str]) -> list[str]:
    out = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(item).replace("\n", " ") for item in row) + " |")
    return out


def render_markdown(intel: dict[str, Any]) -> str:
    headline = intel["headline"]
    primary = headline["primary_no_self_dna"]
    all_judges = headline["all_judges"]
    primary_clean = headline["primary_clean_no_self_dna"]
    lines = [
        "# Benchmark Intelligence Report",
        "",
        f"Run ID: `{intel['run_id']}`",
        f"Run status: `{intel['run_status']}`",
        f"Benchmark credit: `{intel['benchmark_credit']}`",
        f"Public claim: `{intel['public_claim']}`",
        f"Routing config: `{intel['routing_config_id']}`",
        f"Gov: `{intel['holo_governor_model']}`",
        "",
        "## Executive Readout",
        "",
        (
            f"- Primary no-self-DNA gap: {fmt(primary['gap_holo_minus_solo'])} "
            f"({fmt(primary['percent_improvement_over_solo'])}% over solo, "
            f"{fmt(primary['judge_rows'])} judge rows)."
        ),
        (
            f"- All-judge gap: {fmt(all_judges['gap_holo_minus_solo'])} "
            f"({fmt(all_judges['percent_improvement_over_solo'])}% over solo)."
        ),
        (
            f"- Primary clean no-self-DNA gap: {fmt(primary_clean['gap_holo_minus_solo'])} "
            f"({fmt(primary_clean['percent_improvement_over_solo'])}% over solo)."
        ),
        "",
        "## Methodology Caveats",
        "",
    ]
    if intel["methodology_caveats"]:
        lines.extend(f"- {item}" for item in intel["methodology_caveats"])
    else:
        lines.append("- No caveats generated by the report builder.")

    lines.extend(["", "## Score Summary", ""])
    lines.extend(
        md_table(
            [
                ["All judges", all_judges["holo_mean"], all_judges["solo_mean"], all_judges["gap_holo_minus_solo"], all_judges["percent_improvement_over_solo"], all_judges["judge_rows"]],
                ["Primary no-self-DNA", primary["holo_mean"], primary["solo_mean"], primary["gap_holo_minus_solo"], primary["percent_improvement_over_solo"], primary["judge_rows"]],
                ["Primary clean no-self-DNA", primary_clean["holo_mean"], primary_clean["solo_mean"], primary_clean["gap_holo_minus_solo"], primary_clean["percent_improvement_over_solo"], primary_clean["judge_rows"]],
            ],
            ["View", "Holo", "Solo", "Gap", "% Improvement", "Rows"],
        )
    )

    lines.extend(["", "## Criterion Gaps", ""])
    primary_criteria = intel["criterion_gap_summary"]["primary_no_self_dna"] or intel["criterion_gap_summary"]["all_judges"]
    lines.extend(
        md_table(
            [[item["criterion_id"], item["gap_holo_minus_solo"]] for item in primary_criteria],
            ["Criterion", "Gap Holo - Solo"],
        )
    )

    lines.extend(["", "## Judge Rationale Digest", ""])
    digest = intel["judge_rationale_digest"]
    for label, key in [
        ("Holo Strengths", "holo_strengths"),
        ("Solo Hidden Failures / Weaknesses", "solo_weaknesses_or_hidden_failures"),
        ("Validation Flags", "validation_flags"),
    ]:
        lines.extend([f"### {label}", ""])
        values = digest.get(key) or []
        if key == "validation_flags":
            if not values:
                lines.append("- None")
            for item in values:
                lines.append(f"- `{item['judge_id']}`: {'; '.join(item['flags'])}")
        else:
            lines.extend(f"- {value}" for value in values[:8]) if values else lines.append("- None")
        lines.append("")

    insights = intel.get("insight_extraction") or {}
    lines.extend(["## Extracted Insight Drivers", ""])
    theme_summary = insights.get("theme_summary") or []
    if theme_summary:
        lines.extend(
            md_table(
                [
                    [
                        item["theme"],
                        item["mean_gap_holo_minus_solo"],
                        item["evidence_count"],
                        item["sample_evidence"],
                    ]
                    for item in theme_summary[:10]
                ],
                ["Theme", "Mean Gap", "Evidence Count", "Sample Evidence"],
            )
        )
    else:
        lines.append("- No deterministic insight themes met the extraction threshold.")

    lines.extend(["", "## Top Lift Drivers", ""])
    lift_drivers = insights.get("top_lift_drivers") or []
    if lift_drivers:
        lines.extend(
            md_table(
                [
                    [
                        item["criterion_id"],
                        item["theme"],
                        item["mean_gap_holo_minus_solo"],
                        item["evidence_count"],
                    ]
                    for item in lift_drivers[:10]
                ],
                ["Criterion", "Theme", "Mean Gap", "Evidence Count"],
            )
        )
    else:
        lines.append("- No lift drivers extracted.")

    lines.extend(["## Token And Latency Accounting", ""])
    by_condition = intel["token_summary"]["by_condition"]
    lines.extend(
        md_table(
            [
                [
                    condition,
                    values["calls"],
                    values["input_tokens"],
                    values["output_tokens"],
                    values["total_tokens"],
                    round(values["latency_ms"] / 1000, 1),
                ]
                for condition, values in by_condition.items()
            ],
            ["Condition", "Calls", "Input Tokens", "Output Tokens", "Total Tokens", "Latency Sec"],
        )
    )

    lines.extend(["", "## Turn Trajectory", ""])
    lines.extend(
        md_table(
            [
                [
                    item["condition"],
                    item["turn"],
                    item["call_type"],
                    item["provider_model"],
                    item["input_tokens"],
                    item["output_tokens"],
                    item["word_count"],
                ]
                for item in intel["turn_trajectory"]
            ],
            ["Condition", "Turn", "Call Type", "Provider Model", "Input", "Output", "Words"],
        )
    )

    lines.extend(["", "## Final Artifact Integrity", ""])
    lines.extend(
        md_table(
            [
                [
                    item["condition"],
                    item["word_count"],
                    item["clean_ending"],
                    item["possible_mid_bullet_cutoff"],
                ]
                for item in intel["final_artifact_checks"]
            ],
            ["Condition", "Words", "Clean Ending", "Mid-Bullet Cutoff"],
        )
    )

    lines.extend(["", "## Chart Data", ""])
    lines.append("Chart-ready data is available in `benchmark_intelligence.json` and `chart_data.csv`.")
    return "\n".join(lines) + "\n"


def flatten_chart_data(chart_data: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for chart_name, items in chart_data.items():
        for item in items:
            row = {"chart": chart_name}
            row.update(item)
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", action="store_true", help="Build intelligence for latest run folder.")
    parser.add_argument("--run-id", help="Build intelligence for a specific run id.")
    args = parser.parse_args()
    if bool(args.latest) == bool(args.run_id):
        parser.error("Choose exactly one of --latest or --run-id")
    run_dir = latest_run_dir() if args.latest else RUNS_DIR / str(args.run_id)
    if not (run_dir / "run_manifest.json").exists():
        raise SystemExit(f"Missing run manifest: {run_dir / 'run_manifest.json'}")
    intel = build_intelligence(run_dir)
    out_dir = run_dir / "intelligence"
    write_json(out_dir / "benchmark_intelligence.json", intel)
    write_text(out_dir / "benchmark_intelligence.md", render_markdown(intel))
    chart_rows_flat = flatten_chart_data(intel["chart_data"])
    chart_fields = sorted({key for row in chart_rows_flat for key in row})
    write_csv(out_dir / "chart_data.csv", chart_rows_flat, chart_fields)
    result = {
        "status": intel["status"],
        "run_id": intel["run_id"],
        "primary_gap_holo_minus_solo": intel["headline"]["primary_no_self_dna"]["gap_holo_minus_solo"],
        "primary_percent_improvement": intel["headline"]["primary_no_self_dna"]["percent_improvement_over_solo"],
        "outputs": {
            "benchmark_intelligence_json": str(out_dir / "benchmark_intelligence.json"),
            "benchmark_intelligence_md": str(out_dir / "benchmark_intelligence.md"),
            "chart_data_csv": str(out_dir / "chart_data.csv"),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
