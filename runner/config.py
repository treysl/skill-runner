from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

SKILL_PACKAGE = Path(
    os.getenv("SKILL_PACKAGE", ROOT / "skills" / "cip-report-06-03-26-tl.skill")
).expanduser()
SKILL_CACHE_DIR = Path(
    os.getenv("SKILL_CACHE_DIR", ROOT / ".runner-cache" / "cip-report-06-03-26-tl")
).expanduser()

DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data")).expanduser()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", ROOT / "outputs")).expanduser()
OUTPUT_FILENAME_PREFIX = (
    os.getenv("OUTPUT_FILENAME_PREFIX", "CIP_Report").strip() or "CIP_Report"
)
LOGO_PATH = os.getenv("LOGO_PATH", "").strip() or None

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

RUNNER_HOST = os.getenv("RUNNER_HOST", "127.0.0.1")
RUNNER_PORT = int(os.getenv("RUNNER_PORT", "8787"))

DEFAULT_CLIENT_NAME = os.getenv("DEFAULT_CLIENT_NAME", "Client")
DEFAULT_USER = os.getenv("DEFAULT_USER", "n8n")

N8N_API_KEY = os.getenv("N8N_API_KEY", "").strip()
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "http://127.0.0.1:5678/api/v1").rstrip("/")
N8N_WORKFLOW_ID = os.getenv("N8N_WORKFLOW_ID", "").strip()

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_skill_dir() -> Path:
    from runner.skill_loader import ensure_skill_extracted

    return ensure_skill_extracted(SKILL_PACKAGE, SKILL_CACHE_DIR)


def get_build_script() -> Path:
    return get_skill_dir() / "scripts" / "build_cip_report.py"


def get_skill_md() -> Path:
    return get_skill_dir() / "SKILL.md"
