# Manual vs. Automated Efficiency Evaluation

## Purpose

This framework measures whether the deterministic CIP pipeline reduces analyst
effort without confusing machine runtime with human touch time. Manual-process
measurements remain pending until the process owner can time the approved
workflow.

## Current automated baseline

| Metric | Automated result | Evidence status |
| --- | ---: | --- |
| Trigger actions | 1 workflow trigger | Observed |
| Input rows | 6,989 | Verified |
| End-to-end elapsed time | 133.818 seconds | Verified on 2026-08-09 |
| Output worksheets | 9 | Verified |
| Output size | 3,926,024 bytes | Verified |
| Unit tests | 29/29 after evidence-tooling additions | Verified |
| Human review time | Pending measurement | Not yet measured |

Elapsed time is not the same as analyst effort. The pipeline can run without
continuous analyst attention, but the final workbook still requires human
review before distribution.

## Manual timing worksheet

Complete this table while performing the approved manual process on the other
machine. Use a representative report rather than a best-case demonstration.

| Manual activity | Start | End | Active minutes | Waiting minutes | Rework minutes | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Acquire and validate source export | | | | | | |
| Filter and prepare source data | | | | | | |
| Build in-process schedules | | | | | | |
| Build completed schedules | | | | | | |
| Refresh dashboards and summaries | | | | | | |
| Reconcile totals | | | | | | |
| Format and package workbook | | | | | | |
| Final review and distribution | | | | | | |
| **Total** | | | | | | |

## Comparison metrics

| Metric | Manual | Automated | Calculation |
| --- | ---: | ---: | --- |
| Analyst touch time | Pending | Trigger + review time | Sum of active and rework minutes |
| Elapsed processing time | Pending | 2.230 minutes | End time minus start time |
| Manual interventions | Pending | 1 trigger plus review | Count of required user actions |
| Rework time | Pending | Pending review result | Minutes correcting errors |
| Reports per month | Pending | Same frequency | Process-owner input |
| Monthly hours saved | Pending | — | `(manual touch - automated touch) × monthly runs ÷ 60` |
| Annual hours saved | Pending | — | `monthly hours saved × 12` |

## Measurement rules

1. Use the same input scope and reporting requirements for both approaches.
2. Separate active work from waiting time.
3. Include validation and correction time for both approaches.
4. Record failures and reruns rather than discarding them.
5. Use at least three manual observations if schedule permits; report the median
   and range rather than relying on one unusually easy or difficult run.
6. Do not convert time savings to dollar savings without an approved loaded
   labor-rate assumption.

## Decision criteria

The efficiency claim is ready for the capstone when:

- manual and automated runs use comparable inputs and scope;
- manual touch time and automated review time are both measured;
- calculation assumptions are visible;
- exceptions and rework are included; and
- the result is presented as descriptive evidence, not a guaranteed future saving.

## Current status

**Pending manual measurement.** The automated elapsed-time baseline is verified,
but analyst time savings cannot yet be calculated defensibly.
