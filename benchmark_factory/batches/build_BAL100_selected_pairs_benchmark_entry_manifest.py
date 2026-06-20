from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from holo_builder.freeze_manifest import compute_payload_hash, payload_visibility_errors


EXPECTED_FAMILIES = ("BEC-PAIR-009", "BEC-PAIR-010")
SCORECARD_PATH = Path("reports/BAL100_scorecard.json")
JUDGE_SUMMARY_PATH = Path("reports/BAL100_BATCH_001_selected_pairs_judge_summary.json")
DEFAULT_JSON_OUT = Path("reports/BAL100_selected_pairs_benchmark_entry_manifest.json")
DEFAULT_MD_OUT = Path("reports/BAL100_selected_pairs_benchmark_entry_manifest.md")
DEFAULT_LEADERBOARD_JSON_OUT = Path("reports/BAL100_leaderboard.json")
DEFAULT_LEADERBOARD_MD_OUT = Path("reports/BAL100_leaderboard.md")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def _scorecard_families(scorecard: dict[str, Any]) -> list[dict[str, Any]]:
    families = scorecard.get("proof_credit_ready_families", [])
    return [family for family in families if family.get("family_id") in EXPECTED_FAMILIES]


def _packet_entries_for_family(family: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"role": "ALLOW", **family["allow_packet"]},
        {"role": "ESCALATE", **family["escalate_packet"]},
    ]


def _judge_packet_by_id(judge_summary: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        packet["packet_id"]: packet
        for packet in judge_summary.get("packet_level_verdicts", [])
    }


