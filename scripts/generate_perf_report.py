"""Generate HTML performance report + latency chart for screenshots."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
DOCS = ROOT / "docs" / "images"
DOCS.mkdir(parents=True, exist_ok=True)

data = json.loads((OUT / "performance-eval.json").read_text(encoding="utf-8"))

# --- Chart via matplotlib ---
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

labels = ["GET /health\nmean", "GET /data\nmean", "POST /inspect\nmean"]
values = [
    data["latency_health"]["mean_ms"],
    data["latency_data"]["mean_ms"],
    data["latency_inspect"]["mean_ms"],
]

fig, ax = plt.subplots(figsize=(8, 4.5))
bars = ax.bar(labels, values, color=["#2f6fed", "#2f6fed", "#c45c26"])
ax.set_ylabel("Latency (ms)")
ax.set_title("API endpoint mean latency (skill-runner @ 127.0.0.1:8787)")
ax.set_yscale("log")
for bar, val in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val * 1.15,
        f"{val:.1f} ms",
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
chart_path = DOCS / "perf-latency-chart.png"
fig.savefig(chart_path, dpi=140)
plt.close(fig)

# Second chart: summary KPIs normalized for display (accuracy %, throughput/10, memory/10, e2e seconds)
fig2, ax2 = plt.subplots(figsize=(8, 4.5))
kpi_labels = [
    "Accuracy\n(%)",
    "Throughput\n(req/s)",
    "Memory RSS\n(MB)",
    "E2E pipeline\n(s)",
]
kpi_values = [
    data["accuracy"]["pass_rate_pct"],
    data["throughput"]["rps"],
    data["memory"]["rss_mb"],
    data["e2e_pipeline"]["latency_s"],
]
colors = ["#1a7f37", "#2f6fed", "#8250df", "#c45c26"]
bars2 = ax2.bar(kpi_labels, kpi_values, color=colors)
ax2.set_ylabel("Measured value")
ax2.set_title("Quantitative performance indicators — skill-runner")
for bar, val in zip(bars2, kpi_values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        val,
        f"{val:g}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
fig2.tight_layout()
kpi_path = DOCS / "perf-kpi-chart.png"
fig2.savefig(kpi_path, dpi=140)
plt.close(fig2)

a = data["accuracy"]
h = data["latency_health"]
d = data["latency_data"]
ins = data["latency_inspect"]
th = data["throughput"]
mem = data["memory"]
e2e = data["e2e_pipeline"]

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>skill-runner Performance Evaluation</title>
  <style>
    body {{ font-family: Segoe UI, sans-serif; margin: 32px; color: #1f2328; background: #fff; }}
    h1 {{ font-size: 22px; margin: 0 0 8px; }}
    h2 {{ font-size: 16px; margin: 28px 0 10px; border-bottom: 1px solid #d0d7de; padding-bottom: 6px; }}
    .meta {{ color: #656d76; font-size: 13px; margin-bottom: 20px; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
    th, td {{ border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; }}
    th {{ background: #f6f8fa; }}
    .ok {{ color: #1a7f37; font-weight: 600; }}
    .cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 16px 0; }}
    .card {{ border: 1px solid #d0d7de; border-radius: 6px; padding: 12px 14px; min-width: 140px; }}
    .card .label {{ font-size: 11px; color: #656d76; text-transform: uppercase; }}
    .card .value {{ font-size: 22px; font-weight: 650; margin-top: 4px; }}
    img.chart {{ max-width: 100%; border: 1px solid #d0d7de; border-radius: 6px; }}
    .note {{ font-size: 12px; color: #656d76; margin-top: 8px; }}
  </style>
</head>
<body>
  <h1>skill-runner Performance Evaluation</h1>
  <div class="meta">Measured 2026-07-28 against localhost:8787 · Unit tests + API timing + process RSS · E2E from n8n prototype run</div>

  <div class="cards">
    <div class="card"><div class="label">Accuracy</div><div class="value ok">{a['pass_rate_pct']}%</div></div>
    <div class="card"><div class="label">Health latency</div><div class="value">{h['mean_ms']:.1f} ms</div></div>
    <div class="card"><div class="label">Throughput</div><div class="value">{th['rps']} rps</div></div>
    <div class="card"><div class="label">Memory RSS</div><div class="value">{mem['rss_mb']} MB</div></div>
    <div class="card"><div class="label">E2E CIP run</div><div class="value">{e2e['latency_display']}</div></div>
  </div>

  <h2>1. Quantitative results table</h2>
  <table>
    <thead>
      <tr><th>Metric</th><th>Type</th><th>Result</th><th>Method / notes</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>Accuracy (unit test pass rate)</td>
        <td>Quantitative</td>
        <td class="ok">{a['pass_rate_pct']}% ({a['passed']}/{a['tests_run']})</td>
        <td>unittest discover — {a['suite_seconds']}s suite</td>
      </tr>
      <tr>
        <td>Latency GET /health</td>
        <td>Quantitative</td>
        <td>mean {h['mean_ms']} ms · p50 {h['p50_ms']} · p95 {h['p95_ms']}</td>
        <td>n={h['n']} sequential requests</td>
      </tr>
      <tr>
        <td>Latency GET /data</td>
        <td>Quantitative</td>
        <td>mean {d['mean_ms']} ms · p50 {d['p50_ms']} · p95 {d['p95_ms']}</td>
        <td>n={d['n']} sequential requests</td>
      </tr>
      <tr>
        <td>Latency POST /inspect</td>
        <td>Quantitative</td>
        <td>mean {ins['mean_ms']} ms · p50 {ins['p50_ms']}</td>
        <td>n={ins['n']} — Excel parse dominates</td>
      </tr>
      <tr>
        <td>Throughput GET /health</td>
        <td>Quantitative</td>
        <td>{th['rps']} req/s ({th['ok']}/{th['requests']} OK)</td>
        <td>Sequential client, {th['elapsed_s']}s window</td>
      </tr>
      <tr>
        <td>Memory footprint (RSS)</td>
        <td>Quantitative</td>
        <td>{mem['rss_mb']} MB (pid {mem['pid']})</td>
        <td>Uvicorn worker listening on :8787</td>
      </tr>
      <tr>
        <td>E2E CIP pipeline latency</td>
        <td>Quantitative</td>
        <td>{e2e['latency_display']} for {e2e['input_rows']} rows</td>
        <td>n8n POST /run prototype evidence</td>
      </tr>
      <tr>
        <td>Interface usability / clarity</td>
        <td>Qualitative</td>
        <td>High — clear success path, reasoning field, named outputs</td>
        <td>n8n canvas + FastAPI /docs + CLI orchestration output</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Latency visualization (log scale)</h2>
  <img class="chart" src="perf-latency-chart.png" alt="Latency bar chart" />
  <p class="note">Source: scripts/measure_performance.py · health/data ~12 ms mean; inspect ~3.3 s (workbook I/O).</p>

  <h2>3. KPI overview</h2>
  <img class="chart" src="perf-kpi-chart.png" alt="KPI bar chart" />

  <h2>4. Brief interpretation</h2>
  <p>
    The runner is healthy and responsive for control-plane endpoints (~12 ms, ~126 req/s) with a modest
    ~{mem['rss_mb']} MB resident footprint. Correctness checks passed completely (18/18). Workbook inspection
    (~3.3 s) and full CIP generation (~1m 54s for ~7k rows) dominate end-user wait time — expected for Excel
    ETL rather than API overhead. Qualitatively, operators get a readable n8n success path and explicit
    orchestration reasoning, supporting trust and handoff clarity.
  </p>
</body>
</html>
"""

# Write HTML next to charts so relative image paths work when opened from docs/images
report_docs = DOCS / "performance-evaluation.html"
report_docs.write_text(html, encoding="utf-8")
# Also copy charts already written to DOCS; write a copy under outputs for convenience
(OUT / "performance-evaluation.html").write_text(
    html.replace('src="perf-latency-chart.png"', 'src="../docs/images/perf-latency-chart.png"')
    .replace('src="perf-kpi-chart.png"', 'src="../docs/images/perf-kpi-chart.png"'),
    encoding="utf-8",
)
print(f"Wrote {chart_path}")
print(f"Wrote {kpi_path}")
print(f"Wrote {report_docs}")
