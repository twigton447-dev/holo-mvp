from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from holo_builder.freeze_manifest import compute_payload_hash
from holo_builder.frozen_4dna_runner import (
    build_pair_dry_run_report,
    load_available_mini_pool,
    load_frozen_packet_for_dry_run,
    main,
    select_4dna_roster,
)


COHORT = Path("ablation_cohort_mini.json")
ALLOW = Path("holo_builder/outputs/frozen/HBB-BEC-001_8181d83c.json")
ESCALATE = Path("holo_builder/outputs/frozen/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc.json")
ALLOW_HASH = "8181d83ceb7f36f97160f078a4d4d35bdced5555fba5478c55bd3d954f40c4f1"
ESCALATE_HASH = "807468fcba476a97ef92cf4058af0767c73a66a450bda37c60c6bfaa8be5e883"
SESSION_ID = "HBB-BEC-001_pair_4dna_seed447"


def test_4dna_roster_is_fixed_size_and_excludes_one_non_gov() -> None:
    pool = load_available_mini_pool(COHORT)
    roster = select_4dna_roster(pool, seed=447, session_id=SESSION_ID)

    gov = roster["holo_gov"]
    active_non_gov = roster["active_non_gov"]
    excluded = roster["excluded"]

    assert roster["active_roster_size"] == 4
    assert len(active_non_gov) == 3
    assert len(excluded) == 1
    assert gov not in active_non_gov
    assert len({model["provider"] for model in [gov, *active_non_gov, *excluded]}) == 5


def test_same_seed_replays_same_roster_and_different_seed_can_differ() -> None:
    pool = load_available_mini_pool(COHORT)
    first = select_4dna_roster(pool, seed=447, session_id=SESSION_ID)
    replay = select_4dna_roster(pool, seed=447, session_id=SESSION_ID)

    assert first == replay

    alternatives = {
        json.dumps(select_4dna_roster(pool, seed=seed, session_id=f"session-{seed}"), sort_keys=True)
        for seed in range(440, 455)
    }
    assert len(alternatives) > 1


def test_pair_dry_run_uses_one_roster_for_both_packets_and_writes_no_traces() -> None:
    report = build_pair_dry_run_report(
        cohort_path=COHORT,
        seed=447,
        session_id=SESSION_ID,
        allow_packet_path=ALLOW,
        allow_expected_hash=ALLOW_HASH,
        escalate_packet_path=ESCALATE,
        escalate_expected_hash=ESCALATE_HASH,
    )

    assert report["dry_run"] is True
    assert report["no_live_calls"] is True
    assert report["no_traces_created"] is True
    assert report["output_dirs"] == []
    assert report["roster"]["session_id"] == SESSION_ID
    assert len(report["packets"]) == 2
    assert len(report["run_ids"]) == 2
    assert report["packets"][0]["payload_hash"] == ALLOW_HASH
    assert report["packets"][1]["payload_hash"] == ESCALATE_HASH
    assert report["packets"][0]["model_visible_keys"] == ["action", "context"]
    assert report["packets"][1]["model_visible_keys"] == ["action", "context"]


def test_frozen_packet_hash_mismatch_blocks_adapter() -> None:
    with pytest.raises(ValueError, match="payload hash mismatch"):
        load_frozen_packet_for_dry_run(ALLOW, "0" * 64)


def test_missing_taylor_approval_blocks_adapter(tmp_path: Path) -> None:
    packet = json.loads(ALLOW.read_text())
    packet["_frozen"]["approved_by"] = None
    path = tmp_path / "missing_approval.json"
    path.write_text(json.dumps(packet))

    with pytest.raises(ValueError, match="missing Taylor freeze approval"):
        load_frozen_packet_for_dry_run(path, ALLOW_HASH)


def test_hidden_metadata_excluded_from_model_visible_extraction() -> None:
    loaded = load_frozen_packet_for_dry_run(ALLOW, ALLOW_HASH)

    assert sorted(loaded["model_visible"].keys()) == ["action", "context"]
    assert "_frozen" not in loaded["model_visible"]
    assert "_builder" not in loaded["model_visible"]
    assert "_internal" not in loaded["model_visible"]
    assert "expected_verdict" not in loaded["model_visible"]


def test_forbidden_metadata_inside_payload_blocks_adapter(tmp_path: Path) -> None:
    packet = copy.deepcopy(json.loads(ALLOW.read_text()))
    packet["payload"]["context"]["expected_verdict"] = "ALLOW"
    new_hash = compute_payload_hash(packet)
    packet["_frozen"]["hash"] = new_hash
    path = tmp_path / "leaky_payload.json"
    path.write_text(json.dumps(packet))

    with pytest.raises(ValueError, match="payload visibility errors"):
        load_frozen_packet_for_dry_run(path, new_hash)


def test_unknown_provider_or_model_in_mini_cohort_fails_closed(tmp_path: Path) -> None:
    cohort = json.loads(COHORT.read_text())
    cohort["models"]["mystery"] = "tiny-but-unknown"
    path = tmp_path / "unknown_provider.json"
    path.write_text(json.dumps(cohort))

    with pytest.raises(ValueError, match="approved five-mini"):
        load_available_mini_pool(path)

    cohort = json.loads(COHORT.read_text())
    cohort["models"]["openai"] = "gpt-5.4"
    path = tmp_path / "wrong_model.json"
    path.write_text(json.dumps(cohort))

    with pytest.raises(ValueError, match="approved five-mini"):
        load_available_mini_pool(path)


def test_malformed_mini_cohort_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "malformed.json"
    path.write_text(json.dumps({"cohort_id": "bad", "models": []}))

    with pytest.raises(ValueError, match="non-empty models mapping"):
        load_available_mini_pool(path)


def test_cli_missing_required_hash_fails_closed() -> None:
    with pytest.raises(SystemExit) as exc:
        main([
            "--seed", "447",
            "--session-id", SESSION_ID,
            "--allow-packet", str(ALLOW),
            "--allow-hash", ALLOW_HASH,
            "--escalate-packet", str(ESCALATE),
        ])

    assert exc.value.code != 0


def test_dry_run_module_has_no_provider_adapter_imports_or_trace_writes() -> None:
    source = Path("holo_builder/frozen_4dna_runner.py").read_text()

    assert "llm_adapters" not in source
    assert "OpenAIAdapter" not in source
    assert "AnthropicAdapter" not in source
    assert "GoogleAdapter" not in source
    assert "write_text(" not in source
    assert "open(" not in source


def test_cli_dry_run_does_not_create_trace_files(tmp_path: Path) -> None:
    before = {path.name for path in tmp_path.iterdir()}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "holo_builder.frozen_4dna_runner",
            "--seed",
            "447",
            "--session-id",
            SESSION_ID,
            "--allow-packet",
            str(ALLOW),
            "--allow-hash",
            ALLOW_HASH,
            "--escalate-packet",
            str(ESCALATE),
            "--escalate-hash",
            ESCALATE_HASH,
        ],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    after = {path.name for path in tmp_path.iterdir()}
    report = json.loads(result.stdout)

    assert before == after
    assert report["dry_run"] is True
    assert report["no_live_calls"] is True
    assert report["no_traces_created"] is True
    assert report["output_dirs"] == []
