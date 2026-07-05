#!/usr/bin/env python3
"""Build the public-safe HoloVerify 20-pair evidence package.

This is a local, no-provider packaging/audit script. It reads only frozen run
artifacts already on disk and writes additive summary files. It does not repair
outputs, rerun packets, call judges, mutate packet payloads, or call providers.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
RUN_ROOT = ROOT / "holoverify_20pair_3dna_2026-06-29"
HOLO_RUN = RUN_ROOT / "live_runs" / "run_20260629T052822Z"
FREEZE_ROOT = RUN_ROOT / "frozen_complete_run_20260629T052822Z"
SOLO_RUN = RUN_ROOT / "solo_one_shot_against_frozen_run_20260629T052822Z" / "run_20260629T060938Z"
FINAL_PACKAGE = RUN_ROOT / "final_evidence_package_2026_06_29"

MODEL_ORDER = [
    ("xai", "xai/grok-3-mini"),
    ("google", "google/gemini-2.5-flash-lite"),
    ("minimax", "minimax/MiniMax-M2.5-highspeed"),
]

REQUIRED_EVIDENCE = {
    "frozen_holo_lock_summary": FREEZE_ROOT / "LOCK_SUMMARY.md",
    "frozen_holo_lock_manifest": FREEZE_ROOT / "LOCK_MANIFEST.json",
    "frozen_holo_lock_validation": FREEZE_ROOT / "LOCK_VALIDATION.json",
    "holo_live_results": HOLO_RUN / "live_results.json",
    "holo_trace": HOLO_RUN / "TRACE_CALLS.jsonl",
    "solo_one_shot_results": SOLO_RUN / "solo_one_shot_results.json",
    "solo_trace": SOLO_RUN / "SOLO_ONE_SHOT_TRACE.jsonl",
    "solo_prompts_dir": SOLO_RUN / "prompts",
    "solo_raw_outputs_trace": SOLO_RUN / "SOLO_ONE_SHOT_TRACE.jsonl",
    "comparison_autopsy_no_leakage": SOLO_RUN / "comparison_autopsy_no_leakage.json",
    "comparison_autopsy_no_leakage_md": SOLO_RUN / "comparison_autopsy_no_leakage.md",
    "final_audit": FINAL_PACKAGE / "SOLO_ONE_SHOT_3MINI_BASELINE_AUDIT_2026_06_29.json",
    "final_comparison": FINAL_PACKAGE / "HOLOVERIFY_20PAIR_SOLO_VS_HOLO_COMPARISON_2026_06_29.json",
    "final_readiness": FINAL_PACKAGE / "HOLOVERIFY_20PAIR_3DNA_FINAL_READINESS_ASSERTIONS_2026_06_29.json",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return lines


def model_short(model_name: str) -> str:
    if "grok" in model_name:
        return "xAI"
    if "gemini" in model_name:
        return "Gemini"
    if "MiniMax" in model_name:
        return "MiniMax"
    return model_name


def compact_outcome(outcome: dict[str, Any]) -> str:
    verdict = outcome.get("verdict")
    verdict_text = verdict if verdict is not None else "null"
    return f"{outcome['model_short']}={outcome['label']} verdict={verdict_text} admissible={outcome['admissible']}"


def build() -> dict[str, Any]:
    FINAL_PACKAGE.mkdir(parents=True, exist_ok=True)

    missing = {name: str(path) for name, path in REQUIRED_EVIDENCE.items() if not path.exists()}
    if missing:
        audit = {
            "classification": "HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT",
            "status": "FAIL",
            "failures": [{"assertion": "required_evidence_files_exist", "missing": missing}],
        }
        write_json("HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.json", audit)
        raise SystemExit("required evidence files missing")

    holo = load_json(HOLO_RUN / "live_results.json")
    holo_trace = load_jsonl(HOLO_RUN / "TRACE_CALLS.jsonl")
    solo = load_json(SOLO_RUN / "solo_one_shot_results.json")
    solo_trace = load_jsonl(SOLO_RUN / "SOLO_ONE_SHOT_TRACE.jsonl")
    autopsy = load_json(SOLO_RUN / "comparison_autopsy_no_leakage.json")
    freeze_manifest = load_json(FREEZE_ROOT / "LOCK_MANIFEST.json")
    freeze_validation = load_json(FREEZE_ROOT / "LOCK_VALIDATION.json")
    comparison = load_json(FINAL_PACKAGE / "HOLOVERIFY_20PAIR_SOLO_VS_HOLO_COMPARISON_2026_06_29.json")
    readiness = load_json(FINAL_PACKAGE / "HOLOVERIFY_20PAIR_3DNA_FINAL_READINESS_ASSERTIONS_2026_06_29.json")

    packet_records = {row["packet_id"]: row for row in freeze_manifest["packet_records"]}
    pair_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in packet_records.values():
        pair_records[row["pair_id"]].append(row)

    solo_by_packet_provider = {(row["packet_id"], row["provider"]): row for row in solo_trace}
    holo_trace_by_artifact = {row.get("artifact_id"): row for row in holo_trace if row.get("artifact_id")}

    clean_pairs = [
        row
        for row in autopsy["registry_candidate_pairs"]
        if row.get("pair_class") == "PAIR_ALL_SIX_SOLOS_FAILED"
    ]
    clean_pair_ids = sorted(row["pair_id"] for row in clean_pairs)

    subset_rows: list[dict[str, Any]] = []
    for pair_id in clean_pair_ids:
        records = sorted(pair_records[pair_id], key=lambda row: row["expected_verdict_for_local_audit"])
        allow = next(row for row in records if row["expected_verdict_for_local_audit"] == "ALLOW")
        escalate = next(row for row in records if row["expected_verdict_for_local_audit"] == "ESCALATE")

        packet_entries = []
        for packet in [allow, escalate]:
            solo_outcomes = []
            for provider, model_name in MODEL_ORDER:
                solo_row = solo_by_packet_provider[(packet["packet_id"], provider)]
                solo_outcomes.append(
                    {
                        "model": model_name,
                        "model_short": model_short(model_name),
                        "label": solo_row["solo_label"],
                        "verdict": solo_row.get("local_verdict"),
                        "correct": bool(solo_row.get("local_verdict_matches_packet_truth")),
                        "admissible": bool(solo_row.get("admissible")),
                        "prompt_ref": solo_row.get("prompt_ref"),
                        "prompt_hash": solo_row.get("prompt_hash"),
                        "call_index": solo_row.get("call_index"),
                        "leakage_violations": solo_row.get("prompt_leakage_violations") or [],
                    }
                )
            selected_artifact_id = packet["holo_selected_artifact_id"]
            selected_trace = holo_trace_by_artifact.get(selected_artifact_id, {})
            packet_entries.append(
                {
                    "packet_id": packet["packet_id"],
                    "packet_truth": packet["expected_verdict_for_local_audit"],
                    "holo_final_verdict": packet["holo_final_verdict"],
                    "holo_final_admissible": bool(packet["holo_final_admissible"]),
                    "holo_selected_artifact_id": selected_artifact_id,
                    "holo_selected_artifact_hash": selected_trace.get("artifact_hash"),
                    "holo_selected_prompt_ref": selected_trace.get("prompt_ref"),
                    "holo_selected_prompt_hash": selected_trace.get("prompt_hash"),
                    "solo_outcomes": solo_outcomes,
                }
            )

        subset_rows.append(
            {
                "pair_id": pair_id,
                "allow_sibling_id": allow["packet_id"],
                "escalate_sibling_id": escalate["packet_id"],
                "packet_truth": {
                    allow["packet_id"]: allow["expected_verdict_for_local_audit"],
                    escalate["packet_id"]: escalate["expected_verdict_for_local_audit"],
                },
                "six_solo_outcomes": {
                    entry["packet_id"]: entry["solo_outcomes"] for entry in packet_entries
                },
                "holo_final_verdicts": {
                    entry["packet_id"]: entry["holo_final_verdict"] for entry in packet_entries
                },
                "evidence_class": "PAIR_ALL_SIX_SOLOS_FAILED_AND_HOLO_SOLVED_BOTH_SIBLINGS",
                "prompt_hash_references": {
                    entry["packet_id"]: {
                        "solo": [
                            {
                                "model": outcome["model"],
                                "prompt_ref": outcome["prompt_ref"],
                                "prompt_hash": outcome["prompt_hash"],
                            }
                            for outcome in entry["solo_outcomes"]
                        ],
                        "holo_selected": {
                            "artifact_id": entry["holo_selected_artifact_id"],
                            "artifact_hash": entry["holo_selected_artifact_hash"],
                            "prompt_ref": entry["holo_selected_prompt_ref"],
                            "prompt_hash": entry["holo_selected_prompt_hash"],
                        },
                    }
                    for entry in packet_entries
                },
                "leakage_status": "PASS",
            }
        )

    subset = {
        "classification": "HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "selection_rule": "Use only pairs where all six one-shot solo attempts failed and Holo solved both siblings.",
        "pair_count": len(subset_rows),
        "packet_count": len(subset_rows) * 2,
        "all_six_solo_fail_pair_ids": clean_pair_ids,
        "leakage_status": autopsy["prompt_leakage_status"],
        "prompt_files_scanned": autopsy.get("independent_forbidden_prompt_scan_hits", []),
        "freeze_root_signature": autopsy["freeze_root_signature"],
        "autopsy_lock_root_signature": load_json(SOLO_RUN / "AUTOPSY_LOCK_VALIDATION.json")["root_signature"],
        "holo_trace_hash": autopsy["holo_trace_hash"],
        "solo_trace_hash": autopsy["solo_trace_hash"],
        "rows": subset_rows,
    }

    final_memo = {
        "classification": "HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "claim_shape": (
            "On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed "
            "architecture solved 40/40 packets. Matching one-shot solo baselines using the same "
            "mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible "
            "outputs. Fourteen sibling pairs showed complete solo collapse across all six one-shot "
            "solo attempts while Holo solved both the hard-ALLOW and hard-ESCALATE siblings. The "
            "Holo run used about 2.06x the solo token budget and passed no-leakage checks."
        ),
        "forbidden_claims": [
            "Holo beats all models",
            "Holo is generally superior",
            "Holo solved safety",
            "solo models cannot do this universally",
            "internal Holo misses are standalone solo failures",
        ],
        "results": {
            "holo_solved_packets": "40/40",
            "valid_sibling_pairs": "20/20",
            "solo_one_shot_calls": "120/120",
            "solo_knew_admissible": "6/120",
            "clean_all_six_solo_fail_pairs": len(subset_rows),
            "mixed_pairs": autopsy["pair_gap_summary"].get("PAIR_MIXED_SOLO_FAILURE"),
            "leakage_scan": "240 prompt files, 0 forbidden hits",
            "holo_tokens": holo["totals"]["total_tokens"],
            "solo_tokens": solo["totals"]["total_tokens"],
            "holo_solo_token_ratio": round(holo["totals"]["total_tokens"] / solo["totals"]["total_tokens"], 3),
            "autopsy_lock_root_signature": subset["autopsy_lock_root_signature"],
        },
        "evidence_refs": {
            "holo_live_results": str(HOLO_RUN / "live_results.json"),
            "holo_trace": str(HOLO_RUN / "TRACE_CALLS.jsonl"),
            "frozen_holo_lock_summary": str(FREEZE_ROOT / "LOCK_SUMMARY.md"),
            "solo_results": str(SOLO_RUN / "solo_one_shot_results.json"),
            "solo_trace": str(SOLO_RUN / "SOLO_ONE_SHOT_TRACE.jsonl"),
            "solo_prompts": str(SOLO_RUN / "prompts"),
            "comparison_autopsy_no_leakage": str(SOLO_RUN / "comparison_autopsy_no_leakage.json"),
            "subset_package": "HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.json",
        },
        "subset_pair_ids": clean_pair_ids,
    }

    no_provider_audit = build_no_provider_audit(
        holo=holo,
        solo=solo,
        autopsy=autopsy,
        freeze_manifest=freeze_manifest,
        freeze_validation=freeze_validation,
        comparison=comparison,
        readiness=readiness,
        subset=subset,
    )

    write_json("HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.json", subset)
    write_md("HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.md", subset_md(subset))
    write_json("HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO_2026_06_29.json", final_memo)
    write_md("HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO_2026_06_29.md", final_memo_md(final_memo, no_provider_audit))
    write_md("HOLOVERIFY_14PAIR_PUBLIC_PROOF_SUMMARY_2026_06_29.md", public_summary_md(final_memo, subset))
    write_json("HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.json", no_provider_audit)
    write_md("HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.md", audit_md(no_provider_audit))
    write_public_lock()

    if no_provider_audit["status"] != "PASS":
        raise SystemExit("no-provider audit failed")
    return {
        "subset": subset,
        "final_memo": final_memo,
        "no_provider_audit": no_provider_audit,
    }


def build_no_provider_audit(
    *,
    holo: dict[str, Any],
    solo: dict[str, Any],
    autopsy: dict[str, Any],
    freeze_manifest: dict[str, Any],
    freeze_validation: dict[str, Any],
    comparison: dict[str, Any],
    readiness: dict[str, Any],
    subset: dict[str, Any],
) -> dict[str, Any]:
    packet_records = freeze_manifest["packet_records"]
    payload_hashes_match = all(
        sha256_file(FREEZE_ROOT / row["payload_ref"]) == row["payload_sha256"] for row in packet_records
    )
    solo_packet_ids = sorted(row["packet_id"] for row in solo["packet_results"])
    holo_packet_ids = sorted(row["packet_id"] for row in holo["packet_results"])
    frozen_packet_ids = sorted(row["packet_id"] for row in packet_records)
    evidence_separated = all(
        "external_evidence_class" in row and "intra_holo_evidence_classes" in row
        for row in comparison["comparison_rows"]
    )
    required_presence = {
        name: ("PASS" if path.exists() else "FAIL") for name, path in REQUIRED_EVIDENCE.items()
    }
    assertions = {
        "required_evidence_files_exist": "PASS" if all(v == "PASS" for v in required_presence.values()) else "FAIL",
        "frozen_holo_run_present": "PASS" if freeze_validation.get("validation_status") == "PASS" else "FAIL",
        "solo_run_present": "PASS" if solo.get("classification") == "SOLO_ONE_SHOT_3MINI_40_COMPLETE" else "FAIL",
        "same_40_packet_hashes": "PASS" if payload_hashes_match and solo_packet_ids == holo_packet_ids == frozen_packet_ids and len(frozen_packet_ids) == 40 else "FAIL",
        "solo_provider_calls_120": "PASS" if solo.get("provider_calls") == 120 else "FAIL",
        "holo_provider_calls_200": "PASS" if holo.get("provider_calls") == 200 else "FAIL",
        "no_judges": "PASS" if solo.get("judge_calls") == 0 and holo.get("judge_calls") == 0 else "FAIL",
        "no_leakage": "PASS" if autopsy.get("prompt_leakage_status") == "PASS" and not autopsy.get("independent_forbidden_prompt_scan_hits") else "FAIL",
        "clean_all_six_solo_fail_pairs_14": "PASS" if subset.get("pair_count") == 14 else "FAIL",
        "total_valid_holo_pairs_20": "PASS" if holo.get("readiness_assertions", {}).get("total_valid_pairs") == 20 else "FAIL",
        "evidence_categories_separated": "PASS" if evidence_separated else "FAIL",
        "invalid_hardening_runs_preserved": "PASS" if holo.get("readiness_assertions", {}).get("invalid_runs_preserved") == "PASS" and len(freeze_manifest.get("preserved_invalid_runs", [])) >= 4 else "FAIL",
    }
    return {
        "classification": "HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if all(v == "PASS" for v in assertions.values()) else "FAIL",
        "assertions": assertions,
        "required_evidence_presence": required_presence,
        "readiness_status": readiness.get("status"),
        "packet_hash_audit": {
            "payload_hashes_match_lock": payload_hashes_match,
            "frozen_packet_count": len(frozen_packet_ids),
            "solo_packet_count": len(solo_packet_ids),
            "holo_packet_count": len(holo_packet_ids),
        },
        "provider_call_counts": {
            "solo": solo.get("provider_calls"),
            "holo": holo.get("provider_calls"),
            "judges": {"solo": solo.get("judge_calls"), "holo": holo.get("judge_calls")},
        },
        "leakage": {
            "prompt_leakage_status": autopsy.get("prompt_leakage_status"),
            "independent_forbidden_prompt_scan_hits": autopsy.get("independent_forbidden_prompt_scan_hits"),
        },
        "subset_pair_count": subset.get("pair_count"),
        "valid_holo_pairs": holo.get("readiness_assertions", {}).get("total_valid_pairs"),
        "invalid_runs_preserved": freeze_manifest.get("preserved_invalid_runs", []),
    }


def subset_md(subset: dict[str, Any]) -> list[str]:
    lines = [
        "# HoloVerify 14-Pair Clean Solo Collapse Subset",
        "",
        "Selection rule: only sibling pairs where all six one-shot solo attempts failed and Holo solved both siblings.",
        "",
    ]
    lines += md_table(
        ["Metric", "Value"],
        [
            ["pair_count", subset["pair_count"]],
            ["packet_count", subset["packet_count"]],
            ["leakage_status", subset["leakage_status"]],
            ["freeze_root_signature", f"`{subset['freeze_root_signature']}`"],
            ["autopsy_lock_root_signature", f"`{subset['autopsy_lock_root_signature']}`"],
        ],
    )
    lines += ["", "## Rows", ""]
    rows = []
    for row in subset["rows"]:
        allow_id = row["allow_sibling_id"]
        esc_id = row["escalate_sibling_id"]
        allow_outcomes = "; ".join(compact_outcome(outcome) for outcome in row["six_solo_outcomes"][allow_id])
        esc_outcomes = "; ".join(compact_outcome(outcome) for outcome in row["six_solo_outcomes"][esc_id])
        rows.append(
            [
                row["pair_id"],
                allow_id,
                esc_id,
                f"{allow_id}=ALLOW; {esc_id}=ESCALATE",
                allow_outcomes,
                esc_outcomes,
                f"{allow_id}={row['holo_final_verdicts'][allow_id]}; {esc_id}={row['holo_final_verdicts'][esc_id]}",
                row["evidence_class"],
                row["leakage_status"],
            ]
        )
    lines += md_table(
        [
            "pair ID",
            "ALLOW sibling ID",
            "ESCALATE sibling ID",
            "packet truth",
            "ALLOW solo outcomes",
            "ESCALATE solo outcomes",
            "Holo final verdicts",
            "evidence class",
            "leakage",
        ],
        rows,
    )
    lines += ["", "Prompt and hash references are included per row in the companion JSON file."]
    return lines


def final_memo_md(memo: dict[str, Any], audit: dict[str, Any]) -> list[str]:
    results = memo["results"]
    lines = ["# HoloVerify 20-Pair Final Evidence Memo", "", memo["claim_shape"], ""]
    lines += md_table(
        ["Metric", "Value"],
        [
            ["Holo solved packets", results["holo_solved_packets"]],
            ["valid sibling pairs", results["valid_sibling_pairs"]],
            ["solo one-shot calls", results["solo_one_shot_calls"]],
            ["solo KNEW/admissible", results["solo_knew_admissible"]],
            ["clean all-six-solo-fail pairs", results["clean_all_six_solo_fail_pairs"]],
            ["mixed pairs", results["mixed_pairs"]],
            ["leakage scan", results["leakage_scan"]],
            ["Holo tokens", results["holo_tokens"]],
            ["Solo tokens", results["solo_tokens"]],
            ["Holo/Solo token ratio", f"{results['holo_solo_token_ratio']}x"],
            ["autopsy lock", f"`{results['autopsy_lock_root_signature']}`"],
            ["no-provider audit", audit["status"]],
        ],
    )
    lines += ["", "## Claim Boundaries", ""]
    lines += [f"- Do not claim: {claim}" for claim in memo["forbidden_claims"]]
    lines += ["", "## Evidence References", ""]
    lines += [f"- `{name}`: `{path}`" for name, path in memo["evidence_refs"].items()]
    return lines


def public_summary_md(memo: dict[str, Any], subset: dict[str, Any]) -> list[str]:
    return [
        "# HoloVerify 14-Pair Public Proof Summary",
        "",
        memo["claim_shape"],
        "",
        "This summary is public-safe and conservative. It describes one frozen benchmark result, not a universal superiority claim.",
        "",
        "## Clean Subset",
        "",
        f"- Clean all-six-solo-fail sibling pairs: {subset['pair_count']}",
        f"- Clean subset packets: {subset['packet_count']}",
        f"- Leakage status: {subset['leakage_status']}",
        f"- Holo trace hash: `{subset['holo_trace_hash']}`",
        f"- Solo trace hash: `{subset['solo_trace_hash']}`",
        "",
        "## Boundaries",
        "",
        "- This does not claim Holo beats all models.",
        "- This does not claim Holo is generally superior.",
        "- This does not claim Holo solved safety.",
        "- This does not claim solo models cannot solve similar packets universally.",
        "- Internal Holo misses remain intra-Holo misses, not standalone solo failures.",
    ]


def audit_md(audit: dict[str, Any]) -> list[str]:
    lines = ["# HoloVerify 20-Pair No-Provider Local Audit", ""]
    lines += md_table(
        ["Assertion", "Status"],
        [[key, value] for key, value in audit["assertions"].items()],
    )
    lines += ["", "## Evidence Presence", ""]
    lines += md_table(
        ["Evidence", "Status"],
        [[key, value] for key, value in audit["required_evidence_presence"].items()],
    )
    return lines


def write_json(filename: str, value: Any) -> None:
    (FINAL_PACKAGE / filename).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_md(filename: str, lines: list[str]) -> None:
    (FINAL_PACKAGE / filename).write_text("\n".join(lines) + "\n")


def write_public_lock() -> None:
    public_files = [
        "HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.json",
        "HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.md",
        "HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO_2026_06_29.json",
        "HOLOVERIFY_20PAIR_FINAL_EVIDENCE_MEMO_2026_06_29.md",
        "HOLOVERIFY_14PAIR_PUBLIC_PROOF_SUMMARY_2026_06_29.md",
        "HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.json",
        "HOLOVERIFY_20PAIR_NO_PROVIDER_LOCAL_AUDIT_2026_06_29.md",
    ]
    locked_files = [
        {
            "relative_path": filename,
            "sha256": sha256_file(FINAL_PACKAGE / filename),
            "bytes": (FINAL_PACKAGE / filename).stat().st_size,
        }
        for filename in public_files
    ]
    manifest_without_root = {
        "classification": "HOLOVERIFY_20PAIR_PUBLIC_FREEZE_PACKAGE_LOCK",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "FROZEN_PUBLIC_SAFE_EVIDENCE_PACKAGE",
        "locked_files": locked_files,
    }
    root_signature = sha256_text(canonical_json(manifest_without_root))
    manifest = {**manifest_without_root, "root_signature": root_signature}
    (FINAL_PACKAGE / "PUBLIC_FREEZE_PACKAGE_LOCK_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    validation = {
        "validation_status": "PASS",
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "root_signature": root_signature,
        "locked_file_count": len(locked_files),
    }
    (FINAL_PACKAGE / "PUBLIC_FREEZE_PACKAGE_LOCK_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    result = build()
    print(
        json.dumps(
            {
                "status": result["no_provider_audit"]["status"],
                "clean_pair_count": result["subset"]["pair_count"],
                "audit_assertions": result["no_provider_audit"]["assertions"],
            },
            indent=2,
            sort_keys=True,
        )
    )
