from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from runner.build import run_build
from runner.config import DATA_DIR, DEFAULT_CLIENT_NAME, DEFAULT_USER
from runner.inspect import find_input_file, inspect_export
from runner.orchestrate import orchestrate_build_config


class RunRequest(BaseModel):
    filename: str | None = Field(
        default=None,
        description="Aspire export filename inside DATA_DIR. Uses newest .xlsx if omitted.",
    )
    client_name: str | None = None
    user: str | None = None
    overrides: dict[str, Any] = Field(default_factory=dict)


class InspectRequest(BaseModel):
    filename: str | None = None


class BuildRequest(BaseModel):
    filename: str | None = None
    config: dict[str, Any]


async def run_pipeline(
    *,
    filename: str | None = None,
    client_name: str | None = None,
    user: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    input_file = find_input_file(DATA_DIR, filename)
    inspection = inspect_export(input_file)
    config = await orchestrate_build_config(
        inspection,
        client_name=client_name or DEFAULT_CLIENT_NAME,
        user=user or DEFAULT_USER,
        overrides=overrides or {},
    )
    build_result = run_build(config, input_file)
    return {
        "input_file": str(input_file.resolve()),
        "inspection": inspection.to_dict(),
        "config": config,
        "build": build_result,
    }
