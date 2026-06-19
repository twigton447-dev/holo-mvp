from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import CRITERIA, read_json, weighted_score, write_json


def blank_score(cid: str) -> dict[str, Any]:
    return {"criterion_id": cid, "score_1_5": None, "score_1_10": None, "notes": ""}


def proof_credit_metadata(form: dict[str, Any]) -> dict[str, Any]:
    harness = form.get("_harness") or {}
    overlap = str(harness.get("judge_dna_overlap") or "")
    proof_credit_eligible = harness.get("proof_credit_eligible") is True and not overlap
    if proof_credit_eligible:
        score_credit_label = harness.get("score_credit_label") or "proof_credit_candidate"
        score_use = harness.get("score_use") or "proof_credit_if_blind_and_boundary_clean"
    elif overlap:
        score_credit_label = harness.get("score_credit_label") or "diagnostic_same_dna"
        score_use = "diagnostic_only"
    else:
        score_credit_label = harness.get("score_credit_label") or "diagnostic_unknown_dna"
        score_use = "diagnostic_only"
    return {
        "proof_credit_eligible": proof_credit_eligible,
        "score_credit_label": score_credit_label,
        "score_use": score_use,
        "judge_dna_overlap": overlap,
    }


def blank_form(packet: dict[str, Any], judge_id: str) -> dict[str, Any]:
    return {
        "judge_id": judge_id,
        "judge_packet_id": packet["judge_packet_id"],
        "domain_id": packet["domain_id"],
        "scores": {
            "document_x": {cid: blank_score(cid) for cid in CRITERIA},
            "document_y": {cid: blank_score(cid) for cid in CRITERIA},
        },
        "qualitative_feedback": {
            "document_x": "",
            "document_y": "",
            "comparative_notes": "",
        },
        "validation_flags": [],
        "_harness": {
            "proof_credit_eligible": False,
            "score_credit_label": "diagnostic_unknown_dna",
            "score_use": "diagnostic_only",
            "judge_dna_overlap": "unknown_generation_dna",
        },
    }


def validate_score_form(form: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    for doc_key in ["document_x", "document_y"]:
        for cid in CRITERIA:
            s5 = form["scores"][doc_key][cid]["score_1_5"]
            s10 = form["scores"][doc_key][cid]["score_1_10"]
            if s5 is None or s10 is None:
                raise ValueError(f"{doc_key}.{cid} missing score")
            if not (1 <= float(s5) <= 5 and 1 <= float(s10) <= 10):
                raise ValueError(f"{doc_key}.{cid} out of range")
    credit = proof_credit_metadata(form)
    return {
        "document_x_weighted": weighted_score(form["scores"]["document_x"], rubric),
        "document_y_weighted": weighted_score(form["scores"]["document_y"], rubric),
        **credit,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance_dir", type=Path)
    parser.add_argument("--run-id", default="stub_no_live_001")
    parser.add_argument("--create-blank-forms", action="store_true")
    args = parser.parse_args()

    root = args.instance_dir / "runs" / args.run_id
    if args.create_blank_forms:
        count = 0
        for packet_path in sorted((root / "judge_packets").glob("*.json")):
            packet = read_json(packet_path)
            for number in range(1, 4):
                judge_id = f"judge_{number:02d}"
                write_json(root / "judge_scores" / f"{packet['judge_packet_id']}_{judge_id}.json", blank_form(packet, judge_id))
                count += 1
        print("ARTIFACT_BENCHMARK_JUDGE_FORMS_CREATED")
        print(f"run_id={args.run_id} forms={count}")
        return 0

    complete = []
    incomplete = []
    flags = []
    rubric = read_json(args.instance_dir / "prompts" / "scoring_rubric_8criteria.json")
    for form_path in sorted((root / "judge_scores").glob("*.json")):
        form = read_json(form_path)
        try:
            complete.append({"form": form_path.name, **validate_score_form(form, rubric)})
        except Exception as exc:
            incomplete.append({"form": form_path.name, "reason": str(exc)})
    write_json(root / "judge_score_summary.json", {"complete": complete, "incomplete": incomplete, "flags": flags})
    print("ARTIFACT_BENCHMARK_JUDGE_FORMS_VALIDATED")
    print(f"complete={len(complete)} incomplete={len(incomplete)} flags={len(flags)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
