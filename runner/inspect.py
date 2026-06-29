from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ExportInspection:
    input_file: str
    row_count: int
    columns: list[str]
    branches: list[dict[str, Any]]
    divisions: list[dict[str, Any]]
    job_statuses: list[dict[str, Any]]
    opportunity_statuses: list[dict[str, Any]]
    missing_required_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


REQUIRED_COLUMNS = [
    "Branch",
    "Opportunity #",
    "Property Name",
    "Division",
    "Invoice Type",
    "Opportunity Name",
    "Opportunity Type",
    "Revision #",
    "Job Status",
    "Won Date",
    "Revenue Estimated",
    "Earned Revenue",
    "Invoiced Revenue",
    "Labor Hours Actual",
    "Labor Hours Estimated",
    "Labor Cost Actual",
    "Labor Cost Estimated",
    "Material Cost Actual",
    "Material Cost Estimated",
    "Sub Cost Actual",
    "Sub Cost Estimated",
    "Equipment Cost Actual",
    "Equipment Cost Estimated",
    "Other Cost Actual",
    "Other Cost Estimated",
]


def _value_counts(series: pd.Series) -> list[dict[str, Any]]:
    counts = series.fillna("(blank)").astype(str).value_counts()
    return [{"value": str(name), "count": int(count)} for name, count in counts.items()]


def inspect_export(input_path: Path) -> ExportInspection:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_excel(input_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    branches = _value_counts(df["Branch"]) if "Branch" in df.columns else []
    divisions = _value_counts(df["Division"]) if "Division" in df.columns else []
    job_statuses = _value_counts(df["Job Status"]) if "Job Status" in df.columns else []
    opp_statuses = (
        _value_counts(df["Opportunity Status Name"])
        if "Opportunity Status Name" in df.columns
        else []
    )

    return ExportInspection(
        input_file=str(input_path.resolve()),
        row_count=len(df),
        columns=[str(c) for c in df.columns],
        branches=branches,
        divisions=divisions,
        job_statuses=job_statuses,
        opportunity_statuses=opp_statuses,
        missing_required_columns=missing,
    )


def find_input_file(data_dir: Path, filename: str | None = None) -> Path:
    if filename:
        candidate = data_dir / filename
        if not candidate.exists():
            raise FileNotFoundError(f"File not found in data folder: {filename}")
        return candidate

    xlsx_files = sorted(
        data_dir.glob("*.xlsx"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not xlsx_files:
        raise FileNotFoundError(
            f"No .xlsx files found in {data_dir}. Drop an Aspire Opportunity export there."
        )
    return xlsx_files[0]
