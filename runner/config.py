from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "cip-report-06-03-26-tl"
BUILD_SCRIPT = SKILL_DIR / "scripts" / "build_cip_report.py"
SKILL_MD = SKILL_DIR / "SKILL.md"

DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data")).expanduser()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", ROOT / "outputs")).expanduser()
LOGO_PATH = os.getenv("LOGO_PATH", "").strip() or None

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

RUNNER_HOST = os.getenv("RUNNER_HOST", "127.0.0.1")
RUNNER_PORT = int(os.getenv("RUNNER_PORT", "8787"))

DEFAULT_CLIENT_NAME = os.getenv("DEFAULT_CLIENT_NAME", "Client")
DEFAULT_USER = os.getenv("DEFAULT_USER", "n8n")

DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
