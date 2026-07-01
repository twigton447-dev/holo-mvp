#!/usr/bin/env python3
"""Build a no-provider operator handoff for Wave5 batched Holo execution."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
PREFLIGHT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_EXECUTION_PREFLIGHT_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_OPERATOR_HANDOFF_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_OPERATOR_HANDOFF_2026_07_01.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def current_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def build() -> dict[str, Any]:
    preflight = load_json(PREFLIGHT_JSON)
    batches = preflight["batches"]
    if preflight["status"] != "PASS":
        raise RuntimeError(f"wave5_preflight_not_pass:{preflight.get('status')}")
    if preflight["totals"]["providers_called_during_preflight"] != 0:
        raise RuntimeError("provider_calls_present_in_preflight")
    if preflight["totals"]["judges_called_during_preflight"] != 0:
        raise RuntimeError("judge_calls_present_in_preflight")

    next_batch = batches[0]
    report = {
        "classification": "HOLOVERIFY_WAVE5_BATCH_OPERATOR_HANDOFF_NO_PROVIDER",
        "status": "PASS",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_from_head": current_head(),
        "preflight_ref": str(PREFLIGHT_JSON.relative_to(REPO_ROOT)),
        "preflight_status": preflight["status"],
        "freeze_root_hash": preflight["freeze_root_hash"],
        "execution_policy": {
            "one_batch_per_approval": True,
            "do_not_run_full_wave5_at_once": True,
            "providers_called_by_this_handoff": 0,
            "judges_called_by_this_handoff": 0,
            "solo_called_by_this_handoff": 0,
            "fallback_or_substitution_allowed": False,
            "stop_on_invalid_batch": True,
        },
        "totals": preflight["totals"],
        "next_recommended_batch": next_batch,
        "batch_queue": batches,
        "operator_rules": [
            "Run only one Wave5 batch at a time.",
            "Use the exact approval statement and approval packet SHA for that batch.",
            "Do not run solo or judges during Wave5 Holo batch execution.",
            "Do not edit frozen packets or prompts.",
            "If a batch fails, preserve the invalid run and stop for autopsy before continuing.",
            "Do not treat future unrun batches as evidence.",
        ],
    }
    return report


def render_md(report: dict[str, Any]) -> str:
    next_batch = report["next_recommended_batch"]
    lines = [
        "# HoloVerify Wave5 Batch Operator Handoff",
        "",
        f"Status: `{report['status']}`",
        f"Generated from head: `{report['generated_from_head']}`",
        f"Freeze root: `{report['freeze_root_hash']}`",
        f"Preflight: `{report['preflight_ref']}`",
        "",
        "## Scope",
        "",
        "- No providers were called by this handoff.",
        "- No judges were called by this handoff.",
        "- Wave5 remains split into 28 independent 5-pair batches.",
        "- Each approved batch is 10 packets and 50 Holo provider calls.",
        "- Do not run the full 280-packet bank as one live job.",
        "",
        "## Next Batch",
        "",
        f"- Batch: `{next_batch['batch_id']}`",
        f"- Family: `{next_batch['family_id']}`",
        f"- Pairs: `{next_batch['pairs']}`",
        f"- Packets: `{next_batch['packets']}`",
        f"- Expected provider calls if approved: `{next_batch['expected_provider_calls']}`",
        f"- Approval packet SHA: `{next_batch['approval_packet_sha256']}`",
        "",
        "```bash",
        next_batch["run_command_after_explicit_approval"],
        "```",
        "",
        "## Operator Rules",
        "",
    ]
    for rule in report["operator_rules"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Batch Queue",
            "",
            "| # | Batch | Family | Pairs | Packets | Calls | Approval SHA |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for index, row in enumerate(report["batch_queue"], start=1):
        lines.append(
            f"| `{index}` | `{row['batch_id']}` | `{row['family_id']}` | `{row['pairs']}` | "
            f"`{row['packets']}` | `{row['expected_provider_calls']}` | `{row['approval_packet_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Evidence Boundary",
            "",
            "This handoff is not benchmark evidence. A batch becomes evidence only after a clean live run, lock validation, no-leakage audit, and readiness assertions pass for that specific batch.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    report = build()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    print(json.dumps({"status": report["status"], "batches": len(report["batch_queue"]), "providers_called": 0, "judges_called": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
