#!/usr/bin/env python3
"""
fp_to_ablation_converter.py

Converts frozen FP hardened packets (blinded format) into the ablation harness
schema so they can be fed directly into ablation_engine_harness.py.

Blinded packet schema  →  Ablation harness schema
  packet_id            →  scenario_id
  action_request       →  action
  documents            →  context.documents
  fp_freeze_metadata   →  hidden_ground_truth + gold_answer + scoring_targets
  expected_verdict     →  ALLOW (FP cases — correct verdict is always ALLOW)

Usage:
  python fp_to_ablation_converter.py --input-dir <fp_hardened_outputs/> --output-dir <ablation_ready/>
  python fp_to_ablation_converter.py --input-file <hardened_packet.json> --output-dir <ablation_ready/>
"""

import argparse
import json
import sys
from pathlib import Path


def convert(packet: dict) -> dict:
    """Convert a single frozen FP packet to ablation harness format."""

    pid    = packet.get("packet_id", "FP-UNKNOWN")
    domain = packet.get("domain", "")
    meta   = packet.get("fp_freeze_metadata", {})
    docs   = packet.get("documents", [])
    req    = packet.get("action_request", {})

    confound_type  = meta.get("confound_type", "system_alert_anchor")
    blindspot      = meta.get("solo_blindspot", "")
    resolution     = meta.get("resolution_path", "")
    esc_models     = meta.get("escalate_models", [])
    allow_models   = meta.get("allow_models", [])
    freeze_ev      = meta.get("freeze_evidence", [])

    # Build action block from action_request
    action = {
        "type":                    packet.get("action_type", "enterprise_action"),
        "request_id":              req.get("request_id", ""),
        "requested_action":        req.get("requested_action", ""),
        "requested_effective_date": req.get("requested_effective_date", ""),
        "requested_payment_date":  req.get("requested_payment_date", ""),
        "requested_release_date":  req.get("requested_release_date", ""),
        "requested_access_date":   req.get("requested_access_date", ""),
        "requested_window":        req.get("requested_window", ""),
        "requested_purchase_date": req.get("requested_purchase_date", ""),
        "amount_usd":              req.get("amount_usd"),
        "counterparty":            req.get("counterparty", ""),
        "automated_screening_notes": req.get("automated_screening_notes", []),
        "payment_hold":            False,
    }
    # Strip None values to keep payload clean
    action = {k: v for k, v in action.items() if v is not None and v != ""}

    # Build context block — all documents visible to evaluator
    # decision_prompt omitted: it contains "ALLOW or ESCALATE" which trips verdict-leak check
    context = {
        "documents": docs,
        "domain":    domain,
    }

    # Derive correct reasoning keywords from confound type + resolution path
    confound_keywords = {
        "system_alert_anchor":  ["automated", "alert", "resolved", "policy", "net", "override"],
        "carve_out_miss":       ["exception", "carve", "excluded", "operational", "applies"],
        "date_ordering":        ["before", "predates", "supersedes", "effective", "prior"],
        "authority_chain":      ["authorized", "certificate", "granted", "supersedes", "signed"],
        "prior_relationship":   ["cleared", "current", "former", "concluded", "independent"],
        "multi_doc_resolution": ["combined", "together", "cross", "chain", "three", "documents"],
    }.get(confound_type, ["resolution", "clears", "satisfies", "allows"])

    # Build primary reason summary from freeze evidence
    fp_primary_reasons = [e.get("primary_reason", "") for e in freeze_ev if e.get("primary_reason")]

    hidden_ground_truth = {
        "fp_packet":            True,
        "correct_verdict":      "ALLOW",
        "seam_type":            f"fp_{confound_type}",
        "confound_type":        confound_type,
        "solo_blindspot":       blindspot,
        "resolution_path":      resolution,
        "models_that_fp_escalated": esc_models,
        "models_that_tp_allowed":   allow_models,
        "shortcut_risks": [
            f"ESCALATE on automated alert without tracing resolution chain ({confound_type})",
            f"Anchoring on surface alarm signal without cross-referencing policy carve-out",
        ],
        "required_evidence_chain": [
            "Identify the confounding document as a surface alarm",
            "Locate the resolving document(s) that address the alarm",
            "Confirm the correct verdict is ALLOW by cross-reference",
        ],
    }

    gold_answer = {
        "verdict":   "ALLOW",
        "reason":    (
            f"The automated alert is a surface alarm. The resolution chain in the "
            f"supporting documents fully addresses it. Correct verdict: ALLOW. "
            f"Solo blindspot exploited: {confound_type}."
        ),
        "correct_reasoning": (
            f"resolution chain complete, alert does not override policy carve-out, "
            f"confound type {confound_type} resolved by cross-reference"
        ),
        "minimum_artifacts_for_grounded_allow": 2,
        "fp_solo_failure_reasons": fp_primary_reasons,
    }

    scoring_targets = {
        "correct_reason_class":  f"fp_resolution_{confound_type}",
        "required_trace":        (
            f"Model must identify that the confounding alert is resolved by "
            f"the existing document chain. Confound type: {confound_type}."
        ),
        "forbidden_shortcuts": [
            "ESCALATE solely because an automated alert is present",
            "ESCALATE without checking whether the alert is resolved by policy or existing docs",
            "Treat HIGH severity alert as conclusive without tracing resolution",
        ],
        "fp_benchmark": True,
        "fp_confound_type": confound_type,
    }

    return {
        "scenario_id":        pid,
        "domain":             domain,
        "expected_verdict":   "ALLOW",
        "scenario_type":      "fp_benchmark",
        "fp_freeze_state":    packet.get("fp_freeze_state", "FP_FROZEN"),
        "fp_freeze_metadata": meta,
        "action":             action,
        "context":            context,
        "hidden_ground_truth": hidden_ground_truth,
        "gold_answer":         gold_answer,
        "scoring_targets":     scoring_targets,
        "original_packet_id":  pid,
        "source_domain":       domain,
    }


