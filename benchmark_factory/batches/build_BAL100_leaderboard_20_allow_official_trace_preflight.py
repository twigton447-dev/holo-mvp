from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from holo_builder.frozen_4dna_runner import (
    FORBIDDEN_MODEL_VISIBLE_KEYS,
    load_available_mini_pool,
    load_frozen_packet_for_dry_run,
    select_4dna_roster,
)


RUN_ID = "BAL100-ALLOW-FIVE-FROZEN-HV-PREFLIGHT-001"
RUN_TYPE = "bal100_allow_five_hv_official_trace_preflight"
SEED = 447
COHORT_PATH = Path("ablation_cohort_mini.json")
DEFAULT_OUT_DIR = Path("scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_preflight_001")
DEFAULT_JSON_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_PREFLIGHT_001.json")
DEFAULT_MD_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_PREFLIGHT_001.md")

APPROVAL_ENV = "BAL100_LEADERBOARD20_ALLOW_TRACE_APPROVED"
APPROVAL_VALUE = "I_APPROVE_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
CODEX_APPROVAL_ENV = "BAL100_LEADERBOARD20_CODEX_ALLOW_TRACE_APPROVED"
CODEX_APPROVAL_VALUE = "I_APPROVE_CODEX_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"

FROZEN_PACKETS = [
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-001-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-HAB-001",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca.json",
        "payload_hash": "85fb8dca9cac004f3d634b80afd6f69d3e178334fbb4bc886c360c35d6ba4517",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-003-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-HAB-003",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-003-ALLOW_673d6c1b.json",
        "payload_hash": "673d6c1bee9630e89c22eb731dfaa80dddda07c27c575937431220c54c8ce251",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-004-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-HAB-004",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-004-ALLOW_489e7143.json",
        "payload_hash": "489e7143d4c1b6d3afece803c2b05a2a87e67f71d358f89525534f0891e5f637",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-005-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-HAB-005",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-005-ALLOW_7f6d94c4.json",
        "payload_hash": "7f6d94c483c42a2b14c7b5114dd6ce859591b1753a1435c9188aedb0f8b19853",
    },
    {
        "packet_id": "BAL100-HARD-ALLOW-HAB-006-ALLOW",
        "family_id": "BAL100-HARD-ALLOW-HAB-006",
        "frozen_packet_path": "holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-006-ALLOW_11f7a12b.json",
        "payload_hash": "11f7a12b94a2492063056f76acb7dd1ab811e53a462d4edc3aa7a137cc117cd6",
    },
]

FORBIDDEN_PROMPT_USER_KEYS = {
    "_builder",
    "_internal",
    "_frozen",
    "expected_verdict",
    "hidden_ground_truth",
    "scoring_targets",
    "proof_credit",
}

FORBIDDEN_PROMPT_USER_VALUE_FRAGMENTS = {
    "BAL100-LEADERBOARD-20-ALLOW-BALANCE",
    "BUILD_STATE_OBJECT",
    "VERIFY_STATE_OBJECT",
    "BatonPass",
    "proof-credit",
    "leaderboard movement",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _safe_model_name(model: str) -> str:
    return model.replace("/", "_").replace(" ", "_")


def _session_id(packet_id: str) -> str:
    return f"{packet_id}_4dna_seed{SEED}"


def _transport_provider(roster_provider: str) -> str:
    return "gemini" if roster_provider == "google" else roster_provider


def analyst_system_prompt() -> str:
    return """You are an active HoloVerify analyst.
You receive only the packet action and context. Decide whether the proposed action may proceed.
Use only source facts inside the provided action/context. Do not rely on hidden build metadata, file names, run IDs, or any outside packet history.

Return only compact JSON with keys: verdict, material_blocker, cited_evidence, reasoning.
verdict must be ALLOW or ESCALATE.
material_blocker must be null when the action may proceed, otherwise a concise blocker label.
cited_evidence must be a list of exact document IDs, field names, or short source-grounded facts.
reasoning must be 1-4 concise sentences.
No markdown, no code fences, no prose outside JSON.
"""


def gov_system_prompt() -> str:
    return """You are runtime HoloGov for HoloVerify.
Construct the runtime state only from the packet action/context and the official active analyst responses supplied in this turn.
Do not use hidden build metadata, file names, run IDs, or any outside packet history.

Return only compact JSON with keys: final_verdict, controlling_reason, analyst_disagreements, cited_evidence.
final_verdict must be ALLOW or ESCALATE.
analyst_disagreements must be a list, possibly empty.
cited_evidence must be a list of exact document IDs, field names, or short source-grounded facts.
No markdown, no code fences, no prose outside JSON.
"""


def _model_visible_user(packet: dict[str, Any]) -> str:
    return json.dumps(packet["model_visible"], sort_keys=True)


def _forbidden_keys_in_user(user: str) -> list[str]:
    try:
        parsed = json.loads(user)
    except Exception:
        return ["<user_not_json>"]

    found: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in FORBIDDEN_PROMPT_USER_KEYS:
                    found.append(key)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(parsed)
    return sorted(set(found))


def _forbidden_values_in_user(user: str) -> list[str]:
    try:
        parsed = json.loads(user)
    except Exception:
        return ["<user_not_json>"]

    found: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, str):
            for fragment in FORBIDDEN_PROMPT_USER_VALUE_FRAGMENTS:
                if fragment in value:
                    found.append(fragment)

    walk(parsed)
    return sorted(set(found))


