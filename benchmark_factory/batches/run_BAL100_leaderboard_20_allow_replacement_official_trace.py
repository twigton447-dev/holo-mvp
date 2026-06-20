from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmark_factory.batches import build_BAL100_leaderboard_20_allow_replacement_official_trace_preflight as preflight
from benchmark_factory.batches import run_BAL100_leaderboard_20_allow_official_trace as base_runner
from holo_builder.frozen_4dna_runner import FORBIDDEN_MODEL_VISIBLE_KEYS


def _replacement_packet_trace_record(
    packet: dict[str, Any],
    roster: dict[str, Any],
    active_records: list[dict[str, Any]],
    gov_record: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    return {
        "record_type": "bal100_allow_replacement_official_trace",
        "run_id": preflight.RUN_ID,
        "run_type": preflight.RUN_TYPE,
        "official_trace": True,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "scorecard_movement": False,
        "leaderboard_movement": False,
        "session_id": packet["session_id"],
        "seed": preflight.SEED,
        "git_head": base_runner._git_head(),
        "created_at": base_runner._utc_now(),
        "packet": {
            "scenario_id": packet["scenario_id"],
            "family_id": packet["family_id"],
            "path": packet["path"],
            "payload_hash": packet["payload_hash"],
            "hash8": packet["hash8"],
            "model_visible_keys": packet["model_visible_keys"],
            "frozen_approved_by": packet["frozen_approved_by"],
        },
        "roster": {
            "holo_gov": roster["holo_gov"],
            "active_non_gov": roster["active_non_gov"],
            "excluded": roster["excluded"],
            "selection_rule": roster["selection_rule"],
        },
        "calls": {
            "active_non_gov": active_records,
            "holo_gov": gov_record,
        },
        "hidden_metadata_excluded": sorted(FORBIDDEN_MODEL_VISIBLE_KEYS),
        "output_directory": str(out_dir),
        "proof_credit_remains_unchanged": True,
    }


def _replacement_summarize(
    records: list[dict[str, Any]],
    trace_paths: list[str],
    *,
    execution_mode: str,
    operator: str,
    out_dir: Path,
) -> dict[str, Any]:
    error_records = [record for record in records if not record.get("provider_call_ok") or not record.get("parse_ok")]
    verdicts_by_packet: dict[str, dict[str, str]] = {}
    for record in records:
        verdicts_by_packet.setdefault(record["packet_id"], {})[
            f"{record['role']}:{record['provider']}:{record['model']}"
        ] = record.get("verdict", "ERROR")
    return {
        "run_id": preflight.RUN_ID,
        "run_type": preflight.RUN_TYPE,
        "run_status": "complete" if not error_records else "complete_with_errors",
        "official_trace": True,
        "judge": False,
        "qa_or_ablation": False,
        "freeze": False,
        "benchmark_credit": False,
        "scorecard_movement": False,
        "leaderboard_movement": False,
        "execution_mode": execution_mode,
        "operator": operator,
        "out_dir": str(out_dir),
        "packet_count": 3,
        "expected_row_count": 12,
        "results": len(records),
        "error_results": len(error_records),
        "provider_error_counts": dict(Counter(record.get("provider", "unknown") for record in error_records)),
        "verdicts_by_packet": verdicts_by_packet,
        "official_trace_record_paths": trace_paths,
        "proof_credit_remains_unchanged": True,
        "created_at": base_runner._utc_now(),
    }


def _patch_base_runner() -> None:
    base_runner.RUN_ID = preflight.RUN_ID
    base_runner.RUN_TYPE = preflight.RUN_TYPE
    base_runner.SEED = preflight.SEED
    base_runner.DEFAULT_OUT_DIR = preflight.DEFAULT_OUT_DIR
    base_runner.APPROVAL_ENV = preflight.APPROVAL_ENV
    base_runner.APPROVAL_VALUE = preflight.APPROVAL_VALUE
    base_runner.CODEX_APPROVAL_ENV = preflight.CODEX_APPROVAL_ENV
    base_runner.CODEX_APPROVAL_VALUE = preflight.CODEX_APPROVAL_VALUE
    base_runner._active_prompt_card = preflight._active_prompt_card
    base_runner._gov_template_card = preflight._gov_template_card
    base_runner._load_packets = preflight._load_packets
    base_runner._roster = preflight._roster
    base_runner._safe_model_name = preflight._safe_model_name
    base_runner._transport_provider = preflight._transport_provider
    base_runner.build_preflight = preflight.build_preflight
    base_runner._packet_trace_record = _replacement_packet_trace_record
    base_runner._summarize = _replacement_summarize


def main(argv: list[str] | None = None) -> int:
    _patch_base_runner()

    parser = argparse.ArgumentParser(description="Preflight or execute exact three-packet BAL100 replacement ALLOW official trace run.")
    parser.add_argument("--execute-provider-calls", action="store_true")
    parser.add_argument("--operator", default="")
    parser.add_argument("--allow-codex-provider-calls", action="store_true")
    parser.add_argument("--i-am-taylor-local", action="store_true")
    parser.add_argument("--yes-send-frozen-payloads-to-providers", action="store_true")
    parser.add_argument("--out-dir", type=Path, default=preflight.DEFAULT_OUT_DIR)
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args(argv)

    if not args.execute_provider_calls:
        manifest = preflight.build_preflight(args.out_dir)
        print(
            "preflight status={status} packets={packets} prompt_cards={cards} expected_future_rows={rows}".format(
                status=manifest["status"],
                packets=manifest["packet_count"],
                cards=manifest["prompt_cards"]["total"],
                rows=manifest["expected_future_live_outputs"]["provider_rows"],
            )
        )
        return 0 if manifest["status"] == "PASS" else 1

    execution_mode = base_runner._require_execution_approval(args)
    summary = base_runner.execute_official_trace(args.timeout, args.out_dir, execution_mode=execution_mode, operator=args.operator)
    print(
        "official_trace status={status} rows={rows} errors={errors} out_dir={out_dir}".format(
            status=summary["run_status"],
            rows=summary["results"],
            errors=summary["error_results"],
            out_dir=summary["out_dir"],
        )
    )
    return 0 if summary["run_status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
