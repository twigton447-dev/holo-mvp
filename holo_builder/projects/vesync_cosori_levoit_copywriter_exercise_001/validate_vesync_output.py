#!/usr/bin/env python3
"""Validate VeSync copywriter JSON artifacts for schema shape and word count."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def compare_shape(template: Any, candidate: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(template, dict):
        if not isinstance(candidate, dict):
            return [f"{path}: expected object"]
        template_keys = set(template)
        candidate_keys = set(candidate)
        for key in sorted(template_keys - candidate_keys):
            errors.append(f"{path}.{key}: missing key")
        for key in sorted(candidate_keys - template_keys):
            errors.append(f"{path}.{key}: extra key")
        for key in sorted(template_keys & candidate_keys):
            errors.extend(compare_shape(template[key], candidate[key], f"{path}.{key}"))
    elif isinstance(template, list):
        if not isinstance(candidate, list):
            errors.append(f"{path}: expected list")
    elif not isinstance(candidate, str):
        errors.append(f"{path}: expected string")
    return errors


def nonempty_string_checks(candidate: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def walk(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, f"{path}.{k}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"{path}: empty string")

    for key in (
        "assignment_id",
        "product",
        "section_1_meta_ads",
        "section_2_website_banners",
        "section_3_email",
    ):
        walk(candidate.get(key), f"$.{key}")
    return errors


def validate(path: Path, schema_path: Path) -> int:
    schema = json.loads(schema_path.read_text())
    candidate = json.loads(path.read_text())

    errors = compare_shape(schema, candidate)
    errors.extend(nonempty_string_checks(candidate))

    body = candidate.get("section_3_email", {}).get("body", "")
    body_words = word_count(body)
    if body_words < 100 or body_words > 150:
        errors.append(
            f"$.section_3_email.body: {body_words} words, expected 100-150"
        )

    ps_words = word_count(candidate.get("section_3_email", {}).get("ps", ""))
    print(json.dumps({
        "artifact": str(path),
        "schema": str(schema_path),
        "email_body_words": body_words,
        "ps_words": ps_words,
        "passed": not errors,
        "errors": errors,
    }, indent=2))
    return 0 if not errors else 1


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(
            "usage: validate_vesync_output.py ARTIFACT_JSON [SCHEMA_JSON]",
            file=sys.stderr,
        )
        return 2
    artifact = Path(argv[1])
    schema = Path(argv[2]) if len(argv) == 3 else Path(__file__).with_name("05_output_schema.json")
    return validate(artifact, schema)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
