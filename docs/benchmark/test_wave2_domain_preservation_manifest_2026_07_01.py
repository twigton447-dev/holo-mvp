#!/usr/bin/env python3
"""No-provider regression test for the Wave 2 preservation manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
MANIFEST_MD = MANIFEST.with_suffix(".md")


def package_sha256(data: dict) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return hashlib.sha256((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8")).hexdigest()


def current_status_paths() -> set[str]:
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "-z"], cwd=REPO_ROOT)
    parts = [part.decode("utf-8") for part in raw.split(b"\0") if part]
    paths: set[str] = set()
    index = 0
    while index < len(parts):
        entry = parts[index]
        status = entry[:2]
        paths.add(entry[3:])
        if "R" in status or "C" in status:
            index += 1
        index += 1
    return paths


def manifest_paths(manifest: dict) -> set[str]:
    return {row["path"] for rows in manifest["dirty_groups"].values() for row in rows}


def current_package_sha(relpath: str) -> str | None:
    data = json.loads((REPO_ROOT / relpath).read_text())
    return data.get("package_sha256")


def main() -> int:
    manifest = json.loads(MANIFEST.read_text())
    md = MANIFEST_MD.read_text()
    policy = manifest["safe_staging_policy"]
    assert manifest["status"] == "PASS", manifest
    assert manifest["generated_without_provider_calls"] is True, manifest
    assert package_sha256(manifest) == manifest["package_sha256"], manifest["package_sha256"]
    assert manifest["summary"]["other_dirty_path_count"] == 0, manifest["summary"]
    assert "git add ." in policy["do_not_use"], policy
    assert "git add -A" in policy["do_not_use"], policy
    assert policy["stage_by_named_group_only"] is True, policy
    assert policy["preserve_unrelated_dirty_paths"] is True, policy
    assert current_status_paths() == manifest_paths(manifest), "preservation_manifest_stale"
    assert sorted(manifest["artifact_inputs"]) == ["control_room", "readiness"], manifest["artifact_inputs"]
    for row in manifest["artifact_inputs"].values():
        assert row["package_sha256"] == current_package_sha(row["path"]), row
    assert "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01" in manifest["artifact_input_scope"][
        "excludes_downstream_summaries"
    ], manifest["artifact_input_scope"]
    assert "Do not use `git add .`." in md, md
    assert "other_dirty_paths" in manifest["review_order"], manifest["review_order"]
    print(
        json.dumps(
            {
                "dirty_paths": manifest["summary"]["tracked_or_untracked_path_count"],
                "other_dirty_paths": manifest["summary"]["other_dirty_path_count"],
                "preservation_manifest_sha256": manifest["package_sha256"],
                "provider_calls_made": 0,
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
