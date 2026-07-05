#!/usr/bin/env python3
"""
Canonical validator for D11-lock full gated 100-point benchmark judgments.

This module is intentionally local and provider-free. It does not judge artifact
quality itself. It decides whether a saved judge output is allowed to count as
an official benchmark judgment.

Official means all of the following are true:
  - local deterministic audit evidence is present for both blind artifacts
  - the judge used the canonical artifact_a/artifact_b schema
  - both artifacts contain all four 25-point ledgers
  - each total equals the sum of the four ledgers
  - deterministic admissibility matches the local audit
  - an inadmissible artifact cannot be eligible for the official win
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


ARTIFACT_KEYS = ("artifact_a", "artifact_b")

BLIND_KEYS_BY_ARTIFACT = {
    "artifact_a": "A",
    "artifact_b": "B",
}

SCORE_FIELDS = (
    "deterministic_score_25",
    "epistemic_score_25",
    "structural_score_25",
    "argument_score_25",
)

FINDING_FIELDS = (
    "deterministic_findings",
    "epistemic_findings",
    "structural_findings",
    "argument_findings",
)

REQUIRED_TOP_LEVEL_PARSED_FIELDS = (
    "official_winner",
    "argument_quality_winner",
    "winner_reason",
    "confidence",
    "official_judgment_valid",
    "rubric_compliance_note",
)


@dataclass(frozen=True)
class FullGatedValidation:
    official_valid: bool
    classification: str
    failures: list[str]
    official_winner_key: str | None
    argument_quality_winner_key: str | None
    artifact_scores: dict[str, dict[str, Any]]


def _parsed_payload(judgment: Mapping[str, Any]) -> Mapping[str, Any]:
    parsed = judgment.get("parsed_json", judgment)
    if not isinstance(parsed, Mapping):
        return {}
    return parsed


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _artifact_failures(
    artifact_key: str,
    artifact: Mapping[str, Any],
    local_audit: Mapping[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    failures: list[str] = []
    score_report: dict[str, Any] = {}

    for field in SCORE_FIELDS:
        value = artifact.get(field)
        if not _is_number(value):
            failures.append(f"{artifact_key}.{field}: missing_or_not_numeric")
            continue
        if not 0 <= float(value) <= 25:
            failures.append(f"{artifact_key}.{field}: out_of_25_range")
        score_report[field] = float(value)

    total = artifact.get("total_score_100")
    if not _is_number(total):
        failures.append(f"{artifact_key}.total_score_100: missing_or_not_numeric")
    else:
        total_float = float(total)
        score_report["total_score_100"] = total_float
        computed = sum(float(artifact.get(field, 0)) for field in SCORE_FIELDS if _is_number(artifact.get(field)))
        score_report["computed_total_score_100"] = computed
        if not 0 <= total_float <= 100:
            failures.append(f"{artifact_key}.total_score_100: out_of_100_range")
        if abs(total_float - computed) > 0.001:
            failures.append(f"{artifact_key}.total_score_100: does_not_equal_four_ledgers")

    for field in FINDING_FIELDS:
        value = artifact.get(field)
        if not isinstance(value, list) or not value:
            failures.append(f"{artifact_key}.{field}: missing_or_empty")

    for field in ("score_caps", "critical_failures"):
        if not isinstance(artifact.get(field), list):
            failures.append(f"{artifact_key}.{field}: missing_or_not_list")

    local_admissible = local_audit.get("admissible")
    artifact_admissible = artifact.get("admissible_under_local_deterministic_gate")
    eligible = artifact.get("officially_eligible_for_win")

    if not isinstance(local_admissible, bool):
        failures.append(f"{artifact_key}.local_audit.admissible: missing_or_not_bool")
    if not isinstance(artifact_admissible, bool):
        failures.append(f"{artifact_key}.admissible_under_local_deterministic_gate: missing_or_not_bool")
    if not isinstance(eligible, bool):
        failures.append(f"{artifact_key}.officially_eligible_for_win: missing_or_not_bool")

    if isinstance(local_admissible, bool) and isinstance(artifact_admissible, bool):
        if artifact_admissible != local_admissible:
            failures.append(f"{artifact_key}.admissible_under_local_deterministic_gate: contradicts_local_audit")

    if local_admissible is False:
        if eligible is not False:
            failures.append(f"{artifact_key}.officially_eligible_for_win: inadmissible_artifact_marked_eligible")
        det_score = artifact.get("deterministic_score_25")
        if _is_number(det_score) and float(det_score) > 15:
            failures.append(f"{artifact_key}.deterministic_score_25: inadmissible_score_above_15_cap")
        if not artifact.get("score_caps"):
            failures.append(f"{artifact_key}.score_caps: inadmissible_artifact_missing_score_cap")

    if local_admissible is True and eligible is not True:
        failures.append(f"{artifact_key}.officially_eligible_for_win: admissible_artifact_marked_ineligible")

    score_report["local_audit"] = dict(local_audit)
    score_report["admissible_under_local_deterministic_gate"] = artifact_admissible
    score_report["officially_eligible_for_win"] = eligible
    score_report["score_caps"] = artifact.get("score_caps")
    score_report["critical_failures"] = artifact.get("critical_failures")
    return failures, score_report


def validate_full_gated_judgment(judgment: Mapping[str, Any]) -> FullGatedValidation:
    """Return whether a saved judgment is official under the D11-lock rule."""
    failures: list[str] = []
    parsed = _parsed_payload(judgment)

    local_audit = judgment.get("local_deterministic_audit_by_blind")
    if not isinstance(local_audit, Mapping):
        failures.append("local_deterministic_audit_by_blind: missing_or_not_object")
        local_audit = {}
    else:
        for blind_key in ("A", "B"):
            if blind_key not in local_audit or not isinstance(local_audit.get(blind_key), Mapping):
                failures.append(f"local_deterministic_audit_by_blind.{blind_key}: missing_or_not_object")

    for field in REQUIRED_TOP_LEVEL_PARSED_FIELDS:
        if field not in parsed:
            failures.append(f"parsed_json.{field}: missing")

    if parsed.get("official_judgment_valid") is not True:
        failures.append("parsed_json.official_judgment_valid: not_true")

    artifact_scores: dict[str, dict[str, Any]] = {}
    for artifact_key in ARTIFACT_KEYS:
        artifact = parsed.get(artifact_key)
        if not isinstance(artifact, Mapping):
            failures.append(f"parsed_json.{artifact_key}: missing_or_not_object")
            continue
        blind_key = BLIND_KEYS_BY_ARTIFACT[artifact_key]
        audit_entry = local_audit.get(blind_key, {}) if isinstance(local_audit, Mapping) else {}
        artifact_failures, score_report = _artifact_failures(artifact_key, artifact, audit_entry)
        failures.extend(artifact_failures)
        artifact_scores[artifact_key] = score_report

    official_winner = parsed.get("official_winner")
    argument_quality_winner = parsed.get("argument_quality_winner")

    if official_winner not in ARTIFACT_KEYS:
        failures.append("parsed_json.official_winner: must_be_artifact_a_or_artifact_b")
    if argument_quality_winner not in ARTIFACT_KEYS:
        failures.append("parsed_json.argument_quality_winner: must_be_artifact_a_or_artifact_b")

    if official_winner in ARTIFACT_KEYS and artifact_scores:
        winner_score = artifact_scores.get(official_winner, {})
        if winner_score.get("officially_eligible_for_win") is not True:
            failures.append("parsed_json.official_winner: selected_artifact_not_officially_eligible")

        eligible_scores = {
            key: value.get("total_score_100")
            for key, value in artifact_scores.items()
            if value.get("officially_eligible_for_win") is True
            and _is_number(value.get("total_score_100"))
        }
        if eligible_scores:
            max_score = max(float(value) for value in eligible_scores.values())
            winner_total = winner_score.get("total_score_100")
            if not _is_number(winner_total) or float(winner_total) < max_score - 0.001:
                failures.append("parsed_json.official_winner: lower_than_best_eligible_total")
        else:
            failures.append("parsed_json.official_winner: no_eligible_artifact_exists")

    for field in ("winner_reason", "confidence", "rubric_compliance_note"):
        if field in parsed and not str(parsed.get(field, "")).strip():
            failures.append(f"parsed_json.{field}: empty")

    official_valid = not failures
    classification = (
        "OFFICIAL_FULL_GATED_100PT_VALID"
        if official_valid
        else "DIAGNOSTIC_ONLY_INVALID_FULL_GATED_100PT"
    )
    return FullGatedValidation(
        official_valid=official_valid,
        classification=classification,
        failures=failures,
        official_winner_key=official_winner if official_winner in ARTIFACT_KEYS else None,
        argument_quality_winner_key=(
            argument_quality_winner if argument_quality_winner in ARTIFACT_KEYS else None
        ),
        artifact_scores=artifact_scores,
    )


def validate_full_gated_judgment_file(path: str | Path) -> FullGatedValidation:
    with Path(path).open("r", encoding="utf-8") as fh:
        judgment = json.load(fh)
    return validate_full_gated_judgment(judgment)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate whether a D11-lock full gated 100-point judge result is official."
    )
    parser.add_argument("judgment_json", help="Path to a saved judge result JSON file")
    args = parser.parse_args()

    result = validate_full_gated_judgment_file(args.judgment_json)
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.official_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
