#!/usr/bin/env python3
"""Independent judge for HoloVerify-V Kit C registry candidate.

The judge receives blinded outputs and must return a full 100-point judgment.
Raw judge output is saved before local unblinding.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "live_runs"
MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _latest_run_dir() -> Path:
    dirs = sorted([path for path in RUNS.iterdir() if path.is_dir()])
    if not dirs:
        raise RuntimeError("no live runs found")
    return dirs[-1]


def _target_free_row(row: dict[str, Any]) -> dict[str, Any]:
    failures = [
        f
        for f in (row.get("deterministic_failures") or [])
        if not str(f).startswith("local_audit_target_expected_")
    ]
    parsed = row.get("parsed_json") if isinstance(row.get("parsed_json"), dict) else {}
    return {
        "packet_id": row.get("packet_id"),
        "output_json": parsed,
        "parse_ok": row.get("parse_ok"),
        "structural_gate_failures": failures,
    }


def build_blind_packet(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_json(ROOT / "PRE_RUN_MANIFEST.json")
    rows = [json.loads(line) for line in (run_dir / "TRACE_CALLS.jsonl").read_text().splitlines() if line.strip()]
    packet_payloads = {
        record["packet_id"]: _load_json(Path(record["frozen_payload_path"]))
        for record in manifest["packet_records"]
    }
    # Deterministic anonymization. Do not expose lane names to the judge.
    blinded_outputs = []
    blinding_key = {}
    for index, row in enumerate(rows, 1):
        blind_id = f"artifact_{index:02d}"
        blinded_outputs.append({"blind_id": blind_id, **_target_free_row(row)})
        blinding_key[blind_id] = {
            "lane": row.get("lane"),
            "pair_id": row.get("pair_id"),
            "packet_id": row.get("packet_id"),
            "call_index": row.get("call_index"),
        }
    blind_packet = {
        "judge_packet_label": "HV_KITC_SOURCE_BOUNDARY_BLIND_JUDGE_PACKET",
        "run_root_signature": manifest["root_signature"],
        "run_trace_hash": _sha((run_dir / "TRACE_CALLS.jsonl").read_text()),
        "instructions": {
            "task": "Derive the evidence-supported ALLOW or ESCALATE verdict for each packet, then grade each blinded artifact.",
            "do_not_assume": [
                "Do not assume any artifact is correct because it is longer or more structured.",
                "Do not infer lane identity from style.",
                "Do not use hidden expected verdicts; none are provided.",
            ],
            "score_100": {
                "deterministic_compliance": 25,
                "epistemic_grounding": 25,
                "structural_completeness": 25,
                "argument_source_binding": 25,
            },
            "labels": ["KNEW", "LUCKY", "WRONG", "CONFUSED"],
        },
        "required_output_schema": {
            "judge_model": "string",
            "judge_status": "COMPLETE | INVALID",
            "packet_adjudications": [
                {
                    "packet_id": "string",
                    "adjudicated_verdict": "ALLOW | ESCALATE",
                    "confidence": "LOW | MEDIUM | HIGH",
                    "controlling_evidence_chain": ["string"],
                }
            ],
            "artifact_scores": [
                {
                    "blind_id": "string",
                    "packet_id": "string",
                    "label": "KNEW | LUCKY | WRONG | CONFUSED",
                    "deterministic_compliance_25": 0,
                    "epistemic_grounding_25": 0,
                    "structural_completeness_25": 0,
                    "argument_source_binding_25": 0,
                    "total_score_100": 0,
                    "rationale": "string",
                }
            ],
            "overall_notes": "string",
        },
        "packets": packet_payloads,
        "blinded_artifacts": blinded_outputs,
    }
    return blind_packet, blinding_key


def _call_anthropic(prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY missing")
    payload = {
        "model": MODEL,
        "max_tokens": 6000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": "Return only valid JSON matching the required schema. No markdown fences.\n\n" + prompt,
            }
        ],
    }
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    parts = data.get("content") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    return text.strip()


def _parse_judge(text: str) -> tuple[bool, dict[str, Any] | None, str | None]:
    if text.startswith("```"):
        return False, None, "markdown_fence_present"
    try:
        obj = json.loads(text)
    except Exception as exc:
        return False, None, f"json_parse_error:{type(exc).__name__}"
    if obj.get("judge_status") != "COMPLETE":
        return False, obj, "judge_status_not_complete"
    scores = obj.get("artifact_scores")
    if not isinstance(scores, list) or len(scores) != 8:
        return False, obj, "artifact_scores_count_not_8"
    for score in scores:
        dims = [
            score.get("deterministic_compliance_25"),
            score.get("epistemic_grounding_25"),
            score.get("structural_completeness_25"),
            score.get("argument_source_binding_25"),
        ]
        if any(not isinstance(v, int) for v in dims):
            return False, obj, "score_dimension_not_int"
        if score.get("total_score_100") != sum(dims):
            return False, obj, "total_score_mismatch"
    return True, obj, None


def main() -> int:
    run_dir = _latest_run_dir()
    judge_dir = run_dir / "independent_judge_haiku_001"
    judge_dir.mkdir(exist_ok=False)
    blind_packet, blinding_key = build_blind_packet(run_dir)
    (judge_dir / "JUDGE_PACKET_BLINDED.json").write_text(json.dumps(blind_packet, indent=2, sort_keys=True) + "\n")
    (judge_dir / "JUDGE_BLINDING_KEY_LOCAL_ONLY.json").write_text(json.dumps(blinding_key, indent=2, sort_keys=True) + "\n")
    text = _call_anthropic(json.dumps(blind_packet, separators=(",", ":")))
    (judge_dir / "RAW_JUDGE_OUTPUT.txt").write_text(text + "\n")
    parse_ok, parsed, error = _parse_judge(text)
    result = {
        "classification": "INDEPENDENT_JUDGE_COMPLETE" if parse_ok else "INDEPENDENT_JUDGE_INVALID",
        "judge_model": MODEL,
        "held_out_from_live_generation": True,
        "run_dir": str(run_dir),
        "judge_dir": str(judge_dir),
        "parse_ok": parse_ok,
        "parse_error": error,
        "raw_output_path": str(judge_dir / "RAW_JUDGE_OUTPUT.txt"),
        "parsed_judge": parsed,
    }
    (judge_dir / "judge_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if parse_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
