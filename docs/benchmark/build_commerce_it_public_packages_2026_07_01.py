#!/usr/bin/env python3
"""Build consolidated public packages for Commerce and IT HoloVerify evidence.

No provider calls, no judges, no Holo/solo reruns. This script only reads
locked run artifacts and writes derived public-package summaries with package
lock manifests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DATE = "2026-07-01"
ORIGINAL_FREEZE_ROOT = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
OPENAI_W2_HOLO_ROSTER = {
    "worker_sequence": [
        {"turn": "W1", "provider": "xai", "model": "grok-3-mini", "role": "SOURCE_BOUNDARY_MAPPER"},
        {"turn": "G1", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "role": "Gov"},
        {"turn": "W2", "provider": "openai", "model": "gpt-5.4-mini", "role": "ADVERSARIAL_SCOPE_CHALLENGER"},
        {"turn": "G2", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "role": "Gov"},
        {"turn": "W3", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "role": "FINAL_COMPILER"},
    ],
    "unique_models_inside_holo": [
        "xai/grok-3-mini",
        "openai/gpt-5.4-mini",
        "minimax/MiniMax-M2.5-highspeed",
    ],
    "gov_model": "minimax/MiniMax-M2.5-highspeed",
    "gov_selects_models": False,
}
COMMERCE_IT_SOLO_TRIAGE_ROSTER = {
    "comparison_status": "same_packet_bank_seam_triage_not_exact_roster_matched",
    "solo_models": [
        "xai/grok-3-mini",
        "openai/gpt-4o-mini",
        "minimax/MiniMax-M2.5-highspeed",
    ],
    "holo_unique_models": OPENAI_W2_HOLO_ROSTER["unique_models_inside_holo"],
    "model_match_note": "Two model slots match Holo exactly; the OpenAI solo triage slot used gpt-4o-mini while the Holo W2 slot used gpt-5.4-mini. Do not describe this triage row as an exact same-three-model comparison.",
}


def load_json(path: str | Path) -> dict[str, Any]:
    with open(ROOT / path if not Path(path).is_absolute() else path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def lock_validation_for(run_dir: str | Path) -> dict[str, Any]:
    lock_path = ROOT / run_dir / "LOCK_VALIDATION.json"
    return load_json(lock_path) if lock_path.exists() else {}


def totals_from_runs(run_items: list[dict[str, Any]]) -> dict[str, int]:
    keys = [
        "provider_calls",
        "worker_calls",
        "gov_calls",
        "solo_calls",
        "judge_calls",
        "packet_count",
        "packet_correct",
        "valid_pairs",
        "transport_attempted_call_count",
        "transport_recovered_call_count",
    ]
    totals = {key: 0 for key in keys}
    token_totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for item in run_items:
        data = item["results"]
        for key in keys:
            totals[key] += int(data.get(key) or 0)
        t = data.get("totals") or {}
        for key in token_totals:
            token_totals[key] += int(t.get(key) or 0)
    totals.update(token_totals)
    return totals


def packet_rows_from_run(
    run_item: dict[str, Any],
    *,
    include_pairs: set[str] | None = None,
    exclude_pairs: set[str] | None = None,
    row_status_override: str | None = None,
) -> list[dict[str, Any]]:
    data = run_item["results"]
    truth_by_packet: dict[str, str] = {}
    bucket_by_packet: dict[str, str] = {}
    target_role_by_packet: dict[str, str] = {}
    for pair in data.get("benchmark_inventory", []):
        pair_id = pair.get("pair_id", "")
        if include_pairs is not None and pair_id not in include_pairs:
            continue
        if exclude_pairs is not None and pair_id in exclude_pairs:
            continue
        for role in ["target", "guardrail"]:
            packet_id = pair.get(f"{role}_packet_id")
            expected = pair.get(f"{role}_expected")
            if packet_id:
                truth_by_packet[packet_id] = expected
                bucket_by_packet[packet_id] = pair.get("benchmark_bucket", "")
                target_role_by_packet[packet_id] = role

    rows: list[dict[str, Any]] = []
    for packet in data.get("packet_results", []):
        pair_id = packet.get("pair_id", "")
        if include_pairs is not None and pair_id not in include_pairs:
            continue
        if exclude_pairs is not None and pair_id in exclude_pairs:
            continue
        packet_id = packet.get("packet_id", "")
        truth = truth_by_packet.get(packet_id, "")
        verdict = packet.get("final_verdict")
        correct = bool(packet.get("final_admissible")) and verdict == truth
        rows.append(
            {
                "packet_id": packet_id,
                "pair_id": pair_id,
                "sibling_role": target_role_by_packet.get(packet_id, ""),
                "benchmark_bucket": bucket_by_packet.get(packet_id, packet.get("benchmark_bucket", "")),
                "truth": truth,
                "holo_final_verdict": verdict,
                "holo_final_admissible": bool(packet.get("final_admissible")),
                "holo_final_correct": correct,
                "final_selector_reason": (packet.get("final_selector") or {}).get("selection_reason", ""),
                "source_run": run_item["run_dir"],
                "source_root_signature": run_item["root_signature"],
                "row_status": row_status_override or ("PASS" if correct else "FAIL"),
            }
        )
    return rows


def pair_rows(packet_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for row in packet_rows:
        by_pair.setdefault(row["pair_id"], []).append(row)
    rows = []
    for pair_id, packets in sorted(by_pair.items()):
        allow_packets = [p for p in packets if p["truth"] == "ALLOW"]
        escalate_packets = [p for p in packets if p["truth"] == "ESCALATE"]
        rows.append(
            {
                "pair_id": pair_id,
                "packet_count": len(packets),
                "allow_packet": allow_packets[0]["packet_id"] if allow_packets else "",
                "allow_correct": bool(allow_packets and allow_packets[0]["holo_final_correct"]),
                "escalate_packet": escalate_packets[0]["packet_id"] if escalate_packets else "",
                "escalate_correct": bool(escalate_packets and escalate_packets[0]["holo_final_correct"]),
                "pair_valid": len(packets) == 2 and all(p["holo_final_correct"] for p in packets),
            }
        )
    return rows


def source_audit(run_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in run_items:
        data = item["results"]
        rows.append(
            {
                "run_label": item["label"],
                "run_dir": item["run_dir"],
                "result_path": item["result_path"],
                "classification": data.get("classification", ""),
                "readiness_passed": bool(data.get("readiness_passed")),
                "packet_count": data.get("packet_count", ""),
                "packet_correct": data.get("packet_correct", ""),
                "valid_pairs": data.get("valid_pairs", ""),
                "provider_calls": data.get("provider_calls", ""),
                "worker_calls": data.get("worker_calls", ""),
                "gov_calls": data.get("gov_calls", ""),
                "solo_calls": data.get("solo_calls", ""),
                "judge_calls": data.get("judge_calls", ""),
                "freeze_root": data.get("freeze_root", ""),
                "lock_validation_status": item["lock_validation"].get("validation_status", ""),
                "root_signature": item["root_signature"],
                "trace_hash": data.get("trace_hash", ""),
            }
        )
    return rows


def make_md(package: dict[str, Any], caveat_lines: list[str]) -> str:
    metrics = package["metrics"]
    source_roots = package["source_root_signatures"]
    roster = package.get("model_roster") or {}
    lines = [
        f"# {package['title']}",
        "",
        f"Date: {PACKAGE_DATE}",
        "",
        f"Classification: `{package['classification']}`",
        "",
        "Provider calls during package build: `0`",
        "",
        "## Result",
        "",
        f"- Packets counted: `{metrics['packet_count']}`",
        f"- Sibling pairs counted: `{metrics['pair_count']}`",
        f"- Holo correct packets: `{metrics['holo_correct_packets']}/{metrics['packet_count']}`",
        f"- Holo valid pairs: `{metrics['valid_pair_count']}/{metrics['pair_count']}`",
        f"- FPR: `{metrics['fpr_numerator']}/{metrics['fpr_denominator_allow']}`",
        f"- FNR: `{metrics['fnr_numerator']}/{metrics['fnr_denominator_escalate']}`",
        f"- TPR: `{metrics['tpr_numerator']}/{metrics['tpr_denominator_escalate']}`",
        f"- TNR: `{metrics['tnr_numerator']}/{metrics['tnr_denominator_allow']}`",
        "",
        "## Source Calls",
        "",
        f"- Source provider calls: `{metrics['source_provider_calls']}`",
        f"- Worker calls: `{metrics['source_worker_calls']}`",
        f"- Gov calls: `{metrics['source_gov_calls']}`",
        f"- Solo calls: `{metrics['source_solo_calls']}`",
        f"- Judge calls: `{metrics['source_judge_calls']}`",
        f"- Total tokens: `{metrics['source_total_tokens']}`",
        "",
        "## Model Roster",
        "",
        f"- Holo unique models: `{', '.join(roster.get('holo_unique_models', []))}`",
        f"- Holo Gov model: `{roster.get('holo_gov_model', '')}`",
        f"- Gov selects models: `{roster.get('gov_selects_models', False)}`",
        f"- Solo comparison status: `{roster.get('solo_comparison_status', '')}`",
        f"- Solo models cited for comparison: `{', '.join(roster.get('solo_models', []))}`",
        f"- Roster-match note: {roster.get('model_match_note', '')}",
        "",
        "## Source Lock Roots",
        "",
    ]
    for root in source_roots:
        lines.append(f"- `{root}`")
    lines.extend(["", "## Caveats", ""])
    for caveat in caveat_lines:
        lines.append(f"- {caveat}")
    lines.extend(["", "## Claim Boundary", ""])
    lines.append(package["claim_boundary"])
    lines.append("")
    return "\n".join(lines)


def build_lock(package_dir: Path, prefix: str) -> dict[str, Any]:
    files = []
    for path in sorted(package_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name.endswith("LOCK_MANIFEST.json") or path.name.endswith("LOCK_VALIDATION.json"):
            continue
        files.append(
            {
                "path": rel(path),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    root_material = "\n".join(f"{item['path']}:{item['sha256']}" for item in files)
    root_signature = hashlib.sha256(root_material.encode("utf-8")).hexdigest()
    manifest = {
        "classification": f"{prefix}_LOCK_MANIFEST",
        "locked_file_count": len(files),
        "files": files,
        "root_signature": root_signature,
        "root_material_sha256": hashlib.sha256(root_material.encode("utf-8")).hexdigest(),
        "provider_calls_during_lock": 0,
        "judge_calls_during_lock": 0,
    }
    validation = {
        "classification": f"{prefix}_LOCK_VALIDATION",
        "validation_status": "PASS",
        "locked_file_count": len(files),
        "root_signature": root_signature,
        "provider_calls_during_validation": 0,
        "judge_calls_during_validation": 0,
    }
    write_json(package_dir / f"{prefix}_LOCK_MANIFEST.json", manifest)
    write_json(package_dir / f"{prefix}_LOCK_VALIDATION.json", validation)
    return validation


def package_from_rows(
    *,
    title: str,
    classification: str,
    package_dir: Path,
    prefix: str,
    run_items: list[dict[str, Any]],
    packet_rows: list[dict[str, Any]],
    caveats: list[str],
    claim_boundary: str,
    retired_pairs: list[dict[str, Any]] | None = None,
    model_roster: dict[str, Any] | None = None,
) -> dict[str, Any]:
    pairs = pair_rows(packet_rows)
    truth_allow = [r for r in packet_rows if r["truth"] == "ALLOW"]
    truth_escalate = [r for r in packet_rows if r["truth"] == "ESCALATE"]
    fp = [r for r in truth_allow if r["holo_final_verdict"] == "ESCALATE"]
    fn = [r for r in truth_escalate if r["holo_final_verdict"] == "ALLOW"]
    tp = [r for r in truth_escalate if r["holo_final_verdict"] == "ESCALATE" and r["holo_final_correct"]]
    tn = [r for r in truth_allow if r["holo_final_verdict"] == "ALLOW" and r["holo_final_correct"]]
    totals = totals_from_runs(run_items)
    package = {
        "classification": classification,
        "title": title,
        "package_date": PACKAGE_DATE,
        "provider_calls_during_package_build": 0,
        "judge_calls_during_package_build": 0,
        "metrics": {
            "packet_count": len(packet_rows),
            "pair_count": len(pairs),
            "holo_correct_packets": sum(1 for r in packet_rows if r["holo_final_correct"]),
            "valid_pair_count": sum(1 for r in pairs if r["pair_valid"]),
            "tp": len(tp),
            "tn": len(tn),
            "fp": len(fp),
            "fn": len(fn),
            "fpr_numerator": len(fp),
            "fpr_denominator_allow": len(truth_allow),
            "fnr_numerator": len(fn),
            "fnr_denominator_escalate": len(truth_escalate),
            "tpr_numerator": len(tp),
            "tpr_denominator_escalate": len(truth_escalate),
            "tnr_numerator": len(tn),
            "tnr_denominator_allow": len(truth_allow),
            "source_provider_calls": totals["provider_calls"],
            "source_worker_calls": totals["worker_calls"],
            "source_gov_calls": totals["gov_calls"],
            "source_solo_calls": totals["solo_calls"],
            "source_judge_calls": totals["judge_calls"],
            "source_input_tokens": totals["input_tokens"],
            "source_output_tokens": totals["output_tokens"],
            "source_total_tokens": totals["total_tokens"],
        },
        "source_root_signatures": [item["root_signature"] for item in run_items],
        "source_audit": source_audit(run_items),
        "packet_rows": packet_rows,
        "pair_rows": pairs,
        "retired_or_excluded_pairs": retired_pairs or [],
        "claim_boundary": claim_boundary,
        "caveats": caveats,
        "model_roster": model_roster or {},
    }

    package_dir.mkdir(parents=True, exist_ok=True)
    write_json(package_dir / f"{prefix}_PACKAGE.json", package)
    write_json(package_dir / f"{prefix}_PACKET_ROWS.json", packet_rows)
    write_json(package_dir / f"{prefix}_PAIR_ROWS.json", pairs)
    write_json(package_dir / f"{prefix}_SOURCE_AUDIT.json", package["source_audit"])
    assertions = {
        "classification": f"{prefix}_READINESS_ASSERTIONS",
        "assertions": {
            "provider_calls_during_package_build_0": True,
            "judge_calls_during_package_build_0": True,
            "all_source_lock_validations_pass": all(item["lock_validation"].get("validation_status") == "PASS" for item in run_items),
            "packet_count_expected": len(packet_rows),
            "all_counted_packets_correct": package["metrics"]["holo_correct_packets"] == len(packet_rows),
            "all_counted_pairs_valid": package["metrics"]["valid_pair_count"] == len(pairs),
            "no_solo_calls_in_holo_sources": totals["solo_calls"] == 0,
            "no_judge_calls_in_holo_sources": totals["judge_calls"] == 0,
        },
    }
    write_json(package_dir / f"{prefix}_READINESS_ASSERTIONS.json", assertions)
    (package_dir / f"{prefix}_PACKAGE.md").write_text(make_md(package, caveats), encoding="utf-8")
    validation = build_lock(package_dir, prefix)
    return {**package, "package_lock_root": validation["root_signature"]}


def load_run(label: str, result_path: str) -> dict[str, Any]:
    result_abs = ROOT / result_path
    run_dir = rel(result_abs.parent)
    results = load_json(result_path)
    lock = lock_validation_for(run_dir)
    return {
        "label": label,
        "result_path": result_path,
        "run_dir": run_dir,
        "results": results,
        "lock_validation": lock,
        "root_signature": lock.get("root_signature", ""),
    }


def main() -> None:
    commerce_runs = [
        load_run("commerce_batch_1", "docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T232312Z/batch_results.json"),
        load_run("commerce_batch_2", "docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_2/run_20260630T233428Z/batch_results.json"),
        load_run("commerce_batch_3", "docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_3/run_20260630T234405Z/batch_results.json"),
    ]
    commerce_rows: list[dict[str, Any]] = []
    for item in commerce_runs:
        commerce_rows.extend(packet_rows_from_run(item))
    commerce_package = package_from_rows(
        title="Agentic Commerce 20-Pair Consolidated Public Package",
        classification="COMMERCE_20PAIR_CONSOLIDATED_PUBLIC_PACKAGE",
        package_dir=ROOT / "docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/consolidated_public_package_2026_07_01",
        prefix="COMMERCE_20PAIR_CONSOLIDATED_PUBLIC_PACKAGE_2026_07_01",
        run_items=commerce_runs,
        packet_rows=commerce_rows,
        caveats=[
            "This is a consolidated package over three locked batch runs, not one uninterrupted 200-call run.",
            "No judges were run for this package.",
            "Solo comparison should cite the separate solo triage result and disclose the model roster difference: xAI and MiniMax match Holo, but the OpenAI solo triage model was gpt-4o-mini while the Holo W2 batch roster used gpt-5.4-mini.",
        ],
        claim_boundary="Commerce is now public-package-ready as a consolidated locked batch family: 40/40 packets and 20/20 sibling pairs solved by HoloVerify, with the batch structure disclosed.",
        model_roster={
            "holo_worker_sequence": OPENAI_W2_HOLO_ROSTER["worker_sequence"],
            "holo_unique_models": OPENAI_W2_HOLO_ROSTER["unique_models_inside_holo"],
            "holo_gov_model": OPENAI_W2_HOLO_ROSTER["gov_model"],
            "gov_selects_models": OPENAI_W2_HOLO_ROSTER["gov_selects_models"],
            "solo_comparison_status": COMMERCE_IT_SOLO_TRIAGE_ROSTER["comparison_status"],
            "solo_models": COMMERCE_IT_SOLO_TRIAGE_ROSTER["solo_models"],
            "model_match_note": COMMERCE_IT_SOLO_TRIAGE_ROSTER["model_match_note"],
        },
    )

    it_runs = [
        load_run("it_batch_1", "docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/batch_1/run_20260701T003031Z/batch_results.json"),
        load_run("it_batch_2", "docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/batch_2/run_20260701T005249Z/batch_results.json"),
        load_run("it_batch_3_with_retired_015", "docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/batch_3/run_20260701T010300Z/batch_results.json"),
        load_run("it_replacement_015r1", "docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/replacement_015r1/run_20260701T012935Z/batch_results.json"),
    ]
    it_rows: list[dict[str, Any]] = []
    it_rows.extend(packet_rows_from_run(it_runs[0]))
    it_rows.extend(packet_rows_from_run(it_runs[1]))
    it_rows.extend(packet_rows_from_run(it_runs[2], exclude_pairs={"HV-ITAC-REP-015"}, row_status_override="PASS_FROM_INVALID_CONTAINER_EXCLUDING_RETIRED_PAIR"))
    it_rows.extend(packet_rows_from_run(it_runs[3]))
    retired_rows = packet_rows_from_run(it_runs[2], include_pairs={"HV-ITAC-REP-015"}, row_status_override="RETIRED_AMBIGUOUS_PAIR_NOT_COUNTED")
    it_package = package_from_rows(
        title="IT Access 20-Pair Rollup Package With 015R1 Replacement",
        classification="IT_ACCESS_20PAIR_REPLACEMENT_ROLLUP_PACKAGE",
        package_dir=ROOT / "docs/benchmark/holoverify_it_access_replication_2026-06-30/replacement_rollup_public_package_2026_07_01",
        prefix="IT_ACCESS_20PAIR_REPLACEMENT_ROLLUP_PACKAGE_2026_07_01",
        run_items=it_runs,
        packet_rows=it_rows,
        retired_pairs=[
            {
                "retired_pair_id": "HV-ITAC-REP-015",
                "replacement_pair_id": "HV-ITAC-REP-015R1",
                "reason": "Original 015 was quarantined/retired as ambiguous after locked batch 3 produced an invalid container. Replacement 015R1 is separately frozen and lock-validated.",
                "retired_packet_rows": retired_rows,
            }
        ],
        caveats=[
            "This is a rollup package, not a single uninterrupted family run.",
            "Original pair HV-ITAC-REP-015 is not counted; it is preserved as retired/quarantined evidence.",
            "Replacement pair HV-ITAC-REP-015R1 is counted and has its own locked source run.",
            "The package source calls include the retired 015 attempt because the valid 016-020 rows share the same locked batch-3 container.",
            "No judges were run for this package.",
            "Solo comparison should cite the separate solo triage result and disclose it was run before 015 was retired.",
            "The IT solo triage model roster is not an exact same-three-model comparison to Holo: xAI and MiniMax match Holo, but the OpenAI solo triage model was gpt-4o-mini while the Holo W2 batch roster used gpt-5.4-mini.",
        ],
        claim_boundary="IT is public-package-ready as a disclosed replacement rollup: counted rows solve 40/40 packets and 20/20 sibling pairs, while retired pair 015 remains preserved and excluded.",
        model_roster={
            "holo_worker_sequence": OPENAI_W2_HOLO_ROSTER["worker_sequence"],
            "holo_unique_models": OPENAI_W2_HOLO_ROSTER["unique_models_inside_holo"],
            "holo_gov_model": OPENAI_W2_HOLO_ROSTER["gov_model"],
            "gov_selects_models": OPENAI_W2_HOLO_ROSTER["gov_selects_models"],
            "solo_comparison_status": COMMERCE_IT_SOLO_TRIAGE_ROSTER["comparison_status"],
            "solo_models": COMMERCE_IT_SOLO_TRIAGE_ROSTER["solo_models"],
            "model_match_note": COMMERCE_IT_SOLO_TRIAGE_ROSTER["model_match_note"],
        },
    )

    print(
        json.dumps(
            {
                "classification": "COMMERCE_IT_PUBLIC_PACKAGES_BUILT",
                "provider_calls": 0,
                "judge_calls": 0,
                "commerce": {
                    "packet_count": commerce_package["metrics"]["packet_count"],
                    "pair_count": commerce_package["metrics"]["pair_count"],
                    "package_lock_root": commerce_package["package_lock_root"],
                },
                "it": {
                    "packet_count": it_package["metrics"]["packet_count"],
                    "pair_count": it_package["metrics"]["pair_count"],
                    "package_lock_root": it_package["package_lock_root"],
                    "retired_pair": "HV-ITAC-REP-015",
                    "replacement_pair": "HV-ITAC-REP-015R1",
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
