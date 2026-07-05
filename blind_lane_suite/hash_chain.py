"""T3 - artifact provenance hash chain.

Falsifies: "the harness never writes into worker artifacts."

verify_hash_chain compares each worker row against the raw mock output that
produced it: recorded raw hash, stored artifact text, and any downstream
copies must all hash-equal the raw output.

Passing does NOT show artifacts are correct - only untouched.
"""

from __future__ import annotations

import hashlib


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_hash_chain(run_result: dict, raw_outputs: list[str]) -> list[dict]:
    violations: list[dict] = []
    rows = run_result.get("worker_rows") or []
    if len(rows) != len(raw_outputs):
        violations.append(
            {
                "kind": "row_count_mismatch",
                "worker_rows": len(rows),
                "raw_outputs": len(raw_outputs),
            }
        )
    for i, (row, raw) in enumerate(zip(rows, raw_outputs)):
        expected = sha256_text(raw)
        recorded = row.get("raw_output_sha256")
        if recorded != expected:
            violations.append({"kind": "recorded_hash_mismatch", "index": i, "recorded": recorded, "expected": expected})
        stored = row.get("artifact_text")
        if stored is None:
            violations.append({"kind": "artifact_text_missing", "index": i})
        elif sha256_text(stored) != expected:
            violations.append({"kind": "artifact_mutated", "index": i, "stored_sha256": sha256_text(stored), "expected": expected})
        for stage in ("gate_input_sha256", "selector_input_sha256", "scorer_input_sha256"):
            if stage in row and row[stage] != expected:
                violations.append({"kind": f"{stage}_mismatch", "index": i, "got": row[stage], "expected": expected})
    return violations
