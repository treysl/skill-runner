---
name: cip-report-06-03-26-tl
description: >-
  Version 06-03-26. Builds the THG Construction In Process (CIP) Excel workbook
  from an Aspire Opportunity export with a bundled Python script. The Complete
  Overview's Non Sub Rev backs out implied sub revenue at an expected sub margin
  (default 28.1%, prompted) so heavy-sub jobs stop distorting self-performed
  margin. The Completed tab and Complete Overview use independent date windows.
  In Process tabs carry an editable in-sheet pace threshold driving dynamic
  conditional formatting on the Act/Est columns, plus a configurable Invoice %
  rule; the Dashboard shows total backlog by Division. Use whenever a user
  supplies an Aspire Opportunity export and wants CIP analysis — budget,
  invoicing, margin, labor overrun, or backlog. Triggers on "CIP report",
  "construction in process", "project tracking", "in process report",
  "opportunity report", "job costing", "percent complete report", "margin
  erosion", "backlog", or an Aspire Opportunity upload with any project
  performance request. Client-agnostic.
---
# Construction In Process (CIP) Report — Script-Backed

*Last updated: June 3, 2026*

**v06-03-26 changes (this build):**
1. **Original Opp cutoff is backend-only.** Defaults to 2024-01-01, not prompted, not shown on the disclosure tab.
2. **Two independent date windows.** Completed tab: This month / Last 30 days / YTD — always ending on the **current day** (not month-end). Complete Overview: Last calendar year / Last 12 completed months. They are set separately.
3. **GM% never highlights a not-started job** (Earned Revenue = 0) on any tab.
4. **In Process Potential Hr Overage** shows positive values only; non-positive is left blank (unscheduled hours don't imply a job will come in under).
5. **Job Status & Opp Status columns removed** from In Process, In Process By Property, and Completed (all rows are Won and already filtered by status).
6. **Invoice % highlight rule** (In Process) is configurable: flag when Invoice % is more than a chosen gap below Rev % Completed (default 10%), or flag any Invoice % above Earned.
7. **Editable dynamic pace conditional formatting** (In Process). A % threshold lives in an editable cell on row 4; the Act/Est columns turn red when `(Act/Est ratio − Rev % Completed) > threshold`. Editing the cell re-evaluates the formatting live in Excel. Columns covered: Total Act/Est Cost, Labor Hrs Act/Est, Labor $ Act/Est, Materials Act/Est, Sub Act/Est, Equip Act/Est, Other Act/Est.
8. **Column checklist** — the included columns on the In Process and Completed tabs are selectable.
9. **Dashboard: Total Backlog by Division** — all open jobs incl. below-threshold. Backlog $ = Σ(Est Rev − Earned Rev); Backlog Hours = Σ max(Est Hours − Act Hours, 0) (over-budget jobs don't offset).
10. **Dashboard alignment** — $ right, hours left, % center.
11. **Completed tab** — removed the blue not-started highlight and the orange ≥100% highlight (a completed job can't be not-started, and all should be ~100%).
12. **Completed Dashboard View** — waterfall chart anchored to cell A4.
13. **Table tab reordered** — Opp #, Revision #, Property Name lead; then a report-like order; remaining source columns at the end. Values are unchanged, only column order.
14. **Complete Overview Non Sub Rev** = `Earned Revenue − (Act Sub Cost ÷ (1 − sub_margin))`, sub margin prompted (default 28.1%).

## Overview

A canonical Python build script produces a 9-tab THG-branded workbook from one Aspire Opportunity export.

| Tab | Purpose |
|-----|---------|
| **Proprietary Disclosure** | Logo, confidentiality, filters + window labels + sub margin assumption, purpose |
| **Dashboard** | Total Backlog by Division, Top 5, Budget Overruns, Cash Flow Risks, Labor Concerns |
| **In Process** | Detail by Opp #; editable pace threshold (row 4) drives dynamic Act/Est CF |
| **In Process By Property** | Property-level rollup of IP jobs; same dynamic CF |
| **Completed** | Jobs completed in the Completed-tab window (to current day) |
| **Completed Dashboard View** | GP waterfall chart anchored at A4 + Branch×Division pivot |
| **Complete Overview** | GM Range + Revenue Range analysis over the Overview window; sub-margin-adjusted Non Sub Rev |
| **Table** | Reordered source data (Opp #, Revision #, Property first) for verification |
| **Version History** | Append-only Date/User/Change log |

## Required Input

**Single Aspire Opportunity export** (.xlsx).

**Required (build fails if missing):** Branch, Opportunity #, Property Name, Division, Invoice Type, Opportunity Name, Opportunity Type, Revision #, Job Status, Won Date, Revenue Estimated, Earned Revenue, Invoiced Revenue, Labor Hours Actual, Labor Hours Estimated, Labor Cost Actual, Labor Cost Estimated, Material Cost Actual, Material Cost Estimated, Sub Cost Actual, Sub Cost Estimated, Equipment Cost Actual, Equipment Cost Estimated, Other Cost Actual, Other Cost Estimated.

**Optional (display only):** Master Opportunity Name, Future Scheduled Hours, Company Name, Sales Rep, Operations Mgr Name, Start Date, Opportunity Status Name, Oppty Complete Date.

---

## Pre-Flight Checks — HARD GATE

**Do NOT run until every applicable question is answered.** Present questions in batches via `ask_user_input_v0` (max 3 per call). Inspect the data first: read headers and unique Branch / Division / Job Status / Opportunity Status Name values with row counts. If Job Status values don't clearly map to "In P…" / "Complete", show them and confirm the mapping.

**Round 1** (2): 1) Branch (multi-select, row counts, "All"); 2) Division (multi-select, ≥1 required).

**Round 2** (3):
3) **Completed-tab window** (single): This month *(default)*, Last 30 days, YTD. Always ends on the current day. → `--completed-range`.
4) **Complete Overview window** (single): Last 12 completed months *(default)*, Last calendar year. → `--overview-range`. *(Explain this is intentionally separate from the Completed-tab window.)*
5) **Minimum Estimated Revenue** (single): Greater than $0 *(default)*, Greater than $10,000, Custom. → `--min-est-revenue`. *(Note: the Dashboard backlog-by-division table ignores this filter by design.)*

