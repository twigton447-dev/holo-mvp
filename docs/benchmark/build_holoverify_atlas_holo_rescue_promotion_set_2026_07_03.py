#!/usr/bin/env python3
"""Promoted solo-failure seams for a small Holo rescue test.

No providers are called by this module. It only assembles the Fable-reviewed
promotion set after V4/V6 solo scouts.

Promotion set per Fable review:
- HV-ATLAS-DISC-023
- HV-ATLAS-DISC-025
- HV-ATLAS-DISC-020
- HV-ATLAS-DISC-033
- HV-ATLAS-DISC-035
- HV-ATLAS-DISC-036

HV-ATLAS-DISC-034 is explicitly excluded; its fixed replacement is
HV-ATLAS-DISC-036.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


BENCH = Path(__file__).resolve().parent
SOURCES = [
    BENCH / "build_holoverify_atlas_seam_discovery_minirun_v3_2026_07_03.py",
    BENCH / "build_holoverify_atlas_seam_discovery_minirun_v4_fable_bank_2026_07_03.py",
    BENCH / "build_holoverify_atlas_seam_discovery_minirun_v6_fable_v5_affordance_2026_07_03.py",
    BENCH / "build_holoverify_atlas_seam_discovery_minirun_v6b_fix034_2026_07_03.py",
]
PROMOTED_PAIR_IDS = {
    "HV-ATLAS-DISC-020",
    "HV-ATLAS-DISC-023",
    "HV-ATLAS-DISC-025",
    "HV-ATLAS-DISC-033",
    "HV-ATLAS-DISC-035",
    "HV-ATLAS-DISC-036",
}
EXCLUDED_PAIR_IDS = {
    "HV-ATLAS-DISC-034",
}


def load_specs(path: Path) -> list[dict]:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return list(module.SPECS)


loaded: dict[str, dict] = {}
for source in SOURCES:
    for item in load_specs(source):
        pair_id = item["pair_id"]
        if pair_id in PROMOTED_PAIR_IDS:
            loaded[pair_id] = item

missing = PROMOTED_PAIR_IDS - set(loaded)
if missing:
    raise RuntimeError(f"missing promoted pairs: {sorted(missing)}")
if EXCLUDED_PAIR_IDS & set(loaded):
    raise RuntimeError(f"excluded pair loaded: {sorted(EXCLUDED_PAIR_IDS & set(loaded))}")

SPECS = [loaded[pair_id] for pair_id in sorted(PROMOTED_PAIR_IDS)]
