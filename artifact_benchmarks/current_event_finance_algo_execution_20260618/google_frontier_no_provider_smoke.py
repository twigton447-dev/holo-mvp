from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKET_DIR = Path(__file__).resolve().parent
SOLO_SWEEP = PACKET_DIR / "solo_model_sweep.json"

SOLO_CONDITIONS = {
    "solo_openai": "openai:gpt-5.5",
    "solo_anthropic": "anthropic:claude-opus-4-8",
    "solo_google": "google:gemini-3.1-pro-preview",
}
STATE_OBJECT_VERSION = "patent_grade_holo_state_v1"
HC_STATE_AUTHORITY_RULE = (
    "Only HC may mutate benchmark architecture/state. HoloAgents may write artifacts; "
    "Gov may baton, gate, and summarize; durable architecture updates enter through "
    "HC via ROLLING_SUMMARY."
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(read_text(path))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return sha_text(read_text(path))


def turn_prompt_parity_contract(role_flow: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "turn": int(item["turn"]),
            "role": item["role"],
            "turn_instruction_sha256": sha_text(item["instruction"]),
            "same_base_turn_prompt_for_solo_and_holo": True,
            "holo_extra_context": "Gov Baton Pass plus STATE_OBJECT plus pinned artifacts.",
        }
        for item in role_flow["turns"]
    ]


def load_routing_config(routing_config_id: str | None) -> dict[str, Any]:
    suite = read_json(PACKET_DIR / "holo_routing_configs.json")
    selected = routing_config_id or suite["default_routing_config_id"]
    for config in suite["routing_configs"]:
        if config["routing_config_id"] == selected:
            return config
    valid = ", ".join(config["routing_config_id"] for config in suite["routing_configs"])
    raise RuntimeError(f"unknown_routing_config:{selected}; valid={valid}")


def load_solo_conditions(solo_suite_id: str | None) -> tuple[str, dict[str, str]]:
    suites = read_json(SOLO_SWEEP)
    selected = solo_suite_id or suites["default_solo_suite_id"]
    suite = suites.get("solo_suites", {}).get(selected)
    if not suite:
        valid = ", ".join(sorted(suites.get("solo_suites", {})))
        raise RuntimeError(f"unknown_solo_suite:{selected}; valid={valid}")
    return selected, dict(suite["conditions"])


def apply_holo_routing_config(role_flow: dict[str, Any], routing_config: dict[str, Any]) -> dict[str, Any]:
    turns = role_flow["turns"]
    rotation = routing_config["analyst_rotation"]
    if len(rotation) != len(turns):
        raise RuntimeError("routing_config_must_have_one_model_per_turn")
    routed = json.loads(json.dumps(role_flow))
    for idx, provider_model in enumerate(rotation):
        routed["turns"][idx]["provider_model"] = provider_model
    routed["routing_config_id"] = routing_config["routing_config_id"]
    routed["routing_config_label"] = routing_config.get("label")
    return routed


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def source_label(source: dict[str, Any]) -> str:
    sid = source["id"].split("_", 1)[0]
    return f"[{sid}]"


def clean_ending(text: str) -> bool:
    stripped = text.strip()
    return bool(stripped) and stripped[-1] in ".!?)]`\"'"


def source_ids_in_text(text: str) -> list[str]:
    return sorted(set(re.findall(r"\[S\d+(?:_[A-Z0-9_]+)?\]", text)))


def allowed_source_ids(source_entries: list[dict[str, Any]]) -> set[str]:
    ids = set()
    for entry in source_entries:
        full_id = entry["id"]
        ids.add(f"[{full_id}]")
        ids.add(f"[{full_id.split('_', 1)[0]}]")
    return ids


