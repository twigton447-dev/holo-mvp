#!/usr/bin/env python3
"""Judge every HB draft against the VeSync brief and emit graph-ready data."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

PROJECT = Path(__file__).parent
RUN = PROJECT / "runs/live_lane-01_hb_creative_20260626T222600Z"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

RUBRIC_DIMENSIONS = [
    "brief_alignment",
    "strategic_positioning",
    "product_focus",
    "wellness_lifestyle_bridge",
    "evidence_claim_safety",
    "feature_functionality_use",
    "audience_newness_resonance",
    "emotional_resonance",
    "creativity_originality",
    "brand_voice_tone",
    "meta_ad_channel_fit",
    "website_banner_channel_fit",
    "email_channel_fit",
    "clarity_concision",
    "conversion_momentum",
    "schema_word_count",
    "downstream_copywriter_usefulness",
]

JUDGES = [
    {
        "judge_id": "judge-gemini",
        "provider": "google",
        "model_id": "gemini-2.5-pro",
        "label": "Gemini 2.5 Pro",
    },
    {
        "judge_id": "judge-minimax",
        "provider": "minimax",
        "model_id": os.getenv("VESYNC_JUDGE_MINIMAX_MODEL", os.getenv("MINIMAX_MODEL", "MiniMax-M2.5-highspeed")),
        "label": "MiniMax",
    },
]

JUDGE_CHUNK_SIZE = 3

JUDGE_FALLBACKS = {
    "judge-gemini": {
        "judge_id": "judge-gemini-fallback-claude-haiku",
        "provider": "anthropic",
        "model_id": os.getenv("VESYNC_JUDGE_HAIKU_MODEL", "claude-haiku-4-5-20251001"),
        "label": "Claude Haiku fallback for Gemini",
        "fallback_for": "judge-gemini",
    }
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


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def load_drafts() -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []
    initial = json.loads((PROJECT / "02_initial_draft.json").read_text())
    drafts.append(
        {
            "step_index": 0,
            "step_id": "step-00-initial-seed-draft",
            "source": "02_initial_draft.json",
            "turn": 0,
            "role": "initial_seed",
            "status": "SEED",
            "artifact": initial,
            "email_body_words": word_count(initial["section_3_email"]["body"]),
        }
    )

    seen_turns: set[int] = set()
    for output in read_jsonl(RUN / "turn_outputs.jsonl"):
        if output.get("status") != "PASS" or not isinstance(output.get("artifact"), dict):
            continue
        turn = int(output["turn"])
        if turn in seen_turns:
            continue
        seen_turns.add(turn)
        artifact = output["artifact"]
        drafts.append(
            {
                "step_index": len(drafts),
                "step_id": f"step-{len(drafts):02d}-turn-{turn:02d}",
                "source": "turn_outputs.jsonl",
                "turn": turn,
                "role": output.get("role"),
                "provider": output.get("provider"),
                "model_id": output.get("model_id"),
                "status": "PASS",
                "artifact": artifact,
                "email_body_words": word_count(artifact["section_3_email"]["body"]),
            }
        )

    final_path = RUN / "final_candidate_artifact.json"
    if final_path.exists():
        final = json.loads(final_path.read_text())
        drafts.append(
            {
                "step_index": len(drafts),
                "step_id": f"step-{len(drafts):02d}-final-governor-repair",
                "source": "final_candidate_artifact.json",
                "turn": "post_run_final",
                "role": "post_run_governor_repair",
                "status": "PASS",
                "artifact": final,
                "email_body_words": word_count(final["section_3_email"]["body"]),
            }
        )
    return drafts


def extract_json(text: str) -> dict[str, Any] | None:
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped).strip()
    try:
        return json.loads(stripped)
    except Exception:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(stripped[start : end + 1])
            except Exception:
                return None
    return None


def call_model(provider: str, model_id: str, system: str, user: str) -> dict[str, Any]:
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
            max_tokens=7000,
            temperature=0.1,
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
            max_tokens=7000,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return {
            "text": response.content[0].text,
            "input_tokens": getattr(response.usage, "input_tokens", None),
            "output_tokens": getattr(response.usage, "output_tokens", None),
            "elapsed_ms": int((time.time() - started) * 1000),
        }
    if provider == "google":
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY"),
            http_options={"timeout": 60000},
        )
        response = client.models.generate_content(
            model=model_id,
            contents=f"{system}\n\n---\n\n{user}",
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=12000,
                response_mime_type="application/json",
            ),
        )
        usage = getattr(response, "usage_metadata", None)
        return {
            "text": response.text,
            "input_tokens": getattr(usage, "prompt_token_count", None) if usage else None,
            "output_tokens": getattr(usage, "candidates_token_count", None) if usage else None,
            "elapsed_ms": int((time.time() - started) * 1000),
        }
    if provider == "minimax":
        from openai import OpenAI

        client = OpenAI(
            api_key=os.getenv("MINIMAX_API_KEY"),
            base_url="https://api.minimax.chat/v1",
        )
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=7000,
            temperature=0.1,
        )
        return {
            "text": response.choices[0].message.content,
            "input_tokens": getattr(response.usage, "prompt_tokens", None),
            "output_tokens": getattr(response.usage, "completion_tokens", None),
            "elapsed_ms": int((time.time() - started) * 1000),
        }
    raise ValueError(f"unsupported provider {provider}")


def validate_judge_output(obj: Any, expected_steps: list[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["judge output is not object"]
    for key in ("judge_id", "rubric_version", "ranked_best_step_id", "trend_summary", "graph_notes"):
        if key not in obj:
            errors.append(f"{key} missing")
    scores = obj.get("scores")
    if not isinstance(scores, list):
        return ["scores missing or not list"]
    got_steps = [row.get("step_id") for row in scores if isinstance(row, dict)]
    if got_steps != expected_steps:
        errors.append(f"step_id sequence mismatch expected={expected_steps} got={got_steps}")
    for row in scores:
        if not isinstance(row, dict):
            errors.append("score row is not object")
            continue
        for dim in RUBRIC_DIMENSIONS + ["overall_score"]:
            value = row.get(dim)
            if not isinstance(value, (int, float)):
                errors.append(f"{row.get('step_id')}.{dim} missing numeric score")
            elif value < 0 or value > (100 if dim == "overall_score" else 10):
                errors.append(f"{row.get('step_id')}.{dim} out of range: {value}")
        for key in ("strengths", "defects"):
            if not isinstance(row.get(key), list):
                errors.append(f"{row.get('step_id')}.{key} missing list")
        if not isinstance(row.get("evolution_note"), str):
            errors.append(f"{row.get('step_id')}.evolution_note missing string")
    return errors


def build_prompt(drafts: list[dict[str, Any]], chunk_label: str) -> str:
    brief = json.loads((PROJECT / "00_input_brief.json").read_text())
    seed_packet = json.loads((PROJECT / "01_research_packet_seed.json").read_text())
    source_records = read_jsonl(RUN / "research_lane-01.jsonl")
    compact_drafts = [
        {
            "step_index": d["step_index"],
            "step_id": d["step_id"],
            "source": d["source"],
            "turn": d["turn"],
            "role": d["role"],
            "provider": d.get("provider"),
            "model_id": d.get("model_id"),
            "email_body_words": d["email_body_words"],
            "artifact": d["artifact"],
        }
        for d in drafts
    ]
    expected_steps = [d["step_id"] for d in drafts]
    return (
        "Grade each draft independently against the VeSync Cosori TurboBlaze copywriter exercise brief. "
        "Do not reward a draft merely because it is later in the sequence. Penalize unsupported claims, "
        "weak lifestyle linkage, schema/word-count issues, generic ad language, emotional flatness, "
        "strategy that feels like a feature list, and copy that does not answer how the product supports "
        "a better wellness-forward home routine.\n\n"
        f"Chunk: {chunk_label}. Required output: one JSON object only with keys judge_id, rubric_version, scores, "
        "ranked_best_step_id, trend_summary, graph_notes. The scores array must contain exactly one row "
        f"for each step_id in this exact order: {expected_steps}. Each score row must contain step_id, "
        f"{', '.join(RUBRIC_DIMENSIONS)}, overall_score, strengths, defects, evolution_note. "
        "Dimension scores are 0-10. overall_score is 0-100. strengths and defects must be arrays of strings. "
        "Do not use obsolete fields named channel_fit, brand_voice, or creative_strength.\n\n"
        "Wide rubric guidance:\n"
        "- brief_alignment: answers the exact VeSync assignment and all three deliverable sections.\n"
        "- strategic_positioning: has a clear campaign idea, not just assorted lines.\n"
        "- product_focus: stays on Cosori TurboBlaze Air Fryer only.\n"
        "- wellness_lifestyle_bridge: connects functions to better routines and lifestyle without medical/diet claims.\n"
        "- evidence_claim_safety: protects source boundaries and required qualifiers.\n"
        "- feature_functionality_use: uses verified features in a persuasive, non-stuffy way.\n"
        "- audience_newness_resonance: could plausibly resonate with new audiences, not only existing owners.\n"
        "- emotional_resonance: creates a felt reason to care: relief, ease, pride, confidence, appetite, momentum.\n"
        "- creativity_originality: avoids default bland appliance phrasing and overused wellness cliches.\n"
        "- brand_voice_tone: feels food-first, capable, accessible, and Cosori-compatible.\n"
        "- meta_ad_channel_fit: strong hooks, scannable proof, plausible feed behavior.\n"
        "- website_banner_channel_fit: each banner works as a crisp site unit with sequence logic.\n"
        "- email_channel_fit: subject/body/P.S. feel like a short consumer email, not a product memo.\n"
        "- clarity_concision: copy is easy to understand without becoming thin.\n"
        "- conversion_momentum: CTAs and line endings create next-action energy.\n"
        "- schema_word_count: exact schema and email body word count compliance.\n"
        "- downstream_copywriter_usefulness: a human/model copywriter could use it without re-researching.\n\n"
        "Brief:\n"
        f"{json.dumps(brief, ensure_ascii=False, indent=2)}\n\n"
        "Seed research packet and constraints:\n"
        f"{json.dumps(seed_packet, ensure_ascii=False, indent=2)}\n\n"
        "Source records available for claim validation:\n"
        f"{json.dumps(source_records, ensure_ascii=False, indent=2)}\n\n"
        "Draft steps to grade:\n"
        f"{json.dumps(compact_drafts, ensure_ascii=False, indent=2)}"
    )


def write_svg(rows: list[dict[str, Any]], out: Path) -> None:
    width, height = 980, 420
    left, right, top, bottom = 70, 30, 35, 65
    plot_w = width - left - right
    plot_h = height - top - bottom
    xs = [row["step_index"] for row in rows]
    max_x = max(xs) if xs else 1

    def x_pos(i: int) -> float:
        return left + (i / max_x) * plot_w if max_x else left

    def y_pos(score: float) -> float:
        return top + (100 - score) / 100 * plot_h

    points = " ".join(f"{x_pos(row['step_index']):.1f},{y_pos(row['consensus_overall']):.1f}" for row in rows)
    judge_series = []
    palette = ["#7c3aed", "#0f766e", "#dc2626", "#2563eb"]
    for i, judge in enumerate(JUDGES):
        judge_id = judge["judge_id"]
        series_points = " ".join(
            f"{x_pos(row['step_index']):.1f},{y_pos(row.get(judge_id, 0)):.1f}"
            for row in rows
        )
        judge_series.append(
            {
                "points": series_points,
                "color": palette[i % len(palette)],
                "label": judge["label"],
            }
        )
    labels = []
    for row in rows:
        x = x_pos(row["step_index"])
        labels.append(
            f'<text x="{x:.1f}" y="{height - 35}" font-size="10" text-anchor="middle" '
            f'font-family="Arial">{row["short_label"]}</text>'
        )
    grid = []
    for score in range(0, 101, 20):
        y = y_pos(score)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        grid.append(f'<text x="{left-12}" y="{y+4:.1f}" font-size="11" text-anchor="end" font-family="Arial">{score}</text>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{left}" y="22" font-size="18" font-family="Arial" font-weight="700">HB Draft Evolution Scores</text>
  {''.join(grid)}
  <line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#111827"/>
  <line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#111827"/>
  {''.join(f'<polyline points="{series["points"]}" fill="none" stroke="{series["color"]}" stroke-width="1.5" stroke-dasharray="4 4"/>' for series in judge_series)}
  <polyline points="{points}" fill="none" stroke="#111827" stroke-width="3"/>
  {''.join(f'<circle cx="{x_pos(row["step_index"]):.1f}" cy="{y_pos(row["consensus_overall"]):.1f}" r="4" fill="#111827"/>' for row in rows)}
  {''.join(labels)}
  <text x="{width-310}" y="24" font-size="12" font-family="Arial" fill="#111827">solid: consensus</text>
  {''.join(f'<text x="{width-210 + i*95}" y="24" font-size="12" font-family="Arial" fill="{series["color"]}">dash: {series["label"]}</text>' for i, series in enumerate(judge_series))}
</svg>
"""
    out.write_text(svg)


