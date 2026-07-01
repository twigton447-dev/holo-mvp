#!/usr/bin/env python3
"""Build a no-provider preservation manifest for Wave 2 domain consolidation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01"
OUT_JSON = OUT_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
OUT_MD = OUT_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.md"

CONTROL_ROOM = OUT_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
READINESS = REPO_ROOT / "docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"


GROUPS = [
    (
        "source_scripts_and_tests",
        (
            "docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
            "docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py",
            "docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py",
            "docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
            "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
            "docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py",
            "docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py",
            "docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py",
            "docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
            "docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py",
            "docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py",
            "docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py",
            "docs/benchmark/test_wave2_domain_completion_audit_2026_07_01.py",
            "docs/benchmark/test_wave2_domain_control_room_2026_07_01.py",
            "docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py",
            "docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py",
            "docs/benchmark/test_wave2_domain_selective_staging_plan_2026_07_01.py",
            "docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py",
            "docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py",
            "docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py",
            "docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
        ),
    ),
    (
        "modified_pipeline_scripts",
        (
            "docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py",
            "docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py",
            "docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py",
            "docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py",
            "docs/benchmark/stage_wave2_holo_target_batch_2026_07_01.py",
        ),
    ),
    ("domain_ledger_outputs", ("docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/",)),
    ("readiness_outputs", ("docs/benchmark/wave2_domain_completion_readiness_2026_07_01/",)),
    ("control_room_outputs", ("docs/benchmark/wave2_domain_control_room_2026_07_01/",)),
    (
        "batch004_selected_target_stage",
        (
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_004/",
        ),
    ),
    (
        "batch005_full_family_remainder_stage",
        (
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/wave2_holo_target_batch_005/",
        ),
    ),
    (
        "combined_evidence_and_metrics",
        (
            "docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/",
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.json",
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_COMBINED_EVIDENCE_MEMO_2026_07_01.md",
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json",
            "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.md",
            "outputs/holoverify_holobuild_metrics_2026_07_01/",
        ),
    ),
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_text(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True) + "\n")


def git_value(*args: str) -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "UNAVAILABLE"


def git_status_rows() -> list[dict[str, str]]:
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "-z"], cwd=REPO_ROOT)
    parts = [part.decode("utf-8") for part in raw.split(b"\0") if part]
    rows: list[dict[str, str]] = []
    index = 0
    while index < len(parts):
        entry = parts[index]
        status = entry[:2]
        path = entry[3:]
        row = {"path": path, "status": status}
        if "R" in status or "C" in status:
            index += 1
            if index < len(parts):
                row["source_path"] = parts[index]
        rows.append(row)
        index += 1
    return rows


def group_for_path(path: str) -> str:
    for group_name, prefixes in GROUPS:
        for prefix in prefixes:
            if prefix.endswith("/"):
                if path.startswith(prefix):
                    return group_name
            elif path == prefix:
                return group_name
    return "other_dirty_paths"


def artifact_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "path": str(path.relative_to(REPO_ROOT))}
    data = read_json(path)
    return {
        "exists": True,
        "package_sha256": data.get("package_sha256"),
        "path": str(path.relative_to(REPO_ROOT)),
        "status": data.get("status"),
        "summary": data.get("summary"),
    }


def build_manifest() -> dict[str, Any]:
    status_rows = git_status_rows()
    groups: dict[str, list[dict[str, str]]] = {}
    for row in status_rows:
        groups.setdefault(group_for_path(row["path"]), []).append(row)
    for group_rows in groups.values():
        group_rows.sort(key=lambda item: item["path"])
    group_summaries = {
        group_name: {
            "path_count": len(rows),
            "statuses": sorted({row["status"] for row in rows}),
        }
        for group_name, rows in sorted(groups.items())
    }
    manifest = {
        "artifact_inputs": {
            "control_room": artifact_status(CONTROL_ROOM),
            "readiness": artifact_status(READINESS),
        },
        "artifact_input_scope": {
            "excludes_downstream_summaries": [
                "WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01",
                "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01",
            ],
            "reason": "Avoid circular freshness dependencies: validation may validate this manifest, and the refresh receipt may summarize it.",
        },
        "classification": "WAVE2_DOMAIN_PRESERVATION_MANIFEST_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dirty_group_summaries": group_summaries,
        "dirty_groups": groups,
        "generated_without_provider_calls": True,
        "git": {
            "branch": git_value("branch", "--show-current"),
            "head": git_value("rev-parse", "HEAD"),
            "status_porcelain_count": len(status_rows),
        },
        "package_sha256": "",
        "review_order": [
            "source_scripts_and_tests",
            "modified_pipeline_scripts",
            "combined_evidence_and_metrics",
            "batch004_selected_target_stage",
            "batch005_full_family_remainder_stage",
            "domain_ledger_outputs",
            "readiness_outputs",
            "control_room_outputs",
            "other_dirty_paths",
        ],
        "safe_staging_policy": {
            "do_not_use": ["git add .", "git add -A"],
            "stage_by_named_group_only": True,
            "preserve_unrelated_dirty_paths": True,
        },
        "status": "PASS",
        "summary": {
            "group_count": len(groups),
            "other_dirty_path_count": len(groups.get("other_dirty_paths", [])),
            "provider_calls_made_by_manifest": 0,
            "tracked_or_untracked_path_count": len(status_rows),
        },
    }
    manifest["package_sha256"] = package_sha256(manifest)
    return manifest


def render_md(manifest: dict[str, Any]) -> str:
    lines = [
        "# Wave 2 Domain Preservation Manifest",
        "",
        f"Status: `{manifest['status']}`",
        f"Package SHA-256: `{manifest['package_sha256']}`",
        f"Generated without provider calls: `{manifest['generated_without_provider_calls']}`",
        "",
        "## Source State",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Branch | `{manifest['git']['branch']}` |",
        f"| HEAD | `{manifest['git']['head']}` |",
        f"| Dirty paths | `{manifest['git']['status_porcelain_count']}` |",
        f"| Other dirty paths | `{manifest['summary']['other_dirty_path_count']}` |",
        "",
        "## Artifact Inputs",
        "",
        "| Artifact | Status | Package SHA-256 |",
        "| --- | --- | --- |",
    ]
    for label, row in manifest["artifact_inputs"].items():
        lines.append(f"| `{label}` | `{row.get('status')}` | `{row.get('package_sha256')}` |")
    lines.extend(
        [
            "",
            "## Review Groups",
            "",
            "| Group | Paths | Statuses |",
            "| --- | ---: | --- |",
        ]
    )
    for group_name in manifest["review_order"]:
        summary = manifest["dirty_group_summaries"].get(group_name, {"path_count": 0, "statuses": []})
        statuses = ", ".join(summary["statuses"]) if summary["statuses"] else "none"
        lines.append(f"| `{group_name}` | `{summary['path_count']}` | `{statuses}` |")
    lines.extend(
        [
            "",
            "## Staging Policy",
            "",
            "- Do not use `git add .`.",
            "- Do not use `git add -A`.",
            "- Stage by named group only after review.",
            "- Preserve unrelated dirty paths.",
            "",
            "## Group Paths",
            "",
        ]
    )
    for group_name in manifest["review_order"]:
        rows = manifest["dirty_groups"].get(group_name, [])
        if not rows:
            continue
        lines.extend([f"### {group_name}", ""])
        for row in rows:
            lines.append(f"- `{row['status']}` `{row['path']}`")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    manifest = build_manifest()
    write_json(OUT_JSON, manifest)
    OUT_MD.write_text(render_md(manifest))
    print(
        json.dumps(
            {
                "json": str(OUT_JSON.relative_to(REPO_ROOT)),
                "md": str(OUT_MD.relative_to(REPO_ROOT)),
                "other_dirty_path_count": manifest["summary"]["other_dirty_path_count"],
                "package_sha256": manifest["package_sha256"],
                "status": manifest["status"],
                "tracked_or_untracked_path_count": manifest["summary"]["tracked_or_untracked_path_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
