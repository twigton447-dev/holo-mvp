from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from holo_builder.freeze_manifest import compute_payload_hash, payload_visibility_errors
from holo_builder.lint import check as lint_check


PREFLIGHT_REPORT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_MANIFEST_PREFLIGHT_001.json")
JSON_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_RESULT_001.json")
MD_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_RESULT_001.md")
LEDGER_PATH = Path("holo_builder/outputs/ledger.jsonl")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _ledger_entries() -> list[dict[str, Any]]:
    rows = []
    if not LEDGER_PATH.exists():
        return rows
    for line in LEDGER_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def _ledger_by_scenario() -> dict[str, list[dict[str, Any]]]:
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for row in _ledger_entries():
        by_scenario.setdefault(row.get("scenario_id", ""), []).append(row)
    return by_scenario


def build_report() -> dict[str, Any]:
    preflight = _load_json(PREFLIGHT_REPORT)
    ledger = _ledger_by_scenario()
    rows = []
    failures = []

    for preflight_row in preflight["manifests"]:
        scenario_id = preflight_row["scenario_id"]
        manifest_path = Path(preflight_row["manifest_path"])
        packet_path = Path(preflight_row["packet_path"])
        hash8 = preflight_row["hash8"]
        frozen_path = Path("holo_builder/outputs/frozen") / f"{scenario_id}_{hash8}.json"

        manifest = _load_json(manifest_path) if manifest_path.exists() else {}
        draft_packet = _load_json(packet_path) if packet_path.exists() else {}
        frozen_packet = _load_json(frozen_path) if frozen_path.exists() else {}
        computed_hash = compute_payload_hash(draft_packet) if draft_packet else None
        frozen_meta = frozen_packet.get("_frozen", {})
        lint_result = lint_check(frozen_packet) if frozen_packet else None
        visibility_errors = payload_visibility_errors(frozen_packet) if frozen_packet else ["missing frozen packet"]
        scenario_ledger_entries = ledger.get(scenario_id, [])
        matching_ledger = [
            entry
            for entry in scenario_ledger_entries
            if entry.get("hash8") == hash8 and entry.get("frozen_path") == str(frozen_path)
        ]

        checks = {
            "manifest_exists": manifest_path.exists(),
            "packet_exists": packet_path.exists(),
            "frozen_exists": frozen_path.exists(),
            "manifest_approved": manifest.get("taylor_approved_for_freeze") is True,
            "manifest_approved_by_taylor": manifest.get("approved_by") == "Taylor",
            "payload_hash_matches_manifest": manifest.get("payload_hash") == computed_hash,
            "frozen_hash_matches_manifest": frozen_meta.get("hash") == manifest.get("payload_hash"),
            "frozen_hash8_matches": frozen_meta.get("hash8") == hash8,
            "frozen_approved_by_taylor": frozen_meta.get("approved_by") == "Taylor",
            "scenario_status_frozen": frozen_packet.get("scenario_status") == "frozen",
            "frozen_static_lint_pass": frozen_meta.get("static_lint_result") == "PASS",
            "frozen_payload_visibility_pass": frozen_meta.get("payload_visibility_result") == "PASS",
            "no_model_visible_expected_verdict": frozen_meta.get("no_model_visible_expected_verdict") is True,
            "no_live_model_calls": frozen_meta.get("no_live_model_calls") is True,
            "lint_pass_on_frozen": bool(lint_result and lint_result.passed),
            "payload_visibility_pass_on_frozen": not visibility_errors,
            "ledger_entry_present": bool(matching_ledger),
        }
        failed_checks = [key for key, value in checks.items() if not value]
        if failed_checks:
            failures.append({"scenario_id": scenario_id, "failed_checks": failed_checks})

        rows.append(
            {
                "scenario_id": scenario_id,
                "candidate_id": preflight_row["candidate_id"],
                "packet_path": str(packet_path),
                "manifest_path": str(manifest_path),
                "frozen_path": str(frozen_path),
                "payload_hash": manifest.get("payload_hash"),
                "hash8": hash8,
                "frozen_at": frozen_meta.get("frozen_at"),
                "approved_by": frozen_meta.get("approved_by"),
                "ledger_entries": matching_ledger,
                "checks": checks,
                "failed_checks": failed_checks,
            }
        )

    return {
        "artifact_type": "BAL100_leaderboard_20_allow_freeze_result",
        "created_at": _utc_now(),
        "status": "PASS" if not failures else "FAIL",
        "ticket_id": preflight["ticket_id"],
        "mode": "freeze_completed_no_provider_no_judge_no_trace",
        "source_preflight": str(PREFLIGHT_REPORT),
        "frozen_count": len(rows),
        "frozen_packets": rows,
        "validation": {
            "failures": failures,
            "all_frozen_exist": all(row["checks"]["frozen_exists"] for row in rows),
            "all_manifest_approved_by_taylor": all(row["checks"]["manifest_approved_by_taylor"] for row in rows),
            "all_hashes_match": all(row["checks"]["frozen_hash_matches_manifest"] for row in rows),
            "all_lint_pass": all(row["checks"]["lint_pass_on_frozen"] for row in rows),
            "all_payload_visibility_pass": all(row["checks"]["payload_visibility_pass_on_frozen"] for row in rows),
            "all_ledger_entries_present": all(row["checks"]["ledger_entry_present"] for row in rows),
        },
        "safe_boundaries": {
            "provider_calls": False,
            "judge": False,
            "official_trace": False,
            "qa": False,
            "ablation": False,
            "scorecard_movement": False,
            "leaderboard_update": False,
            "push": False,
            "packet_promotion": False,
            "proof_credit_status_change": False,
        },
        "next_gate": "Official trace / HV-Judge intake requires explicit Taylor approval for the exact frozen packet paths.",
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BAL100 Leaderboard 20 ALLOW Freeze Result",
        "",
        f"Status: {report['status']}  ",
        f"Created: {report['created_at']}  ",
        f"Ticket: `{report['ticket_id']}`  ",
        "Mode: freeze completed; no provider, Judge, trace, scorecard, leaderboard, or push",
        "",
        "## Frozen Packets",
        "",
        "| Scenario ID | Approved By | Lint | Visibility | Ledger | Hash8 | Frozen Path |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in report["frozen_packets"]:
        checks = row["checks"]
        lines.append(
            f"| `{row['scenario_id']}` | {row['approved_by']} | {checks['lint_pass_on_frozen']} | {checks['payload_visibility_pass_on_frozen']} | {checks['ledger_entry_present']} | `{row['hash8']}` | `{row['frozen_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Frozen count: {report['frozen_count']}",
            f"- All frozen exist: {report['validation']['all_frozen_exist']}",
            f"- All manifest approved by Taylor: {report['validation']['all_manifest_approved_by_taylor']}",
            f"- All hashes match: {report['validation']['all_hashes_match']}",
            f"- All lint pass: {report['validation']['all_lint_pass']}",
            f"- All payload visibility pass: {report['validation']['all_payload_visibility_pass']}",
            f"- All ledger entries present: {report['validation']['all_ledger_entries_present']}",
            f"- Failures: {report['validation']['failures'] or 'none'}",
            "",
            "## Next Gate",
            "",
            report["next_gate"],
            "",
            "## Safe Boundaries",
            "",
            "No provider calls, Judge, official trace, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, or push were authorized or performed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = build_report()
    _write_json(JSON_OUT, report)
    MD_OUT.write_text(build_markdown(report))
    print(f"wrote {JSON_OUT}")
    print(f"wrote {MD_OUT}")
    print(f"status {report['status']}")
    print(f"frozen {report['frozen_count']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
