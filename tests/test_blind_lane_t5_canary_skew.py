"""T5 - canary skew check against frozen traces.

Falsifies: "the canary sample was not chosen to be easy."
Passing does NOT show the bank generalizes (it was screened for solo failure).
"""

import json
import re
from pathlib import Path

import pytest

from blind_lane_suite.fixtures import mock_transcripts
from blind_lane_suite.runner_contract import SKIP_REASON, load_runner
from blind_lane_suite.canary_skew import (
    bank_stats,
    find_canary_manifest,
    first_turn_correctness,
    skew_check,
)


def _runtime_and_scoring():
    manifest = find_canary_manifest()
    if manifest is None:
        pytest.skip("no blind canary manifest found - SKIP IS NOT A PASS")
    data = json.loads(manifest.read_text())
    runtime = json.loads(Path(data["runtime_manifest"]).read_text(errors="replace"))
    scoring = json.loads(Path(data["scoring_map"]).read_text(errors="replace"))
    return data, runtime, scoring


def test_bank_first_turn_stats_computable():
    """Smoke: the difficulty proxy must be computable from frozen artifacts,
    otherwise the skew check silently tests nothing."""
    ft = first_turn_correctness()
    assert len(ft) >= 50, (
        f"only {len(ft)} packets with first-turn evidence - skew check would be underpowered; "
        "verify frozen result artifacts are present"
    )
    stats = bank_stats(ft)
    assert stats["rate"] is not None
    print(f"T5 bank baseline: {stats}")


def test_canary_sample_not_skewed_easy():
    manifest = find_canary_manifest()
    if manifest is None:
        pytest.skip(
            "no blind canary manifest found (docs/benchmark/**/*blind*canary*manifest*.json) - "
            "canary not yet sampled. SKIP IS NOT A PASS."
        )
    data = json.loads(manifest.read_text())
    sample_ids = data.get("packet_ids") or []
    assert sample_ids, f"canary manifest {manifest} lists no packet_ids"
    report = skew_check(sample_ids)
    assert not report["sample_ids_missing_from_traces"], (
        f"canary packets without frozen first-turn evidence: {report['sample_ids_missing_from_traces'][:5]}"
    )
    assert not report["skew_violation"], (
        f"CANARY SKEWED EASY: sample first-turn rate {report['sample_rate']:.2f} vs "
        f"bank {report['bank']['rate']:.2f}; one-sided p={report['one_sided_binomial_p_value']}"
    )


def test_canary_runtime_manifest_excludes_scoring_map_fields():
    data, runtime, scoring = _runtime_and_scoring()
    assert data.get("runtime_consumable") is False
    runtime_text = Path(data["runtime_manifest"]).read_text(errors="replace")
    legacy_ids = data.get("packet_ids") or []
    forbidden_terms = [
        "legacy_packet_id",
        "legacy_truth",
        "packet_truth",
        "sibling_id",
        "target_bucket",
        "answer_key",
    ]
    for term in forbidden_terms:
        assert term not in runtime_text, f"runtime manifest leaks scoring field: {term}"
    for legacy_id in legacy_ids:
        assert legacy_id not in runtime_text, f"runtime manifest leaks legacy ID: {legacy_id}"
    assert scoring.get("runtime_consumable") is False


def test_runtime_manifest_does_not_leak_seed_material_or_private_salt():
    _data, runtime, scoring = _runtime_and_scoring()
    forbidden_runtime_keys = {
        "bank_hash",
        "seed_material",
        "seed_label",
        "selection_rule",
        "redraw_policy",
        "redraw_log",
        "private_runtime_salt",
        "scoring_rows",
    }
    hits = sorted(forbidden_runtime_keys.intersection(runtime))
    assert not hits, f"runtime manifest leaks non-runtime metadata: {hits}"
    assert "private_runtime_salt" in scoring, "scoring map must hold private salt for audit only"


def test_private_salt_is_not_public_bank_hash_recipe():
    import hashlib

    data, _runtime, scoring = _runtime_and_scoring()
    public_recipe = hashlib.sha256(
        f"private-runtime-salt|{data['bank_hash']}".encode("utf-8")
    ).hexdigest()
    assert scoring.get("private_runtime_salt") != public_recipe, (
        "private salt is recomputable from public bank hash; use build-time entropy"
    )


