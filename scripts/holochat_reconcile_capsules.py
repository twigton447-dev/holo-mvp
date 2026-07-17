#!/usr/bin/env python3
"""Operator-only, dry-run-first HoloChat identity reconciliation.

The tool reads capsule identity metadata and database-generated record counts.
It never reads or prints messages, memory values, artifacts, or connector
payloads. An apply run invokes one transactional RPC: every supported record
moves to the selected legacy HoloBrain or the database rolls the entire change
back. This script must be run only during the reviewed identity-maintenance
window created by ``20260717_holochat_capsule_identity_preparation.sql``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any

from project_brain import ProjectBrain


def _fingerprint(value: str) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:16]


def _capsule_metadata(client: Any, capsule_id: str) -> dict[str, Any]:
    rows = (
        client.table("holo_capsules")
        .select("capsule_id,email,google_id,identity_status,merged_into_capsule_id,created_at,last_active")
        .eq("capsule_id", capsule_id)
        .limit(2)
        .execute()
        .data
        or []
    )
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one capsule for {capsule_id!r}.")
    return dict(rows[0])


def _preflight(client: Any, source_capsule_id: str, target_capsule_id: str) -> dict[str, Any]:
    response = client.rpc(
        "holo_preflight_capsule_identity_reconciliation",
        {
            "p_source_capsule_id": source_capsule_id,
            "p_target_capsule_id": target_capsule_id,
        },
    ).execute()
    if not isinstance(response.data, dict):
        raise RuntimeError("Identity preflight returned an invalid receipt.")
    return dict(response.data)


def _set_maintenance(client: Any, *, enabled: bool, reason: str) -> dict[str, Any]:
    response = client.rpc(
        "holo_set_identity_maintenance",
        {"p_enabled": enabled, "p_reason": reason},
    ).execute()
    if not isinstance(response.data, dict):
        raise RuntimeError("Identity maintenance control returned an invalid receipt.")
    return dict(response.data)


def build_dry_run(client: Any, source_capsule_id: str, target_capsule_id: str) -> dict[str, Any]:
    if source_capsule_id == target_capsule_id:
        raise RuntimeError("Source and target capsule IDs must be different.")
    source = _capsule_metadata(client, source_capsule_id)
    target = _capsule_metadata(client, target_capsule_id)
    source_email = str(source.get("email") or "").strip().lower()
    target_email = str(target.get("email") or "").strip().lower()
    if not source_email or source_email != target_email:
        raise RuntimeError("Source and target must have the same normalized email.")
    if str(source.get("identity_status") or "active") != "active":
        raise RuntimeError("Source capsule is not active.")
    if str(target.get("identity_status") or "active") != "active":
        raise RuntimeError("Target capsule is not active.")
    source_google_id = str(source.get("google_id") or "")
    target_google_id = str(target.get("google_id") or "")
    if not source_google_id or source_google_id.startswith("email:"):
        raise RuntimeError("Source must be the capsule carrying the verified Google identity.")
    # The target must be the original email-only HoloBrain, not a second
    # verified identity that happens to share the mailbox.
    if not target_google_id.startswith("email:"):
        raise RuntimeError("Target must be the original email-only HoloBrain, not another Google identity.")

    preflight = _preflight(client, source_capsule_id, target_capsule_id)
    if not preflight.get("eligible"):
        raise RuntimeError("Identity preflight found record collisions. No merge was attempted.")

    return {
        "mode": "dry_run",
        "source_capsule_id": source_capsule_id,
        "target_capsule_id": target_capsule_id,
        "normalized_email_fingerprint": _fingerprint(source_email),
        "source_google_subject_fingerprint": _fingerprint(source_google_id),
        "target_prior_google_subject_fingerprint": _fingerprint(target_google_id),
        "source_record_counts": preflight.get("record_counts", {}),
        "collision_counts": preflight.get("collision_counts", {}),
        "will_change": [
            "move all eligible source records atomically into the target HoloBrain",
            "archive the source identity so it can no longer authenticate",
            "rebind the verified Google subject to the target capsule",
            "revoke source API keys; a new key must be issued after the merge",
            "write an audit receipt with hashed identity fingerprints and record counts",
        ],
        "will_not_change": [
            "no message, memory, artifact, or connector content is printed by this tool",
            "no user data is deleted; the source identity is archived only after its records transfer",
            "a source subscription blocks the merge for explicit billing review",
            "a collision or database failure aborts the complete transaction",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Accidental capsule holding the verified Google subject.")
    parser.add_argument("--target", help="Canonical legacy email-only capsule that must retain the HoloBrain.")
    parser.add_argument("--reason", default="operator-approved duplicate identity reconciliation")
    parser.add_argument("--apply", action="store_true", help="Invoke the reconciliation RPC after the dry run succeeds.")
    parser.add_argument("--confirm", default="", help="Required literal for the requested operation.")
    maintenance = parser.add_mutually_exclusive_group()
    maintenance.add_argument("--begin-maintenance", action="store_true", help="Block auth and capsule writes before reconciliation.")
    maintenance.add_argument("--end-maintenance", action="store_true", help="Resume auth only after integrity checks succeed.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    brain = ProjectBrain()
    client = getattr(brain, "_client", None)
    if client is None:
        print("Durable Supabase credentials are required. No changes were made.", file=sys.stderr)
        return 2
    try:
        if args.begin_maintenance or args.end_maintenance:
            expected = "PAUSE_SIGNINS" if args.begin_maintenance else "RESUME_SIGNINS"
            if args.confirm != expected:
                print(f"Refusing maintenance change. Re-run with --confirm {expected!r}.", file=sys.stderr)
                return 2
            receipt = _set_maintenance(
                client,
                enabled=bool(args.begin_maintenance),
                reason=args.reason,
            )
            print(json.dumps({"mode": "maintenance", "receipt": receipt}, indent=2, sort_keys=True))
            return 0

        if not args.source or not args.target:
            print("--source and --target are required for a reconciliation dry run.", file=sys.stderr)
            return 2
        expected_confirmation = f"MERGE:{args.source}:{args.target}"
        report = build_dry_run(client, args.source, args.target)
        print(json.dumps(report, indent=2, sort_keys=True))
        if not args.apply:
            return 0
        if args.confirm != expected_confirmation:
            print(f"Refusing apply. Re-run with --confirm {expected_confirmation!r}.", file=sys.stderr)
            return 2
        result = client.rpc(
            "holo_reconcile_capsule_identity",
            {
                "p_source_capsule_id": args.source,
                "p_target_capsule_id": args.target,
                "p_reason": args.reason,
            },
        ).execute()
        print(json.dumps({"mode": "applied", "receipt": result.data}, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(f"Reconciliation stopped without completing: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
