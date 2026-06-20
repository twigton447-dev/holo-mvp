from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from benchmark_factory.batches import build_BAL100_leaderboard_20_allow_official_trace_preflight as base
from holo_builder.frozen_4dna_runner import FORBIDDEN_MODEL_VISIBLE_KEYS


RUN_ID = "BAL100-ALLOW-REPLACEMENTS-FROZEN-HV-PREFLIGHT-001"
RUN_TYPE = "bal100_allow_replacements_hv_official_trace_preflight"
SEED = base.SEED
COHORT_PATH = base.COHORT_PATH
DEFAULT_OUT_DIR = Path("scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_preflight_001")
DEFAULT_JSON_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_PREFLIGHT_001.json")
DEFAULT_MD_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_PREFLIGHT_001.md")

APPROVAL_ENV = "BAL100_LEADERBOARD20_REPLACEMENT_ALLOW_TRACE_APPROVED"
APPROVAL_VALUE = "I_APPROVE_REPLACEMENT_ALLOW_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
CODEX_APPROVAL_ENV = "BAL100_LEADERBOARD20_CODEX_REPLACEMENT_ALLOW_TRACE_APPROVED"
CODEX_APPROVAL_VALUE = "I_APPROVE_CODEX_REPLACEMENT_ALLOW_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"

FROZEN_PACKETS = [
    {
        "packet_id": "BAL100-HARD-ALLOW-REP-001-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-REP-001",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-001-ALLOW_9706a499.json",
        "payload_hash": "9706a499af2c69003e452f6051642c733bf75fde8d9edb1dbf4245c58fb68991",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-REP-002-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-REP-002",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-002-ALLOW_999d2812.json",
        "payload_hash": "999d2812a089929ccdb359c25deadb4e2b2954ce35a20c7484517233fe4c39c8",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-REP-003-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-REP-003",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-003-ALLOW_c8566512.json",
        "payload_hash": "c8566512d0ef5684701acaec4e0b4fdef2735cbfba3ec8420c3e771d5c9c62ad",
    },
]


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _safe_model_name(model: str) -> str:
    return base._safe_model_name(model)


def _session_id(packet_id: str) -> str:
    return f"{packet_id}_4dna_seed{SEED}"


def _transport_provider(roster_provider: str) -> str:
    return base._transport_provider(roster_provider)


def analyst_system_prompt() -> str:
    return base.analyst_system_prompt()


def gov_system_prompt() -> str:
    return base.gov_system_prompt()


def _model_visible_user(packet: dict[str, Any]) -> str:
    return json.dumps(packet["model_visible"], sort_keys=True)


def _load_packets() -> list[dict[str, Any]]:
    packets = []
    for entry in FROZEN_PACKETS:
        loaded = base.load_frozen_packet_for_dry_run(entry["frozen_packet_path"], entry["payload_hash"])
        if loaded["scenario_id"] != entry["packet_id"]:
            raise SystemExit(f"{entry['frozen_packet_path']}: scenario_id mismatch")
        loaded.update(
            {
                "family_id": entry["family_id"],
                "session_id": _session_id(entry["packet_id"]),
                "expected_private_truth": "ALLOW",
            }
        )
        packets.append(loaded)
    if len(packets) != 3:
        raise SystemExit(f"Expected exactly three frozen replacement ALLOW packets, got {len(packets)}")
    return packets


def _roster(session_id: str) -> dict[str, Any]:
    pool = base.load_available_mini_pool(COHORT_PATH)
    return base.select_4dna_roster(pool, seed=SEED, session_id=session_id)


def _active_prompt_card(packet: dict[str, Any], roster_model: dict[str, str]) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "preflight_only": True,
        "official_trace": False,
        "judge": False,
        "freeze": False,
        "provider_transmitted_fields": ["system", "user"],
        "packet_id": packet["scenario_id"],
        "packet_hash": packet["payload_hash"],
        "hash8": packet["hash8"],
        "family_id": packet["family_id"],
        "provider": roster_model["provider"],
        "transport_provider": _transport_provider(roster_model["provider"]),
        "model": roster_model["model"],
        "role": "active_non_gov",
        "system": analyst_system_prompt(),
        "user": _model_visible_user(packet),
    }


def _gov_template_card(packet: dict[str, Any], roster_model: dict[str, str]) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "preflight_only": True,
        "official_trace": False,
        "judge": False,
        "freeze": False,
        "provider_transmitted_fields": ["system", "user"],
        "packet_id": packet["scenario_id"],
        "packet_hash": packet["payload_hash"],
        "hash8": packet["hash8"],
        "family_id": packet["family_id"],
        "provider": roster_model["provider"],
        "transport_provider": _transport_provider(roster_model["provider"]),
        "model": roster_model["model"],
        "role": "holo_gov_template",
        "system": gov_system_prompt(),
        "user": json.dumps(
            {
                "action": packet["model_visible"]["action"],
                "context": packet["model_visible"]["context"],
                "active_non_gov_responses": [],
            },
            sort_keys=True,
        ),
    }