def has_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def final_artifact_validity_report(
    text: str,
    *,
    source_entries: list[dict[str, Any]],
    min_words: int,
    max_words: int,
) -> dict[str, Any]:
    wc = word_count(text)
    lowered = text.lower()
    flags: list[str] = []
    if not (min_words <= wc <= max_words):
        flags.append(f"final_word_count_out_of_band:{wc}")
    if not clean_ending(text):
        flags.append("final_does_not_end_cleanly")
    tail = text.strip()[-260:].lower()
    if re.search(r"(\n|^)\s*[-*]\s+\S.{0,120}$", text.strip()) and not clean_ending(text):
        flags.append("final_appears_cut_off_mid_bullet")
    if tail.count("(") > tail.count(")") or tail.count("[") > tail.count("]"):
        flags.append("final_tail_has_unbalanced_bracket_or_parenthesis")

    required_topics = {
        "disclaimer_no_investment_advice": ["not investment advice", "not legal", "not a recommendation"],
        "disclaimer_no_live_execution": [
            "does not execute",
            "not a live execution",
            "does not route orders",
            "no live execution",
            "not a live trading",
            "not connected to live brokerage",
            "not an order-routing system",
        ],
        "executive_thesis": ["executive thesis", "thesis"],
        "current_market_setup": ["current market", "market setup", "market regime"],
        "execution_architecture": ["architecture", "execution governor", "control plane"],
        "benchmark_framework": ["implementation shortfall", "arrival price", "benchmark"],
        "portfolio_funding_settlement": ["portfolio", "funding", "settlement"],
        "regulatory_controls_audit": ["controls", "audit", "kill switch", "kill-switch"],
        "model_risk_adversarial": ["model risk", "adversarial", "bias"],
        "implementation_roadmap": ["roadmap", "phase", "implementation"],
        "success_metrics": ["success metrics", "metrics", "kpis", "measurement"],
    }
    for topic, needles in required_topics.items():
        if not has_any(lowered, needles):
            flags.append(f"missing_required_topic:{topic}")

    residue_terms = [
        "state_object",
        "mission packet",
        "baton pass",
        "benchmark_credit",
        "document x",
        "document y",
        "turn_5",
        "turn_6",
        "hologov",
        "holoagent",
    ]
    residue = [term for term in residue_terms if term in lowered]
    if residue:
        flags.append("internal_process_residue:" + ",".join(residue))

    sources = source_ids_in_text(text)
    unknown_source_ids = sorted(set(sources) - allowed_source_ids(source_entries))
    if unknown_source_ids:
        flags.append("unknown_source_ids:" + ",".join(unknown_source_ids))
    if not sources:
        flags.append("missing_source_ids")

    return {
        "valid": not flags,
        "flags": flags,
        "word_count": wc,
        "word_count_in_band": min_words <= wc <= max_words,
        "clean_ending": clean_ending(text),
        "source_ids": sources,
    }


def synthetic_final_doc(
    *,
    title: str,
    condition: str,
    model: str,
    source_entries: list[dict[str, Any]],
    min_words: int,
    target_words: int,
) -> str:
    source_refs = " ".join(source_label(entry) for entry in source_entries[:8])
    header = f"""# {title}

Diagnostic no-provider smoke artifact.

Condition: `{condition}`
Model: `{model}`
Benchmark credit: `false`
Provider calls: `0`
Source refs exercised: {source_refs}

This placeholder exists only to test filesystem layout, trace hashing, final-document word-count gates, deterministic validity gates, and no-browse packet plumbing. It is not a finance report, not a benchmark result, not investment advice, not legal advice, not a recommendation, and not a live execution or order-routing system.

## Executive Thesis
The diagnostic thesis is that an execution governor can organize current market setup, execution architecture, benchmark framework, portfolio funding settlement, regulatory controls audit, model risk adversarial review, implementation roadmap, and success metrics into one complete artifact for gate testing. {source_refs}

## Current Market Setup
The fixture names the market regime, current market context, and market setup so the gate can confirm that source-grounded current-event analysis would be required in a real run.

## Execution Architecture
The fixture names architecture, execution governor, and control plane concepts without claiming deployment capability.

## Benchmark Framework
The fixture names implementation shortfall, arrival price, VWAP, peer benchmark, venue benchmark, and benchmark conflict logic.

## Portfolio Funding Settlement
The fixture names portfolio weights, active risk, funding, settlement, repo, collateral, and cash constraints.

## Regulatory Controls Audit
The fixture names controls, audit, kill switch, pre-trade limits, logs, escalation, and compliance evidence.

## Model Risk Adversarial Review
The fixture names model risk, adversarial pressure, bias, unsupported claims, and disagreement handling.

## Implementation Roadmap
The fixture names roadmap, phase gates, implementation sequencing, validation, and production monitoring.

## Success Metrics
The fixture names success metrics, KPIs, measurement, completion, and client-readiness.

"""
    sentence = (
        "Smoke fixture verifies source grounding order flow benchmark portfolio risk "
        "funding settlement clearing controls audit model bias and client usefulness. "
    )
    body = []
    while word_count(header + "\n".join(body)) < target_words:
        body.append(sentence)
    text = header + "\n".join(body)
    if word_count(text) < min_words:
        raise RuntimeError("synthetic_final_doc_word_count_under_min")
    return text


