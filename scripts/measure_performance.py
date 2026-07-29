"""Measure skill-runner quantitative performance metrics."""
from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8787"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


def timed_get(path: str, n: int = 30) -> dict:
    samples: list[float] = []
    status = None
    for _ in range(n):
        t1 = time.perf_counter()
        with urllib.request.urlopen(BASE + path, timeout=30) as r:
            r.read()
            status = r.status
        samples.append((time.perf_counter() - t1) * 1000)
    return {
        "path": path,
        "n": n,
        "status": status,
        "mean_ms": round(statistics.mean(samples), 3),
        "p50_ms": round(statistics.median(samples), 3),
        "p95_ms": round(sorted(samples)[int(0.95 * (n - 1))], 3),
        "min_ms": round(min(samples), 3),
        "max_ms": round(max(samples), 3),
        "samples_ms": [round(s, 3) for s in samples],
    }


def timed_post(path: str, payload: dict, n: int = 5) -> dict:
    data = json.dumps(payload).encode()
    samples: list[float] = []
    status = None
    for _ in range(n):
        req = urllib.request.Request(
            BASE + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t1 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=120) as r:
            r.read()
            status = r.status
        samples.append((time.perf_counter() - t1) * 1000)
    return {
        "path": path,
        "n": n,
        "status": status,
        "mean_ms": round(statistics.mean(samples), 3),
        "p50_ms": round(statistics.median(samples), 3),
        "p95_ms": round(sorted(samples)[max(0, int(0.95 * (n - 1)))], 3),
        "min_ms": round(min(samples), 3),
        "max_ms": round(max(samples), 3),
        "samples_ms": [round(s, 3) for s in samples],
    }


def measure_accuracy() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    out = (proc.stderr or "") + (proc.stdout or "")
    (OUT / "unit-test-results-perf.txt").write_text(out, encoding="utf-8")
    m = re.search(r"Ran (\d+) tests in ([0-9.]+)s", out)
    n_tests = int(m.group(1)) if m else 0
    suite_time = float(m.group(2)) if m else 0.0
    ok = proc.returncode == 0 and "OK" in out
    passed = n_tests if ok else 0
    return {
        "metric": "Unit test pass rate (correctness proxy)",
        "tests_run": n_tests,
        "passed": passed,
        "failures": 0 if ok else "see log",
        "errors": 0 if ok else "see log",
        "pass_rate_pct": round(100.0 * passed / n_tests, 2) if n_tests else 0.0,
        "suite_seconds": suite_time,
        "ok": ok,
    }


def measure_throughput(n_req: int = 200) -> dict:
    t0 = time.perf_counter()
    ok_count = 0
    for _ in range(n_req):
        with urllib.request.urlopen(BASE + "/health", timeout=10) as r:
            if r.status == 200:
                ok_count += 1
    elapsed = time.perf_counter() - t0
    return {
        "metric": "GET /health sequential throughput",
        "requests": n_req,
        "ok": ok_count,
        "elapsed_s": round(elapsed, 4),
        "rps": round(ok_count / elapsed, 2),
    }


def measure_memory() -> dict:
    if psutil is None:
        return {"error": "psutil not installed"}
    for p in psutil.process_iter(["pid", "name", "cmdline", "memory_info"]):
        try:
            cmd = " ".join(p.info.get("cmdline") or [])
            if "run_server.py" in cmd or ("uvicorn" in cmd and "8787" in cmd):
                info = p.memory_info()
                return {
                    "pid": p.pid,
                    "name": p.name(),
                    "rss_mb": round(info.rss / (1024 * 1024), 2),
                    "vms_mb": round(info.vms / (1024 * 1024), 2),
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {"error": "server process not found"}


def main() -> None:
    results: dict = {}
    print("Measuring accuracy (unit tests)...")
    results["accuracy"] = measure_accuracy()

    print("Measuring latency...")
    results["latency_health"] = timed_get("/health", 50)
    results["latency_data"] = timed_get("/data", 30)
    try:
        results["latency_inspect"] = timed_post("/inspect", {}, n=5)
    except Exception as exc:  # noqa: BLE001
        results["latency_inspect"] = {"error": str(exc)}

    print("Measuring throughput...")
    results["throughput"] = measure_throughput(200)

    print("Measuring memory...")
    results["memory"] = measure_memory()

    # End-to-end CIP pipeline latency from prior prototype evidence
    results["e2e_pipeline"] = {
        "metric": "Full CIP pipeline (n8n POST /run)",
        "source": "docs/images/cip-report-prototype.png",
        "latency_s": 114.352,
        "latency_display": "1m 54.352s",
        "input_rows": 6989,
        "output_size_kb_range": [3832, 3881],
        "reproducibility_runs": 5,
    }

    (OUT / "performance-eval.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    a = results["accuracy"]
    h = results["latency_health"]
    d = results["latency_data"]
    ins = results["latency_inspect"]
    th = results["throughput"]
    mem = results["memory"]
    e2e = results["e2e_pipeline"]

    lines = [
        "SKILL-RUNNER PERFORMANCE EVALUATION",
        "=" * 50,
        "",
        "1. QUANTITATIVE METRICS",
        "-" * 50,
        (
            f"Accuracy (unit test pass rate): {a['pass_rate_pct']}% "
            f"({a['passed']}/{a['tests_run']} passed)"
        ),
        f"  Suite runtime: {a['suite_seconds']}s",
        "",
        (
            f"Latency GET /health (n={h['n']}): mean={h['mean_ms']} ms, "
            f"p50={h['p50_ms']} ms, p95={h['p95_ms']} ms"
        ),
        (
            f"Latency GET /data   (n={d['n']}): mean={d['mean_ms']} ms, "
            f"p50={d['p50_ms']} ms, p95={d['p95_ms']} ms"
        ),
    ]
    if "mean_ms" in ins:
        lines.append(
            f"Latency POST /inspect (n={ins['n']}): mean={ins['mean_ms']} ms, "
            f"p50={ins['p50_ms']} ms, p95={ins['p95_ms']} ms"
        )
    else:
        lines.append(f"Latency POST /inspect: {ins}")
    lines.extend(
        [
            "",
            (
                f"Throughput GET /health: {th['rps']} req/s "
                f"({th['ok']}/{th['requests']} OK in {th['elapsed_s']}s)"
            ),
            "",
        ]
    )
    if "rss_mb" in mem:
        lines.append(
            f"Memory footprint (server RSS): {mem['rss_mb']} MB (pid={mem['pid']})"
        )
    else:
        lines.append(f"Memory: {mem}")
    lines.extend(
        [
            "",
            (
                f"E2E CIP pipeline latency: {e2e['latency_display']} "
                f"({e2e['input_rows']} rows)"
            ),
            f"Reproducibility: {e2e['reproducibility_runs']} consecutive successful runs",
            "",
            "Wrote outputs/performance-eval.json",
        ]
    )
    text = "\n".join(lines)
    (OUT / "performance-eval.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
