#!/usr/bin/env python3
"""No-provider regression test for the Wave 2 selective staging plan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01"
PLAN = CONTROL_ROOT / "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
PLAN_MD = PLAN.with_suffix(".md")
PRESERVATION = CONTROL_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"


def package_sha256(data: dict) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return hashlib.sha256((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8")).hexdigest()


def main() -> int:
    plan = json.loads(PLAN.read_text())
    preservation = json.loads(PRESERVATION.read_text())
    md = PLAN_MD.read_text()
    manifest_paths = sorted(row["path"] for rows in preservation["dirty_groups"].values() for row in rows)
    plan_paths = sorted(path for group in plan["stage_groups"] for path in group["paths"])
    assert plan["status"] == "PASS", plan
    assert plan["generated_without_provider_calls"] is True, plan
    assert package_sha256(plan) == plan["package_sha256"], plan["package_sha256"]
    assert plan["manifest_package_sha256"] == preservation["package_sha256"], plan
    assert plan_paths == manifest_paths, "selective_staging_plan_stale"
    assert all(group["command"].startswith("git add -- ") for group in plan["stage_groups"]), plan
    assert all("git add ." not in group["command"] for group in plan["stage_groups"]), plan
    assert all("git add -A" not in group["command"] for group in plan["stage_groups"]), plan
    assert "This artifact does not stage files." in md, md
    assert "git add --" in md, md
    print(
        json.dumps(
            {
                "path_count": plan["summary"]["path_count"],
                "provider_calls_made": 0,
                "selective_staging_plan_sha256": plan["package_sha256"],
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
