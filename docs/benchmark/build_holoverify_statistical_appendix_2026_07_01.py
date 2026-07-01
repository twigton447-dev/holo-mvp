#!/usr/bin/env python3
"""Build the HoloVerify benchmark statistical appendix.

This is a no-provider compiler. It packages the current benchmark-grade
HoloVerify denominator into plain binomial statistics, confusion-matrix terms,
confidence bands, and sample-size planning.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
DOMAIN_LEDGER = (
    BENCHMARK_ROOT
    / "holoverify_domain_consolidation_ledger_2026_07_01"
    / "HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"
)
WAVE_COMBINED = BENCHMARK_ROOT / "HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
WAVE34_FINAL = BENCHMARK_ROOT / "HOLOVERIFY_WAVE3_WAVE4_FINAL_EVIDENCE_MEMO_2026_07_01.json"

OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.md"

ALPHA = 0.05
Z_95 = 1.959963984540054


INCLUDED_LEDGER_FAMILIES = {
    "Agentic Commerce / Order Execution Replication",
    "Clinical Activation Boundary Controls / Kit C",
    "IT Access / Permission Change Replication",
    "Vendor-Master Payment Controls / AP Replication",
}

EXCLUDED_LEDGER_FAMILIES = {
    "Agentic Commerce / All-Six Collapse Canary": "lock-rooted canary, useful but not benchmark-grade denominator",
    "D11-Lock HoloBuild Mini-Suite": "HoloBuild quality suite, not HoloVerify action-boundary denominator and missing repo evidence",
    "Hard ALLOW FP 5-Pair Precursor": "precursor frozen pending judge, not included in clean denominator",
    "Wave 2 / HR-Data Privacy-Finance Targeted Holo Runs": "superseded here by Wave2+Wave3+Wave4 combined evidence",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def exact_one_sided_upper_zero_errors(n: int, alpha: float = ALPHA) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    return 1.0 - alpha ** (1.0 / n)


def wilson_upper_zero_errors(n: int, z: float = Z_95) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    return (z * z) / (n + z * z)


def rule_of_three(n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    return 3.0 / n


def zero_error_n_for_upper_below(threshold: float, alpha: float = ALPHA) -> int:
    if not 0 < threshold < 1:
        raise ValueError("threshold must be between 0 and 1")
    return math.floor(math.log(alpha) / math.log(1.0 - threshold)) + 1


def pct(value: float) -> float:
    return round(value * 100.0, 6)


def rate(num: int, den: int) -> float:
    return 0.0 if den == 0 else round(num / den, 12)


def included_families_from_ledger(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    family_rows = ledger.get("compiled_evidence_families") or []
    by_name = {row["evidence_family"]: row for row in family_rows}
    missing = sorted(INCLUDED_LEDGER_FAMILIES - set(by_name))
    if missing:
        raise RuntimeError(f"missing_included_families:{missing}")
    unknown_excluded = sorted(set(EXCLUDED_LEDGER_FAMILIES) - set(by_name))
    if unknown_excluded:
        raise RuntimeError(f"missing_excluded_families:{unknown_excluded}")

    included = []
    for name in sorted(INCLUDED_LEDGER_FAMILIES):
        row = by_name[name]
        packets = row["architecture_packets"]
        correct = row["architecture_packet_correct"]
        if not isinstance(packets, int) or not isinstance(correct, int):
            raise RuntimeError(f"non_numeric_included_family:{name}")
        if packets != correct:
            raise RuntimeError(f"included_family_has_errors:{name}:{correct}/{packets}")
        if packets % 2:
            raise RuntimeError(f"included_family_not_pair_balanced:{name}:{packets}")
        included.append(
            {
                "evidence_family": name,
                "domains": row["domains"],
                "packets": packets,
                "pairs": packets // 2,
                "correct_packets": correct,
                "errors": packets - correct,
                "source": "domain_consolidation_ledger",
                "evidence_tiers": row.get("evidence_tiers") or [],
            }
        )
    return included


def excluded_families_from_ledger(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    by_name = {row["evidence_family"]: row for row in ledger.get("compiled_evidence_families") or []}
    excluded = []
    for name, reason in EXCLUDED_LEDGER_FAMILIES.items():
        row = by_name[name]
        excluded.append(
            {
                "evidence_family": name,
                "packets": row["architecture_packets"],
                "correct_packets": row["architecture_packet_correct"],
                "reason": reason,
                "evidence_tiers": row.get("evidence_tiers") or [],
            }
        )
    return sorted(excluded, key=lambda row: row["evidence_family"])


def wave_family_from_combined(wave: dict[str, Any], wave34: dict[str, Any]) -> dict[str, Any]:
    metrics = wave["metrics"]
    if metrics["holo_packets"] != 174 or metrics["holo_packets_correct_admissible"] != 174:
        raise RuntimeError("wave234_packet_denominator_mismatch")
    if metrics["holo_pairs"] != 87 or metrics["holo_valid_pairs"] != 87:
        raise RuntimeError("wave234_pair_denominator_mismatch")
    if metrics["false_positives"] != 0 or metrics["false_negatives"] != 0:
        raise RuntimeError("wave234_has_fp_or_fn")
    if wave34["totals"]["packet_count"] != 54 or wave34["totals"]["holo_packet_correct"] != 54:
        raise RuntimeError("wave34_final_mismatch")
    return {
        "evidence_family": "Wave2+Wave3+Wave4 / HR-Privacy-Finance-Government-Benefits-Banking-Defense-Insurance-Utilities",
        "domains": [
            "HR / payroll / workforce controls",
            "Data privacy / customer data release controls",
            "Finance close / revenue / expense recognition controls",
            "Government procurement / grants controls",
            "Benefits / public casework controls",
            "Banking / KYC / AML controls",
            "Defense administration / logistics controls",
            "Insurance claims / coverage controls",
            "Energy / utilities / infrastructure controls",
        ],
        "packets": metrics["holo_packets"],
        "pairs": metrics["holo_pairs"],
        "correct_packets": metrics["holo_packets_correct_admissible"],
        "errors": metrics["holo_packets"] - metrics["holo_packets_correct_admissible"],
        "source": "wave2_wave3_wave4_combined_evidence",
        "source_roots": {
            "wave_combined_package_sha256": wave.get("package_sha256"),
            "wave34_final_root_signature": wave34.get("root_signature"),
        },
    }


def build() -> dict[str, Any]:
    ledger = load_json(DOMAIN_LEDGER)
    wave = load_json(WAVE_COMBINED)
    wave34 = load_json(WAVE34_FINAL)

    included = included_families_from_ledger(ledger)
    included.append(wave_family_from_combined(wave, wave34))
    excluded = excluded_families_from_ledger(ledger)

    packets = sum(row["packets"] for row in included)
    correct = sum(row["correct_packets"] for row in included)
    errors = packets - correct
    pairs = sum(row["pairs"] for row in included)
    allow_truths = pairs
    escalate_truths = pairs

    if packets != 334 or pairs != 167:
        raise RuntimeError(f"unexpected_grand_total:{packets}_packets_{pairs}_pairs")
    if errors != 0:
        raise RuntimeError(f"unexpected_errors:{errors}")

    tp = escalate_truths
    tn = allow_truths
    fp = 0
    fn = 0

    packet_exact = exact_one_sided_upper_zero_errors(packets)
    packet_wilson = wilson_upper_zero_errors(packets)
    per_class_exact = exact_one_sided_upper_zero_errors(allow_truths)
    per_class_wilson = wilson_upper_zero_errors(allow_truths)

    sample_size_targets = []
    for threshold in (0.05, 0.025, 0.01, 0.005):
        n = zero_error_n_for_upper_below(threshold)
        sample_size_targets.append(
            {
                "target_upper_bound": threshold,
                "target_upper_bound_percent": pct(threshold),
                "zero_error_n_required_exact_one_sided": n,
                "additional_packets_needed_for_overall": max(0, n - packets),
                "additional_allow_needed_for_fpr": max(0, n - allow_truths),
                "additional_escalate_needed_for_fnr": max(0, n - escalate_truths),
                "additional_balanced_pairs_needed_for_both_fpr_and_fnr": max(0, n - pairs),
                "additional_balanced_packets_needed_for_both_fpr_and_fnr": max(0, (n - pairs) * 2),
            }
        )

    rootless = {
        "classification": "HOLOVERIFY_STATISTICAL_APPENDIX_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_without_provider_calls": True,
        "source_paths": {
            "domain_consolidation_ledger": str(DOMAIN_LEDGER.relative_to(BENCHMARK_ROOT)),
            "domain_consolidation_ledger_sha256": sha256_file(DOMAIN_LEDGER),
            "wave2_wave3_wave4_combined_evidence": str(WAVE_COMBINED.relative_to(BENCHMARK_ROOT)),
            "wave2_wave3_wave4_combined_evidence_sha256": sha256_file(WAVE_COMBINED),
            "wave3_wave4_final_evidence": str(WAVE34_FINAL.relative_to(BENCHMARK_ROOT)),
            "wave3_wave4_final_evidence_sha256": sha256_file(WAVE34_FINAL),
        },
        "claim_boundary": {
            "included_denominator": "clean benchmark-grade HoloVerify action-boundary packets only",
            "excluded_denominator": "canaries, precursor lanes, missing-evidence HoloBuild rows, and public copy drafts",
            "positive_class": "ESCALATE",
            "negative_class": "ALLOW",
            "confidence_language": "Exact upper bands are one-sided binomial/Clopper-Pearson zero-error upper bounds at alpha=0.05. Wilson values use z=1.96.",
            "zero_error_warning": "Zero observed errors does not mean zero real risk; it bounds plausible risk under the sampled distribution.",
        },
        "included_evidence_families": included,
        "excluded_evidence_families": excluded,
        "grand_totals": {
            "packets": packets,
            "correct_packets": correct,
            "observed_errors": errors,
            "sibling_pairs": pairs,
            "allow_truths": allow_truths,
            "escalate_truths": escalate_truths,
            "observed_packet_error_rate": rate(errors, packets),
            "observed_packet_error_rate_percent": pct(rate(errors, packets)),
        },
        "confusion_matrix_positive_class_escalate": {
            "true_positive": tp,
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "sensitivity_tpr_observed": rate(tp, tp + fn),
            "sensitivity_tpr_observed_percent": pct(rate(tp, tp + fn)),
            "specificity_tnr_observed": rate(tn, tn + fp),
            "specificity_tnr_observed_percent": pct(rate(tn, tn + fp)),
            "false_positive_rate_observed": rate(fp, fp + tn),
            "false_positive_rate_observed_percent": pct(rate(fp, fp + tn)),
            "false_negative_rate_observed": rate(fn, fn + tp),
            "false_negative_rate_observed_percent": pct(rate(fn, fn + tp)),
            "precision_ppv_observed": rate(tp, tp + fp),
            "precision_ppv_observed_percent": pct(rate(tp, tp + fp)),
            "negative_predictive_value_observed": rate(tn, tn + fn),
            "negative_predictive_value_observed_percent": pct(rate(tn, tn + fn)),
        },
        "confidence_intervals": {
            "overall_packet_error": {
                "n": packets,
                "errors": errors,
                "exact_one_sided_95_upper": packet_exact,
                "exact_one_sided_95_upper_percent": pct(packet_exact),
                "wilson_95_upper": packet_wilson,
                "wilson_95_upper_percent": pct(packet_wilson),
                "rule_of_three_upper": rule_of_three(packets),
                "rule_of_three_upper_percent": pct(rule_of_three(packets)),
            },
            "false_positive_rate": {
                "n": allow_truths,
                "errors": fp,
                "exact_one_sided_95_upper": per_class_exact,
                "exact_one_sided_95_upper_percent": pct(per_class_exact),
                "wilson_95_upper": per_class_wilson,
                "wilson_95_upper_percent": pct(per_class_wilson),
                "rule_of_three_upper": rule_of_three(allow_truths),
                "rule_of_three_upper_percent": pct(rule_of_three(allow_truths)),
            },
            "false_negative_rate": {
                "n": escalate_truths,
                "errors": fn,
                "exact_one_sided_95_upper": per_class_exact,
                "exact_one_sided_95_upper_percent": pct(per_class_exact),
                "wilson_95_upper": per_class_wilson,
                "wilson_95_upper_percent": pct(per_class_wilson),
                "rule_of_three_upper": rule_of_three(escalate_truths),
                "rule_of_three_upper_percent": pct(rule_of_three(escalate_truths)),
            },
        },
        "sample_size_planning": sample_size_targets,
        "plain_english": {
            "current_claim": (
                "Across 334 clean benchmark-grade HoloVerify action-boundary packets, "
                "the architecture observed 0 errors. The exact one-sided 95% upper "
                "bound on packet-level error is 0.893%, with a Wilson upper band of 1.137%."
            ),
            "per_class_claim": (
                "With 167 ALLOW and 167 ESCALATE truths, observed FPR and FNR are 0%. "
                "The exact one-sided 95% upper bound per side is 1.778%, with a Wilson upper band of 2.248%."
            ),
            "zero_error_caveat": (
                "Zero observed errors means no failures appeared in this locked sample. "
                "It does not prove the true error rate is zero; it means the plausible upper risk is bounded by the confidence interval."
            ),
            "next_statistical_milestone": (
                "A balanced 299 ALLOW / 299 ESCALATE zero-error denominator is enough to put FPR and FNR exact one-sided 95% upper bounds below 1%."
            ),
        },
        "assertions": {
            "packets_334": "PASS",
            "pairs_167": "PASS",
            "allow_truths_167": "PASS",
            "escalate_truths_167": "PASS",
            "observed_errors_zero": "PASS",
            "tp_167": "PASS",
            "tn_167": "PASS",
            "fp_zero": "PASS",
            "fn_zero": "PASS",
            "no_provider_calls": "PASS",
            "canaries_and_precursors_excluded": "PASS",
        },
    }
    root_signature = sha256_text(canonical_json(rootless))
    return {**rootless, "root_signature": root_signature}


def render_md(report: dict[str, Any]) -> str:
    totals = report["grand_totals"]
    cm = report["confusion_matrix_positive_class_escalate"]
    ci = report["confidence_intervals"]
    lines = [
        "# HoloVerify Statistical Appendix",
        "",
        f"Classification: `{report['classification']}`",
        f"Root signature: `{report['root_signature']}`",
        "",
        "This appendix packages the current clean benchmark-grade HoloVerify action-boundary denominator.",
        "It was generated without provider calls and excludes canaries, precursors, and missing-evidence rows.",
        "",
        "## Current Denominator",
        "",
        f"- Packets: `{totals['packets']}`",
        f"- Correct packets: `{totals['correct_packets']}`",
        f"- Observed errors: `{totals['observed_errors']}`",
        f"- Sibling pairs: `{totals['sibling_pairs']}`",
        f"- ALLOW truths: `{totals['allow_truths']}`",
        f"- ESCALATE truths: `{totals['escalate_truths']}`",
        "",
        "## Confusion Matrix",
        "",
        "Positive class: `ESCALATE`. Negative class: `ALLOW`.",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| TP | {cm['true_positive']} |",
        f"| TN | {cm['true_negative']} |",
        f"| FP | {cm['false_positive']} |",
        f"| FN | {cm['false_negative']} |",
        "",
        "| Rate | Observed |",
        "| --- | ---: |",
        f"| Sensitivity / TPR | {cm['sensitivity_tpr_observed_percent']:.2f}% |",
        f"| Specificity / TNR | {cm['specificity_tnr_observed_percent']:.2f}% |",
        f"| FPR | {cm['false_positive_rate_observed_percent']:.2f}% |",
        f"| FNR | {cm['false_negative_rate_observed_percent']:.2f}% |",
        f"| PPV | {cm['precision_ppv_observed_percent']:.2f}% |",
        f"| NPV | {cm['negative_predictive_value_observed_percent']:.2f}% |",
        "",
        "## 95% Upper Bounds",
        "",
        "| Metric | Errors | n | Exact one-sided 95% upper | Wilson 95% upper | Rule of three |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, key in [
        ("Overall packet error", "overall_packet_error"),
        ("False positive rate", "false_positive_rate"),
        ("False negative rate", "false_negative_rate"),
    ]:
        row = ci[key]
        lines.append(
            f"| {label} | {row['errors']} | {row['n']} | "
            f"{row['exact_one_sided_95_upper_percent']:.3f}% | "
            f"{row['wilson_95_upper_percent']:.3f}% | "
            f"{row['rule_of_three_upper_percent']:.3f}% |"
        )

    lines.extend(
        [
            "",
            "## Included Evidence Families",
            "",
            "| Evidence family | Packets | Pairs | Correct | Source |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in report["included_evidence_families"]:
        lines.append(
            f"| `{row['evidence_family']}` | {row['packets']} | {row['pairs']} | "
            f"{row['correct_packets']} | `{row['source']}` |"
        )

    lines.extend(
        [
            "",
            "## Excluded From Clean Denominator",
            "",
            "| Evidence family | Packets | Reason |",
            "| --- | ---: | --- |",
        ]
    )
    for row in report["excluded_evidence_families"]:
        lines.append(f"| `{row['evidence_family']}` | {row['packets']} | {row['reason']} |")

    lines.extend(
        [
            "",
            "## Sample Size Planning",
            "",
            "| Target upper bound | n needed with zero errors | More packets for overall | More balanced pairs for both FP/FN | More balanced packets for both FP/FN |",
            "| ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["sample_size_planning"]:
        lines.append(
            f"| < {row['target_upper_bound_percent']:.1f}% | "
            f"{row['zero_error_n_required_exact_one_sided']} | "
            f"{row['additional_packets_needed_for_overall']} | "
            f"{row['additional_balanced_pairs_needed_for_both_fpr_and_fnr']} | "
            f"{row['additional_balanced_packets_needed_for_both_fpr_and_fnr']} |"
        )

    lines.extend(
        [
            "",
            "## Why Zero Errors Does Not Mean Zero Risk",
            "",
            report["plain_english"]["zero_error_caveat"],
            "",
            "The current honest packet-level statement is:",
            "",
            f"> {report['plain_english']['current_claim']}",
            "",
            "The current honest FP/FN statement is:",
            "",
            f"> {report['plain_english']['per_class_claim']}",
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
    report = build()
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