def test_runtime_manifest_order_has_no_truth_parity_or_pair_adjacency():
    _data, runtime, scoring = _runtime_and_scoring()
    truth_by_opaque = {
        row["opaque_runtime_id"]: row["legacy_truth"]
        for row in scoring.get("scoring_rows", [])
    }
    legacy_by_opaque = {
        row["opaque_runtime_id"]: row["legacy_packet_id"]
        for row in scoring.get("scoring_rows", [])
    }
    sequence = [truth_by_opaque[row["opaque_runtime_id"]] for row in runtime.get("packets", [])]
    assert len(sequence) == 20
    odd = sequence[0::2]
    even = sequence[1::2]
    assert len(set(odd)) > 1, f"runtime manifest odd positions encode truth: {odd}"
    assert len(set(even)) > 1, f"runtime manifest even positions encode truth: {even}"
    adjacent_pairs = 0
    legacy_sequence = [legacy_by_opaque[row["opaque_runtime_id"]] for row in runtime.get("packets", [])]
    for left, right in zip(legacy_sequence, legacy_sequence[1:]):
        if left[:-2] == right[:-2]:
            adjacent_pairs += 1
    assert adjacent_pairs <= 2, f"runtime manifest preserves too many adjacent sibling pairs: {adjacent_pairs}"


def test_frozen_bank_hash_matches_manifest_pin():
    manifest = find_canary_manifest()
    if manifest is None:
        pytest.skip("no blind canary manifest found - SKIP IS NOT A PASS")
    data = json.loads(manifest.read_text())
    bank_ref = Path(data["bank_ref"])
    frozen = json.loads(bank_ref.read_text(errors="replace"))
    assert frozen.get("bank_hash") == data.get("bank_hash")
    assert frozen.get("bank_stats") == data.get("bank", {}).get("frozen_bank_stats")


def test_blind_runner_source_does_not_reference_scoring_map():
    source = Path("holoverify_blind_runner_v0.py").read_text(errors="replace")
    forbidden = [
        "scoring_map",
        "legacy_packet_id",
        "legacy_truth",
        "packet_truth",
    ]
    hits = [term for term in forbidden if term in source]
    assert not hits, f"blind runner source references post-hoc scoring fields: {hits}"


def test_runtime_executor_reads_only_runtime_manifest_payloads_and_outdir(monkeypatch, tmp_path):
    runner, missing = load_runner()
    if runner is None:
        pytest.skip(SKIP_REASON)
    assert not missing, f"blind runner contract violation - missing attrs: {missing}"

    data, runtime, _scoring = _runtime_and_scoring()
    runtime_path = Path(data["runtime_manifest"]).resolve()
    payload_paths = [
        Path(row["runtime_payload_ref"]).resolve()
        for row in runtime.get("packets", [])
    ]
    assert payload_paths, "runtime manifest has no payload refs"
    payload_dirs = {path.parent for path in payload_paths}
    out_root = tmp_path.resolve()

    original_read_text = Path.read_text
    original_open = Path.open
    read_paths: list[str] = []

    def allowed(path: Path, mode: str) -> bool:
        resolved = path.resolve()
        if "r" in mode and resolved == runtime_path:
            return True
        if "r" in mode and resolved in payload_paths:
            return True
        if any(flag in mode for flag in ("w", "a", "x")):
            try:
                resolved.relative_to(out_root)
                return True
            except ValueError:
                return False
        return False

    def guarded_read_text(self, *args, **kwargs):
        resolved = self.resolve()
        read_paths.append(str(resolved))
        assert allowed(self, "r"), f"runtime executor attempted forbidden read: {resolved}"
        return original_read_text(self, *args, **kwargs)

    def guarded_open(self, mode="r", *args, **kwargs):
        resolved = self.resolve()
        assert allowed(self, mode), f"runtime executor attempted forbidden file access: {resolved}"
        return original_open(self, mode, *args, **kwargs)

    def transport(messages):
        content = messages[0]["content"]
        if "blind Gov actuator" in content:
            return "\n".join(
                [
                    "route_verdict=CONTINUE",
                    "repair_target=preserve blind source-grounded reasoning",
                    "blocked_move=do not invent source IDs",
                ]
            )
        ids = re.findall(r"\b([A-Z]{2,}(?:-[A-Z0-9]+)+):", content)
        cited = "|".join(ids[:2] or ["SRC-FIXTURE"])
        return "\n".join(
            [
                mock_transcripts(1, verdict="ESCALATE")[0],
                f"cited_evidence={cited}",
            ]
        )

    monkeypatch.setattr(Path, "read_text", guarded_read_text)
    monkeypatch.setattr(Path, "open", guarded_open)
    result = runner.run_blind_runtime_manifest(str(runtime_path), str(tmp_path), transport=transport)
    assert result["packet_count"] == len(payload_paths)
    assert result["observed_call_count"] == len(payload_paths) * runner.BUDGET_LIMITS["max_calls_per_packet"]
    assert str(runtime_path) in read_paths
    for path in payload_paths:
        assert str(path) in read_paths
    assert all(path == runtime_path or any(path.parent == d for d in payload_dirs) for path in map(Path, read_paths))
