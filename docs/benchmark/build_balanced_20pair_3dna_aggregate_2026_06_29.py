#!/usr/bin/env python3
"""Build the balanced 20-pair aggregate for the 3-DNA HoloVerify runner.

This script creates metadata only. It does not call providers. Direct historical
payloads are explicitly tagged and include deterministic knew_terms so the live
runner's local gate remains source-bound.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
DEFAULT_AGGREGATE = BENCHMARK_ROOT / "three_mini_seam_scout_2026-06-29" / "AGGREGATE_20_ONE_SHOT_MINI_SOLO_FAILURE_CANDIDATES.json"
TARGET_ESCALATE_SUMMARY = (
    BENCHMARK_ROOT
    / "targeted_hard_escalate_three_mini_scout_2026-06-29"
    / "run_20260629T034412Z"
    / "scout_summary.json"
)
OUT = BENCHMARK_ROOT / "three_mini_seam_scout_2026-06-29" / "AGGREGATE_20_BALANCED_3DNA_CURRENT_FAILURE_CANDIDATES.json"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _payload_from_json_path(path: str) -> dict[str, Any]:
    data = _load_json(Path(path))
    payload = data.get("payload") if isinstance(data, dict) else None
    return payload if isinstance(payload, dict) else data


def _payload_from_prompt_card(path: str) -> dict[str, Any]:
    return json.loads(_load_json(Path(path))["user"])


def _wrong_allow(candidate: dict[str, Any]) -> bool:
    return any(
        item.get("behavior_label") == "NOT_KNEW_WRONG_VERDICT"
        and item.get("expected") == "ALLOW"
        and item.get("verdict") == "ESCALATE"
        for item in candidate.get("failing_models", [])
    )


def _wrong_escalate(candidate: dict[str, Any]) -> bool:
    return any(
        item.get("behavior_label") == "NOT_KNEW_WRONG_VERDICT"
        and item.get("expected") == "ESCALATE"
        and item.get("verdict") == "ALLOW"
        for item in candidate.get("failing_models", [])
    )


def _doc_by_id(payload: dict[str, Any], doc_id: str) -> str:
    context = payload.get("context", {}) if isinstance(payload.get("context"), dict) else {}
    for group in ("internal_documents", "policy_documents"):
        for doc in context.get(group, []) or []:
            if isinstance(doc, dict) and doc.get("doc_id") == doc_id:
                return str(doc.get("content") or "")
    return ""


def _terms_from_delta_doc(payload: dict[str, Any], doc_id: str) -> list[str]:
    content = _doc_by_id(payload, doc_id)
    terms = [doc_id]
    patterns = (
        r"source object [A-Z0-9-]+",
        r"account [A-Z0-9-]+",
        r"[A-Z]{2,5} (?:production|readiness|lab) scope \d+",
        r"release condition [A-Z0-9-]+(?:-S)?",
        r"completed at [0-9: T-]+",
        r"DG-41B (?:production|lab) telemetry units",
        r"Site 18-[A-Z]",
        r"ACT-[A-Z0-9-]+",
    )
    for pattern in patterns:
        for match in re.findall(pattern, content):
            if match not in terms:
                terms.append(match)
    return terms[:8]


def _direct_spec_from_payloads(pair_id: str, payload_a: dict[str, Any], payload_b: dict[str, Any], seam: str | None, delta_doc_id: str | None) -> dict[str, Any]:
    context = payload_a.get("context", {}) if isinstance(payload_a.get("context"), dict) else {}
    action = payload_a.get("action", {}) if isinstance(payload_a.get("action"), dict) else {}
    delta_doc = delta_doc_id or ""
    return {
        "pair_id": pair_id,
        "type": action.get("type") or "business_action_review",
        "vendor": action.get("vendor") or "unknown",
        "action_vendor": action.get("vendor") or "unknown",
        "action_amount": action.get("amount", 0),
        "action_date": action.get("action_date") or "2026-06-29",
        "boundary": context.get("action_boundary") or "Decide whether the action may proceed.",
        "anomaly": context.get("anomaly_observed") or context.get("explanation_summary") or "Verify exact source-boundary closure.",
        "failure_class_notes": seam or "direct_payload_current_failure_candidate",
        "knew_terms": {
            "A": _terms_from_delta_doc(payload_a, delta_doc),
            "B": _terms_from_delta_doc(payload_b, delta_doc),
        },
    }


def _closeout_022_candidate() -> dict[str, Any]:
    root = Path("/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/prompt_cards")
    pair_id = "BAL100-BEC-SUBTLE-CLOSEOUT-022"
    prompt_cards = {
        "A": str(root / f"{pair_id}-A__minimax__MiniMax-Text-01.json"),
        "B": str(root / f"{pair_id}-B__minimax__MiniMax-Text-01.json"),
    }
    payload_a = _payload_from_prompt_card(prompt_cards["A"])
    payload_b = _payload_from_prompt_card(prompt_cards["B"])
    spec = _direct_spec_from_payloads(pair_id, payload_a, payload_b, "SUBTLE_ACTION_BOUNDARY_PRECISION", "CAL-ACR-022")
    spec["knew_terms"] = {
        "A": ["CAL-ACR-022", "DG-41B production telemetry units", "Site 18-P", "ACT-ACR-2026-8022"],
        "B": ["CAL-ACR-022", "DG-41B lab telemetry units", "Site 18-L", "DG-41B production telemetry units"],
    }
    return {
        "candidate_reason": "current_minimax_m25_hard_allow_false_positive_control_failure",
        "completed_model_count": 1,
        "failing_models": [
            {
                "behavior_label": "NOT_KNEW_WRONG_VERDICT",
                "expected": "ALLOW",
                "model": "MiniMax-M2.5-highspeed",
                "packet_id": f"{pair_id}-A",
                "provider": "minimax",
                "verdict": "ESCALATE",
            }
        ],
        "failure_classes": ["SUBTLE_ACTION_BOUNDARY_PRECISION"],
        "failure_sides": ["ALLOW"],
        "pair_id": pair_id,
        "seam": "Current MiniMax over-escalates valid telemetry activation despite exact matching calibration evidence.",
        "source_kind": "direct_prompt_card_payload_pair",
        "source_prompt_cards": prompt_cards,
        "spec_metadata": spec,
        "source_control_summary": str(
            BENCHMARK_ROOT
            / "control_failure_screen_minimax_m25_2026-06-28"
            / "run_continue_20260628T211143Z"
            / "control_screen_summary.json"
        ),
    }


def _direct_hard_escalate_candidate(item: dict[str, Any]) -> dict[str, Any]:
    pair_id = item["family_id"]
    paths = {
        "A": item["sibling_packet_path"],
        "B": item["packet_path"],
    }
    payload_a = _payload_from_json_path(paths["A"])
    payload_b = _payload_from_json_path(paths["B"])
    wrapper_b = _load_json(Path(paths["B"]))
    builder = wrapper_b.get("_builder", {}) if isinstance(wrapper_b, dict) else {}
    delta_doc_id = builder.get("material_delta_doc_id")
    spec = _direct_spec_from_payloads(pair_id, payload_a, payload_b, item.get("seam"), delta_doc_id)
    return {
        "candidate_reason": "current_three_mini_hard_escalate_false_negative_targeted_scout",
        "completed_model_count": 2,
        "failing_models": [
            {
                "behavior_label": "NOT_KNEW_WRONG_VERDICT",
                "expected": "ESCALATE",
                "model": item["current_failure_model"],
                "packet_id": item["packet_id"],
                "provider": item["current_failure_provider"],
                "verdict": item["current_failure_verdict"],
            }
        ],
        "failure_classes": [item.get("seam") or "HARD_ESCALATE_FALSE_NEGATIVE"],
        "failure_sides": ["ESCALATE"],
        "pair_id": pair_id,
        "seam": item.get("seam"),
        "source_kind": "direct_payload_path_pair",
        "source_payload_paths": paths,
        "spec_metadata": spec,
        "source_scout_summary": str(TARGET_ESCALATE_SUMMARY),
        "source_trace_call_index": item.get("trace_call_index"),
    }


def main() -> int:
    base = _load_json(DEFAULT_AGGREGATE)
    hard_allow = [candidate for candidate in base["candidates"] if _wrong_allow(candidate)]
    hard_escalate = [candidate for candidate in base["candidates"] if _wrong_escalate(candidate)]

    hard_allow.append(_closeout_022_candidate())

    targeted = _load_json(TARGET_ESCALATE_SUMMARY)
    for item in targeted["selected"]:
        hard_escalate.append(_direct_hard_escalate_candidate(item))

    candidates = hard_allow[:10] + hard_escalate[:10]
    if len(hard_allow) < 10 or len(hard_escalate) < 10 or len(candidates) != 20:
        raise RuntimeError(f"balanced_counts_failed:hard_allow={len(hard_allow)} hard_escalate={len(hard_escalate)} total={len(candidates)}")

    aggregate = {
        "classification": "BALANCED_20_3DNA_CURRENT_FAILURE_CANDIDATES",
        "source_default_aggregate": str(DEFAULT_AGGREGATE),
        "source_targeted_hard_escalate_summary": str(TARGET_ESCALATE_SUMMARY),
        "selection_rule": "10 current hard-ALLOW false-positive candidates + 10 current hard-ESCALATE false-negative candidates; direct historical payloads remain non-benchmark until full Holo run passes.",
        "candidate_count": len(candidates),
        "counts": {
            "hard_allow_wrong_verdict_candidates": len(hard_allow),
            "hard_escalate_wrong_verdict_candidates": len(hard_escalate),
            "selected_hard_allow": 10,
            "selected_hard_escalate": 10,
        },
        "candidates": candidates,
    }
    OUT.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"wrote": str(OUT), "counts": aggregate["counts"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
