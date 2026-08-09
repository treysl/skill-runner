# Capstone Evidence Validation

## Overall assessment: Share with caveats

The capstone evidence is ready to support claims that the prototype executes
successfully, produces the expected workbook structure, rejects an unsafe path,
and can record a traceable audit manifest. It is not yet ready to support final
claims of financial reconciliation or quantified analyst time savings.

## The current pipeline is traceable and operationally validated

The instrumented n8n run completed in 87.314 seconds using 6,989 anonymized
source rows. It produced a 3,925,982-byte workbook with nine worksheets and a
companion JSON manifest. The output's independently calculated SHA-256 hash
matched the hash stored in the manifest. All four system acceptance checks
passed.

The expanded unit suite passes 29 of 29 tests. New coverage verifies success and
failure manifests, neutral output naming, reconciliation tolerances, pipeline
manifest integration, and reproducibility hashing.

## Recent workbook construction is structurally stable

Fourteen generated workbooks were inspected. Twelve files, including the latest
instrumented run, share the current worksheet-name and used-dimension signature.
Two early files form a separate structural group with larger Dashboard, In
Process, In Process By Property, Completed, and Completed Dashboard View ranges.

This is a mixed historical result rather than a pipeline failure. Historical
manifests do not exist, so differences in code version, input, or configuration
cannot be isolated confidently for those two artifacts.

## Scope, definitions, and evidence

- **Run:** one generated `CIP_Report_*.xlsx` artifact.
- **Current structural signature:** the worksheet order, names, and used
  dimensions found in the latest instrumented workbook.
- **Structural match:** exact agreement with that signature.
- **Normalized package signature:** a hash of XLSX ZIP members excluding document
  metadata, calculation-chain data, and Version History content.
- **Financial reconciliation:** agreement with approved reference values and
  aggregates within defined tolerances. This has not been performed.

Primary evidence is stored in `docs/evidence/reproducibility-evidence.json`,
`docs/evidence/structural-reconciliation-latest.json`, and the local runtime
manifest under `outputs/run-manifests/`.

## Methodology

1. Rebuilt and tested the Python environment.
2. Added success and failure manifest generation to the pipeline.
3. Ran the complete n8n-to-runner-to-workbook workflow.
4. Recomputed the generated workbook hash independently.
5. Ran workbook and API acceptance checks.
6. Profiled all generated XLSX artifacts by file hash, ZIP-member hash,
   worksheet inventory, and used dimensions.
7. Ran the reconciliation harness between two recent outputs in structure-only
   mode.

## Issues and limitations

1. **High - approved reference unavailable:** Financial accuracy is not verified.
   The comparison harness and configuration template are ready, but authoritative
   cells, aggregates, and tolerances still need approval.
2. **Medium - manual effort unmeasured:** Automated elapsed time is known, but
   analyst touch-time savings cannot be calculated until the manual process and
   automated review are timed comparably.
3. **Medium - incomplete historical provenance:** Two early artifacts have a
   different structure and lack manifests, preventing causal attribution.
4. **Low - visual workbook QA not repeated during this validation:** Structural checks do
   not replace a human review of layout, formulas, and presentation quality.

## Calculation spot-checks

| Claim | Result | Evidence |
| --- | --- | --- |
| Latest instrumented runtime | Verified: 87.314 seconds | Runtime manifest |
| Input size | Verified: 6,989 rows | Runtime inspection |
| Workbook structure | Verified: 9 worksheets | Manifest and acceptance check |
| Output integrity | Verified: manifest hash matches file | Independent SHA-256 calculation |
| Current structural group | Verified: 12 of 14 files | Reproducibility profile |
| Golden-workbook values | Not verified | Reference workbook pending |
| Analyst hours saved | Not verified | Manual timing pending |

## Required presentation caveats

- Describe the workbook evidence as structural reproducibility, not financial
  reconciliation.
- Describe 87.314 seconds as one instrumented run, not a guaranteed service
  level.
- Do not claim analyst hours or cost savings until the manual baseline is measured.
- Retain human review as a required control before report distribution.

## Recommended next steps

1. Continue capturing manifests for every new run.
2. Complete the manual timing worksheet on the other machine.
3. Identify authoritative reference cells, aggregates, and tolerances.
4. Run and review the golden-workbook reconciliation.
5. Perform final visual and formula QA before presentation.

## Further questions

- Which financial totals are authoritative for acceptance?
- Which differences are allowed because of rounding, dates, or version history?
- How many manual observations are feasible before the capstone deadline?
- Should the two early structural variants remain in the presentation evidence
  or be moved to a historical appendix?
