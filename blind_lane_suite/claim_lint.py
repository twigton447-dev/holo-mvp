"""T7 - public claim-scope lint.

Falsifies: "no rate claim will be derived from the canary."

ERROR: a ratio with denominator <= CANARY_MAX_DENOMINATOR in the same
sentence as a blind-lane keyword on a public surface.
WARNING: such a ratio within a proximity window (human review, not failure).
ERROR: canary spec lacking a pre-registered stopping rule / full-run size.

Passing does NOT validate any claim; this lint only blocks premature ones.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import BENCH, CANARY_MAX_DENOMINATOR, FRONTEND, ROOT

RATIO_RE = re.compile(r"\b(\d{1,4})\s*/\s*(\d{1,4})\b")
BLIND_KEYWORDS = ("blind-gate", "blind gate", "blind lane", "blind-lane", "blind canary", "canary")
WINDOW = 400

PUBLIC_SURFACES = [
    FRONTEND / "benchmark.html",
    FRONTEND / "benchmark-v2.html",
    FRONTEND / "benchmark-v3.html",
    FRONTEND / "whitepaper.html",
    ROOT / "KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF_2026_06_29.md",
    BENCH / "BENCHMARK_PAGE_V7_52_DRAFT_2026_07_01.md",
]

CANARY_SPEC = BENCH / "HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.md"


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def _sentences(text: str) -> list[str]:
    return re.split(r"(?<=[.!?])\s+|\n{2,}", text)


def lint_text(text: str, source: str, max_denominator: int = CANARY_MAX_DENOMINATOR) -> dict:
    text = _strip_tags(text)
    errors, warnings = [], []
    for sent in _sentences(text):
        low = sent.lower()
        if not any(kw in low for kw in BLIND_KEYWORDS):
            continue
        for m in RATIO_RE.finditer(sent):
            denom = int(m.group(2))
            if 0 < denom <= max_denominator:
                errors.append({"source": source, "ratio": m.group(0), "sentence": sent.strip()[:200]})
    low_all = text.lower()
    for kw in BLIND_KEYWORDS:
        for hit in re.finditer(re.escape(kw), low_all):
            seg = text[max(0, hit.start() - WINDOW): hit.end() + WINDOW]
            for m in RATIO_RE.finditer(seg):
                denom = int(m.group(2))
                if 0 < denom <= max_denominator:
                    warnings.append({"source": source, "keyword": kw, "ratio": m.group(0)})
    return {"errors": errors, "warnings": warnings[:50]}


def lint_public_surfaces(max_denominator: int = CANARY_MAX_DENOMINATOR) -> dict:
    errors, warnings, scanned = [], [], []
    for path in PUBLIC_SURFACES:
        if not path.exists():
            continue
        scanned.append(str(path))
        result = lint_text(path.read_text(errors="replace"), source=str(path), max_denominator=max_denominator)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])
    return {"surfaces_scanned": scanned, "errors": errors, "warnings": warnings}


def lint_canary_spec(spec_path: Path | str = CANARY_SPEC) -> dict:
    spec_path = Path(spec_path)
    if not spec_path.exists():
        return {"present": False, "missing": ["spec_file"]}
    low = spec_path.read_text(errors="replace").lower()
    missing = []
    # A mere mention (e.g., a table describing this very lint) does not count.
    # Require a heading or a definition line that states the rule.
    if not re.search(r"(?m)^#+ .*stopping rule|^\s*stopping rule\s*:", low):
        missing.append("pre_registered_stopping_rule")
    if not re.search(r"(full[- ]run|full family|larger blind-gate family)[^.\n]{0,120}\d{2,}", low):
        missing.append("pre_registered_full_run_size")
    return {"present": True, "path": str(spec_path), "missing": missing}
