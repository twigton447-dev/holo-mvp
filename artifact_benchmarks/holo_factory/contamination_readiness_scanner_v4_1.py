from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCANNER_ID = "contamination_readiness_scanner_v4_1"
PROVIDER_CALLS = 0

HARD_FORBIDDEN_VISIBLE_LABELS = [
    "Holo",
    "Gov",
    "Governor",
    "draft_not_frozen",
    "benchmark_credit",
    "proof_credit",
    "candidate_not_frozen",
    "holo_frontier_fixed_v1",
    "solo_openai",
    "ablation",
    "Context Governor",
    "STATE_OBJECT",
    "Artifact Registry",
    "Model Router",
    "BATON_PASS",
    "adversarial role",
    "role compliance",
    "state audit",
    "synthesis trigger",
]

CONTEXT_SENSITIVE_TERMS = [
    "condition",
    "internal",
]

HARD_FORBIDDEN_PATTERNS = {
    "Holo": re.compile(r"holo", re.IGNORECASE),
    "Gov": re.compile(r"(?<![a-z])gov(?![a-z])", re.IGNORECASE),
    "Governor": re.compile(r"governor", re.IGNORECASE),
    "draft_not_frozen": re.compile(r"draft_not_frozen", re.IGNORECASE),
    "benchmark_credit": re.compile(r"benchmark_credit", re.IGNORECASE),
    "proof_credit": re.compile(r"proof_credit", re.IGNORECASE),
    "candidate_not_frozen": re.compile(r"candidate_not_frozen", re.IGNORECASE),
    "holo_frontier_fixed_v1": re.compile(r"holo_frontier_fixed_v1", re.IGNORECASE),
    "solo_openai": re.compile(r"solo_openai", re.IGNORECASE),
    "ablation": re.compile(r"ablation", re.IGNORECASE),
    "Context Governor": re.compile(r"context governor", re.IGNORECASE),
    "STATE_OBJECT": re.compile(r"state_object", re.IGNORECASE),
    "Artifact Registry": re.compile(r"artifact registry", re.IGNORECASE),
    "Model Router": re.compile(r"model router", re.IGNORECASE),
    "BATON_PASS": re.compile(r"baton_pass", re.IGNORECASE),
    "adversarial role": re.compile(r"adversarial role", re.IGNORECASE),
    "role compliance": re.compile(r"role[-_ ]compliance", re.IGNORECASE),
    "state audit": re.compile(r"state[-_ ]audit", re.IGNORECASE),
    "synthesis trigger": re.compile(r"synthesis trigger", re.IGNORECASE),
}

CONTEXT_SENSITIVE_PROCESS_PATTERNS = {
    "condition": [
        re.compile(r"\bcondition_id\b", re.IGNORECASE),
        re.compile(r"\bbenchmark_condition\b", re.IGNORECASE),
        re.compile(r"\bcondition_family\b", re.IGNORECASE),
        re.compile(r"\bholo_condition\b", re.IGNORECASE),
        re.compile(r"\bsolo_condition\b", re.IGNORECASE),
        re.compile(r"\bgeneration_condition\b", re.IGNORECASE),
        re.compile(r"\bcondition_manifest\b", re.IGNORECASE),
        re.compile(r"\bcondition_type\b", re.IGNORECASE),
        re.compile(r"\bmodel_condition\b", re.IGNORECASE),
    ],
    "internal": [
        re.compile(r"\binternal_generation\b", re.IGNORECASE),
        re.compile(r"\binternal_state\b", re.IGNORECASE),
        re.compile(r"\binternal_label\b", re.IGNORECASE),
        re.compile(r"\binternal_scaffold\b", re.IGNORECASE),
        re.compile(r"\binternal_process\b", re.IGNORECASE),
        re.compile(r"\binternal_run\b", re.IGNORECASE),
        re.compile(r"\binternal_metadata\b", re.IGNORECASE),
        re.compile(r"\bbuilder_internal\b", re.IGNORECASE),
    ],
}


def read_payload(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def context_excerpt(text: str, start: int, end: int, radius: int = 90) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return re.sub(r"\s+", " ", text[left:right]).strip()


def scan_text(text: str, *, path: str) -> dict[str, Any]:
    hard_hits: list[dict[str, Any]] = []
    context_hits: list[dict[str, Any]] = []

    for label, pattern in HARD_FORBIDDEN_PATTERNS.items():
        for match in pattern.finditer(text):
            hard_hits.append(
                {
                    "term": label,
                    "start": match.start(),
                    "end": match.end(),
                    "excerpt": context_excerpt(text, match.start(), match.end()),
                }
            )

    for term, patterns in CONTEXT_SENSITIVE_PROCESS_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                context_hits.append(
                    {
                        "term": term,
                        "process_pattern": pattern.pattern,
                        "start": match.start(),
                        "end": match.end(),
                        "excerpt": context_excerpt(text, match.start(), match.end()),
                    }
                )

    return {
        "path": path,
        "hard_forbidden_hit_count": len(hard_hits),
        "context_sensitive_process_hit_count": len(context_hits),
        "hard_forbidden_hits": hard_hits,
        "context_sensitive_process_hits": context_hits,
        "ordinary_condition_or_internal_not_counted": True,
        "passed": not hard_hits and not context_hits,
    }


def scan_paths(paths: list[Path]) -> dict[str, Any]:
    results = [scan_text(read_payload(path), path=str(path)) for path in paths]
    hard_total = sum(item["hard_forbidden_hit_count"] for item in results)
    context_total = sum(item["context_sensitive_process_hit_count"] for item in results)
    return {
        "scanner_id": SCANNER_ID,
        "provider_calls": PROVIDER_CALLS,
        "hard_forbidden_visible_labels": HARD_FORBIDDEN_VISIBLE_LABELS,
        "context_sensitive_terms": CONTEXT_SENSITIVE_TERMS,
        "context_sensitive_policy": "ordinary domain uses of condition/internal do not fail; harness/process metadata usages fail",
        "file_count": len(paths),
        "hard_forbidden_hit_count": hard_total,
        "context_sensitive_process_hit_count": context_total,
        "passed": hard_total == 0 and context_total == 0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan visible HoloBuild benchmark payloads for contamination labels.")
    parser.add_argument("paths", nargs="+", help="Visible payload files to scan.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    paths = [Path(raw) for raw in args.paths]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        result = {
            "scanner_id": SCANNER_ID,
            "provider_calls": PROVIDER_CALLS,
            "passed": False,
            "error": "missing_paths",
            "missing_paths": missing,
        }
        print(json.dumps(result, indent=2, sort_keys=False))
        return 2

    result = scan_paths(paths)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
