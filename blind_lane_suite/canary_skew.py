"""T5 - canary skew check against frozen traces (read-only).

Falsifies: "the canary sample was not chosen to be easy."

Difficulty proxy: first-worker-turn correctness BEFORE any repair, computed
from frozen result artifacts (artifact_registry turn_number == 1,
verification_verdict vs suffix truth). Truth is used post-hoc for
measurement only; nothing is written.

Passing does NOT show the bank generalizes - the bank was screened for solo
failure and no sampling cures a curated bank.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from . import BENCH

RESULT_NAMES = ("live_results.json", "batch_results.json")


def _truth(suffix: str) -> str | None:
    return {"A": "ALLOW", "B": "ESCALATE"}.get(suffix)


def iter_result_rows():
    """Yield (packet_id, run_id, row) deduped by (packet_id, run_id)."""
    seen = set()
    for name in RESULT_NAMES:
        for path in sorted(BENCH.rglob(name)):
            try:
                data = json.loads(path.read_text(errors="replace"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            run_id = next((p for p in path.parts if p.startswith("run_")), path.parent.name)
            for row in data.get("packet_results") or []:
                if not isinstance(row, dict):
                    continue
                pid = row.get("packet_id")
                if not isinstance(pid, str):
                    continue
                key = (pid, run_id)
                if key in seen:
                    continue
                seen.add(key)
                yield pid, run_id, row


def first_turn_correctness() -> dict[str, bool]:
    """packet_id -> first-worker-turn verdict correct (latest run wins on dupes)."""
    out: dict[str, bool] = {}
    for pid, _run, row in iter_result_rows():
        truth = _truth(str(row.get("suffix")))
        if truth is None:
            continue
        first = None
        for art in row.get("artifact_registry") or []:
            if isinstance(art, dict) and art.get("turn_number") == 1:
                first = art
                break
        if first is None:
            continue
        out[pid] = first.get("verification_verdict") == truth
    return out


def bank_stats(first_turn: dict[str, bool] | None = None) -> dict:
    ft = first_turn if first_turn is not None else first_turn_correctness()
    n = len(ft)
    correct = sum(1 for v in ft.values() if v)
    return {"packets": n, "first_turn_correct": correct, "rate": (correct / n) if n else None}


def _binomial_upper_tail(n: int, k: int, p: float) -> float | None:
    if n <= 0 or p < 0 or p > 1:
        return None
    return sum(
        math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
        for i in range(k, n + 1)
    )


def skew_check(sample_ids: list[str], alpha: float = 0.05) -> dict:
    """Falsified when the sample is statistically easier than the bank.

    Uses an exact one-sided binomial upper-tail test against the frozen bank
    first-turn correctness rate. This avoids additive thresholds that can rise
    above 1.0 and become unfailable at small n.
    """
    ft = first_turn_correctness()
    bank = bank_stats(ft)
    sample = {pid: ft[pid] for pid in sample_ids if pid in ft}
    missing = [pid for pid in sample_ids if pid not in ft]
    n = len(sample)
    k = sum(1 for v in sample.values() if v)
    rate = (k / n) if n else None
    p_value = _binomial_upper_tail(n, k, bank["rate"]) if n and bank["rate"] is not None else None
    skewed = (
        rate is not None
        and bank["rate"] is not None
        and rate > bank["rate"]
        and p_value is not None
        and p_value < alpha
    )
    return {
        "bank": bank,
        "sample_packets": n,
        "sample_first_turn_correct": k,
        "sample_rate": rate,
        "sample_ids_missing_from_traces": missing,
        "alpha": alpha,
        "one_sided_binomial_p_value": p_value,
        "skew_violation": bool(skewed),
    }


def find_canary_manifest() -> Path | None:
    hits = sorted(BENCH.rglob("*blind*canary*manifest*.json"))
    return hits[0] if hits else None
