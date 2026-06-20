from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


FACTORY_DIR = Path(__file__).resolve().parent
SUITE_RUNS_ROOT = FACTORY_DIR / "suite_runs"
POLICY_PATH = FACTORY_DIR / "scoring_policies" / "combined_artifact_scoring_protocol_v4.lock.json"

sys.path.insert(0, str(FACTORY_DIR))

from run_holo_factory_suite import (  # noqa: E402
    load_kit,
    read_kit_dataset_and_exhibit_payload,
    sha_text,
    utc_iso,
    validity_report,
)


INTERNAL_PACKET_KEYS = {
    "status",
    "benchmark_credit",
    "public_claim",
}

LEAK_TERMS = [
    "hologov",
    "holo gov",
    "holobuild",
    "batonpass",
    "baton pass",
    "build_state_object",
    "verify_state_object",
    "govstate",
    "draft_not_frozen",
    "benchmark_credit",
    "provider_calls",
    "model slot",
    "solo model slot",
    "holo condition",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def scrub_text(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("status:"):
            continue
        if "draft_not_frozen" in stripped.lower():
            continue
        if "benchmark_credit" in stripped.lower():
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def scrub_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: scrub_json(item) for key, item in value.items() if key not in INTERNAL_PACKET_KEYS}
    if isinstance(value, list):
        return [scrub_json(item) for item in value]
    if isinstance(value, str):
        return value.replace("draft_not_frozen", "").replace("benchmark_credit", "")
    return value


def neutral_domain_packet(kit: dict[str, Any]) -> dict[str, Any]:
    return {
        "domain_id": kit["domain_id"],
        "brief_md": scrub_text(kit["brief"]),
        "source_pack": scrub_json(kit["source_pack"]),
        "datasets_and_exhibits": read_kit_dataset_and_exhibit_payload(kit),
        "required_sections": kit["gov_protocol"]["validity_gate"].get("required_sections_must_be_present", []),
        "required_disclaimer": kit["gov_protocol"]["validity_gate"].get("required_disclaimer", ""),
        "word_band": kit["gov_protocol"]["validity_gate"].get("word_band", {}),
        "hidden_failure_targets": kit["hidden_failure_targets"].get("targets", kit["hidden_failure_targets"]),
        "math_requirements": kit["source_pack"].get("math_requirements", []),
        "rubric": scrub_json(kit["rubric"]),
        "judge_brief_md": scrub_text(kit["judge_brief"]),
    }


def judge_visible_policy(policy: dict[str, Any]) -> dict[str, Any]:
    rigorous = policy["rigorous_rubric"]
    return {
        "policy_id": policy["policy_id"],
        "score_label": policy["score_label"],
        "scoring_order": [
            "Apply deterministic admissibility gate.",
            "Score rigorous quality rubric from visible evidence.",
            "Apply lowest triggered hard cap.",
            "If the gate is invalid, report diagnostic quality score but leave proof_credit_score_1_10 null.",
        ],
        "deterministic_gate": {
            "checks": [
                "word_count_in_domain_band",
                "clean_final_ending",
                "required_sections_present",
                "required_disclaimer_present",
                "source_ids_present",
                "no_unknown_source_ids",
                "no_internal_process_residue",
                "no_internal_scaffold_leakage",
            ]
        },
        "rigorous_rubric": rigorous,
        "hard_caps": policy["hard_caps"],
        "judge_output_schema": policy["judge_output_schema"],
    }


def leak_scan(payload: Any) -> list[str]:
    text = json.dumps(payload, sort_keys=True).lower()
    found = []
    for term in LEAK_TERMS:
        if term in text:
            found.append(term)
    return sorted(set(found))


def condition_dirs(run_root: Path, domain: str, cohort: str, conditions: list[str] | None) -> list[Path]:
    root = run_root / "artifacts" / domain / cohort
    if conditions:
        return [root / condition for condition in conditions]
    return sorted(path for path in root.iterdir() if path.is_dir() and (path / "final.md").exists())


def judge_prompt(packet: dict[str, Any]) -> str:
    return f"""You are a blind artifact judge. Score only ARTIFACT_TEXT against DOMAIN_PACKET and SCORING_PROTOCOL.

Rules:
- Do not browse.
- Do not infer model identity.
- Do not reward polish, length, or confidence.
- Award points only for visible evidence in the artifact.
- Apply hard caps when triggered.
- Return strict JSON matching SCORING_PROTOCOL.judge_output_schema.

SCORING_PROTOCOL:
{json.dumps(packet["scoring_protocol"], indent=2)}

DOMAIN_PACKET:
{json.dumps(packet["domain_packet"], indent=2)}

DETERMINISTIC_GATE_REPORT:
{json.dumps(packet["deterministic_gate_report"], indent=2)}

ARTIFACT_LABEL: {packet["artifact_label"]}

ARTIFACT_TEXT:
{packet["artifact_text"]}
"""


def build_packets(
    *,
    run_id: str,
    domain: str,
    cohort: str,
    conditions: list[str] | None,
    output_dir: Path,
) -> dict[str, Any]:
    run_root = SUITE_RUNS_ROOT / run_id
    kit = load_kit(domain)
    policy = read_json(POLICY_PATH)
    visible_policy = judge_visible_policy(policy)
    domain_packet = neutral_domain_packet(kit)
    packet_leaks = leak_scan({"domain_packet": domain_packet, "scoring_protocol": visible_policy})
    packets = []

    for idx, path in enumerate(condition_dirs(run_root, domain, cohort, conditions), start=1):
        final_path = path / "final.md"
        if not final_path.exists():
            final_path = path / "turn_6.md"
        if not final_path.exists():
            raise FileNotFoundError(f"missing_final_artifact:{path / 'final.md'}")
        artifact_text = final_path.read_text(encoding="utf-8")
        label = f"ARTIFACT_{idx:03d}"
        gate = validity_report(artifact_text, kit)
        artifact_leaks = leak_scan({"artifact_text": artifact_text})
        packet = {
            "packet_type": "combined_gate_rubric_browser_packet_v4",
            "built_at": utc_iso(),
            "run_id": run_id,
            "domain_id": domain,
            "cohort": cohort,
            "artifact_label": label,
            "artifact_sha256": sha_text(artifact_text),
            "scoring_protocol": visible_policy,
            "domain_packet": domain_packet,
            "deterministic_gate_report": {
                "valid": gate.get("valid"),
                "flags": gate.get("flags") or [],
                "word_count": gate.get("word_count"),
                "word_count_in_band": gate.get("word_count_in_band"),
                "clean_ending": gate.get("clean_ending"),
                "required_sections_present": gate.get("required_sections_present"),
                "source_ids": gate.get("source_ids"),
                "proof_credit_eligible": bool(gate.get("valid")),
            },
            "leak_scan": {
                "domain_packet_or_protocol_leaks": packet_leaks,
                "artifact_text_leaks": artifact_leaks,
                "browser_packet_clean": not packet_leaks and not artifact_leaks,
            },
            "artifact_text": artifact_text,
        }
        packet["browser_prompt"] = judge_prompt(packet)
        packet_path = output_dir / f"{label}.json"
        prompt_path = output_dir / f"{label}_prompt.md"
        write_json(packet_path, packet)
        prompt_path.write_text(packet["browser_prompt"], encoding="utf-8")
        packets.append(
            {
                "artifact_label": label,
                "condition": path.name,
                "packet_json": str(packet_path),
                "prompt_md": str(prompt_path),
                "deterministic_gate_valid": gate.get("valid"),
                "deterministic_gate_flags": gate.get("flags") or [],
                "browser_packet_clean": packet["leak_scan"]["browser_packet_clean"],
                "artifact_sha256": packet["artifact_sha256"],
            }
        )

    index = {
        "status": "COMBINED_SCORING_BROWSER_PACKETS_V4_BUILT",
        "built_at": utc_iso(),
        "provider_calls": 0,
        "run_id": run_id,
        "domain_id": domain,
        "cohort": cohort,
        "score_label": policy["score_label"],
        "policy_id": policy["policy_id"],
        "packet_count": len(packets),
        "packets": packets,
    }
    write_json(output_dir / "index.json", index)
    return index


def parse_conditions(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    return [part.strip() for part in re.split(r"[, ]+", raw) if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build blind combined deterministic+rigorous browser scoring packets.")
    parser.add_argument("run_id")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--conditions", default=None, help="Comma or space separated condition IDs. Defaults to all final artifacts.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else (
        SUITE_RUNS_ROOT
        / args.run_id
        / "analysis"
        / "combined_scoring_browser_packets_v4"
        / args.domain
        / args.cohort
    )
    result = build_packets(
        run_id=args.run_id,
        domain=args.domain,
        cohort=args.cohort,
        conditions=parse_conditions(args.conditions),
        output_dir=output_dir,
    )
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
