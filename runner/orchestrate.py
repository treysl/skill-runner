from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx

from runner.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, get_skill_md

ORCHESTRATION_MD = Path(__file__).resolve().parent / "cip-orchestration.md"
from runner.inspect import ExportInspection

BUILD_CONFIG_SCHEMA = {
    "client_name": "string",
    "branches": ["string or empty for all"],
    "divisions": ["string, at least one"],
    "completed_range": "ytd | this_month | last_30_days (pipeline default: ytd)",
    "overview_range": "last_year | last_12_complete_months",
    "min_est_revenue": "number",
    "sub_margin": "decimal e.g. 0.281",
    "invoice_flag_rule": "lag | over",
    "invoice_flag_gap": "decimal e.g. 0.10",
    "cost_pace_threshold": "decimal e.g. 0.0",
    "user": "string",
    "change_note": "string",
    "reasoning": "short explanation of choices",
}


def _load_orchestration_instructions() -> str:
    if ORCHESTRATION_MD.exists():
        return ORCHESTRATION_MD.read_text(encoding="utf-8").strip()
    return ""


def _load_runtime_config() -> dict[str, Any]:
    """Parse the JSON block under '## Runtime config' in cip-orchestration.md."""
    text = _load_orchestration_instructions()
    match = re.search(r"## Runtime config[\s\S]*?```json\s*(\{[\s\S]*?\})\s*```", text)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def _apply_runtime_defaults(config: dict[str, Any]) -> dict[str, Any]:
    runtime = _load_runtime_config()
    for key, value in runtime.items():
        config.setdefault(key, value)
    return config


def _load_skill_excerpt() -> str:
    skill_md = get_skill_md()
    if not skill_md.exists():
        return "CIP report skill unavailable."
    text = skill_md.read_text(encoding="utf-8")
    start = text.find("## Pre-Flight Checks")
    end = text.find("## How to Run")
    if start != -1 and end != -1:
        return text[start:end].strip()
    return text[:4000]


def _extract_json(content: str) -> dict[str, Any]:
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            raise ValueError("OpenRouter response did not contain JSON")
        return json.loads(match.group(0))


def _default_config(inspection: ExportInspection, client_name: str, user: str) -> dict[str, Any]:
    runtime = _load_runtime_config()
    divisions = runtime.get("divisions")
    if not divisions:
        divisions = [item["value"] for item in inspection.divisions if item["value"] != "(blank)"]
    if not divisions:
        divisions = ["Construction"]

    config = {
        "client_name": client_name,
        "branches": [],
        "divisions": divisions,
        "completed_range": "ytd",
        "overview_range": "last_12_complete_months",
        "min_est_revenue": 0,
        "sub_margin": 0.281,
        "invoice_flag_rule": "lag",
        "invoice_flag_gap": 0.10,
        "cost_pace_threshold": 0.0,
        "user": user,
        "change_note": "Generated via skill-runner n8n pipeline",
        "reasoning": "Fallback defaults because OpenRouter was unavailable.",
    }
    return _apply_runtime_defaults(config)


async def orchestrate_build_config(
    inspection: ExportInspection,
    *,
    client_name: str,
    user: str,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    overrides = overrides or {}

    if inspection.missing_required_columns:
        raise ValueError(
            "Export is missing required columns: "
            + ", ".join(inspection.missing_required_columns)
        )

    if not OPENROUTER_API_KEY:
        config = _default_config(inspection, client_name, user)
        config.update(overrides)
        return config

    skill_excerpt = _load_skill_excerpt()
    pipeline_instructions = _load_orchestration_instructions()
    system_prompt = (
        "You orchestrate the THG Construction In Process (CIP) report skill. "
        "Read the export inspection data, pipeline orchestration defaults, and skill pre-flight rules, "
        "then return ONLY valid JSON matching the schema. "
        "Pipeline orchestration defaults in `pipeline_orchestration_instructions` override interactive "
        "skill defaults in `skill_preflight_rules` when they conflict. "
        "Use the Runtime config JSON in `pipeline_orchestration_instructions` for divisions and other defaults. "
        "branches=[] means all branches."
    )
    user_prompt = {
        "pipeline_orchestration_instructions": pipeline_instructions,
        "runtime_config": _load_runtime_config(),
        "skill_preflight_rules": skill_excerpt,
        "expected_json_schema": BUILD_CONFIG_SCHEMA,
        "export_inspection": inspection.to_dict(),
        "requested_overrides": overrides,
        "instructions": (
            "Choose build parameters for one CIP report run. "
            "Use pipeline defaults and Runtime config JSON unless "
            "requested_overrides explicitly change them."
        ),
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, indent=2)},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/treysl/skill-runner",
        "X-Title": "skill-runner CIP orchestrator",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        body = response.json()

    content = body["choices"][0]["message"]["content"]
    config = _extract_json(content)
    config.setdefault("client_name", client_name)
    config.setdefault("user", user)
    _apply_runtime_defaults(config)
    config.update(overrides)
    return config