def synthetic_turn_doc(
    *,
    title: str,
    condition: str,
    model: str,
    turn: int,
    role: str,
    source_entries: list[dict[str, Any]],
) -> str:
    refs = " ".join(source_label(entry) for entry in source_entries[:4])
    return f"""# {title} Turn {turn} Diagnostic Artifact

Condition: `{condition}`
Model: `{model}`
Role: `{role}`
Provider calls: `0`
Benchmark credit: `false`
Source refs exercised: {refs}

This no-provider artifact is a smoke-test placeholder. It confirms that the harness can persist turn artifacts, bind them to model order, include frozen source-pack hashes, and carry previous-turn state without treating this output as benchmark evidence.
"""


def mission_packet(
    *,
    turn: int,
    role_item: dict[str, Any],
    gov_protocol: dict[str, Any],
    source_entries: list[dict[str, Any]],
    previous_artifacts: list[dict[str, Any]],
) -> str:
    required = gov_protocol["mission_packet_required_fields"]
    probes = gov_protocol["standing_probe_bank"]
    probe_lines = []
    for category, questions in probes.items():
        if questions:
            probe_lines.append(f"- {category}: {questions[0]}")
    anchors = ", ".join(entry["id"] for entry in source_entries[:5])
    previous = ", ".join(f"turn_{item['turn']}" for item in previous_artifacts) or "none"
    return f"""# HoloGov Mission Packet - Turn {turn}

## Current Best State
Diagnostic placeholder state from previous artifacts: {previous}.

## New Learnings From Prior Turns
This no-provider smoke confirms the Gov packet can summarize accumulated turn state without model calls.

## Highest Value Flaw
Force the next model to resolve technical execution assumptions rather than rewriting generically.

## Source Context Anchors
{anchors}

## Technical Probe Questions
{chr(10).join(probe_lines)}

## Order Flow And Microstructure Checks
Probe venue routing, queue fade, adverse selection, odd-lot depth, and fee/rebate economics.

## Benchmark And Peer Comparison Checks
Probe VWAP versus implementation shortfall, arrival price, peer-relative crowding, and benchmark gaming.

## Portfolio Weight And Risk Checks
Probe active risk, target-weight drift, liquidity budget, cash drag, and exposure tradeoffs.

## Funding Settlement And Clearing Checks
Probe T+1, Treasury clearing, repo margin, collateral mobility, and funding throttles.

## Regulatory Control And Audit Checks
Probe pre-trade controls, price collars, participation limits, kill switches, logs, and human escalation.

## Model Risk And Bias Checks
Probe recency bias, extrapolation, unsupported market claims, and disagreement handling.

## Next Role Objective
{role_item['instruction']}

## Constraints And Do Not Do
Do not browse. Do not invent facts outside the frozen source pack. Do not claim live trading capability.

## Open Tensions
Can the next artifact become technically sharper without losing client readability?

## Convergence Target
Create a stronger final report candidate while preserving source grounding, technical specificity, and the word-count band.

## Required Field Coverage
{", ".join(required)}
"""


def trace_payload(
    *,
    call_type: str,
    condition: str,
    turn: int,
    provider_model: str,
    role: str,
    prompt_text: str,
    output_text: str,
    output_path: Path,
    hashes: dict[str, str],
    previous_turns: list[int],
) -> dict[str, Any]:
    return {
        "call_type": call_type,
        "condition": condition,
        "turn": turn,
        "provider_model": provider_model,
        "role": role,
        "provider_call_made": False,
        "benchmark_credit": False,
        "public_claim": False,
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": 0,
        "system_sha256": sha_text("NO_PROVIDER_SMOKE_SYSTEM"),
        "user_sha256": sha_text(prompt_text),
        "output_sha256": sha_text(output_text),
        "artifact_path": str(output_path),
        "previous_turns_included": previous_turns,
        "source_pack_sha256": hashes["source_pack"],
        "report_brief_sha256": hashes["report_brief"],
        "role_flow_sha256": hashes["role_flow"],
        "gov_protocol_sha256": hashes["gov_protocol"],
        "word_count": word_count(output_text),
    }


