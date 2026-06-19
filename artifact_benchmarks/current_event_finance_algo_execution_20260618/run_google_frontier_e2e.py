from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


PACKET_DIR = Path(__file__).resolve().parent
LIVE_HARNESS = PACKET_DIR / "google_frontier_e2e_live.py"
NO_PROVIDER_SMOKE = PACKET_DIR / "google_frontier_no_provider_smoke.py"
HASH_LOCK = PACKET_DIR / "hash_lock.json"
ROUTING_CONFIGS = PACKET_DIR / "holo_routing_configs.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def provider_env_status() -> dict[str, str]:
    return {
        "OPENAI_API_KEY": "PRESENT" if os.getenv("OPENAI_API_KEY") else "MISSING",
        "ANTHROPIC_API_KEY": "PRESENT" if os.getenv("ANTHROPIC_API_KEY") else "MISSING",
        "GOOGLE_API_KEY": "PRESENT" if os.getenv("GOOGLE_API_KEY") else "MISSING",
    }


def run_child(args: list[str]) -> int:
    return subprocess.call([sys.executable, "-B", *args], cwd=str(PACKET_DIR))


def load_routing_config(routing_config_id: str | None) -> dict:
    suite = read_json(ROUTING_CONFIGS)
    selected = routing_config_id or suite["default_routing_config_id"]
    for config in suite["routing_configs"]:
        if config["routing_config_id"] == selected:
            return config
    valid = ", ".join(config["routing_config_id"] for config in suite["routing_configs"])
    raise RuntimeError(f"unknown_routing_config:{selected}; valid={valid}")


def preflight(routing_config_id: str | None) -> int:
    lock = read_json(HASH_LOCK)
    route = load_routing_config(routing_config_id)
    status = provider_env_status()
    payload = {
        "status": "PREFLIGHT_PASS"
        if all(value == "PRESENT" for value in status.values())
        else "PREFLIGHT_MISSING_ENV",
        "provider_env": status,
        "packet_dir": str(PACKET_DIR),
        "hash_lock_id": lock["hash_lock_id"],
        "source_commit": lock["source_commit"],
        "cohort_id": lock["cohort"]["cohort_id"],
        "solo_conditions": lock["solo_conditions"],
        "routing_config_id": route["routing_config_id"],
        "routing_config_label": route.get("label"),
        "available_routing_configs": lock["holo_routing_config_ids"],
        "holo_analyst_rotation": route["analyst_rotation"],
        "holo_governor_model": lock["holo_governor_model"],
        "holo_governor_continuity_rule": lock["holo_governor_continuity_rule"],
        "judge_panel": lock["judge_panel"],
        "live_calls_default": "disabled",
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PREFLIGHT_PASS" else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guarded launcher for the locked Google-main finance frontier benchmark."
    )
    parser.add_argument("--preflight", action="store_true", help="Check env and print locked cohort without provider calls.")
    parser.add_argument("--no-provider-smoke", action="store_true", help="Run deterministic local smoke with zero provider calls.")
    parser.add_argument("--run-live", action="store_true", help="Run the live benchmark. Sends packet/artifacts to providers.")
    parser.add_argument("--run-id", help="Optional run id for the live harness.")
    parser.add_argument("--routing-config", help="Holo analyst order config id. Defaults to hash-locked baseline.")
    parser.add_argument("--timeout", type=int, default=420, help="Provider timeout in seconds for live calls.")
    args = parser.parse_args()

    selected = [args.preflight, args.no_provider_smoke, args.run_live]
    if sum(bool(item) for item in selected) != 1:
        parser.print_help()
        print(
            "\nChoose exactly one mode. Live mode is intentionally explicit because it sends "
            "the frozen finance packet and generated artifacts to external providers."
        )
        return 2

    if args.preflight:
        return preflight(args.routing_config)
    if args.no_provider_smoke:
        child_args = [str(NO_PROVIDER_SMOKE)]
        if args.routing_config:
            child_args.extend(["--routing-config", args.routing_config])
        return run_child(child_args)

    child_args = [str(LIVE_HARNESS), "--run-live", "--timeout", str(args.timeout)]
    if args.run_id:
        child_args.extend(["--run-id", args.run_id])
    if args.routing_config:
        child_args.extend(["--routing-config", args.routing_config])
    return run_child(child_args)


if __name__ == "__main__":
    raise SystemExit(main())
