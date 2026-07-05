#!/usr/bin/env python3
"""Run the approved live HoloBuild creative lane.

This runner intentionally sends the full canonical thread on every turn. It does
not summarize or trim prior state. If a provider rejects the context, the run
blocks rather than compacting.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

PROJECT = Path(__file__).parent
RUN = PROJECT / "runs/live_lane-01_hb_creative_20260626T222600Z"
SCHEMA = json.loads((PROJECT / "05_output_schema.json").read_text())
ASSIGNMENT_ID = SCHEMA["assignment_id"]
PRODUCT = SCHEMA["product"]
WORD_RE = re.compile(r"\b[\w'-]+\b")


ROLE_TASKS = {
    "live_research_and_creative_strategy_builder": (
        "Review the packet and produce a stronger schema-compliant candidate. "
        "Use no new live claim unless source-recorded. Make the "
        "feature-to-wellness lifestyle bridge explicit in every section."
    ),
    "evidence_claim_boundary_attacker": (
        "Pressure-test the prior candidate for unsupported claims, weak wellness "
        "linkage, missing up-to qualifiers, word-count issues, and Meta evidence "
        "laundering. Return an improved candidate JSON with adversarial_notes populated."
    ),
    "meta_ad_builder": (
        "Improve the two Meta ads for channel-native clarity, short hooks, one "
        "concrete product proof per unit, and explicit feature-to-lifestyle payoff. "
        "Preserve claim boundaries."
    ),
    "website_email_builder": (
        "Improve the three website banners as a sequence and improve the short "
        "email body plus P.S. within the exact schema. Do not add preview text or "
        "an email CTA field."
    ),
    "brand_voice_channel_qa_attacker": (
        "Attack brand fit, channel fit, repetition, blandness, claim safety, "
        "explicit lifestyle contribution, and email body word count. Return the "
        "best repaired strict JSON."
    ),
    "convergence_ready_synthesis_author": (
        "Produce a convergence-ready strict JSON candidate. Only preserve strong "
        "evidence-backed improvements and exact word-count compliance."
    ),
    "incremental_improvement_builder": (
        "If meaningful improvement remains, improve the current candidate without "
        "adding unsupported claims. Focus on sharper lifestyle linkage, channel fit, "
        "and copy energy."
    ),
    "regression_and_claim_attacker": (
        "Attack for regressions, stale feature-dump phrasing, claim overreach, weak "
        "new-audience resonance, missing P.S., and email word-count drift. Return "
        "repaired JSON."
    ),
    "final_repair_builder": (
        "Apply only necessary repairs while preserving the strongest accepted copy "
        "and all evidence boundaries. Return strict JSON."
    ),
    "hard_cap_final_synthesis_author": (
        "At the hard cap, produce the best final strict JSON artifact. Do not "
        "continue researching or revising beyond this turn."
    ),
}


def now() -> str:
    return datetime.now(ZoneInfo("America/Los_Angeles")).replace(microsecond=0).isoformat()


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    with path.open("a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical_text() -> str:
    return (RUN / "canonical_thread.jsonl").read_text()


def extract_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\\s*", "", stripped)
        stripped = re.sub(r"\\s*```$", "", stripped).strip()
    try:
        return json.loads(stripped)
    except Exception:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(stripped[start : end + 1])
        except Exception:
            return None
    return None


def validate_artifact(obj: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["output is not an object"]

    def check_shape(template: Any, value: Any, path: str = "") -> None:
        if isinstance(template, dict):
            if not isinstance(value, dict):
                errors.append(f"{path or '$'} is not object")
                return
            if set(value.keys()) != set(template.keys()):
                errors.append(
                    f"{path or '$'} keys mismatch expected={sorted(template.keys())} "
                    f"got={sorted(value.keys())}"
                )
            for key in template:
                if key in value:
                    check_shape(template[key], value[key], f"{path}.{key}" if path else key)
        elif isinstance(template, list):
            if not isinstance(value, list):
                errors.append(f"{path} is not list")
        elif isinstance(template, str):
            if not isinstance(value, str):
                errors.append(f"{path} is not string")
            elif value.strip() == "":
                errors.append(f"{path} is empty")

    check_shape(SCHEMA, obj)
    if obj.get("assignment_id") != ASSIGNMENT_ID:
        errors.append("assignment_id mismatch")
    if obj.get("product") != PRODUCT:
        errors.append("product mismatch")
    email = obj.get("section_3_email", {})
    body = email.get("body", "") if isinstance(email, dict) else ""
    word_count = len(WORD_RE.findall(body))
    if word_count < 100 or word_count > 150:
        errors.append(f"email body word count {word_count} outside 100-150")
    return errors


def call_model(
    provider: str,
    model_id: str,
    system: str,
    user: str,
    max_tokens: int = 4500,
    temperature: float = 0.35,
) -> dict[str, Any]:
    started = time.time()
    if provider == "xai":
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return {
            "text": response.choices[0].message.content,
            "input_tokens": getattr(response.usage, "prompt_tokens", None),
            "output_tokens": getattr(response.usage, "completion_tokens", None),
            "elapsed_ms": int((time.time() - started) * 1000),
        }
    if provider == "anthropic":
        import anthropic

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return {
            "text": response.content[0].text,
            "input_tokens": getattr(response.usage, "input_tokens", None),
            "output_tokens": getattr(response.usage, "output_tokens", None),
            "elapsed_ms": int((time.time() - started) * 1000),
        }
    raise ValueError(f"unsupported provider: {provider}")


def block(status_text: str, reason: Any) -> None:
    status = json.loads((RUN / "RUN_STATUS.json").read_text())
    status.update({"status": status_text, "blocking_reason": reason, "blocked_at": now()})
    (RUN / "RUN_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")


def run() -> None:
    status = json.loads((RUN / "RUN_STATUS.json").read_text())
    if status.get("external_provider_export_approval") != "APPROVED_FOR_HB_ONLY":
        raise SystemExit("external provider export is not approved")
    if status.get("model_preflight") != "PASS":
        raise SystemExit("model preflight is not PASS")
    if status.get("solo_opus_status") != "NOT_RUN_PER_USER_INSTRUCTION":
        raise SystemExit("solo opus boundary missing")
    last_completed_turn = int(status.get("last_completed_turn", 0) or 0)
    status.pop("blocked_at", None)
    status.pop("blocking_reason", None)
    status.update({"status": "RUNNING_LIVE_HB", "run_started_at": now()})
    (RUN / "RUN_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")

    manifest = json.loads((RUN / "model_rotation_v3.json").read_text())
    system_active = (
        "You are a HoloBuild creative builder/attacker operating under a lossless "
        "canonical-thread architecture. Return ONLY valid JSON matching "
        "05_output_schema.json. No markdown, no commentary, no source appendix."
    )
    system_gov = (
        "You are HoloGov for this HoloBuild run. You are Grok 4.3 and remain "
        "constant across every session. Return ONLY valid JSON."
    )

    for item in manifest["turn_rotation"]:
        turn = item["turn"]
        if turn <= last_completed_turn:
            continue
        role = item["role"]
        provider = item["provider"]
        model_id = item["model_id"]
        print(f"TURN {turn} active={item['model_label']} role={role}", flush=True)

        user = (
            "CANONICAL THREAD (verbatim JSONL; do not summarize or ignore):\n"
            f"{canonical_text()}\n\n"
            f"CURRENT TURN: {turn}\nROLE: {role}\nTASK: {ROLE_TASKS[role]}\n\n"
            "Return strict JSON only matching 05_output_schema.json. Keep "
            "assignment_id and product exactly. Populate adversarial_notes arrays. "
            "Email body must be 100-150 words excluding subjects and P.S. No medical, "
            "disease, weight-loss, guilt-free, or guaranteed-health claims. Preserve "
            "“up to” on 46% faster and 95% less oil. If Meta Ads Library examples are "
            "missing, record that in missing_evidence rather than claiming observed "
            "Meta conventions."
        )
        turn_input = {
            "event_type": "turn_input",
            "lane_id": "lane-01",
            "turn": turn,
            "input_revision": "execution",
            "role": role,
            "provider": provider,
            "model_id": model_id,
            "created_at": now(),
            "canonical_thread_policy": "lossless full canonical_thread.jsonl injected",
            "research_record_policy": "raw research not injected; only source-record pointers in canonical thread",
            "prompt_chars": len(user),
            "user_task": ROLE_TASKS[role],
        }
        append_jsonl(RUN / "turn_inputs.jsonl", turn_input)
        append_jsonl(
            RUN / "canonical_thread.jsonl",
            {
                "event_type": "canonical_thread_entry",
                "lane_id": "lane-01",
                "turn": turn,
                "role": "governor",
                "created_at": now(),
                "content_type": "turn_input_execution_locked",
                "content": turn_input,
            },
        )

        try:
            response = call_model(provider, model_id, system_active, user, max_tokens=5000)
            raw = response["text"]
            parsed = extract_json(raw)
            errors = validate_artifact(parsed) if parsed is not None else ["could not parse JSON object"]
            if errors:
                repair_prompt = (
                    f"Your previous output failed validation: {json.dumps(errors)}\n\n"
                    f"RAW OUTPUT:\n{raw}\n\n"
                    f"CANONICAL THREAD:\n{canonical_text()}\n\n"
                    "Return ONLY corrected strict JSON matching 05_output_schema.json."
                )
                repair = call_model(provider, model_id, system_active, repair_prompt, max_tokens=5000, temperature=0.15)
                repair_raw = repair["text"]
                repair_parsed = extract_json(repair_raw)
                repair_errors = (
                    validate_artifact(repair_parsed)
                    if repair_parsed is not None
                    else ["could not parse repair JSON object"]
                )
                active_output = {
                    "event_type": "turn_output",
                    "lane_id": "lane-01",
                    "turn": turn,
                    "role": role,
                    "provider": provider,
                    "model_id": model_id,
                    "created_at": now(),
                    "status": "PASS" if not repair_errors else "VALIDATION_FAILED",
                    "raw_output": raw,
                    "validation_errors": errors,
                    "repair_used": True,
                    "repair_raw_output": repair_raw,
                    "repair_validation_errors": repair_errors,
                    "artifact": repair_parsed if not repair_errors else parsed,
                    "usage": {
                        "initial": {k: response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                        "repair": {k: repair.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                    },
                }
            else:
                active_output = {
                    "event_type": "turn_output",
                    "lane_id": "lane-01",
                    "turn": turn,
                    "role": role,
                    "provider": provider,
                    "model_id": model_id,
                    "created_at": now(),
                    "status": "PASS",
                    "raw_output": raw,
                    "validation_errors": [],
                    "repair_used": False,
                    "artifact": parsed,
                    "usage": {k: response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                }
        except Exception as exc:
            active_output = {
                "event_type": "turn_output",
                "lane_id": "lane-01",
                "turn": turn,
                "role": role,
                "provider": provider,
                "model_id": model_id,
                "created_at": now(),
                "status": "PROVIDER_CALL_FAILED",
                "error_type": type(exc).__name__,
                "error": str(exc)[:1200],
            }

        append_jsonl(RUN / "turn_outputs.jsonl", active_output)
        append_jsonl(
            RUN / "canonical_thread.jsonl",
            {
                "event_type": "canonical_thread_entry",
                "lane_id": "lane-01",
                "turn": turn,
                "role": role,
                "created_at": now(),
                "content_type": "active_model_output",
                "content": active_output,
            },
        )
        if active_output["status"] != "PASS":
            block(f"BLOCKED_TURN_{turn}_{active_output['status']}", active_output.get("error") or active_output.get("validation_errors"))
            print(f"BLOCKED turn {turn}: {active_output['status']}", flush=True)
            return

        gov_user = (
            f"CANONICAL THREAD (verbatim JSONL):\n{canonical_text()}\n\n"
            f"Assess turn {turn}. Return JSON with keys: status, defects, "
            "continue_required, convergence_certified, brief_for_next_turn. "
            "Convergence can be certified only if no meaningful improvement remains. "
            "Preserve missing evidence and claim boundaries."
        )
        try:
            gov_response = call_model("xai", "grok-4.3", system_gov, gov_user, max_tokens=1800, temperature=0.2)
            gov_parsed = extract_json(gov_response["text"]) or {
                "status": "GOV_PARSE_FAILED",
                "raw": gov_response["text"][:1200],
            }
            gov_brief = {
                "event_type": "governor_brief",
                "lane_id": "lane-01",
                "turn": turn,
                "created_at": now(),
                "status": gov_parsed.get("status", "GOV_REVIEWED") if isinstance(gov_parsed, dict) else "GOV_REVIEWED",
                "provider": "xai",
                "model_id": "grok-4.3",
                "parsed": gov_parsed,
                "usage": {k: gov_response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
            }
        except Exception as exc:
            gov_brief = {
                "event_type": "governor_brief",
                "lane_id": "lane-01",
                "turn": turn,
                "created_at": now(),
                "status": "GOVERNOR_CALL_FAILED",
                "provider": "xai",
                "model_id": "grok-4.3",
                "error_type": type(exc).__name__,
                "error": str(exc)[:1200],
            }
        append_jsonl(RUN / "governor_briefs.jsonl", gov_brief)
        append_jsonl(
            RUN / "canonical_thread.jsonl",
            {
                "event_type": "canonical_thread_entry",
                "lane_id": "lane-01",
                "turn": turn,
                "role": "hologov",
                "created_at": now(),
                "content_type": "hologov_brief",
                "content": gov_brief,
            },
        )
        if gov_brief["status"] == "GOVERNOR_CALL_FAILED":
            block(f"BLOCKED_TURN_{turn}_GOVERNOR_CALL_FAILED", gov_brief.get("error"))
            print(f"BLOCKED governor turn {turn}", flush=True)
            return

        status = json.loads((RUN / "RUN_STATUS.json").read_text())
        status.update({"status": f"TURN_{turn}_COMPLETE", "last_completed_turn": turn})
        (RUN / "RUN_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")
        print(f"TURN {turn} complete", flush=True)

    outputs = read_jsonl(RUN / "turn_outputs.jsonl")
    last_pass = next(
        (out for out in reversed(outputs) if out.get("status") == "PASS" and isinstance(out.get("artifact"), dict)),
        None,
    )
    if last_pass:
        (RUN / "final_candidate_artifact.json").write_text(
            json.dumps(last_pass["artifact"], indent=2, ensure_ascii=False) + "\n"
        )
        status = json.loads((RUN / "RUN_STATUS.json").read_text())
        status.update(
            {
                "status": "COMPLETE_HARD_CAP_10_TURNS",
                "final_candidate_artifact": "final_candidate_artifact.json",
                "completed_at": now(),
            }
        )
        (RUN / "RUN_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")
        append_jsonl(
            RUN / "canonical_thread.jsonl",
            {
                "event_type": "canonical_thread_entry",
                "lane_id": "lane-01",
                "turn": 10,
                "role": "governor",
                "created_at": now(),
                "content_type": "final_candidate_artifact_written",
                "content": {"path": "final_candidate_artifact.json"},
            },
        )
        print("RUN COMPLETE", flush=True)


if __name__ == "__main__":
    run()
