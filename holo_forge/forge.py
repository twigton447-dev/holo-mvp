"""
holo_forge/forge.py

CLI entry point for holo_forge. Thin wrapper over loop.py.

Commands:
  build <spec.json> [--output <dir>] [--seed N] [--force-max-turns]
      Run the forge loop. Saves: result JSON + final packet JSON.
      Result: forge_results/<forge_id>.json
      Packet: docs/benchmark/payloads/<scenario_id>_v1.json (or --output dir)

  lint <packet.json>
      Static lint only. Does not call any LLM.

  status <forge_result.json>
      Print forge run status from a saved result.

  authorize-final <packet.json> --confirmed
      Mark packet as FINAL_PENDING. Does not run blind adjudication.
      After this: python run_blind_adjudication.py <packet.json>

Usage:
  python holo_forge/forge.py build holo_forge/specs/AP-BEC-PAYCHNG-001_spec.json
  python holo_forge/forge.py build holo_forge/specs/AP-BEC-PAYCHNG-001_spec.json --seed 42
  python holo_forge/forge.py lint docs/benchmark/payloads/FORGE-BEC-001_v1.json
  python holo_forge/forge.py status forge_results/forge_20260529_FORGE-BEC-001.json
  python holo_forge/forge.py authorize-final docs/benchmark/payloads/FORGE-BEC-001_v1.json --confirmed
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def cmd_build(args):
    from holo_forge import lint as _lint
    from holo_forge.loop import run_forge

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}")
        sys.exit(1)

    spec = json.loads(spec_path.read_text())
    scenario_id = spec.get("scenario_id", spec_path.stem)

    # Pre-flight: confirm the spec has required fields
    for field in ("scenario_id", "domain", "target_verdict"):
        if not spec.get(field):
            print(f"ERROR: spec missing required field: {field}")
            sys.exit(1)

    result = run_forge(
        spec,
        seed=args.seed,
        force_max_turns=args.force_max_turns,
    )

    # Save result JSON
    out_dir = Path("forge_results")
    out_dir.mkdir(exist_ok=True)
    result_path = out_dir / f"{result['forge_id']}.json"
    result_path.write_text(json.dumps(result, indent=2))
    print(f"  Result saved: {result_path}")

    # Save final packet if we have one
    final_draft = result.get("final_draft")
    if final_draft:
        packet_dir = Path(args.output) if args.output else Path("docs/benchmark/payloads")
        packet_dir.mkdir(parents=True, exist_ok=True)
        packet_path = packet_dir / f"{scenario_id}_v1.json"

        # Attach forge provenance to packet
        final_draft["_forge"] = {
            "forge_id":      result["forge_id"],
            "forge_status":  result["forge_status"],
            "converged":     result["converged"],
            "retire_signal": result["retire_signal"],
            "exit_reason":   result["exit_reason"],
            "turns":         result["turns_completed"],
            "qa_turns":      result["qa_turn_count"],
            "qa_deltas":     result["qa_deltas"],
            "seed":          result["seed"],
            "forged_at":     result["timestamp"],
        }

        packet_path.write_text(json.dumps(final_draft, indent=2))
        print(f"  Packet saved: {packet_path}")

        # Auto-lint the packet if converged
        forge_status = result["forge_status"]
        if forge_status == "CONVERGED":
            print(f"\n  Running lint on converged packet...")
            lint_result = _lint.check(final_draft)
            lint_result.print_report(scenario_id)
            if lint_result.passed:
                print("  Lint PASS. Ready for: python run_blind_adjudication.py <packet>")
            else:
                print("  Lint FAIL. Packet has schema issues despite convergence.")
                print("  Fix the errors, then run: python run_blind_adjudication.py <packet>")
        elif forge_status == "RETIRED":
            print(f"\n  RETIRED: structural flaw. Do not iterate. Build a new spec.")
        else:
            print(f"\n  EXHAUSTED ({result['turns_completed']} turns, no convergence).")
            print("  Review the forge result and consider adjusting the spec or seam.")
    else:
        print("  No final draft produced (Builder error on first turn?).")

    return result


def cmd_lint(args):
    from holo_forge import lint
    ok = lint.run(args.packet)
    sys.exit(0 if ok else 1)


def cmd_status(args):
    path = Path(args.result)
    if not path.exists():
        print(f"ERROR: not found: {path}")
        sys.exit(1)

    result = json.loads(path.read_text())
    scenario_id  = result.get("scenario_id", "?")
    forge_status = result.get("forge_status", "?")
    converged    = result.get("converged", False)
    retired      = result.get("retire_signal", False)
    turns        = result.get("turns_completed", 0)
    qa_turns     = result.get("qa_turn_count", 0)
    qa_deltas    = result.get("qa_deltas", [])
    exit_reason  = result.get("exit_reason", "?")
    ts           = result.get("timestamp", "?")
    seed         = result.get("seed", None)

    print(f"\n{'='*65}")
    print(f"  FORGE STATUS: {scenario_id}")
    print(f"  Status:       {forge_status}")
    print(f"  Converged:    {converged}")
    print(f"  Retired:      {retired}")
    print(f"  Exit reason:  {exit_reason}")
    print(f"  Turns:        {turns}  (QA: {qa_turns})")
    print(f"  QA deltas:    {qa_deltas}")
    print(f"  Seed:         {seed}")
    print(f"  Timestamp:    {ts}")

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

    if forge_status == "CONVERGED" and has_draft:
        print("  Next: python run_blind_adjudication.py docs/benchmark/payloads/<scenario>_v1.json")
    elif forge_status == "RETIRED":
        print("  Retired: rebuild the spec, do not re-run this packet.")
    elif forge_status == "EXHAUSTED":
        print("  Exhausted: consider adjusting the seam or spec, then re-run.")


def cmd_authorize_final(args):
    if not args.confirmed:
        print("  Authorization requires --confirmed flag.")
        print("  This is the gate before Final blind adjudication.")
        print("  Review the packet manually first.")
        sys.exit(1)

    path = Path(args.packet)
    if not path.exists():
        print(f"ERROR: not found: {path}")
        sys.exit(1)

    packet = json.loads(path.read_text())
    forge  = packet.get("_forge", {})

    if forge.get("forge_status") != "CONVERGED":
        print(f"  ERROR: packet forge_status is '{forge.get('forge_status')}', must be CONVERGED.")
        sys.exit(1)

    forge["final_auth"] = {
        "authorized_at": datetime.utcnow().isoformat() + "Z",
        "state":         "FINAL_PENDING",
    }
    path.write_text(json.dumps(packet, indent=2))
    scenario_id = packet.get("scenario_id", path.stem)
    print(f"  {scenario_id} -> FINAL_PENDING")
    print(f"  Run: python run_blind_adjudication.py {path}")


def main():
    parser = argparse.ArgumentParser(prog="forge", description="Holo Forge — adversarial packet builder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="Run forge loop on a spec")
    p_build.add_argument("spec", help="Path to spec JSON")
    p_build.add_argument("--output", help="Output directory for packet (default: docs/benchmark/payloads/)")
    p_build.add_argument("--seed", type=int, default=None, help="Fix rotation seed for reproducibility")
    p_build.add_argument("--force-max-turns", action="store_true",
                         help="Disable early convergence — run all 10 turns")
    p_build.set_defaults(func=cmd_build)

    p_lint = sub.add_parser("lint", help="Static lint a packet JSON")
    p_lint.add_argument("packet")
    p_lint.set_defaults(func=cmd_lint)

    p_status = sub.add_parser("status", help="Print forge run status")
    p_status.add_argument("result", help="Path to forge result JSON")
    p_status.set_defaults(func=cmd_status)

    p_final = sub.add_parser("authorize-final",
                              help="Authorize Final blind adjudication (requires --confirmed)")
    p_final.add_argument("packet")
    p_final.add_argument("--confirmed", action="store_true")
    p_final.set_defaults(func=cmd_authorize_final)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