def _validate_packet_artifact(
    *,
    family_id: str,
    packet_entry: dict[str, Any],
    judge_packet: dict[str, Any],
    failures: list[str],
) -> dict[str, Any]:
    packet_id = packet_entry["packet_id"]
    frozen_path = Path(packet_entry["frozen_packet_path"])
    trace_path = Path(packet_entry["trace_path"])
    expected_hash = packet_entry["payload_hash"]
    expected_hash8 = expected_hash[:8]

    _require(frozen_path.exists(), f"{packet_id}: missing frozen packet {frozen_path}", failures)
    _require(trace_path.exists(), f"{packet_id}: missing trace {trace_path}", failures)
    if not frozen_path.exists() or not trace_path.exists():
        return {
            "packet_id": packet_id,
            "family_id": family_id,
            "truth_class": packet_entry["truth_class"],
            "frozen_packet_path": str(frozen_path),
            "trace_path": str(trace_path),
            "payload_hash": expected_hash,
            "status": "missing_artifact",
        }

    packet = _load_json(frozen_path)
    trace = _load_json(trace_path)
    computed_hash = compute_payload_hash(packet)
    visibility_errors = payload_visibility_errors(packet)

    _require(packet.get("scenario_id") == packet_id, f"{packet_id}: frozen scenario_id mismatch", failures)
    _require(packet.get("scenario_status") == "frozen", f"{packet_id}: scenario_status is not frozen", failures)
    _require(packet.get("expected_verdict") == packet_entry["truth_class"], f"{packet_id}: expected_verdict mismatch", failures)
    _require(computed_hash == expected_hash, f"{packet_id}: computed payload hash mismatch", failures)
    _require(packet.get("_frozen", {}).get("hash") == expected_hash, f"{packet_id}: _frozen.hash mismatch", failures)
    _require(packet.get("_frozen", {}).get("hash8") == expected_hash8, f"{packet_id}: _frozen.hash8 mismatch", failures)
    _require(packet.get("_frozen", {}).get("approved_by") == "Taylor", f"{packet_id}: frozen approval is not Taylor", failures)
    _require(packet.get("_frozen", {}).get("static_lint_result") == "PASS", f"{packet_id}: static lint not PASS", failures)
    _require(packet.get("_frozen", {}).get("payload_visibility_result") == "PASS", f"{packet_id}: payload visibility not PASS", failures)
    _require(not visibility_errors, f"{packet_id}: payload visibility errors {visibility_errors}", failures)

    trace_packet = trace.get("packet", {})
    _require(trace.get("official_trace") is True, f"{packet_id}: trace official_trace is not true", failures)
    _require(trace.get("no_judge") is True, f"{packet_id}: trace no_judge is not true", failures)
    _require(trace.get("no_qa_attacker") is True, f"{packet_id}: trace no_qa_attacker is not true", failures)
    _require(trace.get("no_ablation_expansion") is True, f"{packet_id}: trace no_ablation_expansion is not true", failures)
    _require(trace.get("seed") == 447, f"{packet_id}: trace seed mismatch", failures)
    _require(trace_packet.get("scenario_id") == packet_id, f"{packet_id}: trace packet scenario_id mismatch", failures)
    _require(trace_packet.get("payload_hash") == expected_hash, f"{packet_id}: trace packet payload_hash mismatch", failures)
    _require(trace_packet.get("hash8") == expected_hash8, f"{packet_id}: trace packet hash8 mismatch", failures)
    _require(trace_packet.get("path") == str(frozen_path), f"{packet_id}: trace packet path mismatch", failures)
    _require(trace_packet.get("model_visible_keys") == ["action", "context"], f"{packet_id}: trace model_visible_keys mismatch", failures)

    _require(judge_packet.get("packet_id") == packet_id, f"{packet_id}: missing Judge packet entry", failures)
    _require(judge_packet.get("family_id") == family_id, f"{packet_id}: Judge family_id mismatch", failures)
    _require(judge_packet.get("truth_class") == packet_entry["truth_class"], f"{packet_id}: Judge truth_class mismatch", failures)
    _require(judge_packet.get("payload_hash") == expected_hash, f"{packet_id}: Judge payload_hash mismatch", failures)
    _require(judge_packet.get("trace_path") == str(trace_path), f"{packet_id}: Judge trace_path mismatch", failures)
    _require(judge_packet.get("frozen_packet_path") == str(frozen_path), f"{packet_id}: Judge frozen path mismatch", failures)
    _require(judge_packet.get("judge_verdict") == packet_entry["truth_class"], f"{packet_id}: Judge verdict mismatch", failures)
    _require(judge_packet.get("hologov_label") == "KNEW", f"{packet_id}: HoloGov label not KNEW", failures)
    _require(judge_packet.get("confidence") == "HIGH", f"{packet_id}: Judge confidence not HIGH", failures)

    return {
        "packet_id": packet_id,
        "family_id": family_id,
        "truth_class": packet_entry["truth_class"],
        "role": packet_entry["role"],
        "frozen_packet_path": str(frozen_path),
        "trace_path": str(trace_path),
        "payload_hash": expected_hash,
        "hash8": expected_hash8,
        "computed_hash_matches": computed_hash == expected_hash,
        "scenario_status": packet.get("scenario_status"),
        "official_trace": trace.get("official_trace"),
        "judge_verdict": judge_packet.get("judge_verdict"),
        "hologov_label": judge_packet.get("hologov_label"),
        "status": "validated",
    }


