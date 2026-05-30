"""
holo_builder/builder.py

CLI entry point for Holo Builder.

Commands:
  build <spec.json> [--output <dir>] [--seed N] [--force-max-turns] [--skip-provider P]
      Run the Builder loop. Saves: result JSON + final packet JSON.
      Result: builder_results/<builder_id>.json
      Packet: docs/benchmark/payloads/<scenario_id>_v1.json (or --output dir)

  lint <packet.json>
      Static lint only. Does not call any LLM.

  status <builder_result.json>
      Print Builder run status from a saved result.

  qa-attack <packet.json> [--output <dir>]
      Run the standalone QA Attacker on a finished packet candidate.
      Blind: receives payload only. No target verdict. No Builder notes.
      Output: CLEAN_TO_FREEZE / NEEDS_REPAIR / DIRTY_PACKET / TOO_EASY /
              TOO_AMBIGUOUS / OVERFIT_RISK / RETIRE

  freeze <packet.json> <qa_result.json>
      Freeze a packet after QA Attacker returns CLEAN_TO_FREEZE.
      Generates SHA-256 hash, writes ledger entry, stores frozen candidate.

  authorize-final <packet.json> --confirmed
      Gate before Engine blind adjudication. Requires BUILDER_CONVERGED + QA CLEAN_TO_FREEZE.
      After this: python run_blind_adjudication.py <packet.json>

Usage:
  python holo_builder/builder.py build holo_builder/specs/AP-BEC-PAYCHNG-001_spec.json
  python holo_builder/builder.py build holo_builder/specs/AP-BEC-PAYCHNG-001_spec.json --seed 42
  python holo_builder/builder.py lint docs/benchmark/payloads/HBB-BEC-001_v1.json
  python holo_builder/builder.py status builder_results/builder_20260530_HBB-BEC-001.json
  python holo_builder/builder.py qa-attack docs/benchmark/payloads/HBB-BEC-001_v1.json
  python holo_builder/builder.py freeze docs/benchmark/payloads/HBB-BEC-001_v1.json qa_results/qa_20260530_HBB-BEC-001.json
  python holo_builder/builder.py authorize-final docs/benchmark/payloads/HBB-BEC-001_v1.json --confirmed
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def cmd_build(args):
    from holo_builder import lint as _lint
    from holo_builder.loop import run_builder

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}")
        sys.exit(1)

    spec = json.loads(spec_path.read_text())
    scenario_id = spec.get("scenario_id", spec_path.stem)

    for field in ("scenario_id", "domain", "target_verdict"):
        if not spec.get(field):
            print(f"ERROR: spec missing required field: {field}")
            sys.exit(1)

    result = run_builder(
        spec,
        seed=args.seed,
        force_max_turns=args.force_max_turns,
        skip_providers=args.skip_providers,
    )

    out_dir = Path("builder_results")
    out_dir.mkdir(exist_ok=True)
    result_path = out_dir / f"{result['builder_id']}.json"
    result_path.write_text(json.dumps(result, indent=2))
    print(f"  Result saved: {result_path}")

    final_draft = result.get("final_draft")
    if final_draft:
        packet_dir = Path(args.output) if args.output else Path("docs/benchmark/payloads")
        packet_dir.mkdir(parents=True, exist_ok=True)
        packet_path = packet_dir / f"{scenario_id}_v1.json"

        final_draft["_builder"] = {
            "builder_id":      result["builder_id"],
            "builder_status":  result["builder_status"],
            "converged":       result["converged"],
            "retire_signal":   result["retire_signal"],
            "exit_reason":     result["exit_reason"],
            "turns":           result["turns_completed"],
            "qa_turns":        result["qa_turn_count"],
            "qa_deltas":       result["qa_deltas"],
            "seed":            result["seed"],
            "built_at":        result["timestamp"],
        }

        packet_path.write_text(json.dumps(final_draft, indent=2))
        print(f"  Packet saved: {packet_path}")

        builder_status = result["builder_status"]
        if builder_status == "BUILDER_CONVERGED":
            print(f"\n  Running lint on converged packet...")
            lint_result = _lint.check(final_draft)
            lint_result.print_report(scenario_id)
            if lint_result.passed:
                print("  Lint PASS.")
                print("  Next: python holo_builder/builder.py qa-attack <packet>")
            else:
                print("  Lint FAIL. Fix errors before QA Attacker review.")
        elif builder_status == "BUILDER_RETIRED":
            print(f"\n  BUILDER_RETIRED: structural flaw. Build a new spec.")
        else:
            print(f"\n  BUILDER_EXHAUSTED ({result['turns_completed']} turns, no convergence).")
            print("  Review the builder result and consider adjusting the spec or seam.")
    else:
        print("  No final draft produced (Builder error on first turn?).")

    return result


def cmd_lint(args):
    from holo_builder import lint
    ok = lint.run(args.packet)
    sys.exit(0 if ok else 1)


def cmd_status(args):
    path = Path(args.result)
    if not path.exists():
        print(f"ERROR: not found: {path}")
        sys.exit(1)

    result = json.loads(path.read_text())
    scenario_id    = result.get("scenario_id", "?")
    builder_status = result.get("builder_status", "?")
    converged      = result.get("converged", False)
    retired        = result.get("retire_signal", False)
    turns          = result.get("turns_completed", 0)
    qa_turns       = result.get("qa_turn_count", 0)
    qa_deltas      = result.get("qa_deltas", [])
    exit_reason    = result.get("exit_reason", "?")
    ts             = result.get("timestamp", "?")
    seed           = result.get("seed", None)

    print(f"\n{'='*65}")
    print(f"  BUILDER STATUS: {scenario_id}")
    print(f"  Status:         {builder_status}")
    print(f"  Converged:      {converged}")
    print(f"  Retired:        {retired}")
    print(f"  Exit reason:    {exit_reason}")
    print(f"  Turns:          {turns}  (Internal QA: {qa_turns})")
    print(f"  QA deltas:      {qa_deltas}")
    print(f"  Seed:           {seed}")
    print(f"  Timestamp:      {ts}")

    coverage = result.get("coverage", {})
    if coverage:
        print(f"\n  Coverage:")
        for cat, v in coverage.items():
            print(f"    {cat:<22} {v.get('severity','?')}")

    briefs = result.get("governor_briefs", [])
    if briefs:
        last = briefs[-1]
        print(f"\n  Last Governor brief (turn {last.get('after_turn','?')}):")
        print(f"    Trajectory:  {last.get('overall_trajectory','?')}")
        print(f"    Risk cat:    {last.get('highest_risk_category','?')}")
        brief_text = last.get("brief_for_builder", "")
        if brief_text:
            print(f"    Brief:       {brief_text[:200]}")

    has_draft = result.get("final_draft") is not None
    print(f"\n  Final draft:  {'present' if has_draft else 'MISSING'}")
    print(f"{'='*65}\n")

    if builder_status == "BUILDER_CONVERGED" and has_draft:
        print("  Next: python holo_builder/builder.py qa-attack docs/benchmark/payloads/<scenario>_v1.json")
    elif builder_status == "BUILDER_RETIRED":
        print("  Retired: rebuild the spec, do not re-run this packet.")
    elif builder_status == "BUILDER_EXHAUSTED":
        print("  Exhausted: consider adjusting the seam or spec, then re-run.")


def cmd_qa_attack(args):
    from holo_builder.qa_attacker import run_qa_attack

    packet_path = Path(args.packet)
    if not packet_path.exists():
        print(f"ERROR: packet not found: {packet_path}")
        sys.exit(1)

    packet = json.loads(packet_path.read_text())
    scenario_id = packet.get("scenario_id", packet_path.stem)

    result = run_qa_attack(
        packet,
        skip_providers=args.skip_providers,
        seed=args.seed,
    )

    out_dir = Path(args.output) if args.output else Path("qa_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    result_path = out_dir / f"qa_{ts}_{scenario_id}.json"
    result_path.write_text(json.dumps(result, indent=2))
    print(f"  QA result saved: {result_path}")

    classification = result.get("final_classification", "?")
    print(f"\n  QA ATTACKER: {scenario_id}")
    print(f"  Classification: {classification}")
    if classification == "CLEAN_TO_FREEZE":
        print("  Next: python holo_builder/builder.py freeze <packet> <qa_result>")
    elif classification == "RETIRE":
        print("  RETIRE: structural flaw. Rebuild the spec.")
    else:
        print("  Return to Builder for repair.")

    return result


def cmd_freeze(args):
    from holo_builder.freeze import freeze_packet

    packet_path = Path(args.packet)
    qa_path     = Path(args.qa_result)

    for p, label in ((packet_path, "packet"), (qa_path, "qa_result")):
        if not p.exists():
            print(f"ERROR: {label} not found: {p}")
            sys.exit(1)

    packet    = json.loads(packet_path.read_text())
    qa_result = json.loads(qa_path.read_text())

    classification = qa_result.get("final_classification", "")
    if classification != "CLEAN_TO_FREEZE":
        print(f"ERROR: QA Attacker classification is '{classification}', must be CLEAN_TO_FREEZE.")
        print("  Freeze only happens after QA Attacker approves.")
        sys.exit(1)

    frozen_path, pkg_hash = freeze_packet(packet, qa_result, packet_path)
    print(f"  Frozen: {frozen_path}")
    print(f"  Hash:   {pkg_hash}")
    print(f"  Ledger updated.")
    if args.authorize:
        print(f"  Next: python run_blind_adjudication.py {frozen_path}")


def cmd_authorize_final(args):
    if not args.confirmed:
        print("  Authorization requires --confirmed flag.")
        print("  Review the frozen packet manually first.")
        sys.exit(1)

    path = Path(args.packet)
    if not path.exists():
        print(f"ERROR: not found: {path}")
        sys.exit(1)

    packet  = json.loads(path.read_text())
    builder = packet.get("_builder", {})
    frozen  = packet.get("_frozen", {})

    if builder.get("builder_status") != "BUILDER_CONVERGED":
        print(f"  ERROR: builder_status is '{builder.get('builder_status')}', must be BUILDER_CONVERGED.")
        sys.exit(1)

    if not frozen.get("hash"):
        print(f"  ERROR: packet is not frozen. Run 'freeze' first.")
        sys.exit(1)

    if frozen.get("qa_classification") != "CLEAN_TO_FREEZE":
        print(f"  ERROR: QA classification is '{frozen.get('qa_classification')}', must be CLEAN_TO_FREEZE.")
        sys.exit(1)

    frozen["final_auth"] = {
        "authorized_at": datetime.utcnow().isoformat() + "Z",
        "state":         "FINAL_PENDING",
    }
    path.write_text(json.dumps(packet, indent=2))
    scenario_id = packet.get("scenario_id", path.stem)
    print(f"  {scenario_id} -> FINAL_PENDING")
    print(f"  Run: python run_blind_adjudication.py {path}")


def main():
    parser = argparse.ArgumentParser(prog="builder", description="Holo Builder — adversarial packet builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Run Builder loop on a spec")
    p_build.add_argument("spec", help="Path to spec JSON")
    p_build.add_argument("--output", help="Output directory for packet (default: docs/benchmark/payloads/)")
    p_build.add_argument("--seed", type=int, default=None, help="Fix rotation seed for reproducibility")
    p_build.add_argument("--force-max-turns", action="store_true",
                         help="Disable early convergence — run all 10 turns")
    p_build.add_argument("--skip-provider", action="append", dest="skip_providers",
                         metavar="PROVIDER", default=None,
                         help="Exclude a provider from the rotation (repeatable)")
    p_build.set_defaults(func=cmd_build)

    p_lint = sub.add_parser("lint", help="Static lint a packet JSON")
    p_lint.add_argument("packet")
    p_lint.set_defaults(func=cmd_lint)

    p_status = sub.add_parser("status", help="Print Builder run status")
    p_status.add_argument("result", help="Path to builder result JSON")
    p_status.set_defaults(func=cmd_status)

    p_qa = sub.add_parser("qa-attack", help="Run standalone QA Attacker on a finished packet")
    p_qa.add_argument("packet", help="Path to packet JSON")
    p_qa.add_argument("--output", help="Output directory for QA result (default: qa_results/)")
    p_qa.add_argument("--seed", type=int, default=None)
    p_qa.add_argument("--skip-provider", action="append", dest="skip_providers",
                      metavar="PROVIDER", default=None)
    p_qa.set_defaults(func=cmd_qa_attack)

    p_freeze = sub.add_parser("freeze", help="Freeze a packet after QA Attacker approval")
    p_freeze.add_argument("packet", help="Path to packet JSON")
    p_freeze.add_argument("qa_result", help="Path to QA Attacker result JSON")
    p_freeze.add_argument("--authorize", action="store_true",
                          help="Print authorize-final command after freeze")
    p_freeze.set_defaults(func=cmd_freeze)

    p_final = sub.add_parser("authorize-final",
                              help="Authorize Engine blind adjudication (requires --confirmed)")
    p_final.add_argument("packet")
    p_final.add_argument("--confirmed", action="store_true")
    p_final.set_defaults(func=cmd_authorize_final)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