def _write_prompt_cards(packets: list[dict[str, Any]], out_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    prompt_dir = out_dir / "prompt_cards"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    cards: list[dict[str, Any]] = []
    rosters: dict[str, Any] = {}
    for packet in packets:
        roster = _roster(packet["session_id"])
        rosters[packet["session_id"]] = roster
        for roster_model in roster["active_non_gov"]:
            card = _active_prompt_card(packet, roster_model)
            cards.append(card)
            card_path = prompt_dir / f"{packet['scenario_id']}__active__{roster_model['provider']}__{_safe_model_name(roster_model['model'])}.json"
            _write_json(card_path, card)
        gov_card = _gov_template_card(packet, roster["holo_gov"])
        cards.append(gov_card)
        gov_path = prompt_dir / f"{packet['scenario_id']}__hologov_template__{_safe_model_name(roster['holo_gov']['model'])}.json"
        _write_json(gov_path, gov_card)
    return cards, rosters


def _packet_manifest_row(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": packet["scenario_id"],
        "family_id": packet["family_id"],
        "frozen_packet_path": packet["path"],
        "payload_hash": packet["payload_hash"],
        "hash8": packet["hash8"],
        "model_visible_keys": packet["model_visible_keys"],
        "frozen_approved_by": packet["frozen_approved_by"],
        "private_expected_truth_for_later_judge": packet["expected_private_truth"],
    }


def build_preflight(out_dir: Path) -> dict[str, Any]:
    packets = _load_packets()
    cards, rosters = _write_prompt_cards(packets, out_dir)
    prompt_card_failures = [
        {
            "packet_id": card["packet_id"],
            "role": card["role"],
            "provider": card["provider"],
            "forbidden_user_keys": base._forbidden_keys_in_user(card["user"]),
            "forbidden_user_values": base._forbidden_values_in_user(card["user"]),
        }
        for card in cards
        if base._forbidden_keys_in_user(card["user"]) or base._forbidden_values_in_user(card["user"])
    ]

    active_cards = [card for card in cards if card["role"] == "active_non_gov"]
    gov_templates = [card for card in cards if card["role"] == "holo_gov_template"]
    failures: list[str] = []
    if prompt_card_failures:
        failures.append("one or more prompt-card user payloads contains forbidden hidden/build keys")
    if len(active_cards) != 9:
        failures.append(f"expected 9 active prompt cards, got {len(active_cards)}")
    if len(gov_templates) != 3:
        failures.append(f"expected 3 HoloGov template cards, got {len(gov_templates)}")

    manifest = {
        "artifact_type": "BAL100_leaderboard_20_allow_replacement_official_trace_preflight",
        "created_at": base._utc_now(),
        "run_id": RUN_ID,
        "run_type": RUN_TYPE,
        "status": "PASS" if not failures else "FAIL",
        "mode": "official_trace_preflight_no_live_no_judge_no_scorecard",
        "seed": SEED,
        "cohort_path": str(COHORT_PATH),
        "out_dir": str(out_dir),
        "packets": [_packet_manifest_row(packet) for packet in packets],
        "packet_count": len(packets),
        "allow_packets": len(packets),
        "escalate_packets": 0,
        "rosters": rosters,
        "prompt_cards": {
            "directory": str(out_dir / "prompt_cards"),
            "total": len(cards),
            "active_non_gov": len(active_cards),
            "holo_gov_templates": len(gov_templates),
            "provider_transmitted_fields": ["system", "user"],
            "active_user_payload_contract": ["action", "context"],
            "hologov_template_user_payload_contract": ["action", "active_non_gov_responses", "context"],
        },
        "expected_future_live_outputs": {
            "provider_rows": 12,
            "official_trace_records": 3,
            "results_jsonl": str(out_dir / "results.jsonl"),
            "summary_json": str(out_dir / "summary.json"),
            "trace_dir": str(out_dir / "official_trace_records"),
        },
        "approval_contract": {
            "operator": "Taylor",
            "approval_env": APPROVAL_ENV,
            "approval_value": APPROVAL_VALUE,
            "codex_approval_env": CODEX_APPROVAL_ENV,
            "codex_approval_value": CODEX_APPROVAL_VALUE,
            "approval_scope": "exact three frozen replacement BAL100 hard-ALLOW packets listed in this manifest only",
        },
        "future_live_command_shape": [
            f"export {APPROVAL_ENV}=\"{APPROVAL_VALUE}\"",
            f"export {CODEX_APPROVAL_ENV}=\"{CODEX_APPROVAL_VALUE}\"",
            "python3 -B benchmark_factory/batches/run_BAL100_leaderboard_20_allow_replacement_official_trace.py --execute-provider-calls --operator Taylor --allow-codex-provider-calls --yes-send-frozen-payloads-to-providers --out-dir scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_<timestamp>",
        ],
        "validation": {
            "failure_count": len(failures),
            "failures": failures,
            "exact_packet_count": len(packets) == 3,
            "all_packets_allow_private_truth": all(packet["expected_private_truth"] == "ALLOW" for packet in packets),
            "all_frozen_approved_by_taylor": all(packet["frozen_approved_by"] == "Taylor" for packet in packets),
            "all_model_visible_keys_action_context": all(packet["model_visible_keys"] == ["action", "context"] for packet in packets),
            "prompt_card_forbidden_user_key_failures": prompt_card_failures,
            "hidden_metadata_excluded": sorted(FORBIDDEN_MODEL_VISIBLE_KEYS | base.FORBIDDEN_PROMPT_USER_KEYS),
        },
        "non_actions": {
            "provider_calls": False,
            "official_trace": False,
            "judge": False,
            "qa": False,
            "ablation": False,
            "scorecard_movement": False,
            "leaderboard_movement": False,
            "push": False,
        },
        "next_gate": "After Taylor approves the exact replacement live official trace command, run provider execution for these three frozen packets only; Judge and leaderboard remain separate later gates.",
    }
    _write_json(out_dir / "official_trace_preflight_manifest.json", manifest)
    return manifest


def render_markdown(manifest: dict[str, Any]) -> str:
    packet_rows = "\n".join(
        "| {packet_id} | `{hash8}` | `{frozen_packet_path}` | {frozen_approved_by} |".format(**packet)
        for packet in manifest["packets"]
    )
    return f"""# BAL100 Leaderboard 20 ALLOW Replacement Official Trace Preflight

Created: {manifest['created_at']}

Status: `{manifest['status']}`

Mode: `{manifest['mode']}`

## Scope

| Packet | Hash8 | Frozen Path | Frozen Approval |
| --- | --- | --- | --- |
{packet_rows}

## Expected Future Live Shape

- Packets: {manifest['packet_count']}
- ALLOW packets: {manifest['allow_packets']}
- ESCALATE packets: {manifest['escalate_packets']}
- Prompt-card templates: {manifest['prompt_cards']['total']}
- Active non-Gov prompt cards: {manifest['prompt_cards']['active_non_gov']}
- HoloGov template cards: {manifest['prompt_cards']['holo_gov_templates']}
- Expected future provider rows: {manifest['expected_future_live_outputs']['provider_rows']}
- Expected future official trace records: {manifest['expected_future_live_outputs']['official_trace_records']}

## Approval Contract

- `{APPROVAL_ENV}={APPROVAL_VALUE}`
- `{CODEX_APPROVAL_ENV}={CODEX_APPROVAL_VALUE}`
- Scope: {manifest['approval_contract']['approval_scope']}

## Future Live Command Shape

```bash
export {APPROVAL_ENV}="{APPROVAL_VALUE}"
export {CODEX_APPROVAL_ENV}="{CODEX_APPROVAL_VALUE}"
python3 -B benchmark_factory/batches/run_BAL100_leaderboard_20_allow_replacement_official_trace.py \\
  --execute-provider-calls \\
  --operator Taylor \\
  --allow-codex-provider-calls \\
  --yes-send-frozen-payloads-to-providers \\
  --out-dir scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_<timestamp>
```

## Validation

- Failure count: {manifest['validation']['failure_count']}
- Exact packet count: {manifest['validation']['exact_packet_count']}
- All frozen approved by Taylor: {manifest['validation']['all_frozen_approved_by_taylor']}
- All model-visible packet keys are action/context: {manifest['validation']['all_model_visible_keys_action_context']}

## Boundaries

- No provider calls.
- No official trace records written.
- No Judge.
- No QA or ablation.
- No scorecard or leaderboard movement.
- No push.

Next gate: {manifest['next_gate']}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build no-live official trace preflight for the three frozen BAL100 replacement hard-ALLOW packets.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    manifest = build_preflight(out_dir)
    _write_json(Path(args.json_out), manifest)
    Path(args.md_out).write_text(render_markdown(manifest))
    print(f"Wrote {out_dir / 'official_trace_preflight_manifest.json'}")
    print(f"Wrote {args.json_out}")
    print(f"Wrote {args.md_out}")
    print(
        "status={status} packets={packets} prompt_cards={cards} expected_future_rows={rows} failures={failures}".format(
            status=manifest["status"],
            packets=manifest["packet_count"],
            cards=manifest["prompt_cards"]["total"],
            rows=manifest["expected_future_live_outputs"]["provider_rows"],
            failures=manifest["validation"]["failure_count"],
        )
    )
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
