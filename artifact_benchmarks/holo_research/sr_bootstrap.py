from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "research_packet_schema.json"
RUBRIC_PATH = ROOT / "research_judge_rubric.json"


REQUIRED_PACKET_FILES = [
    "research_packet.json",
    "research_packet.md",
    "dispatch_ledger.json",
    "source_ledger.json",
    "question_ledger.json",
    "contradiction_ledger.json",
    "builder_handoff.md",
]


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_stub_packet(domain: str, seed_material: str, source_budget: int) -> dict[str, Any]:
    seed_hash = sha_text(seed_material)
    dispatch = [
        {
            "turn": 1,
            "agent_role": "solo_research_bootstrap",
            "research_mission": "Mine seed material for the highest-value solvable questions and source needs.",
            "why_it_matters": "This creates a frozen research packet for HoloBuild before full HoloResearch is available.",
            "search_angles": [
                "current pressure frame",
                "decision-critical uncertainty",
                "practitioner objection",
                "counter-source need",
            ],
            "source_classes_to_seek": ["primary source", "data source", "expert/practitioner source", "counter-source"],
            "contradiction_to_hunt": "Find the assumption most likely to make the initial thesis false.",
            "source_budget": source_budget,
            "stop_condition": "Stop when the packet has enough source classes to support or reject the main research thesis.",
            "returned_source_ids": ["SR1", "SR2", "SR3"],
            "rejected_sources": [
                {
                    "title": "Generic commentary placeholder",
                    "reason": "Too broad to resolve a decision-critical question.",
                }
            ],
            "thesis_change": "The research objective shifted from broad topic coverage to finding the decision hinge.",
            "builder_use_or_avoid": "Use the question and contradiction ledgers; avoid treating stub sources as real-world evidence.",
        }
    ]
    questions = [
        {
            "question": "What is the decision hinge hidden inside the seed material?",
            "why_it_matters": "HoloBuild needs a solvable problem, not a generic topic.",
            "decision_relevance": "high",
            "evidence_found": ["SR1", "SR2"],
            "contradictions": ["C1"],
            "status": "partially_resolved",
            "builder_implication": "Frame the artifact around the decision hinge and preserve uncertainty.",
        },
        {
            "question": "What source class would a practitioner demand before accepting the thesis?",
            "why_it_matters": "Research quality depends on evidence standard, not prose confidence.",
            "decision_relevance": "high",
            "evidence_found": ["SR3"],
            "contradictions": [],
            "status": "open",
            "builder_implication": "Treat missing practitioner-grade evidence as a limitation.",
        },
    ]
    sources = [
        {
            "source_id": "SR1",
            "title": "Seed Material",
            "source_type": "user-provided seed",
            "url": None,
            "accessed_at": None,
            "retrieval_query": None,
            "excerpt": seed_material[:500],
            "claims_supported": ["The seed defines the starting problem space."],
            "claims_contradicted": [],
            "confidence": "high",
            "limitations": "Seed material is not independently verified.",
        },
        {
            "source_id": "SR2",
            "title": "Decision-Hinge Placeholder",
            "source_type": "no-provider smoke placeholder",
            "url": None,
            "accessed_at": None,
            "retrieval_query": None,
            "excerpt": "Smoke packet placeholder for the source class that would resolve the decision hinge.",
            "claims_supported": ["A decision-hinge source class is required."],
            "claims_contradicted": [],
            "confidence": "low",
            "limitations": "Not benchmark evidence; generated for harness smoke only.",
        },
        {
            "source_id": "SR3",
            "title": "Practitioner Standard Placeholder",
            "source_type": "no-provider smoke placeholder",
            "url": None,
            "accessed_at": None,
            "retrieval_query": None,
            "excerpt": "Smoke packet placeholder for the source a domain practitioner would demand.",
            "claims_supported": ["Practitioner-grade source standards should be explicit."],
            "claims_contradicted": [],
            "confidence": "low",
            "limitations": "Not benchmark evidence; generated for harness smoke only.",
        },
    ]
    contradictions = [
        {
            "contradiction_id": "C1",
            "claim": "The initial topic may look important before the real decision hinge is identified.",
            "counterclaim": "A high-quality research packet should narrow the topic into a solvable question.",
            "source_ids": ["SR1", "SR2"],
            "status": "partially_resolved",
            "builder_implication": "Do not build a generic overview when the packet exposes a decision hinge.",
        }
    ]
    packet = {
        "packet_id": f"sr_bootstrap_{domain}",
        "domain": domain,
        "seed_material_hash": seed_hash,
        "research_mode": "solo_research_bootstrap",
        "source_budget": source_budget,
        "turn_budget": 1,
        "research_thesis": "The bootstrap packet should mine the seed for high-value questions and source needs before HoloBuild writes.",
        "dispatch_ledger": dispatch,
        "question_ledger": questions,
        "source_ledger": sources,
        "contradiction_ledger": contradictions,
        "insight_map": [
            {
                "insight": "Research value begins when the topic is converted into a decision hinge.",
                "source_ids": ["SR1", "SR2"],
                "builder_use": "Use this as the organizing principle for the later HoloBuild artifact.",
            }
        ],
        "open_gaps": [
            {
                "gap": "No live sources were retrieved in smoke mode.",
                "impact": "This packet validates structure only and is not benchmark credit.",
            }
        ],
        "builder_implications": [
            "Build from the question ledger, not from broad topic framing.",
            "Preserve source limitations and do not overclaim smoke placeholders.",
        ],
        "claim_boundaries": [
            "This is a no-provider smoke packet.",
            "Stub sources are not external evidence.",
            "No live research occurred.",
        ],
        "confidence_limits": [
            "Low confidence on real-world claims because no live sources were retrieved.",
            "High confidence that the packet shape can be validated.",
        ],
        "gov_stop_or_unlock_decision": {
            "decision": "stop_after_bootstrap_smoke",
            "reason": "The smoke packet validates structure without provider calls.",
        },
    }
    return packet


