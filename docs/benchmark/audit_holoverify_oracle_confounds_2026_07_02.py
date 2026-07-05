#!/usr/bin/env python3
"""No-provider audit for HoloVerify oracle-gate confounds.

This script scans repo-local source, traces, and result artifacts only. It does
not call providers, judges, or mutate frozen benchmark evidence. Its purpose is
to quantify whether the governed-runtime benchmark lane contains answer-aware
gate/repair influence, and to inventory invalid/complete run artifacts.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "docs" / "benchmark"
OUT_JSON = BENCH / "FABLE_ORACLE_INFLUENCE_CENSUS_2026_07_02.json"
OUT_MD = BENCH / "FABLE_ORACLE_INFLUENCE_CENSUS_2026_07_02.md"
FUNNEL_JSON = BENCH / "FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.json"
FUNNEL_MD = BENCH / "FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.md"

PACKET_RE = re.compile(r"\b(?:HV|BAL100)[A-Z0-9_\-]*-\d{3,}[A-Z0-9_\-]*-[AB]\b")
PAIR_RE = re.compile(r"\b(?:HV|BAL100)[A-Z0-9_\-]*-\d{3,}[A-Z0-9_\-]*\b")
RUN_RE = re.compile(r"run_\d{8}T\d{6}Z")

STATIC_PATTERNS = {
    "suffix_derives_expected_verdict": 'expected = "ALLOW" if suffix == "A" else "ESCALATE"',
    "verdict_mismatch_failure": "action_boundary_verdict_mismatch",
    "truth_conditioned_overblock_repair": "Potential overblock",
    "truth_conditioned_underblock_repair": "Potential underblock",
    "gate_repair_directive_function": "def _gate_repair_directive",
    "gov_gate_compliance_function": "def _enforce_gov_gate_compliance",
    "truth_conditioned_expected_binding": "def _worker_expected_binding",
    "truth_conditioned_worker_normalization": "def _normalize_worker_artifact_after_gate",
    "suffix_conditioned_knew_terms": 'spec.get("knew_terms", {}).get(suffix',
    "normalizer_sets_expected_binding": "binding.setdefault(\"binding_class\", _worker_expected_binding(suffix))",
}

ORACLE_STRINGS = {
    "action_boundary_verdict_mismatch": "action_boundary_verdict_mismatch",
    "potential_overblock": "Potential overblock",
    "potential_underblock": "Potential underblock",
    "lower_potential_overblock": "potential overblock",
    "lower_potential_underblock": "potential underblock",
    "expected_allow_got_escalate": "expected_ALLOW_got_ESCALATE",
    "expected_escalate_got_allow": "expected_ESCALATE_got_ALLOW",
    "knew_terms": "knew_terms",
    "missing_critical_term": "missing_critical_term:",
    "expected_binding_function": "_worker_expected_binding",
    "normalizer_function": "_normalize_worker_artifact_after_gate",
}

PROMPT_FORBIDDEN_TERMS = {
    "packet_truth": "packet_truth",
    "expected_verdict": "expected_verdict",
    "target_bucket": "target_bucket",
    "knew_terms": "knew_terms",
    "allow_rule": "allow_rule",
    "esc_rule": "esc_rule",
    "expected_ALLOW_got_ESCALATE": "expected_ALLOW_got_ESCALATE",
    "expected_ESCALATE_got_ALLOW": "expected_ESCALATE_got_ALLOW",
    "action_boundary_verdict_mismatch": "action_boundary_verdict_mismatch",
    "Potential overblock": "Potential overblock",
    "Potential underblock": "Potential underblock",
}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def safe_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def textify(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=True)
    except TypeError:
        return str(value)


def packet_ids_from_obj(obj: Any) -> set[str]:
    ids: set[str] = set()

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if k in {"packet_id", "packet", "turn_id", "artifact_id"} and isinstance(v, str):
                    ids.update(PACKET_RE.findall(v))
                walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            ids.update(PACKET_RE.findall(value))

    walk(obj)
    return ids


def run_id_from_path(path: Path) -> str:
    match = RUN_RE.search(str(path))
    return match.group(0) if match else path.parent.name


def scan_static_source() -> dict[str, Any]:
    findings: dict[str, list[dict[str, Any]]] = {name: [] for name in STATIC_PATTERNS}
    files = list(BENCH.rglob("*.py"))
    for path in files:
        if path.name == Path(__file__).name:
            continue
        try:
            lines = path.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        for line_no, line in enumerate(lines, start=1):
            for name, needle in STATIC_PATTERNS.items():
                if needle in line:
                    findings[name].append(
                        {"path": rel(path), "line": line_no, "snippet": line.strip()[:220]}
                    )
    return {
        "files_scanned": len(files),
        "patterns": findings,
        "all_required_static_confounds_found": all(findings.values()),
    }


@dataclass
class OracleStats:
    files_scanned: int = 0
    jsonl_records_scanned: int = 0
    oracle_string_hits: Counter = field(default_factory=Counter)
    packets_by_signal: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    runs_by_signal: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    worker_artifacts_total: int = 0
    worker_artifacts_with_mismatch: int = 0
    packets_with_worker_mismatch: set[str] = field(default_factory=set)
    packets_with_first_worker_mismatch: set[str] = field(default_factory=set)
    packets_with_final_selector: set[str] = field(default_factory=set)
    packets_with_final_selector_regression_protection: set[str] = field(default_factory=set)
    intra_holo_miss_packets: set[str] = field(default_factory=set)
    intra_holo_miss_rows: int = 0
    final_packet_rows: int = 0
    final_packet_rows_correct: int = 0
    canonical_result_files: int = 0
    duplicate_result_files_skipped_for_effect: int = 0
    effect_packet_rows: int = 0
    effect_any_worker_mismatch_rows: int = 0
    effect_any_worker_mismatch_final_expected: int = 0
    effect_first_worker_mismatch_rows: int = 0
    effect_first_worker_mismatch_final_expected: int = 0
    effect_first_worker_mismatch_final_changed: int = 0
    effect_first_worker_mismatch_final_same_wrong: int = 0
    effect_examples: list[dict[str, Any]] = field(default_factory=list)
    sample_events: list[dict[str, Any]] = field(default_factory=list)

    def add_sample(self, path: Path, signal: str, obj: Any) -> None:
        if len(self.sample_events) >= 30:
            return
        self.sample_events.append(
            {
                "path": rel(path),
                "run_id": run_id_from_path(path),
                "signal": signal,
                "packet_ids": sorted(packet_ids_from_obj(obj))[:8],
                "keys": sorted(obj.keys())[:30] if isinstance(obj, dict) else [],
                "preview": textify(obj)[:700],
            }
        )

    def add_effect_example(self, row: dict[str, Any], first: dict[str, Any] | None) -> None:
        if len(self.effect_examples) >= 30:
            return
        self.effect_examples.append(
            {
                "packet_id": row.get("packet_id"),
                "pair_id": row.get("pair_id"),
                "suffix": row.get("suffix"),
                "expected_from_suffix": expected_from_suffix(row.get("suffix")),
                "first_worker_verdict": first.get("verification_verdict") if first else None,
                "first_worker_gate_failures": first.get("gate_failures") if first else None,
                "final_verdict": row.get("final_verdict") or row.get("verdict"),
                "final_selector": row.get("final_selector"),
            }
        )


def expected_from_suffix(suffix: Any) -> str | None:
    if suffix == "A":
        return "ALLOW"
    if suffix == "B":
        return "ESCALATE"
    return None


def scan_json_object(path: Path, obj: Any, stats: OracleStats) -> None:
    text = textify(obj)
    packets = packet_ids_from_obj(obj)
    run_id = run_id_from_path(path)

    for signal, needle in ORACLE_STRINGS.items():
        if needle in text:
            stats.oracle_string_hits[signal] += text.count(needle)
            stats.packets_by_signal[signal].update(packets)
            stats.runs_by_signal[signal].add(run_id)
            stats.add_sample(path, signal, obj)

    if isinstance(obj, dict):
        gate = obj.get("gate_result")
        if isinstance(gate, dict) and "action_boundary_verdict_mismatch" in gate.get("failures", []):
            stats.worker_artifacts_with_mismatch += 1
            stats.packets_with_worker_mismatch.update(packets)
            if obj.get("worker_index") in {1, "1"}:
                stats.packets_with_first_worker_mismatch.update(packets)


def scan_trace_files() -> OracleStats:
    stats = OracleStats()
    trace_files = list(BENCH.rglob("TRACE_CALLS.jsonl"))
    for path in trace_files:
        stats.files_scanned += 1
        try:
            with path.open() as f:
                for line in f:
                    if not line.strip():
                        continue
                    stats.jsonl_records_scanned += 1
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(obj, dict) and obj.get("call_kind") == "worker":
                        stats.worker_artifacts_total += 1
                    scan_json_object(path, obj, stats)
        except Exception:
            continue
    return stats


def scan_result_files(stats: OracleStats) -> list[dict[str, Any]]:
    result_paths: list[Path] = []
    for name in ("live_results.json", "batch_results.json", "canary_results.json", "benchmark_results.json"):
        result_paths.extend(BENCH.rglob(name))

    per_result: list[dict[str, Any]] = []
    seen_result_shas: set[str] = set()
    for path in sorted(set(result_paths)):
        data = safe_json(path)
        if not isinstance(data, dict):
            continue
        content_sha = sha256_path(path)
        duplicate_for_effect = content_sha in seen_result_shas
        if not duplicate_for_effect:
            seen_result_shas.add(content_sha)
            stats.canonical_result_files += 1
        else:
            stats.duplicate_result_files_skipped_for_effect += 1
        scan_json_object(path, data, stats)
        rows = data.get("packet_results") or data.get("rows") or []
        if not isinstance(rows, list):
            rows = []
        packet_rows = 0
        packet_correct = 0
        mismatch_packets: set[str] = set()
        selector_packets: set[str] = set()
        intra_rows = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            packet_id = row.get("packet_id")
            if not isinstance(packet_id, str):
                continue
            packet_rows += 1
            final_verdict = row.get("final_verdict") or row.get("verdict")
            suffix = row.get("suffix")
            expected = expected_from_suffix(suffix)
            if expected and final_verdict == expected and row.get("final_admissible", True):
                packet_correct += 1
            artifacts = row.get("artifact_registry") or []
            sorted_artifacts: list[dict[str, Any]] = []
            if isinstance(artifacts, list):
                sorted_artifacts = sorted(
                    [a for a in artifacts if isinstance(a, dict)],
                    key=lambda a: int(a.get("turn_number") or 999),
                )
                for artifact in artifacts:
                    if not isinstance(artifact, dict):
                        continue
                    stats.worker_artifacts_total += 1
                    failures = artifact.get("gate_failures") or []
                    if "action_boundary_verdict_mismatch" in failures:
                        stats.worker_artifacts_with_mismatch += 1
                        stats.packets_with_worker_mismatch.add(packet_id)
                        mismatch_packets.add(packet_id)
                        if artifact.get("turn_number") == 1:
                            stats.packets_with_first_worker_mismatch.add(packet_id)
                    if artifact.get("artifact_id") and artifact.get("gate_passed") is not None:
                        pass
            if not duplicate_for_effect and expected and sorted_artifacts:
                first_worker = next(
                    (
                        a
                        for a in sorted_artifacts
                        if str(a.get("artifact_id", "")).endswith("_WORKER_01")
                        or a.get("turn_number") == 1
                    ),
                    sorted_artifacts[0],
                )
                first_verdict = first_worker.get("verification_verdict")
                first_failures = first_worker.get("gate_failures") or []
                first_mismatch = (
                    first_verdict in {"ALLOW", "ESCALATE"} and first_verdict != expected
                ) or "action_boundary_verdict_mismatch" in first_failures
                any_mismatch = any(
                    "action_boundary_verdict_mismatch" in (a.get("gate_failures") or [])
                    or (
                        a.get("verification_verdict") in {"ALLOW", "ESCALATE"}
                        and a.get("verification_verdict") != expected
                    )
                    for a in sorted_artifacts
                )
                stats.effect_packet_rows += 1
                if any_mismatch:
                    stats.effect_any_worker_mismatch_rows += 1
                    if final_verdict == expected:
                        stats.effect_any_worker_mismatch_final_expected += 1
                if first_mismatch:
                    stats.effect_first_worker_mismatch_rows += 1
                    if final_verdict == expected:
                        stats.effect_first_worker_mismatch_final_expected += 1
                    if final_verdict != first_verdict:
                        stats.effect_first_worker_mismatch_final_changed += 1
                    if final_verdict == first_verdict and final_verdict != expected:
                        stats.effect_first_worker_mismatch_final_same_wrong += 1
                    stats.add_effect_example(row, first_worker)
            final_selector = row.get("final_selector") or {}
            if isinstance(final_selector, dict) and final_selector:
                stats.packets_with_final_selector.add(packet_id)
                selector_packets.add(packet_id)
                reason = str(final_selector.get("selection_reason", ""))
                if "REGRESS" in reason.upper() or "BEST" in reason.upper():
                    stats.packets_with_final_selector_regression_protection.add(packet_id)
            miss_rows = row.get("intra_holo_single_dna_miss_evidence") or []
            if isinstance(miss_rows, list) and miss_rows:
                stats.intra_holo_miss_packets.add(packet_id)
                stats.intra_holo_miss_rows += len(miss_rows)
                intra_rows += len(miss_rows)
            scan_json_object(path, row, stats)
        if packet_rows:
            stats.final_packet_rows += packet_rows
            stats.final_packet_rows_correct += packet_correct
        per_result.append(
            {
                "path": rel(path),
                "sha256": content_sha,
                "duplicate_content_sha_for_effect_stats": duplicate_for_effect,
                "classification": data.get("classification"),
                "readiness_passed": data.get("readiness_passed"),
                "provider_calls": data.get("provider_calls"),
                "worker_calls": data.get("worker_calls"),
                "gov_calls": data.get("gov_calls") or data.get("holo_gov_calls"),
                "judge_calls": data.get("judge_calls"),
                "packet_rows": packet_rows,
                "packet_rows_correct_by_suffix": packet_correct,
                "packets_with_mismatch_artifact": len(mismatch_packets),
                "packets_with_final_selector": len(selector_packets),
                "intra_holo_miss_rows": intra_rows,
            }
        )
    return per_result


def read_public_claim_snapshot() -> dict[str, Any]:
    benchmark = ROOT / "frontend" / "benchmark.html"
    whitepaper = ROOT / "frontend" / "whitepaper.html"
    snapshot: dict[str, Any] = {}
    for path in (benchmark, whitepaper):
        if not path.exists():
            continue
        text = path.read_text(errors="ignore")
        numbers = sorted(set(re.findall(r"\b\d{2,4}/\d{2,4}\b", text)))
        snapshot[rel(path)] = {
            "sha256": sha256_path(path),
            "counted_run_phrasing_present": "counted-run" in text or "counted lane" in text,
            "blind_gate_caveat_present": "blind-gate" in text,
            "ratio_like_numbers": numbers[:20],
        }
    return snapshot


def prompt_visible_text(data: Any) -> str:
    if isinstance(data, dict):
        parts: list[str] = []
        messages = data.get("messages")
        if isinstance(messages, list):
            for msg in messages:
                if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                    parts.append(msg["content"])
        prompt_object = data.get("prompt_object")
        if prompt_object is not None:
            parts.append(textify(prompt_object))
        if not parts:
            parts.append(textify(data))
        return "\n".join(parts)
    return textify(data)


def scan_model_visible_prompts() -> dict[str, Any]:
    prompt_files = [
        p
        for p in BENCH.rglob("*.json")
        if "/prompts/" in str(p).replace("\\", "/") or p.parent.name == "prompts"
    ]
    suffix_id_files = 0
    suffix_id_occurrences = 0
    forbidden_hits: Counter = Counter()
    packet_id_samples: list[dict[str, Any]] = []
    forbidden_samples: list[dict[str, Any]] = []

    for path in sorted(prompt_files):
        data = safe_json(path)
        if data is None:
            continue
        text = prompt_visible_text(data)
        packet_ids = PACKET_RE.findall(text)
        if packet_ids:
            suffix_id_files += 1
            suffix_id_occurrences += len(packet_ids)
            if len(packet_id_samples) < 20:
                packet_id_samples.append(
                    {
                        "path": rel(path),
                        "packet_ids": sorted(set(packet_ids))[:10],
                        "preview": text[:500],
                    }
                )
        for label, needle in PROMPT_FORBIDDEN_TERMS.items():
            count = text.count(needle)
            if count:
                forbidden_hits[label] += count
                if len(forbidden_samples) < 20:
                    forbidden_samples.append(
                        {
                            "path": rel(path),
                            "label": label,
                            "needle": needle,
                            "count": count,
                            "preview": text[:500],
                        }
                    )

    return {
        "prompt_json_files_scanned": len(prompt_files),
        "prompt_files_with_model_visible_suffix_packet_ids": suffix_id_files,
        "model_visible_suffix_packet_id_occurrences": suffix_id_occurrences,
        "forbidden_truth_like_prompt_hits": dict(forbidden_hits),
        "packet_id_samples": packet_id_samples,
        "forbidden_samples": forbidden_samples,
        "blind_claim_blocker": suffix_id_files > 0 or bool(forbidden_hits),
    }


def compiled_metrics_snapshot() -> dict[str, Any]:
    path = BENCH / "compiled_holoverify_holobuild_metrics_2026_07_01" / "compiled_metrics_package.json"
    if not path.exists():
        return {"present": False}
    data = safe_json(path)
    if not isinstance(data, dict):
        return {"present": False, "parse_ok": False}
    packet_rows = data.get("packet_rows") or []
    holo_rows = [r for r in packet_rows if str(r.get("system", "")).lower().startswith("holo")]
    solo_rows = [r for r in packet_rows if str(r.get("system", "")).lower().startswith("solo")]
    by_family = Counter(r.get("evidence_family") for r in holo_rows)
    by_tier = Counter(r.get("evidence_tier") for r in holo_rows)
    return {
        "present": True,
        "path": rel(path),
        "sha256": sha256_path(path),
        "packet_rows_total": len(packet_rows),
        "holo_rows": len(holo_rows),
        "solo_rows": len(solo_rows),
        "holo_rows_binary_correct_true": sum(1 for r in holo_rows if r.get("binary_correct") == "TRUE"),
        "holo_rows_admissible_or_knew_true": sum(1 for r in holo_rows if r.get("admissible_or_knew") == "TRUE"),
        "holo_rows_by_family": dict(by_family),
        "holo_rows_by_tier": dict(by_tier),
        "run_summary_count": len(data.get("run_summaries") or []),
    }


def classify_result_file(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    text = textify(data)
    classification = str(data.get("classification", ""))
    readiness = data.get("readiness_passed")
    provider_failures = data.get("provider_failures")
    invalidation = data.get("invalidation_reason")
    terminal = data.get("terminal_failures") or data.get("root_failure")

    is_invalid = any(token in classification.upper() for token in ("INVALID", "INCOMPLETE", "FAIL", "BLOCK"))
    is_complete = "COMPLETE" in classification.upper() and not is_invalid
    if readiness is True:
        is_complete = True
        is_invalid = False
    if readiness is False or invalidation or terminal:
        is_invalid = True
        is_complete = False
    if isinstance(provider_failures, list) and provider_failures:
        is_invalid = True
        is_complete = False

    reason = None
    if is_invalid:
        upper_text = text.upper()
        for label, needles in {
            "provider_failure": [
                "PROVIDER_FAILURE",
                "HTTP 429",
                "HTTP 500",
                "HTTP 502",
                "HTTP 503",
                "HTTP 504",
                "READ TIMEOUT",
                "CONNECTION RESET",
                "INSUFFICIENT_QUOTA",
            ],
            "gov_contract_or_parse": [
                "GOV",
                "BATON",
                "GOV_MICRO_KEY_VALUE_PARSE_FAILED",
                "GOV_FINISH_REASON_LENGTH",
            ],
            "worker_contract_or_parse": [
                "WORKER",
                "JSONDECODE",
                "UNTERMINATED STRING",
                "COMPACT_KEY_VALUE",
            ],
            "verdict_or_admissibility": [
                "VERDICT",
                "ADMISSIBLE",
                "ACTION_BOUNDARY_VERDICT_MISMATCH",
                "BENCHMARK_LAW_VIOLATION",
            ],
            "leakage_or_lock": ["LEAKAGE", "LOCK", "HASH", "IDENTITY"],
        }.items():
            if any(n in upper_text for n in needles):
                reason = label
                break
    return {
        "path": rel(path),
        "run_id": run_id_from_path(path),
        "classification": classification,
        "status": "complete" if is_complete else "invalid_or_blocked" if is_invalid else "unknown",
        "reason_family": reason,
        "readiness_passed": readiness,
        "provider_calls": data.get("provider_calls"),
        "worker_calls": data.get("worker_calls"),
        "gov_calls": data.get("gov_calls") or data.get("holo_gov_calls"),
        "judge_calls": data.get("judge_calls"),
        "packet_count": data.get("packet_count") or len(data.get("packet_results") or []),
        "packet_correct": data.get("packet_correct"),
        "invalidation_reason": invalidation,
    }


def build_funnel() -> dict[str, Any]:
    paths = []
    for name in ("live_results.json", "batch_results.json", "canary_results.json", "benchmark_results.json"):
        paths.extend(BENCH.rglob(name))
    entries = []
    for path in sorted(set(paths)):
        data = safe_json(path)
        if isinstance(data, dict):
            entries.append(classify_result_file(path, data))
    status_counts = Counter(e["status"] for e in entries)
    reason_counts = Counter(e["reason_family"] for e in entries if e["reason_family"])
    packet_counts_by_status = Counter()
    for e in entries:
        try:
            packet_counts_by_status[e["status"]] += int(e.get("packet_count") or 0)
        except Exception:
            pass
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "NO_PROVIDER_RUN_FUNNEL_RECONCILIATION",
        "result_files_scanned": len(entries),
        "status_counts": dict(status_counts),
        "reason_family_counts": dict(reason_counts),
        "packet_counts_by_status": dict(packet_counts_by_status),
        "invalid_or_blocked_examples": [e for e in entries if e["status"] == "invalid_or_blocked"][:80],
        "complete_examples": [e for e in entries if e["status"] == "complete"][:80],
        "all_entries_csv": rel(BENCH / "FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.csv"),
    }


def write_csv(entries: list[dict[str, Any]], path: Path) -> None:
    keys = sorted({k for e in entries for k in e})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(entries)


def write_md_report(report: dict[str, Any], path: Path) -> None:
    trace = report["trace_and_result_census"]
    prompts = report["model_visible_prompt_scan"]
    public = report["public_claim_snapshot"]
    compiled = report["compiled_metrics_snapshot"]
    static = report["static_source_audit"]
    lines = [
        "# Fable Oracle Influence Census",
        "",
        "Status: NO_PROVIDER_AUDIT",
        "",
        "This audit tests the confound that the current governed-runtime lane can use packet truth inside deterministic gates and route truth-conditioned repair language into later worker prompts.",
        "",
        "## Bottom Line",
        "",
        f"- Static source confound found: `{static['all_required_static_confounds_found']}`.",
        f"- TRACE_CALLS files scanned: `{trace['trace_files_scanned']}`.",
        f"- TRACE_CALLS records scanned: `{trace['trace_records_scanned']}`.",
        f"- Unique packets with worker verdict-mismatch gate evidence: `{trace['unique_packets_with_worker_verdict_mismatch']}`.",
        f"- Unique packets with directional repair hint evidence: `{trace['unique_packets_with_directional_repair_hint']}`.",
        f"- Worker/artifact mismatch rows found: `{trace['worker_artifacts_with_mismatch']}`.",
        f"- Intra-Holo miss rows found in result artifacts: `{trace['intra_holo_miss_rows']}`.",
        f"- Canonical result files used for effect stats: `{trace['canonical_result_files_for_effect_stats']}`.",
        f"- First-worker mismatch rows in canonical result files: `{trace['effect_first_worker_mismatch_rows']}`.",
        f"- First-worker mismatch rows whose final verdict became suffix-derived expected verdict: `{trace['effect_first_worker_mismatch_final_expected']}`.",
        f"- Model-visible prompt files with `-A` / `-B` packet IDs: `{prompts['prompt_files_with_model_visible_suffix_packet_ids']}`.",
        "",
        "## Interpretation",
        "",
        "The current 614-style public number should be treated as a counted governed-runtime result, not as a blind production risk bound, until a blind-gate replication removes answer-aware routing from the runtime path.",
        "",
        "This does not mean the traces are fake. It means the claimed denominator is not measuring only independent model reasoning. Some packets include deterministic/oracle enforcement, later-worker repair influence, and model-visible IDs that encode `A` / `B` sibling position.",
        "",
        "## Exposure vs Effect",
        "",
        "The broad string counts below measure exposure: where answer-aware text or gate labels appear in files. The effect counters below de-duplicate copied result files by content hash and estimate how often a wrong early worker output later ended at the suffix-derived expected verdict.",
        "",
        f"- Canonical result files for effect stats: `{trace['canonical_result_files_for_effect_stats']}`.",
        f"- Duplicate copied result files skipped for effect stats: `{trace['duplicate_result_files_skipped_for_effect_stats']}`.",
        f"- Packet rows with any worker mismatch: `{trace['effect_any_worker_mismatch_rows']}`.",
        f"- Any-worker mismatch rows ending at suffix-derived expected verdict: `{trace['effect_any_worker_mismatch_final_expected']}`.",
        f"- First-worker mismatch rows: `{trace['effect_first_worker_mismatch_rows']}`.",
        f"- First-worker mismatch rows ending at suffix-derived expected verdict: `{trace['effect_first_worker_mismatch_final_expected']}`.",
        f"- First-worker mismatch rows where final verdict changed from the first worker: `{trace['effect_first_worker_mismatch_final_changed']}`.",
        f"- First-worker mismatch rows where final stayed wrong: `{trace['effect_first_worker_mismatch_final_same_wrong']}`.",
        "",
        "## Static Source Evidence",
        "",
    ]
    for name, hits in static["patterns"].items():
        lines.append(f"- `{name}`: `{len(hits)}` hit(s)")
        for hit in hits[:5]:
            lines.append(f"  - `{hit['path']}:{hit['line']}` `{hit['snippet']}`")
    lines.extend(
        [
            "",
            "## Signal Counts",
            "",
            "| Signal | String hits | Unique packets | Unique runs |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for signal, count in sorted(trace["oracle_string_hits"].items()):
        lines.append(
            f"| `{signal}` | {count} | {trace['unique_packets_by_signal'].get(signal, 0)} | {trace['unique_runs_by_signal'].get(signal, 0)} |"
        )
    lines.extend(
        [
            "",
            "## Model-Visible Prompt Leak Scan",
            "",
            f"- Prompt JSON files scanned: `{prompts['prompt_json_files_scanned']}`.",
            f"- Prompt files with model-visible `-A` / `-B` packet IDs: `{prompts['prompt_files_with_model_visible_suffix_packet_ids']}`.",
            f"- Model-visible suffix packet ID occurrences: `{prompts['model_visible_suffix_packet_id_occurrences']}`.",
            f"- Blind-claim blocker: `{prompts['blind_claim_blocker']}`.",
            "",
            "| Forbidden / truth-like term | Hits |",
            "| --- | ---: |",
        ]
    )
    for label, count in sorted(prompts["forbidden_truth_like_prompt_hits"].items()):
        lines.append(f"| `{label}` | {count} |")
    if prompts["packet_id_samples"]:
        lines.extend(["", "Prompt suffix-ID samples:"])
        for sample in prompts["packet_id_samples"][:8]:
            lines.append(f"- `{sample['path']}` IDs `{sample['packet_ids']}`")
    lines.extend(
        [
            "",
            "## Public Claim Snapshot",
            "",
            "The current frontend already has caveat language. This audit is meant to prove whether that caveat is strong enough.",
            "",
        ]
    )
    for p, snap in public.items():
        lines.append(f"- `{p}`")
        lines.append(f"  - counted-run phrasing present: `{snap['counted_run_phrasing_present']}`")
        lines.append(f"  - blind-gate caveat present: `{snap['blind_gate_caveat_present']}`")
        lines.append(f"  - ratio-like numbers: `{', '.join(snap['ratio_like_numbers'])}`")
    lines.extend(
        [
            "",
            "## Compiled Metrics Snapshot",
            "",
            f"- Package present: `{compiled.get('present')}`.",
            f"- Holo rows in compiled package: `{compiled.get('holo_rows')}`.",
            f"- Solo rows in compiled package: `{compiled.get('solo_rows')}`.",
            f"- Holo rows binary-correct TRUE: `{compiled.get('holo_rows_binary_correct_true')}`.",
            "",
            "## Sample Events",
            "",
        ]
    )
    for sample in trace["sample_events"][:12]:
        lines.append(f"- `{sample['signal']}` in `{sample['path']}` packets `{sample['packet_ids']}`")
    lines.extend(["", "## Effect Examples", ""])
    for sample in trace["effect_examples"][:12]:
        lines.append(
            f"- `{sample['packet_id']}` expected `{sample['expected_from_suffix']}`, first worker `{sample['first_worker_verdict']}`, final `{sample['final_verdict']}`"
        )
    lines.extend(
        [
            "",
            "## Required Next Proof",
            "",
            "1. Use opaque runtime packet IDs; never expose `-A` / `-B` sibling IDs to models.",
            "2. Run a blind-gate replication where runtime gates check schema, source IDs, dependencies, and consistency but do not know ALLOW/ESCALATE truth.",
            "3. Keep answer-key scoring entirely post-hoc.",
            "4. Recompute FP/FN only from the blind-gate run.",
            "5. Keep this governed-runtime lane as architecture/debug evidence, not as the production risk-bound headline.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def write_funnel_md(funnel: dict[str, Any], path: Path) -> None:
    lines = [
        "# Fable Run Funnel Reconciliation",
        "",
        "Status: NO_PROVIDER_AUDIT",
        "",
        "This inventory reconciles complete, invalid, blocked, and unknown run-result artifacts found under `docs/benchmark`.",
        "",
        "## Summary",
        "",
        f"- Result files scanned: `{funnel['result_files_scanned']}`.",
        f"- Status counts: `{funnel['status_counts']}`.",
        f"- Reason-family counts: `{funnel['reason_family_counts']}`.",
        f"- Packet counts by status: `{funnel['packet_counts_by_status']}`.",
        "",
        "## Important Caveat",
        "",
        "This is an artifact inventory, not a proof that each complete file belongs in the public denominator. The public denominator still needs a strict inclusion manifest that maps every counted packet to exactly one locked run.",
        "",
        "## Invalid Or Blocked Examples",
        "",
        "| Status | Reason | Classification | Packets | Path |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for e in funnel["invalid_or_blocked_examples"][:40]:
        lines.append(
            f"| {e['status']} | {e.get('reason_family') or ''} | {e.get('classification') or ''} | {e.get('packet_count') or ''} | `{e['path']}` |"
        )
    lines.extend(
        [
            "",
            "## Complete Examples",
            "",
            "| Status | Classification | Packets | Path |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for e in funnel["complete_examples"][:40]:
        lines.append(
            f"| {e['status']} | {e.get('classification') or ''} | {e.get('packet_count') or ''} | `{e['path']}` |"
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    static = scan_static_source()
    stats = scan_trace_files()
    per_result = scan_result_files(stats)

    trace_report = {
        "trace_files_scanned": stats.files_scanned,
        "trace_records_scanned": stats.jsonl_records_scanned,
        "oracle_string_hits": dict(stats.oracle_string_hits),
        "unique_packets_by_signal": {k: len(v) for k, v in stats.packets_by_signal.items()},
        "unique_runs_by_signal": {k: len(v) for k, v in stats.runs_by_signal.items()},
        "unique_packets_with_worker_verdict_mismatch": len(stats.packets_with_worker_mismatch),
        "unique_packets_with_first_worker_verdict_mismatch": len(stats.packets_with_first_worker_mismatch),
        "unique_packets_with_directional_repair_hint": len(
            set().union(
                stats.packets_by_signal.get("potential_overblock", set()),
                stats.packets_by_signal.get("potential_underblock", set()),
                stats.packets_by_signal.get("lower_potential_overblock", set()),
                stats.packets_by_signal.get("lower_potential_underblock", set()),
            )
        ),
        "worker_artifacts_total": stats.worker_artifacts_total,
        "worker_artifacts_with_mismatch": stats.worker_artifacts_with_mismatch,
        "canonical_result_files_for_effect_stats": stats.canonical_result_files,
        "duplicate_result_files_skipped_for_effect_stats": stats.duplicate_result_files_skipped_for_effect,
        "effect_packet_rows": stats.effect_packet_rows,
        "effect_any_worker_mismatch_rows": stats.effect_any_worker_mismatch_rows,
        "effect_any_worker_mismatch_final_expected": stats.effect_any_worker_mismatch_final_expected,
        "effect_first_worker_mismatch_rows": stats.effect_first_worker_mismatch_rows,
        "effect_first_worker_mismatch_final_expected": stats.effect_first_worker_mismatch_final_expected,
        "effect_first_worker_mismatch_final_changed": stats.effect_first_worker_mismatch_final_changed,
        "effect_first_worker_mismatch_final_same_wrong": stats.effect_first_worker_mismatch_final_same_wrong,
        "effect_examples": stats.effect_examples,
        "packets_with_final_selector": len(stats.packets_with_final_selector),
        "packets_with_final_selector_regression_protection": len(
            stats.packets_with_final_selector_regression_protection
        ),
        "intra_holo_miss_packets": len(stats.intra_holo_miss_packets),
        "intra_holo_miss_rows": stats.intra_holo_miss_rows,
        "final_packet_rows_scanned": stats.final_packet_rows,
        "final_packet_rows_correct_by_suffix": stats.final_packet_rows_correct,
        "per_result_file_summaries": per_result,
        "sample_events": stats.sample_events,
    }

    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "NO_PROVIDER_ORACLE_INFLUENCE_CENSUS",
        "scope": "repo-local source, traces, and result artifacts under docs/benchmark",
        "provider_calls": 0,
        "judge_calls": 0,
        "static_source_audit": static,
        "trace_and_result_census": trace_report,
        "model_visible_prompt_scan": scan_model_visible_prompts(),
        "compiled_metrics_snapshot": compiled_metrics_snapshot(),
        "public_claim_snapshot": read_public_claim_snapshot(),
        "conclusion": {
            "truth_conditioned_gate_path_present": static["all_required_static_confounds_found"],
            "directional_repair_hints_found_in_artifacts": trace_report[
                "unique_packets_with_directional_repair_hint"
            ]
            > 0,
            "public_614_should_be_labeled_counted_governed_runtime_not_blind_risk_bound": True,
            "blind_gate_replication_required_before_production_error_bound": True,
            "effect_measured_separately_from_exposure": True,
        },
    }

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_md_report(report, OUT_MD)

    funnel = build_funnel()
    funnel_entries: list[dict[str, Any]] = []
    for name in ("live_results.json", "batch_results.json", "canary_results.json", "benchmark_results.json"):
        for p in sorted(set(BENCH.rglob(name))):
            data = safe_json(p)
            if isinstance(data, dict):
                funnel_entries.append(classify_result_file(p, data))
    write_csv(funnel_entries, BENCH / "FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.csv")
    FUNNEL_JSON.write_text(json.dumps(funnel, indent=2, sort_keys=True) + "\n")
    write_funnel_md(funnel, FUNNEL_MD)

    print(json.dumps({
        "oracle_report": rel(OUT_JSON),
        "oracle_markdown": rel(OUT_MD),
        "funnel_report": rel(FUNNEL_JSON),
        "funnel_markdown": rel(FUNNEL_MD),
        "truth_conditioned_gate_path_present": report["conclusion"]["truth_conditioned_gate_path_present"],
        "unique_packets_with_worker_verdict_mismatch": trace_report["unique_packets_with_worker_verdict_mismatch"],
        "unique_packets_with_directional_repair_hint": trace_report["unique_packets_with_directional_repair_hint"],
        "effect_first_worker_mismatch_rows": trace_report["effect_first_worker_mismatch_rows"],
        "effect_first_worker_mismatch_final_expected": trace_report["effect_first_worker_mismatch_final_expected"],
        "model_visible_prompt_suffix_id_files": report["model_visible_prompt_scan"][
            "prompt_files_with_model_visible_suffix_packet_ids"
        ],
        "provider_calls": 0,
        "judge_calls": 0,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
