from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from holo_builder.freeze_manifest import compute_payload_hash, payload_visibility_errors


FROZEN_PACKETS = [
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-001-ALLOW",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca.json",
        "payload_hash": "85fb8dca9cac004f3d634b80afd6f69d3e178334fbb4bc886c360c35d6ba4517",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-003-ALLOW",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-003-ALLOW_673d6c1b.json",
        "payload_hash": "673d6c1bee9630e89c22eb731dfaa80dddda07c27c575937431220c54c8ce251",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-004-ALLOW",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-004-ALLOW_489e7143.json",
        "payload_hash": "489e7143d4c1b6d3afece803c2b05a2a87e67f71d358f89525534f0891e5f637",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-005-ALLOW",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-005-ALLOW_7f6d94c4.json",
        "payload_hash": "7f6d94c483c42a2b14c7b5114dd6ce859591b1753a1435c9188aedb0f8b19853",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-006-ALLOW",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-006-ALLOW_11f7a12b.json",
        "payload_hash": "11f7a12b94a2492063056f76acb7dd1ab811e53a462d4edc3aa7a137cc117cd6",
    },
]


DEFAULT_JSON_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FROZEN_STATIC_RUN_001.json")
DEFAULT_MD_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FROZEN_STATIC_RUN_001.md")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _packet_row(entry: dict[str, str], failures: list[str]) -> dict[str, Any]:
    packet_id = entry["packet_id"]
    path = Path(entry["frozen_packet_path"])
    expected_hash = entry["payload_hash"]
    expected_hash8 = expected_hash[:8]
    row_failures: list[str] = []

    _require(path.exists(), f"{packet_id}: missing frozen packet {path}", row_failures)
    if not path.exists():
        failures.extend(row_failures)
        return {
            "packet_id": packet_id,
            "frozen_packet_path": str(path),
            "payload_hash": expected_hash,
            "hash8": expected_hash8,
            "status": "FAIL",
            "failures": row_failures,
        }

    packet = _load_json(path)
    computed_hash = compute_payload_hash(packet)
    visibility_errors = payload_visibility_errors(packet)
    payload = packet.get("payload", {})
    frozen = packet.get("_frozen", {})

    _require(packet.get("scenario_id") == packet_id, f"{packet_id}: scenario_id mismatch", row_failures)
    _require(packet.get("scenario_status") == "frozen", f"{packet_id}: scenario_status is not frozen", row_failures)
    _require(packet.get("expected_verdict") == "ALLOW", f"{packet_id}: expected_verdict is not ALLOW", row_failures)
    _require(set(payload.keys()) == {"action", "context"}, f"{packet_id}: payload keys are not action/context only", row_failures)
    _require(not visibility_errors, f"{packet_id}: payload visibility errors {visibility_errors}", row_failures)
    _require(computed_hash == expected_hash, f"{packet_id}: computed hash mismatch", row_failures)
    _require(frozen.get("hash") == expected_hash, f"{packet_id}: _frozen.hash mismatch", row_failures)
    _require(frozen.get("hash8") == expected_hash8, f"{packet_id}: _frozen.hash8 mismatch", row_failures)
    _require(frozen.get("freeze_gate") == "build_freeze_manifest", f"{packet_id}: freeze gate mismatch", row_failures)
    _require(frozen.get("manifest_type") == "build_freeze_manifest", f"{packet_id}: manifest type mismatch", row_failures)
    _require(frozen.get("approved_by") == "Taylor", f"{packet_id}: frozen approval is not Taylor", row_failures)
    _require(frozen.get("static_lint_result") == "PASS", f"{packet_id}: static lint not PASS", row_failures)
    _require(frozen.get("payload_visibility_result") == "PASS", f"{packet_id}: payload visibility not PASS", row_failures)
    _require(frozen.get("no_model_visible_expected_verdict") is True, f"{packet_id}: expected verdict visibility guard not true", row_failures)
    _require(frozen.get("no_live_model_calls") is True, f"{packet_id}: no_live_model_calls guard not true", row_failures)

    failures.extend(row_failures)
    return {
        "packet_id": packet_id,
        "truth_class": "ALLOW",
        "frozen_packet_path": str(path),
        "payload_hash": expected_hash,
        "hash8": expected_hash8,
        "computed_hash_matches": computed_hash == expected_hash,
        "scenario_status": packet.get("scenario_status"),
        "freeze_gate": frozen.get("freeze_gate"),
        "approved_by": frozen.get("approved_by"),
        "static_lint_result": frozen.get("static_lint_result"),
        "payload_visibility_result": frozen.get("payload_visibility_result"),
        "model_visible_payload_contract": sorted(payload.keys()),
        "status": "PASS" if not row_failures else "FAIL",
        "failures": row_failures,
    }