**Round 3** (3):
6) **Expected sub margin (Complete Overview)** (single). Ask exactly: *"What expected sub margin should the Complete Overview use to isolate self-performed margin? Jobs with heavy subcontractor spend can skew overall margin. The Non Sub Rev column pulls that sub influence out by backing implied sub revenue out of the top line at the expected sub margin, so the residual margin reflects only self-performed work. Formula: Non Sub Rev = Earned Revenue − (Act Sub Cost ÷ (1 − sub_margin))."* Options: 28.1% *(default)*, 25%, 30%, Custom. → `--sub-margin` (decimal).
7) **Invoice % highlight (In Process)** (single): "More than 10% below Earned" *(default)*, "Any Invoice % above Earned", "Custom gap". → `--invoice-flag-rule` (lag/over) + `--invoice-flag-gap`.
8) **Act/Est pace threshold (In Process)** (single). Ask: *"On the In Process tabs, how far an Act/Est column may run ahead of Rev % Completed before it flags red. This value is written to an editable cell on row 4 — you can change it live in Excel and the formatting updates."* Options: 0% *(default — flags whenever a column outpaces Rev % Completed)*, 5%, 10%, Custom. → `--cost-pace-threshold` (decimal).

**Round 4** (up to 3):
9) **In Process columns** (multi-select by group, default all): Identifiers (Opp #, Property, Opp Name, Company, Sales Rep, Ops Mgr, Start Date), Revenue (Earned/Est/Invoiced), Hours (Act/Est/Future Sched/Act+Sched/Potential Overage/Remain), Cost detail (Act/Est by category + Act Cost $/Est Cost $), Ratios (GM%, Rev %, Invoice %, all Act/Est), Backlog/Other (Subs/Mat Remain, Backlog, Note, Year-Month). Map the chosen groups to a pipe-delimited header list → `--ip-columns` (and `--bp-columns` for By Property where applicable).
10) **Completed columns** (multi-select by group, default all) → `--comp-columns`.
11) **Complete Overview buckets** — confirm default GM/Revenue buckets or customize.

