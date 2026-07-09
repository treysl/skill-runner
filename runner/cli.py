from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from runner.config import DATA_DIR, DEFAULT_CLIENT_NAME, DEFAULT_USER
from runner.inspect import find_input_file, inspect_export
from runner.n8n_sync import DEFAULT_WORKFLOW_PATH, sync_workflow
from runner.orchestrate import orchestrate_build_config
from runner.pipeline import run_pipeline


def _cmd_inspect(args: argparse.Namespace) -> int:
    input_file = find_input_file(DATA_DIR, args.filename)
    inspection = inspect_export(input_file)
    print(json.dumps(inspection.to_dict(), indent=2))
    return 0


def _cmd_orchestrate(args: argparse.Namespace) -> int:
    input_file = find_input_file(DATA_DIR, args.filename)
    inspection = inspect_export(input_file)
    overrides = json.loads(args.overrides) if args.overrides else {}
    config = asyncio.run(
        orchestrate_build_config(
            inspection,
            client_name=args.client_name or DEFAULT_CLIENT_NAME,
            user=args.user or DEFAULT_USER,
            overrides=overrides,
        )
    )
    print(json.dumps(config, indent=2))
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    overrides = json.loads(args.overrides) if args.overrides else {}
    result = asyncio.run(
        run_pipeline(
            filename=args.filename,
            client_name=args.client_name,
            user=args.user,
            overrides=overrides,
        )
    )
    print(json.dumps(result, indent=2))
    return 0 if result["build"]["success"] else 1


def _cmd_n8n_sync(args: argparse.Namespace) -> int:
    result = sync_workflow(
        Path(args.file) if args.file else None,
        workflow_id=args.workflow_id,
        activate=args.activate,
    )
    print(json.dumps(result, indent=2))
    if result["action"] == "created":
        print(
            "\nTip: add N8N_WORKFLOW_ID to .env for faster future syncs.",
            file=sys.stderr,
        )
    return 0


def _cmd_install(_args: argparse.Namespace) -> int:
    from runner.config import SKILL_PACKAGE, get_build_script, get_skill_dir, get_skill_md

    skill_dir = get_skill_dir()
    print(
        json.dumps(
            {
                "skill_package": str(SKILL_PACKAGE.resolve()),
                "skill_dir": str(skill_dir.resolve()),
                "skill_md": str(get_skill_md().resolve()),
                "build_script": str(get_build_script().resolve()),
            },
            indent=2,
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="skill-runner CLI for CIP report pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect", help="Inspect newest or named Aspire export")
    inspect_parser.add_argument("--filename", help="File inside DATA_DIR")
    inspect_parser.set_defaults(func=_cmd_inspect)

    orchestrate_parser = sub.add_parser("orchestrate", help="Use OpenRouter to choose build settings")
    orchestrate_parser.add_argument("--filename")
    orchestrate_parser.add_argument("--client-name")
    orchestrate_parser.add_argument("--user")
    orchestrate_parser.add_argument("--overrides", help="JSON object of build overrides")
    orchestrate_parser.set_defaults(func=_cmd_orchestrate)

    run_parser = sub.add_parser("run", help="Inspect, orchestrate, and build the CIP report")
    run_parser.add_argument("--filename")
    run_parser.add_argument("--client-name")
    run_parser.add_argument("--user")
    run_parser.add_argument("--overrides", help="JSON object of build overrides")
    run_parser.set_defaults(func=_cmd_run)

    install_parser = sub.add_parser("install", help="Extract the packaged .skill file to cache")
    install_parser.set_defaults(func=_cmd_install)

    n8n_sync_parser = sub.add_parser(
        "n8n-sync",
        help="Push n8n/cip-report-pipeline.json to your n8n instance via API",
    )
    n8n_sync_parser.add_argument(
        "--file",
        help=f"Workflow JSON to upload (default: {DEFAULT_WORKFLOW_PATH})",
    )
    n8n_sync_parser.add_argument(
        "--workflow-id",
        help="n8n workflow ID to update (overrides N8N_WORKFLOW_ID)",
    )
    n8n_sync_parser.add_argument(
        "--activate",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Activate the workflow after sync (default: follow JSON active flag)",
    )
    n8n_sync_parser.set_defaults(func=_cmd_n8n_sync)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - CLI should surface any pipeline error
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
