from __future__ import annotations
import json
from pathlib import Path
from typing import Any
CRITERIA = ['source_grounding','requirement_fit','depth_and_novel_insight','risk_detection','actionability','internal_consistency','executive_clarity','domain_judgment']
def read_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as handle:
        return json.load(handle)
def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write('\n')
def weighted_score(criteria_scores: dict[str, dict[str, float]], rubric: dict[str, Any]) -> float:
    total = sum(float(item['weight']) for item in rubric['criteria'])
    return round(sum(float(criteria_scores[item['id']]['score_1_10']) * float(item['weight']) for item in rubric['criteria']) / total, 3)