def build_manifest(scorecard_path: Path = SCORECARD_PATH, judge_summary_path: Path = JUDGE_SUMMARY_PATH) -> dict[str, Any]:
    failures: list[str] = []
    scorecard = _load_json(scorecard_path)
    judge_summary = _load_json(judge_summary_path)

    proof_ready = scorecard.get("proof_credit_ready", {})
    _require(scorecard.get("benchmark_credit_scope") == "selected_pairs_only", "scorecard scope is not selected_pairs_only", failures)
    _require(tuple(proof_ready.get("families", [])) == EXPECTED_FAMILIES, "scorecard proof_ready families mismatch", failures)
    _require(proof_ready.get("pair_families") == 2, "scorecard pair_families must be 2", failures)
    _require(proof_ready.get("packets") == 4, "scorecard packets must be 4", failures)
    _require(proof_ready.get("allow_packets") == 2, "scorecard allow_packets must be 2", failures)
    _require(proof_ready.get("escalate_packets") == 2, "scorecard escalate_packets must be 2", failures)

    _require(tuple(judge_summary.get("families_judged", [])) == EXPECTED_FAMILIES, "Judge families_judged mismatch", failures)
    _require(judge_summary.get("losses_requiring_autopsy") == [], "Judge losses_requiring_autopsy is not empty", failures)
    proof_reco = judge_summary.get("proof_credit_ready_recommendation", {})
    _require(proof_reco.get("selected_pairs_only") is True, "Judge recommendation not selected_pairs_only", failures)
    _require(proof_reco.get("full_batch") is False, "Judge recommendation advances full batch", failures)

    selected_families = _scorecard_families(scorecard)
    _require([family.get("family_id") for family in selected_families] == list(EXPECTED_FAMILIES), "selected scorecard family order mismatch", failures)
    judge_by_packet = _judge_packet_by_id(judge_summary)

    families = []
    packet_entries = []
    for family in selected_families:
        family_id = family["family_id"]
        _require(family.get("status") == "proof_credit_ready", f"{family_id}: status is not proof_credit_ready", failures)
        _require(family.get("judge_status") == "PASS", f"{family_id}: judge_status is not PASS", failures)
        _require(family.get("hologov_result") == "2/2 KNEW", f"{family_id}: hologov_result mismatch", failures)
        _require(family.get("active_model_result") == "6/6 KNEW", f"{family_id}: active_model_result mismatch", failures)
        _require(family.get("seam_id") == "BEC_CALLBACK_PROVENANCE", f"{family_id}: seam_id mismatch", failures)
        family_packets = []
        for packet_entry in _packet_entries_for_family(family):
            packet_manifest = _validate_packet_artifact(
                family_id=family_id,
                packet_entry=packet_entry,
                judge_packet=judge_by_packet.get(packet_entry["packet_id"], {}),
                failures=failures,
            )
            packet_entries.append(packet_manifest)
            family_packets.append(packet_manifest["packet_id"])
        families.append(
            {
                "family_id": family_id,
                "seam_id": family["seam_id"],
                "batch_id": family["batch_id"],
                "status": family["status"],
                "judge_status": family["judge_status"],
                "hologov_result": family["hologov_result"],
                "active_model_result": family["active_model_result"],
                "packet_ids": family_packets,
            }
        )

    manifest = {
        "manifest_id": "BAL100_selected_pairs_benchmark_entry_manifest",
        "created_at": _utc_now(),
        "status": "PASS" if not failures else "FAIL",
        "benchmark_credit_scope": "selected_pairs_only",
        "target_entry": {
            "pair_families": 2,
            "packets": 4,
            "allow_packets": 2,
            "escalate_packets": 2,
            "families": list(EXPECTED_FAMILIES),
        },
        "source_artifacts": {
            "scorecard": str(scorecard_path),
            "judge_summary": str(judge_summary_path),
        },
        "families": families,
        "packets": packet_entries,
        "validation": {
            "failures": failures,
            "failure_count": len(failures),
            "frozen_packets_checked": len(packet_entries),
            "traces_checked": len(packet_entries),
            "judge_packet_entries_checked": len(packet_entries),
            "payload_hashes_recomputed": len(packet_entries),
        },
        "non_actions": {
            "provider_calls": False,
            "new_traces": False,
            "judge_rerun": False,
            "qa": False,
            "ablation": False,
            "packet_edits": False,
            "frozen_artifact_edits": False,
            "scorecard_edits": False,
            "push": False,
        },
        "recommendation": (
            "Ready to use as the selected-pairs benchmark entry package."
            if not failures
            else "Do not use as benchmark entry until failures are resolved."
        ),
    }
    if failures:
        raise ValueError("Selected-pairs benchmark entry validation failed: " + "; ".join(failures))
    return manifest


