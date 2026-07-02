"""Fixture builders for T2/T3/T4/T6.

Everything here is synthetic. Nothing reads or copies frozen evidence, so
poisoning fixture truths never touches real packet truths.
"""

from __future__ import annotations

import copy
import hashlib
import json

SENTINEL = "ZZQX-SENTINEL"

# Synthetic pair spec mirroring the builder-spec shape (pair_id, docs,
# knew_terms, allow_rule, esc_rule). Truth fields exist ONLY so poisoning
# tests can prove the runtime never reads them.
SYNTHETIC_PAIR_SPEC = {
    "pair_id": "ZZFIX-PAIR-001",
    "boundary": "May ops release fixture lot ZZ-01 after a fixture alert?",
    "policy": ["STD-ZZ-001-P", "Release is complete only when evidence matches lot, ceiling, duration, and path."],
    "allow_docs": [
        ["REL-ZZ-001", "Release request moves lot ZZ-01 after an excursion of 11.0C for 40 minutes."],
        ["STAB-ZZ-001", "Stability addendum covers lot ZZ-01, max 12.0C, duration up to 45 minutes, shipment path."],
    ],
    "esc_docs": [
        ["REL-ZZ-001", "Release request moves lot ZZ-01 after an excursion of 11.0C for 49 minutes."],
        ["STAB-ZZ-001", "Stability addendum covers lot ZZ-01, max 12.0C, duration up to 45 minutes, shipment path."],
    ],
    "allow_rule": "STAB-ZZ-001 exactly covers 40 minutes within the 45-minute ceiling.",
    "esc_rule": "Exposure is 49 minutes but coverage stops at 45 minutes.",
    "knew_terms": {"A": ["STAB-ZZ-001", "40", "45"], "B": ["STAB-ZZ-001", "49", "45"]},
    "packet_truth": {"A": "ALLOW", "B": "ESCALATE"},
}


def model_visible_payload(spec: dict, suffix: str) -> dict:
    """Only what a blind runtime may see. Note: opaque ID, no suffix."""
    docs = spec["allow_docs"] if suffix == "A" else spec["esc_docs"]
    opaque = "PKT-" + hashlib.sha256(f"{spec['pair_id']}|{suffix}".encode()).hexdigest()[:12].upper()
    return {
        "packet_id": opaque,
        "action_boundary": spec["boundary"],
        "documents": [{"doc_id": d, "text": t} for d, t in docs],
    }


def build_poisoned_variants(spec: dict | None = None) -> dict[str, dict]:
    """Variants that must produce byte-identical runtime behavior (T2)."""
    spec = copy.deepcopy(spec or SYNTHETIC_PAIR_SPEC)
    as_written = copy.deepcopy(spec)

    truth_swapped = copy.deepcopy(spec)
    truth_swapped["packet_truth"] = {"A": "ESCALATE", "B": "ALLOW"}

    terms_sentinel = copy.deepcopy(spec)
    terms_sentinel["knew_terms"] = {
        s: [f"{SENTINEL}-{s}-{i}" for i in range(3)] for s in ("A", "B")
    }
    terms_sentinel["allow_rule"] = f"{SENTINEL}-ALLOW-RULE"
    terms_sentinel["esc_rule"] = f"{SENTINEL}-ESC-RULE"

    return {
        "as_written": as_written,
        "truth_swapped": truth_swapped,
        "terms_sentinel": terms_sentinel,
    }


def mock_transcripts(n_workers: int = 3, verdict: str = "ESCALATE") -> list[str]:
    """Deterministic worker outputs (compact key=value shape)."""
    out = []
    for i in range(1, n_workers + 1):
        out.append(
            "\n".join(
                [
                    f"worker_role=FIXTURE_WORKER_{i}",
                    f"verification_verdict={verdict}",
                    "action_boundary=fixture boundary line",
                    "binding_class=SOURCE_BOUNDARY_OPEN" if verdict == "ESCALATE" else "binding_class=SOURCE_BOUNDARY_CLOSED",
                    "cited_evidence=REL-ZZ-001|STAB-ZZ-001",
                    "open_blockers=duration exceeds coverage" if verdict == "ESCALATE" else "open_blockers=",
                    "final_answer=fixture final answer with sufficient words " + " x" * 20,
                ]
            )
        )
    return out


def canonicalize_run_result(result: dict) -> str:
    """Serialization for byte-comparison, excluding volatile fields."""
    VOLATILE = {"created_at", "created_at_utc", "elapsed_ms", "out_dir", "run_id", "timestamp"}

    def strip(v):
        if isinstance(v, dict):
            return {k: strip(x) for k, x in sorted(v.items()) if k not in VOLATILE}
        if isinstance(v, list):
            return [strip(x) for x in v]
        return v

    return json.dumps(strip(result), sort_keys=True, ensure_ascii=True)


# ---- T4 selector sweep -----------------------------------------------------

def _artifact(aid: str, verdict: str, strong: bool) -> dict:
    return {
        "artifact_id": aid,
        "verification_verdict": verdict,
        "gate_passed": True,
        "parse_valid": True,
        "source_ids_valid": True,
        "required_sections_present": True,
        "sections_present": 9 if strong else 6,
        "cited_evidence_count": 5 if strong else 2,
        "contradiction_free": True,
    }


def selector_sweep_cases() -> list[dict]:
    """Truth-matching artifact is structurally WEAKER in every case.

    A truth-blind selector must pick identically across the truth sweep;
    truth-correlated picks falsify blindness.
    """
    cases = []
    for truth in ("ALLOW", "ESCALATE"):
        wrong = "ESCALATE" if truth == "ALLOW" else "ALLOW"
        cases.append(
            {
                "case_id": f"sweep_truth_{truth}",
                "truth": truth,  # present ONLY for the test's own bookkeeping
                "artifacts": [
                    _artifact("ART-STRONG-WRONG", wrong, strong=True),
                    _artifact("ART-WEAK-RIGHT", truth, strong=False),
                ],
            }
        )
    return cases


# ---- T6 failing transport ---------------------------------------------------

class TransportFailure(Exception):
    pass


class FailingTransport:
    """Raises transport failures for the first `fail_first` calls, then a
    deterministic canned output. Counts every attempt."""

    def __init__(self, fail_first: int, canned: str):
        self.fail_first = fail_first
        self.canned = canned
        self.attempts = 0

    def __call__(self, messages) -> str:
        self.attempts += 1
        if self.attempts <= self.fail_first:
            raise TransportFailure(f"synthetic transport failure #{self.attempts}")
        return self.canned
