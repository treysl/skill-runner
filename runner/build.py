from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from runner.config import (
    DEFAULT_CLIENT_NAME,
    DEFAULT_USER,
    LOGO_PATH,
    OUTPUT_DIR,
    OUTPUT_FILENAME_PREFIX,
    get_build_script,
)


def _safe_name(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_", " ") else "_" for ch in value)
    return cleaned.strip().replace(" ", "_") or "Client"


def build_output_path() -> Path:
    from datetime import datetime

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{_safe_name(OUTPUT_FILENAME_PREFIX)}_{stamp}.xlsx"
    return OUTPUT_DIR / filename


def config_to_cli_args(
    config: dict[str, Any], input_file: Path, output_file: Path, build_script: Path
) -> list[str]:
    args = [
        sys.executable,
        str(build_script),
        str(input_file),
        str(output_file),
        "--client-name",
        str(config.get("client_name", DEFAULT_CLIENT_NAME)),
    ]

    branches = config.get("branches") or []
    for branch in branches:
        args.extend(["--branch", str(branch)])

    divisions = config.get("divisions") or []
    if not divisions:
        raise ValueError("At least one division is required")
    for division in divisions:
        args.extend(["--division", str(division)])

    args.extend(["--completed-range", str(config.get("completed_range", "this_month"))])
    args.extend(["--overview-range", str(config.get("overview_range", "last_12_complete_months"))])
    args.extend(["--min-est-revenue", str(config.get("min_est_revenue", 0))])
    args.extend(["--sub-margin", str(config.get("sub_margin", 0.281))])
    args.extend(["--invoice-flag-rule", str(config.get("invoice_flag_rule", "lag"))])
    args.extend(["--invoice-flag-gap", str(config.get("invoice_flag_gap", 0.10))])
    args.extend(["--cost-pace-threshold", str(config.get("cost_pace_threshold", 0.0))])
    args.extend(["--user", str(config.get("user", DEFAULT_USER))])
    args.extend(["--change-note", str(config.get("change_note", "Generated via skill-runner"))])

    if LOGO_PATH and Path(LOGO_PATH).exists():
        args.extend(["--logo", LOGO_PATH])
    else:
        args.append("--no-logo")

    return args


def run_build(config: dict[str, Any], input_file: Path, output_file: Path | None = None) -> dict[str, Any]:
    build_script = get_build_script()
    if not build_script.exists():
        raise FileNotFoundError(f"Build script not found: {build_script}")

    output_path = output_file or build_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = config_to_cli_args(config, input_file, output_path, build_script)
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    result = {
        "success": completed.returncode == 0,
        "exit_code": completed.returncode,
        "output_file": str(output_path.resolve()),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": cmd,
    }
    if completed.returncode != 0:
        raise RuntimeError(
            "CIP build failed\n"
            f"exit_code={completed.returncode}\n"
            f"stderr={completed.stderr}\n"
            f"stdout={completed.stdout}"
        )
    return result