*Change orders: included by the backend default (cutoff 2024-01-01). Do NOT prompt. Only pass `--original-opp-cutoff` if the user explicitly asks to zero estimated costs for change orders whose original opp predates a date.*

After answers, echo confirmed settings (branches, divisions, both windows, min rev, sub margin, invoice rule, pace threshold, column selections) and report filtered counts before building.

---

## How to Run

1. Read `/mnt/skills/public/xlsx/SKILL.md` and the THG brand guidelines skill.
2. Copy script + logo:
```bash
cp /mnt/skills/user/cip-report-06-03-26-tl/scripts/build_cip_report.py /home/claude/build_cip_report.py
cp /mnt/skills/organization/thg-brand-guidelines/thg-logo.png /home/claude/thg-logo.png
```
3. Install deps if needed: `pip install pytz Pillow matplotlib --break-system-packages -q`
4. Run:
```bash
python3 /home/claude/build_cip_report.py <input> <output> [options]
```

**CLI Options:**

| Flag | Required | Description |
|------|----------|-------------|
| `--client-name NAME` | Yes | Client display name |
| `--division DIV` | Yes | Division filter (repeatable) |
| `--branch BRANCH` | No | Branch filter (repeatable; omit for all) |
| `--completed-range {this_month,last_30_days,ytd}` | No | Completed-tab window (to current day). Default this_month |
| `--completed-start DATE` / `--completed-end DATE` | No | Custom Completed-tab window (override) |
| `--overview-range {last_year,last_12_complete_months}` | No | Complete Overview window. Default last_12_complete_months |
| `--min-est-revenue AMOUNT` | No | Min Revenue Estimated (default 0). Backlog-by-division ignores this |
| `--sub-margin DEC` | No | Expected sub margin for Non Sub Rev (default 0.281) |
| `--invoice-flag-rule {lag,over}` | No | In Process Invoice % highlight (default lag) |
| `--invoice-flag-gap DEC` | No | Gap below Rev % Completed for lag rule (default 0.10) |
| `--cost-pace-threshold DEC` | No | Initial row-4 editable pace threshold (default 0.0) |
| `--ip-columns "H1\|H2"` | No | In Process columns to include (omit for all) |
| `--bp-columns "H1\|H2"` | No | In Process By Property columns (omit for all) |
| `--comp-columns "H1\|H2"` | No | Completed columns (omit for all) |
| `--original-opp-cutoff DATE` | No | **Backend.** Default 2024-01-01. Not prompted/shown |
| `--user NAME` / `--change-note NOTE` | No | Version History entry |
| `--logo PATH` / `--no-logo` | No | Logo control |

**Example:**
```bash
python3 /home/claude/build_cip_report.py \
  "/mnt/user-data/uploads/Client_Opportunity.xlsx" \
  "/home/claude/Client_CIP_Report.xlsx" \
  --client-name "Client Name" \
  --division "Construction" --division "Enhancement" \
  --completed-range this_month --overview-range last_12_complete_months \
  --min-est-revenue 0 --sub-margin 0.281 \
  --invoice-flag-rule lag --invoice-flag-gap 0.10 \
  --cost-pace-threshold 0.05 \
  --user "Trey" --change-note "Initial CIP build (v06-03-26)" \
  --logo "/home/claude/thg-logo.png"
```

5. **Verify:** stdout prints both window ranges and `RECONCILIATION PASSED`; IP Earned ties detail↔Dashboard; exit code 0.
6. **Deliver:** copy to `/mnt/user-data/outputs/{ClientName}_CIP_Report.xlsx`, `present_files`, and include the AI validation disclaimer (Standard 6):

> "Please note: this report was generated by AI and should be validated before use. While the calculations and formatting follow a tested template, AI can occasionally make mistakes with formatting, formulas, or data output. I recommend spot-checking key totals against your source data before distributing."

---

## What the Script Does

