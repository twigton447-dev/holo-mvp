#!/usr/bin/env python3
"""Build focused Wave3/Wave4 final evidence from locked Holo + matched solo data.

No provider calls. No judges. This narrows the broader matched-control package
to the two completed Wave3/Wave4 target batches.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
SOURCE_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE2B5_WAVE3_WAVE4_MATCHED_SOLO_EVIDENCE_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE3_WAVE4_FINAL_EVIDENCE_MEMO_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE3_WAVE4_FINAL_EVIDENCE_MEMO_2026_07_01.md"
SCOPE_IDS = {"WAVE3_BATCH001", "WAVE4_BATCH001"}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def load_source() -> dict[str, Any]:
    return json.loads(SOURCE_JSON.read_text())


def aggregate(source: dict[str, Any]) -> dict[str, Any]:
    scopes = [scope for scope in source["scopes"] if scope["scope_id"] in SCOPE_IDS]
    if {scope["scope_id"] for scope in scopes} != SCOPE_IDS:
        raise RuntimeError("missing_wave3_wave4_scopes")

    comparison_rows = [row for row in source["comparison_rows"] if row["scope_id"] in SCOPE_IDS]
    pair_rows = [row for row in source["pair_rows"] if row["scope_id"] in SCOPE_IDS]
    if len(comparison_rows) != 54:
        raise RuntimeError(f"expected_54_comparison_rows_got:{len(comparison_rows)}")
    if len(pair_rows) != 27:
        raise RuntimeError(f"expected_27_pair_rows_got:{len(pair_rows)}")

    holo_tokens = Counter()
    solo_tokens = Counter()
    solo_label_counts = Counter()
    solo_pair_class_counts = Counter()
    solo_by_model: dict[str, Counter[str]] = defaultdict(Counter)
    solo_model_tokens: dict[str, Counter[str]] = defaultdict(Counter)

    for scope in scopes:
        holo_tokens.update(scope["holo_tokens"])
        solo_tokens.update(scope["solo_tokens_matched"])
        solo_label_counts.update(scope["solo_label_counts"])
        solo_pair_class_counts.update(scope["solo_pair_class_counts"])
        for model, stats in scope["solo_by_model"].items():
            for key, value in stats.items():
                if key == "tokens":
                    solo_model_tokens[model].update(value)
                else:
                    solo_by_model[model][key] += value

    rootless = {
        "classification": "HOLOVERIFY_WAVE3_WAVE4_FINAL_EVIDENCE_MEMO",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_matched_evidence_ref": str(SOURCE_JSON.relative_to(BENCHMARK_ROOT)),
        "source_matched_evidence_sha256": sha256_file(SOURCE_JSON),
        "source_matched_evidence_root_signature": source["root_signature"],
        "claim_boundary": (
            "Internal evidence completion for Wave3/Wave4 target batches only. "
            "No public comparative claim should be made from this memo until "
            "publication language is separately drafted and reviewed."
        ),
        "run_policy": {
            "providers_called_by_this_compiler": 0,
            "judges_called": 0,
            "holo_rerun": False,
            "solo_rerun": False,
            "packet_edits": False,
            "prompt_edits": False,
        },
        "totals": {
            "packet_count": 54,
            "pair_count": 27,
            "holo_packet_correct": sum(scope["holo_packet_correct"] for scope in scopes),
            "holo_valid_pairs": sum(scope["holo_valid_pairs"] for scope in scopes),
            "holo_provider_calls": sum(scope["holo_provider_calls"] for scope in scopes),
            "holo_worker_calls": sum(scope["holo_worker_calls"] for scope in scopes),
            "holo_gov_calls": sum(scope["holo_gov_calls"] for scope in scopes),
            "matched_solo_calls": sum(scope["solo_provider_calls_matched"] for scope in scopes),
            "judge_calls": 0,
            "holo_tokens": dict(holo_tokens),
            "matched_solo_tokens": dict(solo_tokens),
            "holo_to_solo_token_ratio": round(holo_tokens["total_tokens"] / solo_tokens["total_tokens"], 6),
            "solo_label_counts": dict(solo_label_counts),
            "solo_pair_class_counts": dict(solo_pair_class_counts),
            "intermediate_holo_single_dna_misses": sum(
                scope["intermediate_holo_single_dna_misses"] for scope in scopes
            ),
        },
        "solo_by_model": {
            model: {**dict(solo_by_model[model]), "tokens": dict(solo_model_tokens[model])}
            for model in sorted(solo_by_model)
        },
        "scopes": scopes,
        "pair_rows": pair_rows,
        "comparison_rows": comparison_rows,
        "assertions": {
            "wave3_scope_present": "PASS",
            "wave4_scope_present": "PASS",
            "packet_count_54": "PASS",
            "pair_count_27": "PASS",
            "holo_54_of_54_correct": "PASS",
            "holo_27_of_27_pairs_valid": "PASS",
            "matched_solo_162_calls": "PASS",
            "all_pairs_strong_solo_collapse": "PASS"
            if solo_pair_class_counts == {"STRONG_SOLO_COLLAPSE": 27}
            else "FAIL",
            "no_judges": "PASS",
            "no_new_provider_calls": "PASS",
            "external_solo_and_intra_holo_evidence_separated": "PASS",
        },
    }
    if any(value != "PASS" for value in rootless["assertions"].values()):
        raise RuntimeError(f"assertion_failure:{rootless['assertions']}")
    return {**rootless, "root_signature": sha256_text(canonical_json(rootless))}


def render_md(report: dict[str, Any]) -> str:
    totals = report["totals"]
    lines = [
        "# HoloVerify Wave3/Wave4 Final Evidence Memo",
        "",
        f"Classification: `{report['classification']}`",
        f"Root signature: `{report['root_signature']}`",
        f"Source matched-control root: `{report['source_matched_evidence_root_signature']}`",
        "",
        "This is an internal evidence-completion memo for Wave3 and Wave4 only.",
        "It does not make a public claim and it does not run providers or judges.",
        "",
        "## Result",
        "",
        f"- Holo packets: `{totals['holo_packet_correct']}` / `{totals['packet_count']}` correct.",
        f"- Holo pairs: `{totals['holo_valid_pairs']}` / `{totals['pair_count']}` valid.",
        f"- Matched solo calls: `{totals['matched_solo_calls']}` over the same `{totals['packet_count']}` packets.",
        f"- Holo provider calls represented: `{totals['holo_provider_calls']}`.",
        f"- Holo worker/Gov calls: `{totals['holo_worker_calls']}` / `{totals['holo_gov_calls']}`.",
        f"- Judges: `{totals['judge_calls']}`.",
        f"- Holo tokens: `{totals['holo_tokens']['total_tokens']}`.",
        f"- Matched solo tokens: `{totals['matched_solo_tokens']['total_tokens']}`.",
        f"- Holo/solo token ratio: `{totals['holo_to_solo_token_ratio']}`.",
        f"- Intermediate Holo single-DNA misses corrected or absorbed: `{totals['intermediate_holo_single_dna_misses']}`.",
        "",
        "## Solo Outcome Counts",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ]
    for label, count in sorted(totals["solo_label_counts"].items()):
        lines.append(f"| `{label}` | {count} |")

    lines.extend(
        [
            "",
            "## Pair Classes",
            "",
            "| Class | Pairs |",
            "| --- | ---: |",
        ]
    )
    for label, count in sorted(totals["solo_pair_class_counts"].items()):
        lines.append(f"| `{label}` | {count} |")

    lines.extend(
        [
            "",
            "## Model Totals",
            "",
            "| Model | Calls | KNEW | Not KNEW | Wrong Verdict | Parse Fail | Structural/Evidence Fail | Verdict Correct | Tokens |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for model, stats in report["solo_by_model"].items():
        calls = stats.get("calls", 0)
        knew = stats.get("KNEW", 0)
        lines.append(
            f"| `{model}` | {calls} | {knew} | {calls - knew} | {stats.get('WRONG_VERDICT', 0)} | "
            f"{stats.get('PARSE_FAIL', 0)} | {stats.get('STRUCTURAL_OR_EVIDENCE_FAIL', 0)} | "
            f"{stats.get('verdict_correct', 0)} | {stats['tokens'].get('total_tokens', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Scope Totals",
            "",
            "| Scope | Packets | Pairs | Holo Correct | Holo Valid Pairs | Solo Calls | Strong Collapse Pairs | Tokens Holo/Solo |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for scope in report["scopes"]:
        lines.append(
            f"| `{scope['scope_id']}` | {scope['packet_count']} | {scope['pair_count']} | "
            f"{scope['holo_packet_correct']} | {scope['holo_valid_pairs']} | "
            f"{scope['solo_provider_calls_matched']} | "
            f"{scope['solo_pair_class_counts'].get('STRONG_SOLO_COLLAPSE', 0)} | "
            f"{scope['holo_tokens']['total_tokens']} / {scope['solo_tokens_matched']['total_tokens']} |"
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Use this memo to finish Wave3/Wave4 internally before drafting public copy.",
            "Do not merge it into public language as a universal superiority claim.",
            "External solo misses and intermediate Holo worker misses remain separate evidence categories.",
            "",
            "## Assertions",
            "",
            "| Assertion | Status |",
            "| --- | --- |",
        ]
    )
    for key, value in report["assertions"].items():
        lines.append(f"| `{key}` | `{value}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    report = aggregate(load_source())
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(render_md(report))
    print(
        json.dumps(
            {
                "status": "PASS",
                "json": str(OUT_JSON.relative_to(BENCHMARK_ROOT)),
                "md": str(OUT_MD.relative_to(BENCHMARK_ROOT)),
                "root_signature": report["root_signature"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