def main() -> int:
    status = json.loads((RUN / "RUN_STATUS.json").read_text())
    if status.get("judge_provider_export_approval") != "APPROVED_FOR_GEMINI_MINIMAX_JUDGING":
        raise SystemExit(
            "judge provider export not approved for Gemini/MiniMax; "
            "set RUN_STATUS judge_provider_export_approval only after explicit user approval"
        )
    if status.get("solo_opus_status") != "NOT_RUN_PER_USER_INSTRUCTION":
        raise SystemExit("solo opus boundary missing")

    drafts = load_drafts()
    (RUN / "judging_drafts_bundle.json").write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n")
    draft_chunks = [
        drafts[i : i + JUDGE_CHUNK_SIZE]
        for i in range(0, len(drafts), JUDGE_CHUNK_SIZE)
    ]
    all_expected_steps = [d["step_id"] for d in drafts]

    judge_results: list[dict[str, Any]] = []
    system = "You are an exacting advertising-copy judge. Return only valid JSON."
    for judge in JUDGES:
        print(f"JUDGE {judge['label']}", flush=True)
        combined_scores: list[dict[str, Any]] = []
        chunk_outputs: list[dict[str, Any]] = []
        for chunk_index, chunk in enumerate(draft_chunks, start=1):
            chunk_label = f"{chunk_index}/{len(draft_chunks)}"
            print(f"JUDGE {judge['label']} chunk {chunk_label}", flush=True)
            prompt = build_prompt(chunk, chunk_label)
            expected_steps = [d["step_id"] for d in chunk]
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            judge_input = {
                "event_type": "judge_input",
                "created_at": now(),
                "judge": judge,
                "chunk_index": chunk_index,
                "chunk_count": len(draft_chunks),
                "prompt_sha256": prompt_hash,
                "draft_step_ids": expected_steps,
                "draft_count": len(chunk),
                "rubric_dimensions": RUBRIC_DIMENSIONS,
            }
            append_jsonl(RUN / "judge_inputs.jsonl", judge_input)
            try:
                response = call_model(judge["provider"], judge["model_id"], system, prompt)
                parsed = extract_json(response["text"])
                errors = validate_judge_output(parsed, expected_steps) if parsed is not None else ["could not parse judge JSON"]
                if errors:
                    repair_prompt = (
                        f"Your judging output failed validation: {json.dumps(errors)}\n\n"
                        "Return one corrected JSON object only. Required top-level keys: "
                        "judge_id, rubric_version, scores, ranked_best_step_id, trend_summary, graph_notes. "
                        f"Return scores only for these step_ids in order: {expected_steps}. "
                        f"Each score row must include these exact dimensions: {RUBRIC_DIMENSIONS}, plus "
                        "overall_score, strengths, defects, evolution_note. strengths and defects must be arrays. "
                        "Do not use obsolete fields named channel_fit, brand_voice, or creative_strength.\n\n"
                        f"Original output:\n{response['text']}"
                    )
                    repair = call_model(judge["provider"], judge["model_id"], system, repair_prompt)
                    parsed = extract_json(repair["text"])
                    errors = validate_judge_output(parsed, expected_steps) if parsed is not None else ["could not parse repair JSON"]
                    judge_output = {
                        "event_type": "judge_output",
                        "created_at": now(),
                        "judge": judge,
                        "chunk_index": chunk_index,
                        "chunk_count": len(draft_chunks),
                        "status": "PASS" if not errors else "VALIDATION_FAILED",
                        "validation_errors": errors,
                        "repair_used": True,
                        "parsed": parsed,
                        "raw_output": response["text"],
                        "repair_raw_output": repair["text"],
                        "usage": {
                            "initial": {k: response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                            "repair": {k: repair.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                        },
                    }
                else:
                    judge_output = {
                        "event_type": "judge_output",
                        "created_at": now(),
                        "judge": judge,
                        "chunk_index": chunk_index,
                        "chunk_count": len(draft_chunks),
                        "status": "PASS",
                        "validation_errors": [],
                        "repair_used": False,
                        "parsed": parsed,
                        "raw_output": response["text"],
                        "usage": {k: response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                    }
            except Exception as exc:
                provider_failure = {
                    "event_type": "judge_output",
                    "created_at": now(),
                    "judge": judge,
                    "chunk_index": chunk_index,
                    "chunk_count": len(draft_chunks),
                    "status": "PROVIDER_CALL_FAILED",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:1200],
                }
                fallback = JUDGE_FALLBACKS.get(judge["judge_id"])
                if fallback:
                    print(
                        f"JUDGE {judge['label']} chunk {chunk_label} failed; "
                        f"trying {fallback['label']}",
                        flush=True,
                    )
                    try:
                        response = call_model(fallback["provider"], fallback["model_id"], system, prompt)
                        parsed = extract_json(response["text"])
                        errors = (
                            validate_judge_output(parsed, expected_steps)
                            if parsed is not None
                            else ["could not parse fallback judge JSON"]
                        )
                        if errors:
                            repair_prompt = (
                                f"Your judging output failed validation: {json.dumps(errors)}\n\n"
                                "Return one corrected JSON object only. Required top-level keys: "
                                "judge_id, rubric_version, scores, ranked_best_step_id, trend_summary, graph_notes. "
                                f"Return scores only for these step_ids in order: {expected_steps}. "
                                f"Each score row must include these exact dimensions: {RUBRIC_DIMENSIONS}, plus "
                                "overall_score, strengths, defects, evolution_note. strengths and defects must be arrays. "
                                "Do not use obsolete fields named channel_fit, brand_voice, or creative_strength.\n\n"
                                f"Original output:\n{response['text']}"
                            )
                            repair = call_model(fallback["provider"], fallback["model_id"], system, repair_prompt)
                            parsed = extract_json(repair["text"])
                            errors = (
                                validate_judge_output(parsed, expected_steps)
                                if parsed is not None
                                else ["could not parse fallback repair JSON"]
                            )
                            judge_output = {
                                "event_type": "judge_output",
                                "created_at": now(),
                                "judge": judge,
                                "actual_judge": fallback,
                                "fallback_used": True,
                                "fallback_reason": provider_failure,
                                "chunk_index": chunk_index,
                                "chunk_count": len(draft_chunks),
                                "status": "PASS" if not errors else "VALIDATION_FAILED",
                                "validation_errors": errors,
                                "repair_used": True,
                                "parsed": parsed,
                                "raw_output": response["text"],
                                "repair_raw_output": repair["text"],
                                "usage": {
                                    "initial": {k: response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                                    "repair": {k: repair.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                                },
                            }
                        else:
                            judge_output = {
                                "event_type": "judge_output",
                                "created_at": now(),
                                "judge": judge,
                                "actual_judge": fallback,
                                "fallback_used": True,
                                "fallback_reason": provider_failure,
                                "chunk_index": chunk_index,
                                "chunk_count": len(draft_chunks),
                                "status": "PASS",
                                "validation_errors": [],
                                "repair_used": False,
                                "parsed": parsed,
                                "raw_output": response["text"],
                                "usage": {k: response.get(k) for k in ("input_tokens", "output_tokens", "elapsed_ms")},
                            }
                    except Exception as fallback_exc:
                        judge_output = provider_failure
                        judge_output["fallback_attempted"] = fallback
                        judge_output["fallback_error_type"] = type(fallback_exc).__name__
                        judge_output["fallback_error"] = str(fallback_exc)[:1200]
                else:
                    judge_output = provider_failure
            append_jsonl(RUN / "judge_outputs.jsonl", judge_output)
            if judge_output["status"] != "PASS":
                print(f"JUDGE BLOCKED {judge['label']} chunk {chunk_label}: {judge_output['status']}", flush=True)
                return 1
            chunk_outputs.append(judge_output)
            combined_scores.extend(judge_output["parsed"]["scores"])
        if [row["step_id"] for row in combined_scores] != all_expected_steps:
            print(f"JUDGE BLOCKED {judge['label']}: combined step sequence mismatch", flush=True)
            return 1
        judge_results.append(
            {
                "event_type": "judge_output_combined",
                "created_at": now(),
                "judge": judge,
                "status": "PASS",
                "chunked": True,
                "chunk_count": len(draft_chunks),
                "parsed": {
                    "judge_id": judge["judge_id"],
                    "rubric_version": "vesync_wide_creative_judging_v1_chunked",
                    "scores": combined_scores,
                    "ranked_best_step_id": max(combined_scores, key=lambda row: row["overall_score"])["step_id"],
                    "trend_summary": "Combined from chunked judge calls using the same brief and rubric.",
                    "graph_notes": ["Chunked to avoid provider timeout while preserving per-draft scoring."],
                },
                "chunk_outputs": [
                    {
                        "chunk_index": out["chunk_index"],
                        "usage": out.get("usage"),
                        "repair_used": out.get("repair_used"),
                    }
                    for out in chunk_outputs
                ],
            }
        )

    rows: list[dict[str, Any]] = []
    for draft in drafts:
        row: dict[str, Any] = {
            "step_index": draft["step_index"],
            "step_id": draft["step_id"],
            "short_label": (
                "seed"
                if draft["step_index"] == 0
                else "final" if draft["step_id"].endswith("final-governor-repair") else f"t{draft['turn']}"
            ),
            "turn": draft["turn"],
            "role": draft["role"],
            "email_body_words": draft["email_body_words"],
        }
        per_judge_scores = []
        dim_values: dict[str, list[float]] = {dim: [] for dim in RUBRIC_DIMENSIONS}
        for result in judge_results:
            judge_id = result["judge"]["judge_id"]
            score = next(item for item in result["parsed"]["scores"] if item["step_id"] == draft["step_id"])
            row[judge_id] = float(score["overall_score"])
            per_judge_scores.append(float(score["overall_score"]))
            for dim in RUBRIC_DIMENSIONS:
                dim_values[dim].append(float(score[dim]))
        row["consensus_overall"] = round(mean(per_judge_scores), 2)
        for dim, values in dim_values.items():
            row[f"avg_{dim}"] = round(mean(values), 2)
        rows.append(row)

    previous = None
    for row in rows:
        row["delta_from_previous"] = None if previous is None else round(row["consensus_overall"] - previous, 2)
        previous = row["consensus_overall"]
    seed_score = rows[0]["consensus_overall"]
    for row in rows:
        row["delta_from_seed"] = round(row["consensus_overall"] - seed_score, 2)

    (RUN / "judge_scores.json").write_text(
        json.dumps({"created_at": now(), "judges": JUDGES, "rubric_dimensions": RUBRIC_DIMENSIONS, "rows": rows}, indent=2)
        + "\n"
    )
    with (RUN / "step_graph_data.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (RUN / "step_graph_data.json").write_text(json.dumps(rows, indent=2) + "\n")
    write_svg(rows, RUN / "step_graph.svg")

    audit = {
        "event_type": "governor_brief",
        "lane_id": "lane-01",
        "turn": "post_run_judging",
        "created_at": now(),
        "status": "POST_RUN_JUDGING_COMPLETE",
        "judge_outputs": "judge_outputs.jsonl",
        "scores": "judge_scores.json",
        "graph_csv": "step_graph_data.csv",
        "graph_svg": "step_graph.svg",
        "solo_opus_status": "NOT_RUN_PER_USER_INSTRUCTION",
    }
    append_jsonl(RUN / "governor_briefs.jsonl", audit)
    append_jsonl(
        RUN / "canonical_thread.jsonl",
        {
            "event_type": "canonical_thread_entry",
            "lane_id": "lane-01",
            "turn": "post_run_judging",
            "role": "governor",
            "created_at": now(),
            "content_type": "post_run_judging_complete",
            "content": audit,
        },
    )
    print("JUDGING COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