def build_report() -> dict[str, Any]:
    failures: list[str] = []
    rows = [_packet_row(entry, failures) for entry in FROZEN_PACKETS]
    return {
        "artifact_type": "BAL100_leaderboard_20_allow_frozen_static_run",
        "created_at": _utc_now(),
        "status": "PASS" if not failures else "FAIL",
        "mode": "frozen_static_intake_validation_no_live_no_judge_no_trace",
        "packet_count": len(rows),
        "allow_packets": len(rows),
        "escalate_packets": 0,
        "packets": rows,
        "validation": {
            "failure_count": len(failures),
            "failures": failures,
            "all_packets_frozen": all(row.get("scenario_status") == "frozen" for row in rows),
            "all_hashes_match": all(row.get("computed_hash_matches") is True for row in rows),
            "all_payload_visibility_pass": all(row.get("payload_visibility_result") == "PASS" for row in rows),
            "all_static_lint_pass": all(row.get("static_lint_result") == "PASS" for row in rows),
            "all_taylor_approved": all(row.get("approved_by") == "Taylor" for row in rows),
        },
        "non_actions": {
            "provider_calls": False,
            "official_trace": False,
            "judge": False,
            "qa": False,
            "ablation": False,
            "scorecard_movement": False,
            "leaderboard_movement": False,
            "push": False,
        },
        "next_gate": "Exact HV/Judge or official trace runner approval is required before benchmark-credit or leaderboard accounting.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {packet_id} | {status} | `{hash8}` | {static_lint_result} | {payload_visibility_result} | {approved_by} | `{frozen_packet_path}` |".format(**row)
        for row in report["packets"]
    )
    return f"""# BAL100 Leaderboard 20 ALLOW Frozen Static Run

Created: {report['created_at']}

Status: `{report['status']}`

Mode: `{report['mode']}`

## Packet Rows

| Packet | Status | Hash8 | Static Lint | Payload Visibility | Approved By | Frozen Path |
| --- | --- | --- | --- | --- | --- | --- |
{rows}

## Validation

- Packet count: {report['packet_count']}
- ALLOW packets: {report['allow_packets']}
- ESCALATE packets: {report['escalate_packets']}
- Failure count: {report['validation']['failure_count']}
- All packets frozen: {report['validation']['all_packets_frozen']}
- All hashes match: {report['validation']['all_hashes_match']}
- All payload visibility PASS: {report['validation']['all_payload_visibility_pass']}
- All static lint PASS: {report['validation']['all_static_lint_pass']}
- All Taylor approved: {report['validation']['all_taylor_approved']}

## Boundaries

- No provider calls.
- No official trace.
- No Judge.
- No QA or ablation.
- No scorecard or leaderboard movement.
- No push.

Next gate: {report['next_gate']}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate frozen BAL100 hard-ALLOW packets without live calls.")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT))
    args = parser.parse_args()

    report = build_report()
    _write_json(Path(args.json_out), report)
    Path(args.md_out).write_text(render_markdown(report))
    print(f"Wrote {args.json_out}")
    print(f"Wrote {args.md_out}")
    print(f"status={report['status']} packet_count={report['packet_count']} failure_count={report['validation']['failure_count']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