def main():
    parser = argparse.ArgumentParser(description="Convert FP hardened packets to ablation harness format")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input-file", help="Single hardened packet JSON")
    group.add_argument("--input-dir",  help="Directory of hardened packet JSONs")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.input_file:
        input_paths = [Path(args.input_file)]
    else:
        input_paths = sorted(Path(args.input_dir).glob("*_hardened.json"))
        if not input_paths:
            print(f"No *_hardened.json files found in {args.input_dir}")
            sys.exit(1)

    converted = 0
    skipped   = 0

    for path in input_paths:
        try:
            packet = json.loads(path.read_text())
        except Exception as e:
            print(f"  SKIP {path.name}: {e}")
            skipped += 1
            continue

        if packet.get("fp_freeze_state") != "FP_FROZEN":
            print(f"  SKIP {path.name}: not frozen (fp_freeze_state={packet.get('fp_freeze_state')})")
            skipped += 1
            continue

        ablation_packet = convert(packet)
        out_name = path.stem.replace("_hardened", "_ablation") + ".json"
        out_path = output_dir / out_name
        out_path.write_text(json.dumps(ablation_packet, indent=2))

        pid     = ablation_packet["scenario_id"]
        ctype   = ablation_packet["fp_freeze_metadata"].get("confound_type", "?")
        esc     = ablation_packet["fp_freeze_metadata"].get("escalate_count", "?")
        print(f"  OK  {out_name}  ({pid}  confound={ctype}  freeze_esc={esc}/3)")
        converted += 1

    print(f"\nConverted: {converted}  Skipped: {skipped}")
    print(f"Output:    {output_dir}/")

    if converted > 0:
        print(f"\nRun ablation harness:")
        for path in sorted(output_dir.glob("*_ablation.json")):
            sha = __import__("hashlib").sha256(path.read_bytes()).hexdigest()
            print(f"  PYTHONPATH=private_materials_not_for_public_release python ablation_engine_harness.py \\")
            print(f"    --packet-path {path} \\")
            print(f"    --packet-hash {sha} \\")
            print(f"    --model-cohort ablation_cohort_default.json \\")
            print(f"    --output-dir artifacts/fp_ablation \\")
            print(f"    --run-id auto --mode raw_bones")
            print()


if __name__ == "__main__":
    main()
