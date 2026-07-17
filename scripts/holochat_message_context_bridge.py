#!/usr/bin/env python3
"""Upload a normalized Personal message-context event to HoloChat.

This bridge is intentionally not a message reader. OpenClaw or a future mobile
adapter must produce the bounded event on stdin after its own user-approved
source read. Raw message bodies are rejected before any request is made.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from holochat_message_connectors import MessageConnectorError, normalize_message_event


def _required_environment(name: str) -> str:
    value = str(os.getenv(name) or "").strip()
    if not value:
        raise MessageConnectorError(f"{name} is required")
    return value


def _read_event(stdin: Any) -> dict[str, Any]:
    try:
        body = json.load(stdin)
    except json.JSONDecodeError as exc:
        raise MessageConnectorError("stdin must contain one JSON event object") from exc
    return normalize_message_event(body)


def _build_request(event: dict[str, Any]) -> Request:
    ingest_url = _required_environment("HOLOCHAT_MESSAGE_INGEST_URL")
    connector_id = _required_environment("HOLOCHAT_MESSAGE_CONNECTOR_ID")
    connector_secret = _required_environment("HOLOCHAT_MESSAGE_CONNECTOR_SECRET")
    return Request(
        ingest_url,
        data=json.dumps(event, separators=(",", ":")).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Holo-Connector-Id": connector_id,
            "X-Holo-Connector-Secret": connector_secret,
        },
        method="POST",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upload a normalized Personal Holo message-context event.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate stdin only; do not read credentials or send a request.",
    )
    args = parser.parse_args(argv)

    try:
        event = _read_event(sys.stdin)
        if args.dry_run:
            print(json.dumps({"validated": True, "raw_messages_accepted": False, "event_type": event["event_type"]}))
            return 0
        request = _build_request(event)
        with urlopen(request, timeout=15) as response:  # nosec B310 - user-owned configured endpoint
            payload = json.loads(response.read().decode("utf-8"))
        print(json.dumps({
            "status": payload.get("status"),
            "event_id": payload.get("event_id"),
            "duplicate": bool(payload.get("duplicate")),
            "raw_messages_accepted": False,
        }))
        return 0
    except MessageConnectorError as exc:
        print(f"message context bridge rejected input: {exc}", file=sys.stderr)
    except HTTPError as exc:
        print(f"message context bridge request failed: HTTP {exc.code}", file=sys.stderr)
    except URLError:
        print("message context bridge request failed: connector endpoint unavailable", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
