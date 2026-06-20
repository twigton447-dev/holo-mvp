from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from holo_builder.freeze_manifest import build_freeze_manifest


MIGRATED_DRAFTS_REPORT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.json")
DEFAULT_OUT_DIR = Path("holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_balance")
DEFAULT_JSON_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_MANIFEST_PREFLIGHT_001.json")
DEFAULT_MD_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_MANIFEST_PREFLIGHT_001.md")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _manifest_path(out_dir: Path, scenario_id: str) -> Path:
    return out_dir / f"{scenario_id}_build_freeze_manifest.json"


def build_preflight(migrated_report_path: Path, out_dir: Path) -> dict[str, Any]:
    migrated_report = _load_json(migrated_report_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in migrated_report["drafts"]:
        packet_path = Path(row["draft_packet"])
        packet = _load_json(packet_path)
        manifest = build_freeze_manifest(packet, packet_path)
        path = _manifest_path(out_dir, row["scenario_id"])
        _write_json(path, manifest)
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "scenario_id": row["scenario_id"],
                "packet_path": str(packet_path),
                "manifest_path": str(path),
                "payload_hash": manifest["payload_hash"],
                "hash8": manifest["hash8"],
                "static_lint_result": manifest["static_lint_result"],
                "payload_visibility_result": manifest["payload_visibility_result"],
                "no_model_visible_expected_verdict": manifest["no_model_visible_expected_verdict"],
                "no_live_model_calls": manifest["no_live_model_calls"],
                "taylor_approved_for_freeze": manifest["taylor_approved_for_freeze"],
                "builder_hypothesis_verdict": manifest["builder_hypothesis_verdict"],
            }
        )

    validation_failures = []
    if len(rows) != 5:
        validation_failures.append("expected exactly five freeze-manifest preflight rows")
    if any(row["static_lint_result"] != "PASS" for row in rows):
        validation_failures.append("one or more manifests has static_lint_result != PASS")
    if any(row["payload_visibility_result"] != "PASS" for row in rows):
        validation_failures.append("one or more manifests has payload_visibility_result != PASS")
    if any(row["no_model_visible_expected_verdict"] is not True for row in rows):
        validation_failures.append("one or more manifests has no_model_visible_expected_verdict != true")
    if any(row["no_live_model_calls"] is not True for row in rows):
        validation_failures.append("one or more manifests has no_live_model_calls != true")
    if any(row["taylor_approved_for_freeze"] is not False for row in rows):
        validation_failures.append("one or more manifests unexpectedly has taylor_approved_for_freeze != false")

    return {
        "artifact_type": "BAL100_leaderboard_20_allow_freeze_manifest_preflight",
        "created_at": _utc_now(),
        "status": "PASS" if not validation_failures else "FAIL",
        "mode": "static_freeze_manifest_preflight_no_freeze",
        "ticket_id": migrated_report["ticket_id"],
        "source_migrated_drafts": str(migrated_report_path),
        "out_dir": str(out_dir),
        "manifest_count": len(rows),
        "manifests": rows,
        "validation": {
            "failures": validation_failures,
            "all_static_lint_pass": all(row["static_lint_result"] == "PASS" for row in rows),
            "all_payload_visibility_pass": all(row["payload_visibility_result"] == "PASS" for row in rows),
            "all_no_model_visible_expected_verdict": all(row["no_model_visible_expected_verdict"] is True for row in rows),
            "all_no_live_model_calls": all(row["no_live_model_calls"] is True for row in rows),
            "all_taylor_approved_for_freeze_false": all(row["taylor_approved_for_freeze"] is False for row in rows),
        },
        "safe_boundaries": {
            "provider_calls": False,
            "freeze": False,
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
        "next_gate": "Taylor must explicitly approve freeze for exact manifest paths before any freeze command may run.",
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BAL100 Leaderboard 20 ALLOW Freeze-Manifest Preflight",
        "",
        f"Status: {report['status']}  ",
        f"Created: {report['created_at']}  ",
        f"Ticket: `{report['ticket_id']}`  ",
        "Mode: static freeze-manifest preflight only; not freeze",
        "",
        "## Manifests",
        "",
        "| Scenario ID | Static Lint | Visibility | No Verdict Visible | Taylor Freeze Approval | Hash8 | Manifest Path |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in report["manifests"]:
        lines.append(
            f"| `{row['scenario_id']}` | {row['static_lint_result']} | {row['payload_visibility_result']} | {row['no_model_visible_expected_verdict']} | {row['taylor_approved_for_freeze']} | `{row['hash8']}` | `{row['manifest_path']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Manifest count: {report['manifest_count']}",
            f"- All static lint pass: {report['validation']['all_static_lint_pass']}",
            f"- All payload visibility pass: {report['validation']['all_payload_visibility_pass']}",
            f"- All no model-visible expected verdict: {report['validation']['all_no_model_visible_expected_verdict']}",
            f"- All no live model calls: {report['validation']['all_no_live_model_calls']}",
            f"- All Taylor freeze approvals false: {report['validation']['all_taylor_approved_for_freeze_false']}",
            f"- Failures: {report['validation']['failures'] or 'none'}",
            "",
            "## Next Gate",
            "",
            report["next_gate"],
            "",
            "## Safe Boundaries",
            "",
            "No provider calls, freeze, Judge, official trace, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, or push were authorized or performed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build static freeze-manifest preflight artifacts for the BAL100 hard-ALLOW migrated drafts.")
    parser.add_argument("--migrated-report", type=Path, default=MIGRATED_DRAFTS_REPORT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    report = build_preflight(args.migrated_report, args.out_dir)
    _write_json(args.json_out, report)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(build_markdown(report))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    print(f"status {report['status']}")
    print(f"manifests {report['manifest_count']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
