"""Generate no-provider prompt artifacts for the blind-lane T1 scanner.

This emits prompts for every packet in the opaque canary runtime manifest, not
for a single synthetic packet.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from blind_lane_suite.fixtures import mock_transcripts
import holoverify_blind_runner_v0 as runner


OUT = Path("docs/benchmark/blind_lane_fixture_prompts_2026_07_02")
RUNTIME_MANIFEST = Path("docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json")


def _clean_prompt_dir() -> None:
    prompt_dir = OUT / "prompts"
    if not prompt_dir.exists():
        return
    for path in prompt_dir.glob("*.json"):
        path.unlink()


def main() -> int:
    if not RUNTIME_MANIFEST.exists():
        raise FileNotFoundError(f"runtime manifest missing: {RUNTIME_MANIFEST}")
    manifest = json.loads(RUNTIME_MANIFEST.read_text(errors="replace"))
    _clean_prompt_dir()
    for row in manifest.get("packets", []):
        payload_ref = row.get("runtime_payload_ref")
        if not payload_ref:
            raise RuntimeError(f"runtime payload ref missing in row: {row}")
        payload = json.loads(Path(payload_ref).read_text(errors="replace"))
        runner.run_blind_fixture(payload, mock_transcripts(verdict="ALLOW"), str(OUT))
    print(OUT / "prompts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
