#!/usr/bin/env python3
"""Run the Agentic Commerce HoloVerify replication family.

This wrapper reuses the hardened AP OpenAI-W2 runtime path, but retargets it to
the frozen Agentic Commerce family from the three-family packet bank. It does
not edit packets or prompts.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

AP_RUNNER_PATH = BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py"
AP_ROOT = BENCHMARK_ROOT / "holoverify_ap_procurement_replication_2026-06-29"
COMMERCE_ROOT = BENCHMARK_ROOT / "holoverify_agentic_commerce_replication_2026-06-29"
FAMILY_ID = "HV-ACOM-REP-2026-06-29"
VARIANT_NAME = "COMMERCE_OPENAI_W2_ROSTER_VARIANT_2026_06_29"
REGISTRATION_JSON = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_ROSTER_VARIANT_REGISTRATION_2026_06_29.json"
REGISTRATION_MD = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_ROSTER_VARIANT_REGISTRATION_2026_06_29.md"
AVAILABILITY_JSON = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_MODEL_AVAILABILITY_CHECK_2026_06_29.json"
AVAILABILITY_MD = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_MODEL_AVAILABILITY_CHECK_2026_06_29.md"


def load_ap_runner():
    spec = importlib.util.spec_from_file_location("commerce_wrapped_ap_holo_runner", AP_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


AP = load_ap_runner()


def convert_commerce_payload(packet: dict[str, Any]) -> dict[str, Any]:
    internal_documents = []
    policy_documents = []
    for record in packet["source_control_facts"]:
        doc = {
            "doc_id": record["source_id"],
            "type": record["source_type"],
            "content": record["content"],
        }
        if record["source_type"] == "policy_control":
            policy_documents.append(
                {
                    "doc_id": record["source_id"],
                    "title": "Frozen commerce source-boundary policy",
                    "content": record["content"],
                }
            )
        else:
            internal_documents.append(doc)
    return {
        "action": {
            "business_ref": packet["model_visible_payload"]["case_ref"],
            "type": "agentic_commerce_order_execution_action",
            "vendor": "Frozen commerce account record",
            "amount": 0,
            "currency": "USD",
            "description": packet["action_boundary"],
            "action_date": "2026-06-29",
        },
        "context": {
            "action_boundary": packet["action_boundary"],
            "anomaly_observed": packet["tempting_wrong_move"],
            "explanation_summary": "Verify whether the frozen commerce source records close the exact action boundary before execution.",
            "internal_documents": internal_documents,
            "policy_documents": policy_documents,
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def configure_commerce_runtime() -> None:
    COMMERCE_ROOT.mkdir(parents=True, exist_ok=True)
    AP.AP_ROOT = COMMERCE_ROOT
    AP.PRE_RUN_MANIFEST = COMMERCE_ROOT / "COMMERCE_PRE_RUN_MANIFEST.json"
    AP.OPENAI_W2_PREFLIGHT_MD = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_LIVE_HOLO_PREFLIGHT_2026_06_29.md"
    AP.OPENAI_W2_PREFLIGHT_JSON = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_LIVE_HOLO_PREFLIGHT_2026_06_29.json"
    AP.AP_FAMILY_ID = FAMILY_ID
    AP.OPENAI_W2_VARIANT_NAME = VARIANT_NAME
    AP.OPENAI_W2_REGISTRATION = REGISTRATION_JSON
    AP.OPENAI_W2_AVAILABILITY = AVAILABILITY_JSON
    AP.OPENAI_W2_HOLO_RUN_ROOT = COMMERCE_ROOT / "holo_live_runs_openai_w2"
    AP.convert_payload = convert_commerce_payload


def ensure_registration_files() -> None:
    COMMERCE_ROOT.mkdir(parents=True, exist_ok=True)
    if not REGISTRATION_JSON.exists():
        registration = {
            "classification": "PRE_REGISTERED_ROSTER_VARIANT_NO_LIVE_RUN",
            "variant_name": VARIANT_NAME,
            "created_for": "Agentic commerce order-execution replication family",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reason_for_variant": "Use the hardened OpenAI-W2 runtime path that passed AP full-family Holo execution; original preregistered Gemini W2 lane remains provider-risky.",
            "frozen_packet_bank": {
                "source_commit": AP.EXPECTED_FREEZE_COMMIT,
                "freeze_root": AP.EXPECTED_FREEZE_ROOT_HASH,
                "family_id": FAMILY_ID,
                "packets": 40,
                "pairs": 20,
                "allow_truths": 20,
                "escalate_truths": 20,
                "packet_hashes_match_freeze": "PASS_BY_PREFLIGHT",
                "prompt_hashes_match_freeze": "PASS_BY_PREFLIGHT",
            },
            "new_holo_roster": {
                "worker_sequence": [
                    {"slot": "W1", "provider": "xai", "model": "grok-3-mini", "role": "SOURCE_BOUNDARY_MAPPER"},
                    {"slot": "W2", "provider": "openai", "model": AP.OPENAI_W2_MODEL_ID, "role": "ADVERSARIAL_SCOPE_CHALLENGER"},
                    {"slot": "W3", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "role": "FINAL_COMPILER"},
                ],
                "gov_sequence": [
                    {"slot": "G1", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
                    {"slot": "G2", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
                ],
                "gov_may_choose_models": False,
            },
            "solo_baseline_rule": {
                "requires_valid_variant_holo_freeze_first": True,
                "must_use_same_three_models_as_variant": [
                    "xai/grok-3-mini",
                    f"openai/{AP.OPENAI_W2_MODEL_ID}",
                    "minimax/MiniMax-M2.5-highspeed",
                ],
                "gov": False,
                "holo_state": False,
                "baton": False,
                "selector": False,
                "judges": False,
            },
            "registration_validation": {
                "providers_called": 0,
                "judges_called": 0,
                "holo_runs_started": 0,
                "solo_runs_started": 0,
            },
        }
        write_json(REGISTRATION_JSON, registration)
        write_text(
            REGISTRATION_MD,
            "\n".join(
                [
                    "# Commerce OpenAI-W2 Roster Variant Registration",
                    "",
                    f"Variant: `{VARIANT_NAME}`",
                    f"Family: `{FAMILY_ID}`",
                    f"Freeze root: `{AP.EXPECTED_FREEZE_ROOT_HASH}`",
                    "",
                    "No providers, Holo, solo, or judges were run while creating this registration.",
                    "",
                ]
            ),
        )
    if not AVAILABILITY_JSON.exists():
        ap_availability_path = AP_ROOT / "AP_OPENAI_W2_MODEL_AVAILABILITY_CHECK_2026_06_29.json"
        ap_availability = json.loads(ap_availability_path.read_text()) if ap_availability_path.exists() else {}
        availability = {
            "classification": "COMMERCE_OPENAI_W2_MODEL_AVAILABILITY_INHERITED_NON_BENCHMARK_CHECK",
            "variant_name": VARIANT_NAME,
            "provider": "openai",
            "exact_model_id_requested": AP.OPENAI_W2_MODEL_ID,
            "model_available": bool(ap_availability.get("model_available") is True),
            "provider_response_status": ap_availability.get("provider_response_status"),
            "source_availability_check": str(ap_availability_path.relative_to(BENCHMARK_ROOT)),
            "boundary_confirmation": {
                "commerce_packet_content_included": False,
                "source_ids_included": False,
                "traps_included": False,
                "answer_keys_included": False,
                "benchmark_prompts_included": False,
                "provider_calls_during_this_file": 0,
                "holo_run_started": False,
                "solo_run_started": False,
                "judge_run_started": False,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json(AVAILABILITY_JSON, availability)
        write_text(
            AVAILABILITY_MD,
            "\n".join(
                [
                    "# Commerce OpenAI-W2 Model Availability Note",
                    "",
                    "This file reuses the prior harmless AP OpenAI-W2 availability check. It does not include Commerce packet content and made no provider calls.",
                    f"Model available: `{availability['model_available']}`",
                    f"Provider status: `{availability['provider_response_status']}`",
                    "",
                ]
            ),
        )


def render_commerce_preflight_md(preflight: dict[str, Any]) -> str:
    lines = [
        "# Commerce OpenAI-W2 Live Holo Preflight",
        "",
        f"Classification: `{preflight['classification']}`",
        f"Variant: `{preflight['variant_name']}`",
        f"Status: `{preflight['status']}`",
        f"Result: `{preflight['result']}`",
        f"Freeze root: `{preflight['freeze_root']}`",
        "",
        "## Roster",
        "",
        "| Slot | Provider | Model | Role |",
        "| --- | --- | --- | --- |",
    ]
    for worker in preflight["model_roster_declared"]["worker_sequence"]:
        lines.append(f"| `W{worker['worker_index']}` | `{worker['provider']}` | `{worker['model']}` | `{worker['role_name']}` |")
    for gov in preflight["model_roster_declared"]["gov_sequence"]:
        lines.append(f"| `{gov['slot']}` | `{gov['provider']}` | `{gov['model']}` | Gov |")
    lines.extend(
        [
            "",
            "## Runtime Binding",
            "",
            f"- Actual W2 provider: `{preflight['runner_binding']['actual_w2_provider']}`",
            f"- Actual W2 model: `{preflight['runner_binding']['actual_w2_model']}`",
            f"- Actual W2 kind: `{preflight['runner_binding']['actual_w2_kind']}`",
            f"- Live Holo started: `{preflight['live_holo_started']}`",
            f"- Solo started: `{preflight['solo_started']}`",
            f"- Judges started: `{preflight['judges_started']}`",
            f"- Providers called during preflight: `{preflight['providers_called']}`",
            "",
            "## Checks",
            "",
            "| Check | Value |",
            "| --- | --- |",
        ]
    )
    for key, value in preflight["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Interpretation", ""])
    if preflight["status"] == "PASS":
        lines.append("`COMMERCE_OPENAI_W2_READY_FOR_FULL_HOLO_RUN`")
        lines.append("")
        lines.append("Stop here. Do not start full Holo until explicitly approved.")
    else:
        lines.append("Preflight failed. Do not run Holo.")
        lines.append("")
        lines.append(f"Blocked reason: `{preflight['blocked_reason']}`")
    return "\n".join(lines) + "\n"


def build_commerce_preflight() -> dict[str, Any]:
    preflight = AP.build_openai_w2_live_holo_preflight()
    preflight["classification"] = "COMMERCE_OPENAI_W2_LIVE_HOLO_PREFLIGHT"
    preflight["result"] = (
        "COMMERCE_OPENAI_W2_READY_FOR_FULL_HOLO_RUN"
        if preflight["status"] == "PASS"
        else "COMMERCE_OPENAI_W2_PREFLIGHT_BLOCKED"
    )
    root_preimage = {k: v for k, v in preflight.items() if k not in {"created_at", "root_signature"}}
    preflight["root_signature"] = AP.sha256_text(AP.canonical_json(root_preimage))
    write_json(AP.OPENAI_W2_PREFLIGHT_JSON, preflight)
    write_text(AP.OPENAI_W2_PREFLIGHT_MD, render_commerce_preflight_md(preflight))
    return preflight


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-openai-w2", action="store_true")
    parser.add_argument("--run-holo-openai-w2", action="store_true")
    parser.add_argument("--finalize-holo", action="store_true")
    parser.add_argument("--holo-run-dir")
    args = parser.parse_args()

    configure_commerce_runtime()
    ensure_registration_files()

    if args.preflight_openai_w2:
        preflight = build_commerce_preflight()
        print(
            json.dumps(
                {
                    "preflight": preflight["status"],
                    "result": preflight["result"],
                    "root_signature": preflight["root_signature"],
                    "json": str(AP.OPENAI_W2_PREFLIGHT_JSON),
                    "md": str(AP.OPENAI_W2_PREFLIGHT_MD),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0 if preflight["status"] == "PASS" else 1
    if args.run_holo_openai_w2:
        return AP.run_openai_w2_holo()
    if args.finalize_holo:
        if not args.holo_run_dir:
            raise SystemExit("--holo-run-dir is required for finalize")
        print(json.dumps(AP.finalize_holo_run(Path(args.holo_run_dir)), indent=2, sort_keys=True))
        return 0
    parser.error("Use --preflight-openai-w2, --run-holo-openai-w2, or --finalize-holo")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