def packet_markdown(packet: dict[str, Any]) -> str:
    questions = "\n".join(f"- {item['question']}" for item in packet["question_ledger"])
    sources = "\n".join(f"- `{item['source_id']}`: {item['title']} ({item['confidence']})" for item in packet["source_ledger"])
    gaps = "\n".join(f"- {item['gap']}" for item in packet["open_gaps"])
    return f"""# Solo Research Bootstrap Packet

Packet ID: `{packet['packet_id']}`

Mode: `{packet['research_mode']}`

## Research Thesis

{packet['research_thesis']}

## Questions

{questions}

## Sources

{sources}

## Open Gaps

{gaps}

## Builder Handoff

{'; '.join(packet['builder_implications'])}
"""


def builder_handoff(packet: dict[str, Any]) -> str:
    implications = "\n".join(f"- {item}" for item in packet["builder_implications"])
    boundaries = "\n".join(f"- {item}" for item in packet["claim_boundaries"])
    return f"""# Builder Handoff

Use this packet as solo research bootstrap input for HoloBuild.

## Builder Implications

{implications}

## Claim Boundaries

{boundaries}
"""


def write_packet_dir(out_dir: Path, packet: dict[str, Any]) -> None:
    write_json(out_dir / "research_packet.json", packet)
    write_text(out_dir / "research_packet.md", packet_markdown(packet))
    write_json(out_dir / "dispatch_ledger.json", packet["dispatch_ledger"])
    write_json(out_dir / "source_ledger.json", packet["source_ledger"])
    write_json(out_dir / "question_ledger.json", packet["question_ledger"])
    write_json(out_dir / "contradiction_ledger.json", packet["contradiction_ledger"])
    write_text(out_dir / "builder_handoff.md", builder_handoff(packet))


def validate_packet_dir(packet_dir: Path, require_hash: bool = False) -> list[str]:
    failures: list[str] = []
    schema = read_json(SCHEMA_PATH)
    for rel in REQUIRED_PACKET_FILES:
        if not (packet_dir / rel).exists():
            failures.append(f"missing:{rel}")
    if require_hash and not (packet_dir / "hash_lock.json").exists():
        failures.append("missing:hash_lock.json")
    if failures:
        return failures
    packet = read_json(packet_dir / "research_packet.json")
    for field in schema["required_top_level_fields"]:
        if field not in packet:
            failures.append(f"missing_field:{field}")
    if packet.get("research_mode") not in schema["research_mode_values"]:
        failures.append("invalid_research_mode")
    if packet.get("research_mode") == "web_enabled_controlled_retrieval" and not packet.get("dispatch_ledger"):
        failures.append("missing_dispatch_ledger_for_web_enabled_mode")
    source_ids = [item.get("source_id") for item in packet.get("source_ledger", [])]
    if len(source_ids) != len(set(source_ids)):
        failures.append("duplicate_source_ids")
    if len(source_ids) < 1:
        failures.append("empty_source_ledger")
    for item in packet.get("question_ledger", []):
        for source_id in item.get("evidence_found", []):
            if source_id not in source_ids:
                failures.append(f"unknown_question_source:{source_id}")
    for item in packet.get("contradiction_ledger", []):
        for source_id in item.get("source_ids", []):
            if source_id not in source_ids:
                failures.append(f"unknown_contradiction_source:{source_id}")
    if not packet.get("builder_implications"):
        failures.append("missing_builder_implications")
    if require_hash and (packet_dir / "hash_lock.json").exists():
        lock = read_json(packet_dir / "hash_lock.json")
        for rel, expected in lock.get("files", {}).items():
            path = packet_dir / rel
            if not path.exists():
                failures.append(f"hash_file_missing:{rel}")
            elif sha_file(path) != expected:
                failures.append(f"hash_mismatch:{rel}")
    return sorted(set(failures))


