from __future__ import annotations

"""T1 - ID-channel mutual-information scan.

Falsifies: "no runtime component receives an identifier from which packet
truth is derivable." Passing does NOT show payload content is truth-free.
"""

import os
import json
from pathlib import Path

import pytest

from blind_lane_suite import BENCH
from blind_lane_suite.id_channel import id_channel_report

BLIND_PROMPTS_ENV = "BLIND_LANE_PROMPTS_DIR"


def _find_governed_prompt_dir() -> Path | None:
    for path in sorted(BENCH.rglob("prompts")):
        if not path.is_dir() or not any(path.glob("*.json")):
            continue
        if "blind_lane" in str(path):
            continue
        return path
    return None


def test_detector_catches_synthetic_suffix_leak(tmp_path):
    """Detector validation: a known dirty prompt must fail loudly.

    This cannot depend on finding a dirty repo folder; otherwise the detector
    can choose only folders it already detects and skip when it is broken.
    """
    prompt = {
        "messages": [
            {
                "role": "user",
                "content": "RUN LOCK packet=HV-UNIT-001-A. Use source SRC-UNIT-ALLOW.",
            }
        ]
    }
    prompt_dir = tmp_path / "dirty_prompts"
    prompt_dir.mkdir()
    (prompt_dir / "HV-UNIT-001-A_W1.json").write_text(json.dumps(prompt))
    report = id_channel_report(prompt_dir)
    assert report["violation"], "scanner failed to detect synthetic suffixed packet ID"
    assert report["suffix_channel_hit_count"] > 0


def test_detector_checks_known_governed_dir_when_available():
    """Additional coverage: if old governed prompts exist, they should still
    show the known leak. Absence of such old prompts is not a pass signal."""
    prompt_dir = _find_governed_prompt_dir()
    if prompt_dir is None:
        pytest.skip("no frozen governed prompt dir in this checkout - detector NOT validated; do not trust T1 results")
    report = id_channel_report(prompt_dir)
    assert report["violation"], (
        f"Scanner failed to detect the known suffix channel in {prompt_dir} - "
        "T1 detector is broken; fix before trusting any blind-lane scan."
    )
    assert report["suffix_channel_hit_count"] > 0


def test_blind_lane_prompts_have_no_id_channel():
    """The actual T1 disconfirmation. Falsified if any suffixed ID or
    cross-pair deterministic token appears in blind-lane prompt output."""
    prompt_dir = os.environ.get(BLIND_PROMPTS_ENV, "").strip()
    if not prompt_dir:
        pytest.skip(
            f"{BLIND_PROMPTS_ENV} not set - blind-lane prompts not yet produced. "
            "SKIP IS NOT A PASS."
        )
    report = id_channel_report(Path(prompt_dir))
    assert report["prompt_files_scanned"] > 0, "no prompt files found - nothing was tested"
    assert not report["suffix_channel_hits"], (
        f"TRUTH LEAK: suffixed IDs in blind-lane prompts: {report['suffix_channel_hits'][:5]}"
    )
    assert not report["deterministic_tokens"], (
        f"TRUTH LEAK: tokens deterministically mapped to one truth side: {report['deterministic_tokens'][:5]}"
    )
