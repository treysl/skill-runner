from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from runner.config import N8N_API_KEY, N8N_BASE_URL, N8N_WORKFLOW_ID, ROOT

DEFAULT_WORKFLOW_PATH = ROOT / "n8n" / "cip-report-pipeline.json"

_API_FIELDS = ("name", "nodes", "connections", "settings")


def _headers() -> dict[str, str]:
    if not N8N_API_KEY:
        raise ValueError(
            "N8N_API_KEY is not set. Add it to .env (Settings → n8n API in the n8n UI)."
        )
    return {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def load_workflow(path: Path | None = None) -> dict[str, Any]:
    workflow_path = path or DEFAULT_WORKFLOW_PATH
    with workflow_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def prepare_api_payload(workflow: dict[str, Any]) -> dict[str, Any]:
    payload = {field: workflow[field] for field in _API_FIELDS if field in workflow}
    if "name" not in payload:
        raise ValueError("Workflow JSON is missing a name field.")
    if "nodes" not in payload or "connections" not in payload:
        raise ValueError("Workflow JSON must include nodes and connections.")
    payload.setdefault("settings", {})
    return payload


def _unwrap_list(response: httpx.Response) -> list[dict[str, Any]]:
    body = response.json()
    if isinstance(body, list):
        return body
    if isinstance(body, dict) and isinstance(body.get("data"), list):
        return body["data"]
    raise ValueError(f"Unexpected workflows list response: {body!r}")


def _unwrap_workflow(response: httpx.Response) -> dict[str, Any]:
    body = response.json()
    if isinstance(body, dict) and isinstance(body.get("data"), dict):
        return body["data"]
    if isinstance(body, dict) and "id" in body:
        return body
    raise ValueError(f"Unexpected workflow response: {body!r}")


def find_workflow_id(client: httpx.Client, name: str) -> str | None:
    response = client.get("/workflows", params={"limit": 250})
    response.raise_for_status()
    for workflow in _unwrap_list(response):
        if workflow.get("name") == name:
            workflow_id = workflow.get("id")
            if workflow_id:
                return str(workflow_id)
    return None


def sync_workflow(
    path: Path | None = None,
    *,
    workflow_id: str | None = None,
    activate: bool | None = None,
) -> dict[str, Any]:
    workflow = load_workflow(path)
    payload = prepare_api_payload(workflow)
    target_id = (workflow_id or N8N_WORKFLOW_ID or "").strip() or None
    should_activate = workflow.get("active", False) if activate is None else activate

    with httpx.Client(base_url=N8N_BASE_URL, headers=_headers(), timeout=60.0) as client:
        if target_id:
            response = client.put(f"/workflows/{target_id}", json=payload)
            response.raise_for_status()
            action = "updated"
            saved = _unwrap_workflow(response)
        else:
            existing_id = find_workflow_id(client, payload["name"])
            if existing_id:
                response = client.put(f"/workflows/{existing_id}", json=payload)
                response.raise_for_status()
                action = "updated"
                saved = _unwrap_workflow(response)
            else:
                response = client.post("/workflows", json=payload)
                response.raise_for_status()
                action = "created"
                saved = _unwrap_workflow(response)

        saved_id = str(saved["id"])
        if should_activate and not saved.get("active"):
            activate_response = client.post(f"/workflows/{saved_id}/activate")
            activate_response.raise_for_status()
            saved = _unwrap_workflow(activate_response)

    return {
        "action": action,
        "workflow_id": saved_id,
        "name": saved.get("name", payload["name"]),
        "active": bool(saved.get("active")),
        "editor_url_hint": f"{N8N_BASE_URL.removesuffix('/api/v1')}/workflow/{saved_id}",
    }