def build_turn_judge_packets(
    *,
    root: Path,
    run_id: str,
    role_flow: dict[str, Any],
    solo_conditions: dict[str, str],
    source_pack: dict[str, Any],
    report_brief: dict[str, Any],
    rubric: dict[str, Any],
) -> list[str]:
    packet_ids: list[str] = []
    anonymization = {"run_id": run_id, "pairs": []}
    for solo_condition in solo_conditions:
        for role_item in role_flow["turns"]:
            turn = int(role_item["turn"])
            solo_path = root / "artifacts" / solo_condition / f"turn_{turn}.md"
            holo_path = root / "artifacts" / "holo_frontier_gov" / f"turn_{turn}.md"
            if not solo_path.exists() or not holo_path.exists():
                continue
            pair_id = f"{run_id}_{solo_condition}_vs_holo_turn_{turn}_pair"
            flip = int(hashlib.sha256(pair_id.encode("utf-8")).hexdigest()[:2], 16) % 2 == 0
            if flip:
                doc_x, doc_y = read_text(holo_path), read_text(solo_path)
                x_condition, y_condition = "holo_frontier_gov", solo_condition
            else:
                doc_x, doc_y = read_text(solo_path), read_text(holo_path)
                x_condition, y_condition = solo_condition, "holo_frontier_gov"
            packet = {
                "judge_packet_id": pair_id,
                "packet_type": "turn_level_diagnostic",
                "blind": True,
                "benchmark_credit": False,
                "public_claim": False,
                "domain": report_brief["domain"],
                "turn": turn,
                "turn_role": role_item["role"],
                "turn_instruction": role_item["instruction"],
                "turn_scoring_note": (
                    "Score each document for this turn's assigned role and its contribution "
                    "to the artifact trajectory. Do not score early critique/repair turns as "
                    "if they must be final board-ready reports."
                ),
                "brief": report_brief,
                "source_pack": source_pack,
                "rubric": rubric,
                "documents": {
                    "document_x": {"anonymous_id": "Document X", "text": doc_x},
                    "document_y": {"anonymous_id": "Document Y", "text": doc_y},
                },
            }
            write_json(root / "turn_judge_packets" / f"{pair_id}.json", packet)
            anonymization["pairs"].append(
                {
                    "judge_packet_id": pair_id,
                    "turn": turn,
                    "document_x_condition": x_condition,
                    "document_y_condition": y_condition,
                }
            )
            packet_ids.append(pair_id)
    write_json(root / "sealed" / "turn_anonymization_map.json", anonymization)
    return packet_ids


def word_gate(text: str, min_words: int, max_words: int) -> dict[str, Any]:
    count = word_count(text)
    return {
        "word_count": count,
        "min_words": min_words,
        "max_words": max_words,
        "passes": min_words <= count <= max_words,
    }


