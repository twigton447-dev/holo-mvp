from __future__ import annotations

import re
import json
from pathlib import Path
from typing import Any


FINAL_PUNCTUATION = ('.', '!', '?', ')', ']', '"', "'")
TRAILING_MARKDOWN_MARKERS = ('*', '_', '`')
PROCESS_RESIDUE_PATTERNS = (
    r'\bprobe\s+\d+\s+answered\b',
    r'\bturn\s+\d+\s+mission\b',
    r'\bgovernor mission packet\b',
    r'\bcurrent_best_state\b',
    r'\bnext_role_objective\b',
    r'\bhighest_value_flaw\b',
    r'\btechnical_probe_questions\b',
    r'\brepair_ledger\b',
    r'\bhidden_failure_probes\b',
    r'\bwinning_features_to_preserve\b',
    r'\bconvergence_target\b',
)
DISCLAIMER_PATTERNS = (
    r'not\s+investment\s+advice',
    r'does\s+not\s+recommend\s+(buying|selling|any\s+transaction)',
)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def ends_cleanly(text: str) -> bool:
    stripped = text.rstrip()
    if not stripped:
        return False
    if stripped.endswith(FINAL_PUNCTUATION):
        return True
    stripped = stripped.rstrip(''.join(TRAILING_MARKDOWN_MARKERS))
    if stripped.endswith(FINAL_PUNCTUATION):
        return True
    return bool(re.search(r'```$', stripped))


def _has_any(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _source_tokens(text: str) -> set[str]:
    return set(re.findall(r'\bS\d+(?:_[A-Z0-9_]+)?\b', text))


def _required_item_present(item: str, text: str) -> bool:
    normalized = re.sub(r'[^a-z0-9]+', ' ', item.lower()).strip()
    if not normalized:
        return True
    words = [word for word in normalized.split() if len(word) > 2]
    if not words:
        return True
    haystack = re.sub(r'[^a-z0-9]+', ' ', text.lower())
    return all(word in haystack for word in words)


def context_allowed_source_ids(context: dict[str, Any]) -> set[str] | None:
    tokens = set(re.findall(r'\bS\d+(?:_[A-Z0-9_]+)?\b', json.dumps(context)))
    return tokens or None


def context_required_items(context: dict[str, Any]) -> list[str]:
    deliverable = context.get('deliverable', {})
    items = deliverable.get('must_include')
    if items is None:
        items = context.get('deliverable_requirements', {}).get('must_include', [])
    if isinstance(items, list):
        return [str(item) for item in items]
    return []


def context_requires_disclaimer(context: dict[str, Any]) -> bool:
    text = json.dumps(context, sort_keys=True).lower()
    triggers = (
        'investment advice',
        'buying',
        'selling',
        'buy/sell',
        'security recommendation',
        'brokerage access',
        'legal advice',
    )
    return any(trigger in text for trigger in triggers)


def context_word_bounds(context: dict[str, Any], fallback_max_words: int | None = None) -> tuple[int | None, int | None]:
    target = context.get('deliverable', {}).get('word_count_target', {})
    min_words = target.get('min')
    max_words = target.get('max', fallback_max_words)
    if min_words is None and max_words is None:
        current_event_target = context.get('deliverable_requirements', {}).get('target_length_words')
        if isinstance(current_event_target, list) and len(current_event_target) >= 2:
            min_words, max_words = current_event_target[0], current_event_target[1]
    return (
        int(min_words) if min_words else None,
        int(max_words) if max_words else None,
    )


def artifact_validity_report(
    artifact_path: Path,
    *,
    min_words: int | None = None,
    max_words: int | None = None,
    allowed_source_ids: set[str] | None = None,
    required_items: list[str] | None = None,
    require_disclaimer: bool = False,
    require_clean_final: bool = False,
) -> dict[str, Any]:
    text = artifact_path.read_text(encoding='utf-8') if artifact_path.exists() else ''
    words = word_count(text)
    flags: list[str] = []

    if not artifact_path.exists():
        flags.append('artifact_missing')
    elif artifact_path.stat().st_size <= 0:
        flags.append('artifact_empty')
    if require_clean_final and not ends_cleanly(text):
        flags.append('artifact_ends_uncleanly')
    if min_words is not None and words < min_words:
        flags.append('word_count_below_min')
    if max_words is not None and words > max_words:
        flags.append('word_count_above_max')
    if _has_any(PROCESS_RESIDUE_PATTERNS, text):
        flags.append('internal_process_residue')
    if require_disclaimer and not _has_any(DISCLAIMER_PATTERNS, text):
        flags.append('missing_required_disclaimer')
    if allowed_source_ids is not None:
        unknown = sorted(_source_tokens(text) - allowed_source_ids)
        if unknown:
            flags.append('unknown_source_ids')
    else:
        unknown = []
    missing_items = [
        item for item in required_items or []
        if not _required_item_present(item, text)
    ]
    if missing_items:
        flags.append('missing_required_brief_items')

    return {
        'gate_name': 'GovArtifactValidityGate',
        'artifact_path': str(artifact_path),
        'word_count': words,
        'valid': not flags,
        'flags': flags,
        'unknown_source_ids': unknown,
        'missing_required_items': missing_items,
        'ends_cleanly': ends_cleanly(text),
    }


def gov_artifact_validity_gate(
    artifact_path: Path,
    *,
    context: dict[str, Any],
    fallback_max_words: int | None = None,
    require_clean_final: bool = True,
) -> dict[str, Any]:
    min_words, max_words = context_word_bounds(context, fallback_max_words)
    return artifact_validity_report(
        artifact_path,
        min_words=min_words,
        max_words=max_words,
        allowed_source_ids=context_allowed_source_ids(context),
        required_items=context_required_items(context),
        require_disclaimer=context_requires_disclaimer(context),
        require_clean_final=require_clean_final,
    )


def require_valid_artifact(report: dict[str, Any]) -> None:
    if not report['valid']:
        raise RuntimeError(
            'artifact_validity_failed '
            f"path={report['artifact_path']} flags={','.join(report['flags'])}"
        )
