"""
Release identity for HoloChat.

This module is intentionally small and dependency-free so /health and /version
can report what is actually running in production.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any


APP_VERSION = "HC-GOVSHADOW-001"
ARCHITECTURE_VERSION = "holochat-governed-shadow-v1"


def _first_env(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _git_head_commit() -> str:
    git_dir = Path(__file__).resolve().parent / ".git"
    try:
        if git_dir.is_file():
            for line in git_dir.read_text(encoding="utf-8").splitlines():
                if line.startswith("gitdir:"):
                    git_dir = (git_dir.parent / line.split(":", 1)[1].strip()).resolve()
                    break
        head_path = git_dir / "HEAD"
        head = head_path.read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            ref_path = git_dir / head.split(" ", 1)[1]
            return ref_path.read_text(encoding="utf-8").strip()
        return head
    except Exception:
        return ""


@lru_cache(maxsize=1)
def release_info() -> dict[str, Any]:
    commit = _first_env(
        "HOLOCHAT_GIT_COMMIT",
        "RAILWAY_GIT_COMMIT_SHA",
        "GIT_COMMIT",
        "SOURCE_VERSION",
        "VERCEL_GIT_COMMIT_SHA",
        "RENDER_GIT_COMMIT",
    ) or _git_head_commit()
    branch = _first_env(
        "HOLOCHAT_GIT_BRANCH",
        "RAILWAY_GIT_BRANCH",
        "GIT_BRANCH",
        "VERCEL_GIT_COMMIT_REF",
        "RENDER_GIT_BRANCH",
    )
    deploy_service = _first_env(
        "HOLOCHAT_DEPLOY_SERVICE",
        "RAILWAY_SERVICE_NAME",
        "RAILWAY_PROJECT_NAME",
        "RENDER_SERVICE_NAME",
        "VERCEL_PROJECT_PRODUCTION_URL",
    )
    deploy_environment = _first_env(
        "HOLOCHAT_DEPLOY_ENV",
        "RAILWAY_ENVIRONMENT_NAME",
        "RENDER_SERVICE_TYPE",
        "VERCEL_ENV",
    )
    app_version = os.getenv("HOLOCHAT_APP_VERSION", APP_VERSION).strip() or APP_VERSION
    architecture_version = (
        os.getenv("HOLOCHAT_ARCHITECTURE_VERSION", ARCHITECTURE_VERSION).strip()
        or ARCHITECTURE_VERSION
    )
    commit_short = commit[:8] if commit else ""
    return {
        "app_version": app_version,
        "architecture_version": architecture_version,
        "release_channel": os.getenv("HOLOCHAT_RELEASE_CHANNEL", "production").strip()
        or "production",
        "git_commit": commit,
        "git_commit_short": commit_short,
        "git_branch": branch,
        "deploy_service": deploy_service,
        "deploy_environment": deploy_environment,
        "deploy_instance": _first_env(
            "HOLOCHAT_DEPLOY_INSTANCE",
            "RAILWAY_DEPLOYMENT_ID",
            "RENDER_INSTANCE_ID",
            "VERCEL_DEPLOYMENT_ID",
        ),
        "build_label": f"{app_version}{'+' + commit_short if commit_short else ''}",
    }