def smoke_state_object(
    *,
    report_brief: dict[str, Any],
    routing_config: dict[str, Any],
    role_item: dict[str, Any],
    turn: int,
    previous_holo: list[dict[str, Any]],
) -> dict[str, Any]:
    req = report_brief["deliverable_requirements"]
    return {
        "state_object_version": STATE_OBJECT_VERSION,
        "USER_GOAL": report_brief["task"],
        "LATEST_INPUT_SUMMARY": f"Prepare Turn {turn} for {role_item['role']}.",
        "CRITICAL_CONSTRAINTS": [
            *req["must_not_include"],
            f"Target final length: {req['target_length_words'][0]}-{req['target_length_words'][1]} words.",
            "No browsing during generation or judging.",
            HC_STATE_AUTHORITY_RULE,
        ],
        "ROLLING_SUMMARY": [
            {"turn": item["turn"], "artifact_sha256": item["sha256"]} for item in previous_holo
        ],
        "HC_STATE_AUTHORITY": {
            "architecture_mutation_surface": "HC",
            "mutable_state_surface": "ROLLING_SUMMARY",
            "rule": HC_STATE_AUTHORITY_RULE,
        },
        "SETTLED_DECISIONS": [
            "Fixed Gov for the session.",
            f"Routing config: {routing_config['routing_config_id']}.",
        ],
        "ARTIFACTS_REGISTRY": [
            {
                "artifact_id": f"turn_{item['turn']}_draft_v1",
                "status": "PINNED",
                "turn": item["turn"],
                "sha256": item["sha256"],
                "pointer": item["path"],
            }
            for item in previous_holo
        ],
        "REQUIRED_TOOLS": "NONE",
        "BATON_PASS": {
            "next_turn": turn,
            "next_model_instance": role_item["provider_model"],
            "adversarial_cognitive_role": role_item["role"],
            "role_instruction": role_item["instruction"],
        },
        "PRESERVED_INSIGHT_LEDGER": [],
        "REPAIR_LEDGER": {"open_issue": [], "repaired": [], "regressed": [], "still_missing": []},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--routing-config", default=None)
    parser.add_argument("--solo-suite", default=None)
    args = parser.parse_args()

    source_pack = read_json(PACKET_DIR / "source_pack.json")
    report_brief = read_json(PACKET_DIR / "report_brief.json")
    gov_protocol = read_json(PACKET_DIR / "gov_technical_probe_protocol.json")
    base_role_flow = read_json(PACKET_DIR / "finance_algo_adversarial_role_flow.json")
    routing_config = load_routing_config(args.routing_config)
    role_flow = apply_holo_routing_config(base_role_flow, routing_config)
    solo_suite_id, solo_conditions = load_solo_conditions(args.solo_suite)
    run_prompt = read_text(PACKET_DIR / "holo_frontier_run_prompt.md")
    judge_brief = read_text(PACKET_DIR / "judge_brief.md")
    rubric = read_json(PACKET_DIR / "judge_rubric_8criteria.json")

    source_entries = source_pack["source_entries"]
    min_words, max_words = report_brief["deliverable_requirements"]["target_length_words"]
    target_words = 2900
    turns = role_flow["turns"]
    run_id = (
        f"no_provider_smoke_finance_algo_execution_"
        f"{routing_config['routing_config_id']}_{solo_suite_id}_{utc_stamp()}"
    )
    root = PACKET_DIR / "runs" / run_id

    hashes = {
        "source_pack": sha_file(PACKET_DIR / "source_pack.json"),
        "report_brief": sha_file(PACKET_DIR / "report_brief.json"),
        "role_flow": sha_file(PACKET_DIR / "finance_algo_adversarial_role_flow.json"),
        "routing_configs": sha_file(PACKET_DIR / "holo_routing_configs.json"),
        "gov_protocol": sha_file(PACKET_DIR / "gov_technical_probe_protocol.json"),
        "run_prompt": sha_text(run_prompt),
        "judge_brief": sha_text(judge_brief),
    }

    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any = "") -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    check("provider_calls_disabled", True)
    check("benchmark_credit_false", True)
    check("source_pack_entries", len(source_entries) == 11, len(source_entries))
    check("no_browse_policy", "browse" in source_pack["model_internet_policy"].lower())
    check("word_band", [min_words, max_words] == [2800, 3400], [min_words, max_words])
    check("six_turn_role_flow", len(turns) == 6, len(turns))
    parity_contract = turn_prompt_parity_contract(role_flow)
    check(
        "same_base_turn_prompts_for_solo_and_holo",
        len(parity_contract) == 6
        and all(item["same_base_turn_prompt_for_solo_and_holo"] for item in parity_contract),
        parity_contract,
    )

    all_traces: list[dict[str, Any]] = []
    final_candidates: dict[str, dict[str, Any]] = {}

    for condition, provider_model in solo_conditions.items():
        previous: list[dict[str, Any]] = []
        for turn in range(1, 7):
            role = f"Solo Recursive Builder Turn {turn}"
            if turn == 6:
                text = synthetic_final_doc(
                    title="The Execution Governor: Solo Diagnostic Final",
                    condition=condition,
                    model=provider_model,
                    source_entries=source_entries,
                    min_words=min_words,
                    target_words=target_words,
                )
            else:
                text = synthetic_turn_doc(
                    title="Solo",
                    condition=condition,
                    model=provider_model,
                    turn=turn,
                    role=role,
                    source_entries=source_entries,
                )
            path = root / "artifacts" / condition / f"turn_{turn}.md"
            write_text(path, text)
            prompt = json.dumps(
                {
                    "packet": "diagnostic_no_provider",
                    "condition": condition,
                    "turn": turn,
                    "source_pack_hash": hashes["source_pack"],
                    "brief_hash": hashes["report_brief"],
                    "previous_turns": [item["turn"] for item in previous],
                },
                sort_keys=True,
            )
            trace = trace_payload(
                call_type="solo_turn_no_provider_smoke",
                condition=condition,
                turn=turn,
                provider_model=provider_model,
                role=role,
                prompt_text=prompt,
                output_text=text,
                output_path=path,
                hashes=hashes,
                previous_turns=[item["turn"] for item in previous],
            )
            write_json(root / "traces" / condition / f"turn_{turn}.json", trace)
            all_traces.append(trace)
            previous.append({"turn": turn, "path": str(path), "sha256": trace["output_sha256"]})
        final_candidates[condition] = {
            "artifact_path": str(root / "artifacts" / condition / "turn_6.md"),
            "gate": word_gate(read_text(root / "artifacts" / condition / "turn_6.md"), min_words, max_words),
            "artifact_validity_report": final_artifact_validity_report(
                read_text(root / "artifacts" / condition / "turn_6.md"),
                source_entries=source_entries,
                min_words=min_words,
                max_words=max_words,
            ),
        }

    previous_holo: list[dict[str, Any]] = []
    for role_item in turns:
        turn = int(role_item["turn"])
        condition = "holo_frontier_gov"
        provider_model = role_item["provider_model"]
        state_object = smoke_state_object(
            report_brief=report_brief,
            routing_config=routing_config,
            role_item=role_item,
            turn=turn,
            previous_holo=previous_holo,
        )
        state_path = root / "state_objects" / condition / f"turn_{turn}_state_object.json"
        write_json(state_path, state_object)
        mission_text = ""
        mission_path = None
        if turn > 1:
            mission_text = mission_packet(
                turn=turn,
                role_item=role_item,
                gov_protocol=gov_protocol,
                source_entries=source_entries,
                previous_artifacts=previous_holo,
            )
            mission_path = root / "mission_packets" / condition / f"turn_{turn}_mission.md"
            write_text(mission_path, mission_text)
            gov_trace = trace_payload(
                call_type="gov_mission_packet_no_provider_smoke",
                condition=condition,
                turn=turn,
                provider_model="hologov:deterministic_no_provider",
                role="HoloGov Technical Probe Mission Builder",
                prompt_text=json.dumps(
                    {
                        "turn": turn,
                        "role": role_item,
                        "state_object_sha256": sha_file(state_path),
                        "previous_turns": [item["turn"] for item in previous_holo],
                        "gov_protocol_hash": hashes["gov_protocol"],
                    },
                    sort_keys=True,
                ),
                output_text=mission_text,
                output_path=mission_path,
                hashes=hashes,
                previous_turns=[item["turn"] for item in previous_holo],
            )
            write_json(root / "traces" / condition / f"gov_turn_{turn}.json", gov_trace)
            all_traces.append(gov_trace)

        if turn in (5, 6):
            text = synthetic_final_doc(
                title="The Execution Governor: Holo Diagnostic Final",
                condition=condition,
                model=provider_model,
                source_entries=source_entries,
                min_words=min_words,
                target_words=target_words + (20 if turn == 6 else 0),
            )
        else:
            text = synthetic_turn_doc(
                title="Holo",
                condition=condition,
                model=provider_model,
                turn=turn,
                role=role_item["role"],
                source_entries=source_entries,
            )
        path = root / "artifacts" / condition / f"turn_{turn}.md"
        write_text(path, text)
        prompt = json.dumps(
            {
                "packet": "diagnostic_no_provider",
                "condition": condition,
                "turn": turn,
                "role": role_item,
                "mission_sha256": sha_text(mission_text) if mission_text else None,
                "state_object_sha256": sha_file(state_path),
                "source_pack_hash": hashes["source_pack"],
                "brief_hash": hashes["report_brief"],
                "previous_turns": [item["turn"] for item in previous_holo],
            },
            sort_keys=True,
        )
        trace = trace_payload(
            call_type="holo_analyst_turn_no_provider_smoke",
            condition=condition,
            turn=turn,
            provider_model=provider_model,
            role=role_item["role"],
            prompt_text=prompt,
            output_text=text,
            output_path=path,
            hashes=hashes,
            previous_turns=[item["turn"] for item in previous_holo],
        )
        if mission_path:
            trace["mission_path"] = str(mission_path)
        write_json(root / "traces" / condition / f"turn_{turn}.json", trace)
        all_traces.append(trace)
        previous_holo.append({"turn": turn, "path": str(path), "sha256": trace["output_sha256"]})

    turn5_text = read_text(root / "artifacts" / "holo_frontier_gov" / "turn_5.md")
    turn6_text = read_text(root / "artifacts" / "holo_frontier_gov" / "turn_6.md")
    final_selection = {
        "selection_type": "diagnostic_no_provider_final_gate",
        "benchmark_credit": False,
        "provider_calls": 0,
        "gate_instruction": role_flow["post_turn_6_governor_gate"],
        "candidate_turn_5": {
            "artifact_path": str(root / "artifacts" / "holo_frontier_gov" / "turn_5.md"),
            "sha256": sha_text(turn5_text),
            "word_gate": word_gate(turn5_text, min_words, max_words),
        },
        "candidate_turn_6": {
            "artifact_path": str(root / "artifacts" / "holo_frontier_gov" / "turn_6.md"),
            "sha256": sha_text(turn6_text),
            "word_gate": word_gate(turn6_text, min_words, max_words),
        },
        "selected": "turn_6",
        "selection_reason": (
            "Diagnostic fixture selected Turn 6 because it preserves the required word band "
            "and exercises the no-degradation guard. This is not a quality judgment."
        ),
    }
    write_json(root / "final_selection" / "holo_frontier_gov_final_selection.json", final_selection)
    final_candidates["holo_frontier_gov"] = {
        "artifact_path": str(root / "artifacts" / "holo_frontier_gov" / "turn_6.md"),
        "gate": final_selection["candidate_turn_6"]["word_gate"],
        "artifact_validity_report": final_artifact_validity_report(
            read_text(root / "artifacts" / "holo_frontier_gov" / "turn_6.md"),
            source_entries=source_entries,
            min_words=min_words,
            max_words=max_words,
        ),
    }

    below = "too short"
    within = synthetic_final_doc(
        title="Word Gate Within Fixture",
        condition="word_gate",
        model="deterministic",
        source_entries=source_entries,
        min_words=min_words,
        target_words=target_words,
    )
    above = within + (" overflow" * 700)
    word_gate_tests = {
        "below_min_should_fail": word_gate(below, min_words, max_words),
        "within_band_should_pass": word_gate(within, min_words, max_words),
        "above_max_should_fail": word_gate(above, min_words, max_words),
    }
    validity_gate_tests = {
        "within_complete_should_pass": final_artifact_validity_report(
            within,
            source_entries=source_entries,
            min_words=min_words,
            max_words=max_words,
        ),
        "truncated_mid_bullet_should_fail": final_artifact_validity_report(
            within + "\n- No rout",
            source_entries=source_entries,
            min_words=min_words,
            max_words=max_words,
        ),
        "missing_source_ids_should_fail": final_artifact_validity_report(
            re.sub(r"\[S\d+(?:_[A-Z0-9_]+)?\]", "", within),
            source_entries=source_entries,
            min_words=min_words,
            max_words=max_words,
        ),
    }
    check("word_gate_below_min_fails", word_gate_tests["below_min_should_fail"]["passes"] is False)
    check("word_gate_within_band_passes", word_gate_tests["within_band_should_pass"]["passes"] is True)
    check("word_gate_above_max_fails", word_gate_tests["above_max_should_fail"]["passes"] is False)
    check("validity_gate_within_complete_passes", validity_gate_tests["within_complete_should_pass"]["valid"] is True, validity_gate_tests["within_complete_should_pass"])
    check("validity_gate_truncated_mid_bullet_fails", validity_gate_tests["truncated_mid_bullet_should_fail"]["valid"] is False, validity_gate_tests["truncated_mid_bullet_should_fail"])
    check("validity_gate_missing_source_ids_fails", validity_gate_tests["missing_source_ids_should_fail"]["valid"] is False, validity_gate_tests["missing_source_ids_should_fail"])

    turn_judge_packet_ids = build_turn_judge_packets(
        root=root,
        run_id=run_id,
        role_flow=role_flow,
        solo_conditions=solo_conditions,
        source_pack=source_pack,
        report_brief=report_brief,
        rubric=rubric,
    )

    artifact_count = len(list((root / "artifacts").glob("*/*.md")))
    trace_count = len(list((root / "traces").glob("*/*.json")))
    mission_count = len(list((root / "mission_packets").glob("*/*.md")))
    state_object_count = len(list((root / "state_objects").glob("*/*.json")))
    final_gate_count = len(list((root / "final_selection").glob("*.json")))
    turn_judge_packet_count = len(list((root / "turn_judge_packets").glob("*.json")))
    final_state = read_json(root / "state_objects" / "holo_frontier_gov" / "turn_6_state_object.json")
    expected_artifacts = (len(solo_conditions) * 6) + 6
    expected_traces = (len(solo_conditions) * 6) + 11
    expected_turn_judge_packets = len(solo_conditions) * 6
    check("artifact_count_expected", artifact_count == expected_artifacts, {"actual": artifact_count, "expected": expected_artifacts})
    check("trace_count_expected", trace_count == expected_traces, {"actual": trace_count, "expected": expected_traces})
    check("mission_packet_count_5", mission_count == 5, mission_count)
    check("state_object_count_6", state_object_count == 6, state_object_count)
    check(
        "state_object_required_fields",
        all(
            key in final_state
            for key in [
                "USER_GOAL",
                "CRITICAL_CONSTRAINTS",
                "ROLLING_SUMMARY",
                "HC_STATE_AUTHORITY",
                "SETTLED_DECISIONS",
                "ARTIFACTS_REGISTRY",
                "BATON_PASS",
                "PRESERVED_INSIGHT_LEDGER",
                "REPAIR_LEDGER",
            ]
        ),
        sorted(final_state.keys()),
    )
    check("state_object_version", final_state.get("state_object_version") == STATE_OBJECT_VERSION, final_state.get("state_object_version"))
    check("final_selection_count_1", final_gate_count == 1, final_gate_count)
    check("all_final_word_gates_pass", all(item["gate"]["passes"] for item in final_candidates.values()), final_candidates)
    check(
        "all_final_validity_gates_pass",
        all(item["artifact_validity_report"]["valid"] for item in final_candidates.values()),
        final_candidates,
    )
    check(
        "turn_judge_packet_count_expected",
        turn_judge_packet_count == expected_turn_judge_packets,
        {"actual": turn_judge_packet_count, "expected": expected_turn_judge_packets},
    )

    failures = [item for item in checks if not item["ok"]]
    manifest = {
        "run_id": run_id,
        "status": "NO_PROVIDER_SMOKE_PASS" if not failures else "NO_PROVIDER_SMOKE_FAIL",
        "created_at_utc": utc_iso(),
        "packet_dir": str(PACKET_DIR),
        "benchmark_credit": False,
        "public_claim": False,
        "provider_calls": 0,
        "live_calls_allowed": False,
        "domain": report_brief["domain"],
        "conditions": [*solo_conditions.keys(), "holo_frontier_gov"],
        "solo_suite_id": solo_suite_id,
        "solo_models": solo_conditions,
        "routing_config_id": routing_config["routing_config_id"],
        "routing_config_label": routing_config.get("label"),
        "holo_role_flow": [item["provider_model"] for item in turns],
        "holo_governor_model": report_brief["holo_turn_design"]["governor_model"],
        "holo_architecture_mode": STATE_OBJECT_VERSION,
        "turn_prompt_parity": parity_contract,
        "parity_note": "Solo and Holo share the same base turn role/instruction; Holo additionally receives Gov Baton/state/artifacts.",
        "word_count_band": [min_words, max_words],
        "hashes": hashes,
        "counts": {
            "artifacts": artifact_count,
            "traces": trace_count,
            "mission_packets": mission_count,
            "state_objects": state_object_count,
            "final_selection_files": final_gate_count,
            "turn_judge_packets": turn_judge_packet_count,
        },
        "word_gate_tests": word_gate_tests,
        "validity_gate_tests": validity_gate_tests,
        "final_candidates": final_candidates,
        "turn_judge_packets": turn_judge_packet_ids,
        "turn_judge_packet_count": turn_judge_packet_count,
        "turn_judge_status": "packets_built_not_scored",
        "checks": checks,
        "failures": failures,
        "notes": (
            "No-provider diagnostic smoke only. It validates artifact layout, trace hashes, "
            "Gov mission-packet scaffolding, word-count gates, and final-selection scaffolding. "
            "It is not benchmark evidence."
        ),
    }
    write_json(root / "run_manifest.json", manifest)

    summary = {
        "status": manifest["status"],
        "run_id": run_id,
        "provider_calls": 0,
        "benchmark_credit": False,
        "artifact_count": artifact_count,
        "trace_count": trace_count,
        "mission_packet_count": mission_count,
        "final_selection_count": final_gate_count,
        "turn_judge_packet_count": turn_judge_packet_count,
        "run_manifest": str(root / "run_manifest.json"),
        "failures": failures,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
