# CIP Workbook Reproducibility Evidence

## Technical summary

14 generated workbooks were inspected. Structural consistency is **MIXED** across the full history: 12 of 14 files (85.7%) share the current worksheet structure. This supports stable recent workbook construction, but it does not establish financial reconciliation without the approved manual reference workbook.

## Key findings

- Structural signature groups: **2**.
- Files matching the current structural signature: **12 of 14**.
- Normalized package groups: **14**.
- Output size range: **3,923,690–3,973,149 bytes** (1.258% of the mean).
- Every workbook was checked independently; identical filenames were not assumed to mean identical content.
- The two earliest artifacts form a larger-row structural group, consistent with a different filter, configuration, or build revision; manifests were not available to distinguish those causes.

## Run inventory

| Workbook | Size (bytes) | Sheets | Structural signature | Normalized package | Changed ZIP members vs latest |
| --- | ---: | ---: | --- | --- | ---: |
| `CIP_Report_20260628_204358.xlsx` | 3,973,133 | 9 | `16CDD9CF5DC1` | `FB6B0EB8A4EE` | 13 |
| `CIP_Report_20260628_204810.xlsx` | 3,923,770 | 9 | `FC5F7F9AE5BC` | `F4E63DBA533D` | 10 |
| `CIP_Report_20260628_210626.xlsx` | 3,973,149 | 9 | `16CDD9CF5DC1` | `3E180D454903` | 13 |
| `CIP_Report_20260628_211054.xlsx` | 3,923,756 | 9 | `FC5F7F9AE5BC` | `D39CD93457E8` | 10 |
| `CIP_Report_20260705_105439.xlsx` | 3,923,704 | 9 | `FC5F7F9AE5BC` | `BCE3207D9A5B` | 10 |
| `CIP_Report_20260708_205834.xlsx` | 3,923,696 | 9 | `FC5F7F9AE5BC` | `4C9615BBBF67` | 10 |
| `CIP_Report_20260714_211446.xlsx` | 3,923,690 | 9 | `FC5F7F9AE5BC` | `079438765C6D` | 10 |
| `CIP_Report_20260715_202405.xlsx` | 3,923,690 | 9 | `FC5F7F9AE5BC` | `C9EAF81B8960` | 10 |
| `CIP_Report_20260715_202805.xlsx` | 3,923,708 | 9 | `FC5F7F9AE5BC` | `68C1C49ECA74` | 10 |
| `CIP_Report_20260728_215412.xlsx` | 3,923,720 | 9 | `FC5F7F9AE5BC` | `4C31F1B313DE` | 10 |
| `CIP_Report_20260803_205444.xlsx` | 3,925,979 | 9 | `FC5F7F9AE5BC` | `286A37635E1A` | 9 |
| `CIP_Report_20260809_112243.xlsx` | 3,926,024 | 9 | `FC5F7F9AE5BC` | `BAA5E695DAB4` | 9 |
| `CIP_Report_20260809_114002.xlsx` | 3,925,992 | 9 | `FC5F7F9AE5BC` | `9BF5FB0EFB60` | 9 |
| `CIP_Report_20260809_122617.xlsx` | 3,925,982 | 9 | `FC5F7F9AE5BC` | `0E7B462433EA` | 0 |

## Scope and methodology

The analysis compared worksheet order, names, and used dimensions. It also hashed every file and every ZIP member inside each XLSX package. A normalized package signature excluded document metadata, calculation-chain data, and Version History content because those fields are expected to vary across otherwise equivalent runs.

## Limitations and pending validation

- The approved manual reference workbook was not available.
- Structural and package consistency do not prove financial reconciliation.
- Runs may reflect different code versions or configurations unless a run manifest proves otherwise.
- Normalized package hashes exclude document metadata, calculation chain data, and Version History content.

## Recommended next steps

1. Capture a structured run manifest on every new run so configuration and code version are known.
2. Repeat at least five runs from one fixed input, configuration, skill package, and Git commit.
3. Run the reconciliation harness against the approved manual reference when it becomes available.
4. Treat financial accuracy as pending until the configured value checks pass.

## Further questions

- Which dashboard cells and Table-sheet aggregates are authoritative acceptance measures?
- What absolute or percentage tolerances are acceptable for currency and margin calculations?
- Should Version History and generated timestamps be excluded from formal reproducibility comparisons?