def freeze_packet_dir(packet_dir: Path) -> dict[str, Any]:
    failures = validate_packet_dir(packet_dir)
    if failures:
        raise RuntimeError(f"cannot_freeze_invalid_research_packet:{failures}")
    files = sorted(p for p in packet_dir.rglob("*") if p.is_file() and p.name != "hash_lock.json")
    lock = {
        "hash_lock_id": f"{packet_dir.name}_research_packet_hash_lock",
        "status": "frozen_solo_research_bootstrap_not_holoresearch_credit",
        "frozen_at_utc": utc_iso(),
        "benchmark_credit": False,
        "holoresearch_credit": False,
        "public_claim": False,
        "files": {str(path.relative_to(packet_dir)): sha_file(path) for path in files},
    }
    write_json(packet_dir / "hash_lock.json", lock)
    return lock


def build_judge_packet(packet_dir: Path) -> dict[str, Any]:
    failures = validate_packet_dir(packet_dir, require_hash=True)
    if failures:
        raise RuntimeError(f"cannot_build_judge_packet_for_invalid_research_packet:{failures}")
    packet = read_json(packet_dir / "research_packet.json")
    rubric = read_json(RUBRIC_PATH)
    judge_packet = {
        "judge_packet_id": f"{packet['packet_id']}_research_judge_packet",
        "packet_kind": "research_packet_single",
        "blind": True,
        "research_mode": packet["research_mode"],
        "domain": packet["domain"],
        "judge_visibility": rubric["judge_visibility"],
        "rubric": rubric,
        "documents": {
            "document_r": {
                "anonymous_id": "R",
                "research_packet": packet,
                "research_packet_md": (packet_dir / "research_packet.md").read_text(encoding="utf-8"),
                "builder_handoff_md": (packet_dir / "builder_handoff.md").read_text(encoding="utf-8"),
            }
        },
    }
    write_json(packet_dir / "judge_packet.json", judge_packet)
    return judge_packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Solo Research Bootstrap harness.")
    parser.add_argument("--generate-smoke", action="store_true", help="Create a no-provider solo research bootstrap packet.")
    parser.add_argument("--validate", type=Path, help="Validate an existing research packet directory.")
    parser.add_argument("--freeze", type=Path, help="Hash lock an existing research packet directory.")
    parser.add_argument("--build-judge-packet", type=Path, help="Build a blind research judge packet for a frozen research packet.")
    parser.add_argument("--out-dir", type=Path, default=Path("/private/tmp/holoresearch_sr_bootstrap_smoke"))
    parser.add_argument("--domain", default="capital_markets_trade_shock_execution")
    parser.add_argument("--source-budget", type=int, default=5)
    parser.add_argument("--seed-material", default="Smoke seed: identify a high-value research question and source needs.")
    args = parser.parse_args()

    action_count = sum(bool(item) for item in [args.generate_smoke, args.validate, args.freeze, args.build_judge_packet])
    if action_count != 1:
        parser.print_help()
        return 2

    if args.generate_smoke:
        packet = build_stub_packet(args.domain, args.seed_material, args.source_budget)
        write_packet_dir(args.out_dir, packet)
        failures = validate_packet_dir(args.out_dir)
        status = "SR_BOOTSTRAP_SMOKE_PASS" if not failures else "SR_BOOTSTRAP_SMOKE_FAIL"
        print(json.dumps({"status": status, "provider_calls": 0, "packet_dir": str(args.out_dir), "failures": failures}, indent=2))
        return 0 if not failures else 1

    if args.validate:
        failures = validate_packet_dir(args.validate, require_hash=(args.validate / "hash_lock.json").exists())
        status = "SR_BOOTSTRAP_VALIDATE_PASS" if not failures else "SR_BOOTSTRAP_VALIDATE_FAIL"
        print(json.dumps({"status": status, "packet_dir": str(args.validate), "failures": failures}, indent=2))
        return 0 if not failures else 1

    if args.freeze:
        lock = freeze_packet_dir(args.freeze)
        print(json.dumps({"status": "SR_BOOTSTRAP_FREEZE_COMPLETE", "packet_dir": str(args.freeze), "hash_lock": lock}, indent=2))
        return 0

    if args.build_judge_packet:
        judge_packet = build_judge_packet(args.build_judge_packet)
        print(json.dumps({"status": "SR_BOOTSTRAP_JUDGE_PACKET_CREATED", "packet_dir": str(args.build_judge_packet), "judge_packet_id": judge_packet["judge_packet_id"]}, indent=2))
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
