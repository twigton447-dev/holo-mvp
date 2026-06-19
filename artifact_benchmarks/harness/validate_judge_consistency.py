from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from judge_consistency import score_verdict_consistency_flags


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("**/*.json"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--fail-on-flags", action="store_true")
    args = parser.parse_args()

    checked = 0
    flagged: list[dict[str, Any]] = []
    for root in args.paths:
        for path in candidate_files(root):
            payload = read_json(path)
            if not {"document_x", "document_y", "comparative_verdict"}.issubset(payload):
                continue
            checked += 1
            flags = score_verdict_consistency_flags(payload)
            if flags:
                flagged.append({"path": str(path), "flags": flags})

    print(json.dumps({"checked": checked, "flagged": flagged}, indent=2, sort_keys=True))
    return 2 if args.fail_on_flags and flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