**Pipeline:** Opp Master (Work Order, non-Canceled, valid Revision #, non-T&M; fills blank Master Opp Name) → Data Queries (Work Order, non-T&M, Original Opp flag via 2024-01-01 cutoff, Won filter, Division/Branch filters, join, group by Opp # / Property). Completed rows are windowed twice — once for the Completed tab (to current day) and once for the Complete Overview — and a pre-threshold In Process copy is retained for the Dashboard backlog table.

**Key formulas:** Act Cost $ / Estimated Cost $ = Σ of 5 components; Actual GM% = (Earned − Act Cost)/Earned; Rev % Completed = Earned/Est Rev; Backlog $ = Est Rev − Earned; Potential Hr Overage = max((Act + Future Sched) − Est Hours, 0) else blank; all ratios use safe division.

**Complete Overview Non Sub columns:** Non Sub Costs = Act Cost − Act Sub Cost; **Non Sub Rev = Earned Revenue − (Act Sub Cost ÷ (1 − sub_margin))**; Non Sub GM = (Non Sub Rev − Non Sub Costs) ÷ Non Sub Rev.

**Dashboard Backlog by Division:** over ALL open (In Process) jobs incl. below the revenue threshold; Backlog $ = Σ(Est Rev − Earned); Backlog Hours = Σ max(Est Hrs − Act Hrs, 0).

### Conditional Formatting

| Tab(s) | Column | Condition | Result |
|--------|--------|-----------|--------|
| All | Actual GM% | Act < Est (skip if not started) | Red #F4CCCC |
| All | Actual GM% | Act > Est AND Act > 0% (skip if not started) | Green #C6EFCE |
| In Process | Rev % Completed | ≥ 100% | Orange #F4B084 |
| In Process | Invoice % | lag: >gap below Rev%; or over: > Earned | Yellow #FFF2CC |
| In Process | Act/Est columns | `(ratio − Rev % Completed) > row-4 threshold` (dynamic, editable) | Red #F4CCCC |
| In Process | Property Name | Earned = 0 (not started) | Blue #BDD7EE |
| Completed | Act/Est columns | > 100% (static) | Red #F4CCCC |

Completed tab: no orange, no blue.

### Freeze Panes / Grand Total
In Process freeze D6 (through Opp Name); By Property B6; Completed C6. Grand Total in row 3 uses SUBTOTAL formulas; Potential Hr Overage grand total is blank when not positive; ratios/GM% reference row-3 subtotal cells with IFERROR `"-"`.

---

## Standards Compliance

| Standard | Status | Notes |
|----------|--------|-------|
| 1. Pre-Flight | ✅ | Branch/Division/windows/min rev/sub margin/invoice rule/pace/columns/buckets |
| 2. Safe Division | ✅ | safe_div() everywhere incl. implied sub revenue |
| 3. Formula Recalc | ✅ | Grand Total SUBTOTAL + dynamic CF recalc on open |
| 4. Post-Build Recon | ✅ | Row counts + Earned tie-out + both window ranges to stdout |
| 5. THG Branding | ✅ | Logo/colors/fonts per guidelines |
| 6. AI Disclaimer | ✅ | Delivered in chat |
| 7. Escalation | ✅ | Troubleshooting ends with "escalate to Trey" |
| 8. Script-Backed | ✅ | Canonical script in `scripts/` |
| 9. Version History | ✅ | Append-only tab |

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| Missing required column | Script errors and exits; check names |
| `sub_margin` ≥ 1 | Invalid; safe_div returns 0 for that bucket — restate with user |
| Pace CF not firing | Confirm Rev % Completed column is included; the threshold cell is on row 4 of the first Act/Est column |
| No In Process / Completed rows | Empty tabs; noted in stdout |
| User wants change orders excluded | Pass `--original-opp-cutoff YYYY-MM-DD` |
| Completed tab empty but jobs exist | Check the Completed-tab window (this_month is narrow); try YTD |
| Reconciliation fails | Exits non-zero; investigate before delivering |

If issues persist, escalate to Trey.

## Editing the Spec
Edit `scripts/build_cip_report.py`. Key sections: constants/fills/fonts (~line 55); `resolve_completed_window` / `resolve_overview_window`; `build_data_queries`; column specs IP_COLS/BP_COLS/COMP_COLS; `build_data_tab` (row-4 threshold + dynamic CF + per-cell fills); `build_dashboard` (backlog by division); `compute_bucket_row` / `build_complete_overview` (Non Sub Rev); `build_completed_dashboard_view` (A4 chart); `build_table_tab` (column reorder); `run_reconciliation`.
