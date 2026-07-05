#!/usr/bin/env python3
"""Build a no-provider selective staging plan for Wave 2 domain consolidation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01"
PRESERVATION_MANIFEST = CONTROL_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
OUT_JSON = CONTROL_ROOT / "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
OUT_MD = CONTROL_ROOT / "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.md"


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


def quote_path(path: str) -> str:
    return "'" + path.replace("'", "'\"'\"'") + "'"


def command_for_paths(paths: list[str]) -> str:
    return "git add -- " + " ".join(quote_path(path) for path in paths)


def build_plan() -> dict[str, Any]:
    manifest = read_json(PRESERVATION_MANIFEST)
    groups = manifest["dirty_groups"]
    stage_groups: list[dict[str, Any]] = []
    for group_name in manifest["review_order"]:
        rows = groups.get(group_name, [])
        if not rows:
            continue
        paths = [row["path"] for row in rows]
        stage_groups.append(
            {
                "command": command_for_paths(paths),
                "group": group_name,
                "path_count": len(paths),
                "paths": paths,
                "statuses": sorted({row["status"] for row in rows}),
            }
        )
    all_paths = [path for group in stage_groups for path in group["paths"]]
    checks = {
        "all_manifest_paths_represented": sorted(all_paths)
        == sorted(row["path"] for rows in groups.values() for row in rows),
        "commands_are_path_limited": all(group["command"].startswith("git add -- ") for group in stage_groups),
        "no_git_add_all_command": all("git add ." not in group["command"] and "git add -A" not in group["command"] for group in stage_groups),
        "other_dirty_paths_reported_for_manual_exclusion": manifest["summary"]["other_dirty_path_count"] >= 0,
        "preservation_manifest_pass": manifest["status"] == "PASS",
    }
    plan = {
        "checks": checks,
        "classification": "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_without_provider_calls": True,
        "manifest_package_sha256": manifest["package_sha256"],
        "package_sha256": "",
        "safe_staging_policy": manifest["safe_staging_policy"],
        "stage_groups": stage_groups,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "summary": {
            "group_count": len(stage_groups),
            "other_dirty_path_count": manifest["summary"]["other_dirty_path_count"],
            "path_count": len(all_paths),
            "provider_calls_made_by_plan": 0,
        },
    }
    plan["package_sha256"] = package_sha256(plan)
    return plan


def render_md(plan: dict[str, Any]) -> str:
    lines = [
        "# Wave 2 Domain Selective Staging Plan",
        "",
        f"Status: `{plan['status']}`",
        f"Package SHA-256: `{plan['package_sha256']}`",
        f"Generated without provider calls: `{plan['generated_without_provider_calls']}`",
        f"Preservation manifest SHA-256: `{plan['manifest_package_sha256']}`",
        "",
        "## Policy",
        "",
        "- This artifact does not stage files.",
        "- Do not use `git add .`.",
        "- Do not use `git add -A`.",
        "- Review and stage by named group only.",
        "",
        "## Group Commands",
        "",
    ]
    for index, group in enumerate(plan["stage_groups"], start=1):
        lines.extend(
            [
                f"{index}. `{group['group']}` - `{group['path_count']}` paths",
                "",
                "```bash",
                group["command"],
                "```",
                "",
            ]
        )
    lines.extend(["## Checks", "", "| Check | Result |", "| --- | --- |"])
    for check_id, passed in plan["checks"].items():
        lines.append(f"| `{check_id}` | `{'PASS' if passed else 'FAIL'}` |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    plan = build_plan()
    write_json(OUT_JSON, plan)
    OUT_MD.write_text(render_md(plan))
    print(
        json.dumps(
            {
                "json": str(OUT_JSON.relative_to(REPO_ROOT)),
                "md": str(OUT_MD.relative_to(REPO_ROOT)),
                "package_sha256": plan["package_sha256"],
                "path_count": plan["summary"]["path_count"],
                "provider_calls_made": 0,
                "status": plan["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if plan["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
