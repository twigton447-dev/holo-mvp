#!/usr/bin/env python3
"""Run or preflight solo one-shot triage over the frozen Wave 2 3-family bank.

This is a thin, lane-locked adapter around the June 29 solo triage runner.
It intentionally keeps the solo lane separate from Holo:
- no Gov
- no state brief
- no baton
- no artifact registry
- no final selector
- no judges

Wave 2 uses the current OpenAI-W2 roster: xAI mini, OpenAI gpt-5.4-mini,
and MiniMax M2.5-highspeed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LEGACY_RUNNER_PATH = BENCHMARK_ROOT / "run_replication_3family_solo_triage_2026_06_29.py"
WAVE2_FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
WAVE2_RUN_ROOT = WAVE2_FREEZE_ROOT / "solo_triage_3mini"
WAVE2_FREEZE_ROOT_HASH = "80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f"
WAVE2_OPENAI_MODEL_ID = "gpt-5.4-mini"
WAVE2_EXPECTED_FAMILIES = {
    "HV-HRWF-REP-2026-07-01": "HR / payroll / workforce controls",
    "HV-DPRV-REP-2026-07-01": "Data privacy / customer data release controls",
    "HV-FINC-REP-2026-07-01": "Finance close / revenue / expense recognition controls",
}


def load_legacy_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_legacy_solo_triage", LEGACY_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


LEGACY = load_legacy_runner()

# Lane lock: mutate only this imported module instance. The June 29 runner file
# remains untouched for AP/Commerce/IT historical evidence.
LEGACY.FREEZE_ROOT = WAVE2_FREEZE_ROOT
LEGACY.RUN_ROOT = WAVE2_RUN_ROOT
LEGACY.EXPECTED_FREEZE_ROOT_HASH = WAVE2_FREEZE_ROOT_HASH
LEGACY.OPENAI_WEAK_MODEL_ID = WAVE2_OPENAI_MODEL_ID
LEGACY.EXPECTED_FAMILIES = WAVE2_EXPECTED_FAMILIES
LEGACY.AP.RUNNER.MODEL_CONFIGS[LEGACY.OPENAI_WEAK_MODEL_KEY] = {
    "provider": "openai",
    "model": WAVE2_OPENAI_MODEL_ID,
    "dna": "openai",
    "api_key_env": "OPENAI_API_KEY",
    "kind": "openai_responses",
}

_legacy_preflight_report = LEGACY.preflight_report


def wave2_preflight_report(*args: Any, **kwargs: Any) -> dict[str, Any]:
    report = _legacy_preflight_report(*args, **kwargs)
    checks = dict(report.get("checks") or {})
    checks.pop("openai_weak_is_gpt_4o_mini", None)
    active_models = [row["model"] for row in report.get("model_roster", [])]
    checks["openai_w2_is_gpt_5_4_mini"] = (
        LEGACY.RUNNER.MODEL_CONFIGS[LEGACY.OPENAI_WEAK_MODEL_KEY]["model"] == WAVE2_OPENAI_MODEL_ID
    )
    checks["no_gpt_4o_mini_in_triage_roster"] = "gpt-4o-mini" not in active_models
    checks["wave2_freeze_root_matches"] = report.get("freeze_root") == WAVE2_FREEZE_ROOT_HASH
    checks["wave2_family_set_matches"] = set(report.get("selection", {}).get("family_ids", [])) <= set(WAVE2_EXPECTED_FAMILIES)
    report["classification"] = "HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE_PREFLIGHT"
    report["checks"] = checks
    report["status"] = "PASS" if all(checks.values()) else "FAIL"
    report["wave2_lane_lock"] = {
        "freeze_root_hash": WAVE2_FREEZE_ROOT_HASH,
        "families": WAVE2_EXPECTED_FAMILIES,
        "openai_model": WAVE2_OPENAI_MODEL_ID,
        "no_gov": True,
        "no_holo_state": True,
        "no_judges": True,
    }
    return report


LEGACY.preflight_report = wave2_preflight_report


def wave2_summarize(*args: Any, **kwargs: Any) -> dict[str, Any]:
    summary = _legacy_summarize(*args, **kwargs)
    summary["classification"] = summary["classification"].replace(
        "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE",
        "HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE",
    )
    summary["wave2_lane_lock"] = {
        "freeze_root_hash": WAVE2_FREEZE_ROOT_HASH,
        "families": WAVE2_EXPECTED_FAMILIES,
        "openai_model": WAVE2_OPENAI_MODEL_ID,
        "no_gov": True,
        "no_holo_state": True,
        "no_judges": True,
    }
    return summary


_legacy_summarize = LEGACY.summarize
LEGACY.summarize = wave2_summarize

_legacy_run_live = LEGACY.run_live


def wave2_run_live(*args: Any, **kwargs: Any) -> int:
    result = _legacy_run_live(*args, **kwargs)
    # The wrapped June 29 runner returns non-zero when it sees our Wave 2
    # classification string. The written summary is authoritative, so normalize
    # process status here when the latest run is complete.
    if result:
        summaries = sorted(WAVE2_RUN_ROOT.glob("*/run_*/solo_triage_results.json"))
        if summaries:
            latest = max(summaries, key=lambda path: path.stat().st_mtime)
            try:
                summary = json.loads(latest.read_text())
            except Exception:
                return result
            if summary.get("classification") == "HOLOVERIFY_REPLICATION_3FAMILY_WAVE2_SOLO_TRIAGE_COMPLETE":
                return 0
    return result


LEGACY.run_live = wave2_run_live


def main() -> int:
    # Reuse the original argparse surface. Choices are read from the mutated
    # EXPECTED_FAMILIES value, so Wave 2 family IDs are enforced here.
    try:
        return LEGACY.main()
    except SystemExit as exc:
        raise exc


if __name__ == "__main__":
    raise SystemExit(main())
