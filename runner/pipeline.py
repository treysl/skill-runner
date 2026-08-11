from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
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
    from runner.evidence import write_failure_manifest, write_success_manifest

    started_at = datetime.now(timezone.utc)
    timer = perf_counter()
    input_file = None
    inspection_dict = None
    config = None
    try:
        input_file = find_input_file(DATA_DIR, filename)
        inspection = inspect_export(input_file)
        inspection_dict = inspection.to_dict()
        config = await orchestrate_build_config(
            inspection,
            client_name=client_name or DEFAULT_CLIENT_NAME,
            user=user or DEFAULT_USER,
            overrides=overrides or {},
        )
        build_result = run_build(config, input_file)
        manifest_file = write_success_manifest(
            input_file=input_file,
            output_file=Path(build_result["output_file"]),
            inspection=inspection_dict,
            config=config,
            started_at=started_at,
            elapsed_seconds=perf_counter() - timer,
        )
        return {
            "input_file": str(input_file.resolve()),
            "inspection": inspection_dict,
            "config": config,
            "build": build_result,
            "manifest_file": str(manifest_file.resolve()),
        }
    except Exception as exc:
        try:
            write_failure_manifest(
                started_at=started_at,
                elapsed_seconds=perf_counter() - timer,
                error=exc,
                input_file=input_file,
                inspection=inspection_dict,
                config=config,
            )
        except Exception:
            pass
        raise