def render_markdown(manifest: dict[str, Any]) -> str:
    packet_rows = "\n".join(
        "| {packet_id} | {truth_class} | `{hash8}` | `{frozen_packet_path}` | `{trace_path}` |".format(**packet)
        for packet in manifest["packets"]
    )
    family_rows = "\n".join(
        "| {family_id} | {seam_id} | {judge_status} | {hologov_result} | {active_model_result} |".format(**family)
        for family in manifest["families"]
    )
    return f"""# BAL100 Selected Pairs Benchmark Entry Manifest

Created: {manifest['created_at']}

Status: `{manifest['status']}`

Scope: selected BAL100 Batch 001 pairs only. This package does not advance the full batch.

## Counts

- Pair families: {manifest['target_entry']['pair_families']}
- Packets: {manifest['target_entry']['packets']}
- ALLOW packets: {manifest['target_entry']['allow_packets']}
- ESCALATE packets: {manifest['target_entry']['escalate_packets']}
- Families: `BEC-PAIR-009`, `BEC-PAIR-010`

## Families

| Family | Seam | Judge | HoloGov | Active Models |
| --- | --- | --- | --- | --- |
{family_rows}

## Packets

| Packet | Truth | Hash8 | Frozen Packet | Trace |
| --- | --- | --- | --- | --- |
{packet_rows}

## Validation

- Frozen packets checked: {manifest['validation']['frozen_packets_checked']}
- Traces checked: {manifest['validation']['traces_checked']}
- Judge packet entries checked: {manifest['validation']['judge_packet_entries_checked']}
- Payload hashes recomputed: {manifest['validation']['payload_hashes_recomputed']}
- Failure count: {manifest['validation']['failure_count']}

## Non-Actions

- Provider calls: false
- New traces: false
- Judge rerun: false
- QA: false
- Ablation: false
- Packet edits: false
- Frozen artifact edits: false
- Scorecard edits: false
- Push: false

Recommendation: `{manifest['recommendation']}`
"""


def build_leaderboard(manifest: dict[str, Any]) -> dict[str, Any]:
    entries = []
    for family in manifest["families"]:
        family_packets = [
            packet
            for packet in manifest["packets"]
            if packet["family_id"] == family["family_id"]
        ]
        entries.append(
            {
                "family_id": family["family_id"],
                "batch_id": family["batch_id"],
                "seam_id": family["seam_id"],
                "status": "leaderboard_ready",
                "benchmark_credit_status": family["status"],
                "judge_status": family["judge_status"],
                "hologov_result": family["hologov_result"],
                "active_model_result": family["active_model_result"],
                "packet_count": len(family_packets),
                "packets": [
                    {
                        "packet_id": packet["packet_id"],
                        "truth_class": packet["truth_class"],
                        "hologov_label": packet["hologov_label"],
                        "payload_hash": packet["payload_hash"],
                        "hash8": packet["hash8"],
                        "frozen_packet_path": packet["frozen_packet_path"],
                        "trace_path": packet["trace_path"],
                    }
                    for packet in family_packets
                ],
            }
        )

    return {
        "leaderboard_id": "BAL100_leaderboard",
        "created_at": manifest["created_at"],
        "status": manifest["status"],
        "leaderboard_scope": "BAL100 selected proof-credit pairs only",
        "leaderboard_kind": "proof_credit_packet_leaderboard",
        "benchmark_credit_scope": manifest["benchmark_credit_scope"],
        "counting_unit": "frozen_packet",
        "public_registry_delta": {
            "previous_frozen_packets": 11,
            "added_frozen_packets": manifest["target_entry"]["packets"],
            "current_frozen_packets": 15,
        },
        "bal100_counts": manifest["target_entry"],
        "ranking_basis": [
            "proof_credit_ready family status",
            "Judge PASS",
            "HoloGov KNEW labels",
            "active model KNEW labels",
            "recomputed payload hash match",
            "official trace present",
        ],
        "source_artifacts": {
            **manifest["source_artifacts"],
            "entry_manifest": str(DEFAULT_JSON_OUT),
        },
        "entries": entries,
        "non_credit_boundaries": [
            "Does not promote full BAL100 Batch 001.",
            "Does not count BEC-PAIR-003 through BEC-PAIR-008.",
            "Does not count BEC-PAIR-005.",
            "Does not count HBB-BEC-001 or HBB-BEC-002.",
        ],
        "non_actions": manifest["non_actions"],
    }


