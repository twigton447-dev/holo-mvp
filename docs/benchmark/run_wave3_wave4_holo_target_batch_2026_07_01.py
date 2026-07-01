#!/usr/bin/env python3
"""Run staged Wave 3 / Wave 4 Holo target batches.

This is a thin adapter over the current locked Wave 2 target-batch runner. It
keeps the same Holo architecture and live execution path, but rebinds the
freeze root, batch IDs, and payload wording to the Wave3/Wave4 packet bank.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
WAVE2_RUNNER_PATH = BENCHMARK_ROOT / "run_wave2_holo_target_batch_2026_07_01.py"
EXPECTED_FREEZE_ROOT_HASH = "ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5"

WAVE_CONFIG = {
    "wave3": {
        "batch_prefix": "WAVE3_HOLO_TARGET_BATCH",
        "output_prefix": "wave3_holo_target_batch",
        "title": "Wave 3 Holo Target Batch",
        "payload_label": "Wave 3",
    },
    "wave4": {
        "batch_prefix": "WAVE4_HOLO_TARGET_BATCH",
        "output_prefix": "wave4_holo_target_batch",
        "title": "Wave 4 Holo Target Batch",
        "payload_label": "Wave 4",
    },
}


def load_wave2_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave3_wave4_holo_live_base", WAVE2_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def configure_runner(module: Any, wave: str, batch_number: int) -> None:
    cfg = WAVE_CONFIG[wave]
    suffix = f"{batch_number:03d}"
    batch_id = f"{cfg['batch_prefix']}_{suffix}"
    staging_root = FREEZE_ROOT / "holo_target_batches" / f"{cfg['output_prefix']}_{suffix}"
    registration_path = staging_root / f"{batch_id}_REGISTRATION_2026_07_01.json"
    registration = load_json(registration_path)

    module.__file__ = str(Path(__file__).resolve())
    module.FREEZE_ROOT = FREEZE_ROOT
    module.EXPECTED_FREEZE_ROOT_HASH = EXPECTED_FREEZE_ROOT_HASH
    module.EXPECTED_TARGET_SELECTION_SHA = registration.get("source_target_selection_sha256") or registration.get(
        "source_solo_results_sha256"
    )
    module.BATCH_NUMBER = batch_number
    module.BATCH_SUFFIX = suffix
    module.BATCH_ID = batch_id
    module.STAGING_ROOT = staging_root
    module.REGISTRATION_PATH = registration_path
    module.PREFLIGHT_PATH = staging_root / f"{batch_id}_PREFLIGHT_2026_07_01.json"
    module.LIVE_PREFLIGHT_JSON = staging_root / f"{batch_id}_LIVE_PREFLIGHT_2026_07_01.json"
    module.LIVE_PREFLIGHT_MD = staging_root / f"{batch_id}_LIVE_PREFLIGHT_2026_07_01.md"
    module.LIVE_RUN_ROOT = staging_root / "live_runs"
    original_render_live_summary_md = module.render_live_summary_md

    def convert_payload(packet: dict[str, Any]) -> dict[str, Any]:
        internal_documents = []
        policy_documents = []
        for record in packet["source_control_facts"]:
            doc = {
                "doc_id": record["source_id"],
                "type": record["source_type"],
                "content": record["content"],
            }
            if record["source_type"] == "policy_control":
                policy_documents.append(
                    {
                        "doc_id": record["source_id"],
                        "title": f"Frozen {cfg['payload_label']} source-boundary policy",
                        "content": record["content"],
                    }
                )
            else:
                internal_documents.append(doc)
        return {
            "action": {
                "action_date": "2026-07-01",
                "amount": 0,
                "business_ref": packet["model_visible_payload"]["case_ref"],
                "currency": "USD",
                "description": packet["action_boundary"],
                "type": packet.get("domain_slug") or f"{wave}_action_boundary",
                "vendor": f"Frozen {cfg['payload_label']} record",
            },
            "context": {
                "action_boundary": packet["action_boundary"],
                "anomaly_observed": packet["tempting_wrong_move"],
                "explanation_summary": (
                    f"Verify whether the frozen {cfg['payload_label']} source records close the exact action "
                    "boundary before execution."
                ),
                "internal_documents": internal_documents,
                "policy_documents": policy_documents,
            },
        }

    def render_preflight_md(preflight: dict[str, Any]) -> str:
        expected = preflight["architecture_lock"]["expected_counts"]
        approval_statement = preflight.get("required_approval_statement") or ""
        command = (
            f"python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py --wave {wave} "
            f"--batch-number {batch_number} --run-live "
            "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET "
            f"--approval-statement {json.dumps(approval_statement)}"
        )
        lines = [
            f"# {cfg['title']} {suffix} Live Preflight",
            "",
            f"Status: `{preflight['status']}`",
            f"Batch: `{preflight['batch_id']}`",
            f"Freeze root: `{preflight['freeze_root_hash']}`",
            f"Root signature: `{preflight['root_signature']}`",
            "",
            "## Expected Calls",
            "",
        ]
        for key in ("pairs", "packets", "worker_calls", "gov_calls", "total_provider_calls", "solo_calls", "judge_calls"):
            lines.append(f"- `{key}`: `{expected[key]}`")
        lines.extend(["", "## Checks", "", "| Check | Value |", "| --- | --- |"])
        for key, value in preflight["checks"].items():
            lines.append(f"| `{key}` | `{value}` |")
        lines.extend(
            [
                "",
                "## Provider Approval Gate",
                "",
                f"Approval required: `{preflight.get('provider_approval_required')}`",
                f"Required statement SHA-256: `{preflight.get('required_approval_statement_sha256')}`",
                "",
                "Required approval statement:",
                "",
                f"`{preflight.get('required_approval_statement')}`",
                "",
                "## Next Step",
                "",
            ]
        )
        if preflight["status"] == "PASS":
            lines.append(f"Run `{command}` only when provider calls are explicitly approved.")
        else:
            lines.append(f"Do not run live. Blocked checks: `{preflight['blocked_reason']}`")
        return "\n".join(lines) + "\n"

    def render_live_summary_md(summary: dict[str, Any]) -> str:
        return original_render_live_summary_md(summary).replace("Wave 2 Holo Target Batch", cfg["title"])

    module.convert_payload = convert_payload
    module.render_preflight_md = render_preflight_md
    module.render_live_summary_md = render_live_summary_md


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=tuple(WAVE_CONFIG), required=True)
    parser.add_argument("--batch-number", type=int, default=1)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--approval-statement")
    parser.add_argument("--approval-packet-sha256")
    args = parser.parse_args()
    runner = load_wave2_runner()
    configure_runner(runner, args.wave, args.batch_number)
    if args.preflight:
        manifest = runner.validate_preflight()
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    if args.run_live:
        return runner.run_live(args.approval_statement, args.approval_packet_sha256)
    parser.error("choose --preflight or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
