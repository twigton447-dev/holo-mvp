"""
rerun_google.py — Patch solo_google ERROR results by re-running only the Google condition.

Scans both traces/ and benchmark_results/ for files where solo_google verdict == ERROR,
then re-runs just that condition and patches the file in place.

Usage:
  python rerun_google.py
  python rerun_google.py --dry-run   # show which files would be patched, don't run
"""

import argparse
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from benchmark import run_solo, _inline
from llm_adapters import GoogleAdapter

SEARCH_DIRS = [
    Path("traces"),
    Path("benchmark_results"),
]

SCENARIO_DIR = Path("examples/benchmark_library/scenarios")


def find_errored_files():
    """Return list of (result_path, scenario_name) for all solo_google ERRORs."""
    targets = []
    for d in SEARCH_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            g = data.get("conditions", {}).get("solo_google", {})
            if g.get("verdict") == "ERROR":
                scenario_name = data.get("scenario_name") or f.stem.split("_result")[0]
                # strip bench_YYYYMMDD_HHMMSS_ prefix if present
                if scenario_name.startswith("bench_"):
                    parts = scenario_name.split("_", 3)
                    scenario_name = parts[3] if len(parts) > 3 else scenario_name
                targets.append((f, scenario_name))
    return targets


def find_scenario_file(scenario_name):
    """Locate the scenario JSON in the benchmark library."""
    candidate = SCENARIO_DIR / f"{scenario_name}.json"
    if candidate.exists():
        return candidate
    # fallback: search
    for f in SCENARIO_DIR.glob("*.json"):
        if f.stem == scenario_name:
            return f
    return None


def main():
    parser = argparse.ArgumentParser(description="Re-run failed solo_google benchmark conditions.")
    parser.add_argument("--dry-run", action="store_true", help="Show targets without running")
    args = parser.parse_args()

    targets = find_errored_files()
    if not targets:
        print("No solo_google ERROR results found. Nothing to do.")
        return

    print(f"Found {len(targets)} file(s) with solo_google ERROR:\n")
    for result_path, scenario_name in targets:
        print(f"  {result_path}  ->  scenario: {scenario_name}")
    print()

    if args.dry_run:
        print("--dry-run: exiting without running.")
        return

    google_adapter = GoogleAdapter()
    print(f"Google model: {google_adapter.model_id}\n")
    print("=" * 60)

    patched = 0
    failed = 0

    for result_path, scenario_name in targets:
        scenario_file = find_scenario_file(scenario_name)
        if not scenario_file:
            print(f"[SKIP] No scenario file found for: {scenario_name}")
            failed += 1
            continue

        scenario = json.loads(scenario_file.read_text())
        print(f"\n[RUN] {scenario_name}")
        print(f"      result file: {result_path}")

        cond = run_solo(scenario, google_adapter, "solo_google")
        _inline(cond)

        if cond.get("verdict") == "ERROR":
            print(f"  -> Still erroring: {cond.get('error','?')[:120]}")
            failed += 1
            continue

        # Patch result file in place
        data = json.loads(result_path.read_text())
        data["conditions"]["solo_google"] = cond
        result_path.write_text(json.dumps(data, indent=2))
        print(f"  -> Patched {result_path.name}")
        patched += 1

        # Brief pause between scenarios to avoid rate limits
        time.sleep(2)

    print("\n" + "=" * 60)
    print(f"Done. Patched: {patched}  |  Still failed: {failed}")


if __name__ == "__main__":
    main()
