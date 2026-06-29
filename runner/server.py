from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from runner.config import DATA_DIR, OUTPUT_DIR, RUNNER_HOST, RUNNER_PORT, SKILL_PACKAGE, get_skill_dir
from runner.inspect import find_input_file, inspect_export
from runner.orchestrate import orchestrate_build_config
from runner.pipeline import BuildRequest, InspectRequest, RunRequest, run_pipeline


@asynccontextmanager
async def lifespan(_app: FastAPI):
    skill_dir = get_skill_dir()
    print(f"Skill ready: {SKILL_PACKAGE.name} -> {skill_dir}")
    yield


app = FastAPI(
    title="skill-runner",
    description="Local API for n8n to orchestrate CIP report skills via OpenRouter",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/data")
def list_data_files() -> dict[str, Any]:
    files = sorted(DATA_DIR.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return {
        "data_dir": str(DATA_DIR.resolve()),
        "files": [
            {
                "name": path.name,
                "path": str(path.resolve()),
                "size_bytes": path.stat().st_size,
                "modified_at": path.stat().st_mtime,
            }
            for path in files
        ],
    }


@app.post("/inspect")
def inspect(req: InspectRequest) -> dict[str, Any]:
    try:
        input_file = find_input_file(DATA_DIR, req.filename)
        return inspect_export(input_file).to_dict()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class OrchestrateRequest(BaseModel):
    filename: str | None = None
    client_name: str | None = None
    user: str | None = None
    overrides: dict[str, Any] = Field(default_factory=dict)


@app.post("/orchestrate")
async def orchestrate(req: OrchestrateRequest) -> dict[str, Any]:
    try:
        input_file = find_input_file(DATA_DIR, req.filename)
        inspection = inspect_export(input_file)
        config = await orchestrate_build_config(
            inspection,
            client_name=req.client_name or "Client",
            user=req.user or "n8n",
            overrides=req.overrides,
        )
        return {
            "input_file": str(input_file.resolve()),
            "inspection": inspection.to_dict(),
            "config": config,
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/build")
def build(req: BuildRequest) -> dict[str, Any]:
    from runner.build import run_build

    try:
        input_file = find_input_file(DATA_DIR, req.filename)
        return run_build(req.config, input_file)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/run")
async def run(req: RunRequest) -> dict[str, Any]:
    try:
        return await run_pipeline(
            filename=req.filename,
            client_name=req.client_name,
            user=req.user,
            overrides=req.overrides,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def main() -> None:
    import uvicorn

    uvicorn.run("runner.server:app", host=RUNNER_HOST, port=RUNNER_PORT, reload=False)


if __name__ == "__main__":
    main()
