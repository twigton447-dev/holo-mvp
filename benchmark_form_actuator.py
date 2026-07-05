#!/usr/bin/env python3
"""
Provider-free form actuator for D11-lock Holo benchmark artifacts.

This module does not judge artifact quality and does not rewrite artifact
substance. It computes hard mechanical form defects before a final worker turn
and emits an exact baton that Gov can pass to the worker.

The D12 regression lesson is the contract:

    Gov diagnosis without deterministic actuation is insufficient for hard
    admissibility gates.

The actuator therefore converts local gate facts into bounded instructions:
word count, required sections, exact section quotas, blocked moves, and the
minimum expansion/compression needed to land inside the admissible band.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


DEFAULT_WORD_MIN = 900
DEFAULT_WORD_MAX = 1300
DEFAULT_TARGET_WORDS = 1100

DEFAULT_BLOCKED_MOVES = (
    "Do not replace the artifact with notes, metadata, a rubric, or an outline.",
    "Do not add appendices, source lists, or process commentary to pad length.",
    "Do not drop unresolved dependencies from the state brief.",
    "Do not invent source IDs or cite sources that were not in the frozen packet.",
    "Do not reopen a blocked move unless Gov explicitly permits it.",
)

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class FormGateConfig:
    word_min: int = DEFAULT_WORD_MIN
    word_max: int = DEFAULT_WORD_MAX
    target_words: int = DEFAULT_TARGET_WORDS
    required_sections: tuple[str, ...] = ()
    blocked_moves: tuple[str, ...] = DEFAULT_BLOCKED_MOVES

    def __post_init__(self) -> None:
        if self.word_min < 1:
            raise ValueError("word_min must be positive")
        if self.word_max < self.word_min:
            raise ValueError("word_max must be greater than or equal to word_min")
        if not self.word_min <= self.target_words <= self.word_max:
            raise ValueError("target_words must be inside the allowed word band")


@dataclass(frozen=True)
class SectionReport:
    name: str
    normalized_name: str
    present: bool
    word_count: int
    target_words: int
    min_words: int
    max_words: int
    delta_to_target: int


@dataclass(frozen=True)
class FormActuationBaton:
    classification: str
    primary_defect: str
    failures: list[str]
    word_count: int
    word_band: dict[str, int]
    target_word_count: int
    delta_to_target: int
    minimum_change_to_enter_band: int
    section_reports: list[SectionReport]
    required_section_order: list[str]
    blocked_moves: list[str]
    final_worker_instruction: str


def count_words(text: str) -> int:
    """Count benchmark words deterministically using the local form gate rule."""
    return len(WORD_RE.findall(text or ""))


def normalize_section_name(value: str) -> str:
    """Normalize headings and required section names for exact local matching."""
    words = WORD_RE.findall(value.lower())
    return "-".join(words)


def _extract_heading_sections(text: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(text or ""))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        heading = match.group(2).strip().rstrip("#").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[normalize_section_name(heading)] = text[start:end].strip()
    return sections


def _allocate_quotas(config: FormGateConfig) -> dict[str, dict[str, int]]:
    sections = list(config.required_sections)
    if not sections:
        return {}

    count = len(sections)
    base_target = config.target_words // count
    target_remainder = config.target_words % count
    base_min = config.word_min // count
    min_remainder = config.word_min % count
    base_max = config.word_max // count
    max_remainder = config.word_max % count

    quotas: dict[str, dict[str, int]] = {}
    for index, section in enumerate(sections):
        quotas[section] = {
            "target_words": base_target + (1 if index < target_remainder else 0),
            "min_words": base_min + (1 if index < min_remainder else 0),
            "max_words": base_max + (1 if index < max_remainder else 0),
        }
    return quotas


def build_section_reports(text: str, config: FormGateConfig) -> list[SectionReport]:
    """Return deterministic section presence and quota reports."""
    extracted = _extract_heading_sections(text)
    quotas = _allocate_quotas(config)
    reports: list[SectionReport] = []

    for section in config.required_sections:
        normalized = normalize_section_name(section)
        content = extracted.get(normalized)
        word_count = count_words(content or "")
        quota = quotas.get(section, {"target_words": 0, "min_words": 0, "max_words": 0})
        reports.append(
            SectionReport(
                name=section,
                normalized_name=normalized,
                present=content is not None,
                word_count=word_count,
                target_words=quota["target_words"],
                min_words=quota["min_words"],
                max_words=quota["max_words"],
                delta_to_target=quota["target_words"] - word_count,
            )
        )

    return reports


def compute_form_failures(text: str, config: FormGateConfig) -> list[str]:
    """Compute only local mechanical failures."""
    failures: list[str] = []
    words = count_words(text)
    if words < config.word_min:
        failures.append("word_band_under")
    if words > config.word_max:
        failures.append("word_band_over")

    missing = [
        report.normalized_name
        for report in build_section_reports(text, config)
        if not report.present
    ]
    if missing:
        failures.append("missing_required_sections")
    return failures


def _primary_defect(failures: Sequence[str]) -> str:
    for candidate in (
        "missing_required_sections",
        "word_band_under",
        "word_band_over",
    ):
        if candidate in failures:
            return candidate.upper()
    return "PASS"


def _minimum_change_to_enter_band(word_count: int, config: FormGateConfig) -> int:
    if word_count < config.word_min:
        return config.word_min - word_count
    if word_count > config.word_max:
        return config.word_max - word_count
    return 0


def _section_quota_lines(reports: Sequence[SectionReport]) -> list[str]:
    return [
        (
            f"- {report.name}: target {report.target_words} words "
            f"(allowed {report.min_words}-{report.max_words}; "
            f"current {report.word_count}; delta {report.delta_to_target:+d})"
        )
        for report in reports
    ]


def _build_instruction(
    word_count: int,
    failures: Sequence[str],
    section_reports: Sequence[SectionReport],
    config: FormGateConfig,
) -> str:
    if "word_band_under" in failures:
        change_line = (
            f"Expand by at least {config.word_min - word_count} words and aim for "
            f"{config.target_words} words."
        )
    elif "word_band_over" in failures:
        change_line = (
            f"Compress by at least {word_count - config.word_max} words and aim for "
            f"{config.target_words} words."
        )
    else:
        change_line = f"Preserve the artifact inside {config.word_min}-{config.word_max} words."

    section_line = ""
    if config.required_sections:
        section_line = (
            " Use exactly these sections in this order: "
            + "; ".join(config.required_sections)
            + "."
        )

    quota_lines = _section_quota_lines(section_reports)
    quota_text = ""
    if quota_lines:
        quota_text = "\n\nSection quotas:\n" + "\n".join(quota_lines)

    blocked_text = "\n".join(f"- {move}" for move in config.blocked_moves)
    return (
        "Produce the final artifact only. "
        f"Current artifact has {word_count} words; allowed band is "
        f"{config.word_min}-{config.word_max}; target is {config.target_words}. "
        f"{change_line}{section_line}"
        f"{quota_text}\n\nBlocked moves:\n{blocked_text}"
    )


def build_form_actuation_baton(
    text: str,
    config: FormGateConfig | None = None,
) -> FormActuationBaton:
    """Build the exact deterministic baton for Gov-to-worker form control."""
    active_config = config or FormGateConfig()
    word_count = count_words(text)
    section_reports = build_section_reports(text, active_config)
    failures = compute_form_failures(text, active_config)
    classification = (
        "FORM_ACTUATION_REQUIRED"
        if failures
        else "FORM_ACTUATION_NOT_REQUIRED"
    )

    return FormActuationBaton(
        classification=classification,
        primary_defect=_primary_defect(failures),
        failures=failures,
        word_count=word_count,
        word_band={"min": active_config.word_min, "max": active_config.word_max},
        target_word_count=active_config.target_words,
        delta_to_target=active_config.target_words - word_count,
        minimum_change_to_enter_band=_minimum_change_to_enter_band(word_count, active_config),
        section_reports=section_reports,
        required_section_order=list(active_config.required_sections),
        blocked_moves=list(active_config.blocked_moves),
        final_worker_instruction=_build_instruction(
            word_count,
            failures,
            section_reports,
            active_config,
        ),
    )


def _config_from_mapping(payload: Mapping[str, Any]) -> FormGateConfig:
    return FormGateConfig(
        word_min=int(payload.get("word_min", DEFAULT_WORD_MIN)),
        word_max=int(payload.get("word_max", DEFAULT_WORD_MAX)),
        target_words=int(payload.get("target_words", DEFAULT_TARGET_WORDS)),
        required_sections=tuple(str(item) for item in payload.get("required_sections", ())),
        blocked_moves=tuple(str(item) for item in payload.get("blocked_moves", DEFAULT_BLOCKED_MOVES)),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a provider-free D11-lock form actuation baton."
    )
    parser.add_argument("artifact_markdown", help="Path to artifact markdown/text")
    parser.add_argument(
        "--config-json",
        help="Optional JSON file with word_min, word_max, target_words, required_sections.",
    )
    args = parser.parse_args()

    text = Path(args.artifact_markdown).read_text(encoding="utf-8")
    config = FormGateConfig()
    if args.config_json:
        config_payload = json.loads(Path(args.config_json).read_text(encoding="utf-8"))
        config = _config_from_mapping(config_payload)

    baton = build_form_actuation_baton(text, config)
    print(json.dumps(asdict(baton), indent=2, sort_keys=True))
    return 0 if baton.classification == "FORM_ACTUATION_NOT_REQUIRED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