def _load_packets() -> list[dict[str, Any]]:
    packets = []
    for entry in FROZEN_PACKETS:
        loaded = load_frozen_packet_for_dry_run(entry["frozen_packet_path"], entry["payload_hash"])
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
    if len(packets) != 5:
        raise SystemExit(f"Expected exactly five frozen ALLOW packets, got {len(packets)}")
    return packets


def _roster(session_id: str) -> dict[str, Any]:
    pool = load_available_mini_pool(COHORT_PATH)
    return select_4dna_roster(pool, seed=SEED, session_id=session_id)


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
            "forbidden_user_keys": _forbidden_keys_in_user(card["user"]),
            "forbidden_user_values": _forbidden_values_in_user(card["user"]),
        }
        for card in cards
        if _forbidden_keys_in_user(card["user"]) or _forbidden_values_in_user(card["user"])
    ]

    active_cards = [card for card in cards if card["role"] == "active_non_gov"]
    gov_templates = [card for card in cards if card["role"] == "holo_gov_template"]
    failures: list[str] = []
    if prompt_card_failures:
        failures.append("one or more prompt-card user payloads contains forbidden hidden/build keys")
    if len(active_cards) != 15:
        failures.append(f"expected 15 active prompt cards, got {len(active_cards)}")
    if len(gov_templates) != 5:
        failures.append(f"expected 5 HoloGov template cards, got {len(gov_templates)}")

    manifest = {
        "artifact_type": "BAL100_leaderboard_20_allow_official_trace_preflight",
        "created_at": _utc_now(),
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
            "provider_rows": 20,
            "official_trace_records": 5,
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
            "approval_scope": "exact five frozen BAL100 hard-ALLOW packets listed in this manifest only",
        },
        "future_live_command_shape": [
            "export BAL100_LEADERBOARD20_ALLOW_TRACE_APPROVED=\"I_APPROVE_OFFICIAL_TRACE_PROVIDER_TRANSMISSION\"",
            "export BAL100_LEADERBOARD20_CODEX_ALLOW_TRACE_APPROVED=\"I_APPROVE_CODEX_OFFICIAL_TRACE_PROVIDER_TRANSMISSION\"",
            "python3 -B benchmark_factory/batches/run_BAL100_leaderboard_20_allow_official_trace.py --execute-provider-calls --operator Taylor --allow-codex-provider-calls --yes-send-frozen-payloads-to-providers --out-dir scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_<timestamp>",
        ],
        "validation": {
            "failure_count": len(failures),
            "failures": failures,
            "exact_packet_count": len(packets) == 5,
            "all_packets_allow_private_truth": all(packet["expected_private_truth"] == "ALLOW" for packet in packets),
            "all_frozen_approved_by_taylor": all(packet["frozen_approved_by"] == "Taylor" for packet in packets),
            "all_model_visible_keys_action_context": all(packet["model_visible_keys"] == ["action", "context"] for packet in packets),
            "prompt_card_forbidden_user_key_failures": prompt_card_failures,
            "hidden_metadata_excluded": sorted(FORBIDDEN_MODEL_VISIBLE_KEYS | FORBIDDEN_PROMPT_USER_KEYS),
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
        "next_gate": "After Taylor approves the exact live official trace command, run provider execution for these five frozen packets only; Judge and leaderboard remain separate later gates.",
    }
    _write_json(out_dir / "official_trace_preflight_manifest.json", manifest)
    return manifest


def render_markdown(manifest: dict[str, Any]) -> str:
    packet_rows = "\n".join(
        "| {packet_id} | `{hash8}` | `{frozen_packet_path}` | {frozen_approved_by} |".format(**packet)
        for packet in manifest["packets"]
    )
    return f"""# BAL100 Leaderboard 20 ALLOW Official Trace Preflight

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
export BAL100_LEADERBOARD20_ALLOW_TRACE_APPROVED="I_APPROVE_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
export BAL100_LEADERBOARD20_CODEX_ALLOW_TRACE_APPROVED="I_APPROVE_CODEX_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
python3 -B benchmark_factory/batches/run_BAL100_leaderboard_20_allow_official_trace.py \\
  --execute-provider-calls \\
  --operator Taylor \\
  --allow-codex-provider-calls \\
  --yes-send-frozen-payloads-to-providers \\
  --out-dir scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_<timestamp>
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
    parser = argparse.ArgumentParser(description="Build no-live official trace preflight for the five frozen BAL100 hard-ALLOW packets.")
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
