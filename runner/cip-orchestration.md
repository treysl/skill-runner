# CIP Report — skill-runner orchestration defaults

These instructions apply when **skill-runner** (n8n / OpenRouter pipeline) chooses build parameters automatically. They **override** the interactive skill defaults in `SKILL.md` where noted below.

## Runtime config

Edit the JSON below to change pipeline defaults. No code changes or server restart required — this file is read on every run.

```json
{
  "divisions": ["Construction"]
}
```

## Pipeline defaults (use unless `requested_overrides` says otherwise)

| Setting | Pipeline default | Maps to |
|---------|------------------|---------|
| **Completed-tab window** | **YTD** (year to date) | `"completed_range": "ytd"` |
| Complete Overview window | Last 12 completed months | `"overview_range": "last_12_complete_months"` |
| **Divisions** | **Construction only** (see Runtime config JSON above) | `"divisions": ["Construction"]` |
| Branches | All (no branch filter) | `"branches": []` |
| Minimum estimated revenue | $0 | `"min_est_revenue": 0` |
| Expected sub margin | 28.1% | `"sub_margin": 0.281` |
| Invoice % highlight | More than 10% below Rev % Completed | `"invoice_flag_rule": "lag"`, `"invoice_flag_gap": 0.10` |
| Act/Est pace threshold | 0% | `"cost_pace_threshold": 0.0` |
| Column selection | All columns (omit `ip_columns`, `bp_columns`, `comp_columns`) | — |

## Completed-tab window — important

- **Default to `ytd`**, not `this_month`, even though the interactive skill lists "This month" as its default for manual runs.
- YTD means jobs whose **`Oppty Complete Date`** falls from **January 1 of the current calendar year through today** (inclusive). The build script ends the window on the current day, not month-end.
- Only choose `this_month` or `last_30_days` when `requested_overrides` explicitly asks for a narrower window, or when inspection data clearly shows zero YTD completions and a wider window would still be empty (then explain in `reasoning`).

## Divisions

- Use the **`divisions` list in Runtime config JSON** as the default.
- Only include additional divisions when `requested_overrides.divisions` explicitly expands the list.
- Verify each configured division exists in `export_inspection.divisions`; if Construction is missing, explain in `reasoning` and use what is available.

## Branches

- `"branches": []` means all branches. Only set branch names when overrides request them.

## Output JSON

Return one JSON object matching `expected_json_schema`. Always include `"reasoning"` explaining date window and division choices.