def render_leaderboard_markdown(leaderboard: dict[str, Any]) -> str:
    family_rows = []
    packet_rows = []
    for entry in leaderboard["entries"]:
        family_rows.append(
            "| {family_id} | {seam_id} | {packet_count} | {judge_status} | {hologov_result} | {active_model_result} | {status} |".format(**entry)
        )
        for packet in entry["packets"]:
            packet_rows.append(
                "| {packet_id} | {truth_class} | {hologov_label} | `{hash8}` | `{payload_hash}` |".format(**packet)
            )

    return f"""# BAL100 Leaderboard

Created: {leaderboard['created_at']}

Status: `{leaderboard['status']}`

Scope: BAL100 selected proof-credit pairs only. This is a proof-credit packet leaderboard, not a model-capability ranking.

## Public Registry Delta

| Field | Count |
| --- | ---: |
| Previous frozen packets | {leaderboard['public_registry_delta']['previous_frozen_packets']} |
| Added frozen packets | {leaderboard['public_registry_delta']['added_frozen_packets']} |
| Current frozen packets | {leaderboard['public_registry_delta']['current_frozen_packets']} |

## BAL100 Counts

| Field | Count |
| --- | ---: |
| Pair families | {leaderboard['bal100_counts']['pair_families']} |
| Packets | {leaderboard['bal100_counts']['packets']} |
| ALLOW packets | {leaderboard['bal100_counts']['allow_packets']} |
| ESCALATE packets | {leaderboard['bal100_counts']['escalate_packets']} |

## Leaderboard Entries

| Family | Seam | Packets | Judge | HoloGov | Active Models | Status |
| --- | --- | ---: | --- | --- | --- | --- |
{chr(10).join(family_rows)}

## Packet Rows

| Packet | Truth | HoloGov | Hash8 | Payload Hash |
| --- | --- | --- | --- | --- |
{chr(10).join(packet_rows)}

## Boundaries

- Does not promote full BAL100 Batch 001.
- Does not count `BEC-PAIR-003` through `BEC-PAIR-008`.
- Does not count `BEC-PAIR-005`.
- Does not count `HBB-BEC-001` or `HBB-BEC-002`.
- No provider calls, new traces, Judge rerun, QA, ablation, packet edits, frozen artifact edits, scorecard edits, or push occurred.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate BAL100 selected-pairs benchmark entry manifest.")
    parser.add_argument("--scorecard", type=Path, default=SCORECARD_PATH)
    parser.add_argument("--judge-summary", type=Path, default=JUDGE_SUMMARY_PATH)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    parser.add_argument("--leaderboard-json-out", type=Path, default=DEFAULT_LEADERBOARD_JSON_OUT)
    parser.add_argument("--leaderboard-md-out", type=Path, default=DEFAULT_LEADERBOARD_MD_OUT)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)

    manifest = build_manifest(scorecard_path=args.scorecard, judge_summary_path=args.judge_summary)
    leaderboard = build_leaderboard(manifest)
    if not args.check_only:
        _write_json(args.json_out, manifest)
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(render_markdown(manifest))
        _write_json(args.leaderboard_json_out, leaderboard)
        args.leaderboard_md_out.parent.mkdir(parents=True, exist_ok=True)
        args.leaderboard_md_out.write_text(render_leaderboard_markdown(leaderboard))
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
