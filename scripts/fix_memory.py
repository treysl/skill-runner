"""Fix memory measurement to use the LISTENING uvicorn worker."""
from __future__ import annotations

import json
import re
from pathlib import Path

import psutil

OUT = Path(__file__).resolve().parents[1] / "outputs"
data_path = OUT / "performance-eval.json"
data = json.loads(data_path.read_text(encoding="utf-8"))

# Prefer process listening on 8787
listen_pid = None
for conn in psutil.net_connections(kind="inet"):
    if conn.laddr and conn.laddr.port == 8787 and conn.status == psutil.CONN_LISTEN:
        listen_pid = conn.pid
        break

if listen_pid is None:
    raise SystemExit("No LISTENING process on :8787")

proc = psutil.Process(listen_pid)
info = proc.memory_info()
parent_rss = None
parent_pid = proc.ppid()
try:
    parent_rss = round(psutil.Process(parent_pid).memory_info().rss / (1024 * 1024), 2)
except (psutil.NoSuchProcess, psutil.AccessDenied):
    parent_pid = None

rss_mb = round(info.rss / (1024 * 1024), 2)
data["memory"] = {
    "pid": listen_pid,
    "name": proc.name(),
    "role": "uvicorn worker (LISTENING :8787)",
    "rss_mb": rss_mb,
    "vms_mb": round(info.vms / (1024 * 1024), 2),
    "parent_pid": parent_pid,
    "parent_rss_mb": parent_rss,
    "total_rss_mb": round(rss_mb + (parent_rss or 0), 2),
}
data_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

txt_path = OUT / "performance-eval.txt"
txt = txt_path.read_text(encoding="utf-8")
replacement = (
    f"Memory footprint (server RSS): {rss_mb} MB "
    f"(pid={listen_pid}; total w/ parent {data['memory']['total_rss_mb']} MB)"
)
txt2 = re.sub(r"Memory footprint.*", replacement, txt)
txt_path.write_text(txt2, encoding="utf-8")
print(json.dumps(data["memory"], indent=2))
