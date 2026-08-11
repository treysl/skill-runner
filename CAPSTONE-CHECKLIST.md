# Capstone Project Checklist

**Project:** Deterministic Skill-Runner for Reporting Pipeline  

 Mark items `- [x]` when complete.

## Scope

### In scope

- [x] Requirements elicitation for at least one representative reporting use case (CIP / construction-in-process report)
- [x] Skill-runner architecture designed (GitHub skills repo + deterministic Python scripts)
- [x] Proof-of-concept pipeline: read sample data → invoke skills → run scripts → produce report files
- [x] Basic evaluation: reproducibility, runtime, maintainability (pilot runs + logs)

### Out of scope (explicitly deferred)

- [ ] Full production hardening — **not in this phase**
- [ ] Enterprise-wide change management — **not in this phase**
- [ ] Comprehensive security review — **not in this phase**
- [ ] Full-featured UI beyond minimal run/monitor controls — **not in this phase**

---

## SMART goals

### Goal 1 — Prototype delivery (Specific, Time-bound)

- [x] Working skill-runner prototype implemented
- [x] At least one standardized report generated from sample data
- [x] No interactive chat session required during execution


### Goal 2 — Reproducibility (Measurable)

- [x] Five consecutive runs completed with same input + configuration
- [x] Outputs consistent across runs (differences limited to acceptable formatting variation)
- [x] Structural reconciliation / validation passes for the documented comparison runs
- [x] Output reconciliation completed against the Claude App skill result using the same source data and filters (confirmed by project owner)

![Five consecutive CIP report outputs in outputs/](docs/images/goal2-reproducibility-outputs.png)

### Goal 3 — Efficiency (Measurable, Relevant)

- [x] Comparative execution documented (Claude Teams interactive run vs deterministic skill-runner)
- [x] Measurable reduction demonstrated for the selected report (359 seconds / 19 Claude-reported steps vs 87.314-second runner execution; 75.7% elapsed-time reduction)

The comparison intentionally excludes the traditional manual process, which
requires dozens of hours. The capstone evaluates Claude interactive execution
against the deterministic runner using the same source data and filters.


### Goal 4 — Documentation & maintainability (Achievable, Relevant)

- [x] Architecture documented
- [x] Configuration and execution steps documented
- [x] Documentation prepared for technical handoff (independent execution test deferred to future work)

---

## Expected deliverables

- [x] Skill-runner architecture diagram and description
- [x] Working prototype (sample data → skills/scripts → finished reports in secure output location)
- [x] Evaluation results: structural reproducibility + Claude-versus-runner efficiency
- [x] Reflection on scaling to other reports and production hardening requirements

---

## Project lifecycle phases (Gantt-aligned)


### 1. Initiation Phase — Initiation, problem definition, Literature review & requirements
- [x] Problem statement finalized
- [x] Stakeholders and constraints identified
- [x] Scope statement written
- [x] Research on LLM-in-pipeline / ETL patterns reviewed
- [x] Representative use case selected (CIP report)
- [x] Input data requirements documented (Aspire Opportunity export)

### 2. Planning Phase — Architecture & scope design
- [x] Architecture defined: n8n trigger → runner API → OpenRouter orchestration → packaged `.skill` → Python build script
- [x] Data folder, output folder, and config strategy defined
- [x] Packaged `.skill` file as source of truth (extract to cache at runtime)

###  3. Execution — Prototype development
- [x] GitHub repository created (`skill-runner`)
- [x] Packaged skill stored in repo (`skills/*.skill`)
- [x] Runner API implemented (inspect, orchestrate, build, `/run`)
- [x] OpenRouter integration for pre-flight orchestration
- [x] Runtime config in markdown (`runner/cip-orchestration.md`) for division/date defaults
- [x] n8n workflow created and tested locally
- [x] Sample/anonymized data used for development
- [x] End-to-end pipeline run succeeds
- [x] Completed-tab date window validated (YTD default)
- [x] Division filter validated (Construction-only default)
- [x] Five-run reproducibility test executed and recorded
- [x] Runtime and log output captured

### 4. Monitoring — Draft preparation
- [x] Capstone draft written from prototype results
- [x] Architecture and evaluation sections updated with actual outcomes

###  5. Closure — Final submission
- [x] Final capstone document submitted
- [x] Repository cleaned and documented for reviewer access

---

## Technical implementation checklist (skill-runner)

- [x] Packaged `.skill` file committed (not extracted source in repo)
- [x] Skill loader extracts to `.runner-cache/` on demand
- [x] Local runner API on port 8787
- [x] `DATA_DIR` / `OUTPUT_DIR` configurable via `.env`
- [x] OpenRouter orchestration with markdown-driven defaults
- [x] n8n workflow (`n8n/cip-report-pipeline.json`)
- [x] First successful CIP report generated from anonymized sample data
- [x] Run log: data source, skill package, script version, timestamp per execution
- [x] Five consecutive reproducibility runs documented
- [x] Claude Teams versus skill-runner efficiency comparison documented
- [x] Reference-output reconciliation completed against the standard Claude App skill workbook

---

## Resources

- [x] GitHub repository for version control
- [x] Python runtime and dependencies (`requirements.txt`)
- [x] LLM skill file (packaged `.skill`)
- [x] Sample operational data (anonymized Aspire export)
- [x] Secure output folder for generated reports
- [x] Private repo access controls verified (confirmed by project owner)
- [x] Gantt chart maintained and current (reviewed 2026-08-10)

---

## Ethical considerations

- [x] AI-generated outputs not presented as unquestionable truth
- [x] Human-in-the-loop validation required before external distribution
- [x] Anonymized or synthetic sample data used in prototype

---

## Security & mitigation

- [x] API keys stored in `.env` (not committed)
- [x] `.env.example` contains placeholders only (no live secrets)
- [x] Private GitHub repository with role-based access (confirmed by project owner)
- [x] Credentials loaded from environment variables — not hard-coded
- [x] Pipeline run logging for audit (source, skill, version, timestamp)
- [x] Human review required before sharing reports outside project team

---

## Feasibility assessment


| Dimension   | Planned rating | Status | Notes                                                |
| ----------- | -------------- | ------ | ---------------------------------------------------- |
| Technical   | High           | OK     | Python, GitHub, skills, n8n — no exotic infra        |
| Operational | High           | OK     | Fits existing BI reporting patterns; single use case |
| Economic    | High           | OK     | Tools in place; incremental LLM cost is small        |
| Schedule    | Medium         | OK     | Seven-week window — scope control critical           |


- [x] Feasibility checklist reviewed at initiation
- [x] Scope creep actively guarded through explicit in-scope and out-of-scope boundaries (Oguz)
- [x] Schedule milestones and deadlines tracked on the current Gantt

---

## Acceptance criteria (closure)

- [x] Prototype generates at least one report without chat during execution
- [x] Reproducibility demonstrated (≥ 5 consistent runs)
- [x] Documentation sufficient for handoff; independent execution test deferred to future work
- [x] Ethical/security mitigations implemented for prototype phase
- [x] Evaluation and scaling reflection completed

---

## Future work — not required for capstone closure

- Independent documentation/handoff test by another technical team member
- Confirmation that sensitive-data handling meets organizational policy
- Verification that the AI disclaimer appears inside the distributed workbook
- Least-privilege validation for data and output folders

---

## Notes

*Add run dates, output file paths, test results, and blockers here.*


| Date | Milestone                     | Result |
| ---- | ----------------------------- | ------ |
| 2026-06-28 | First end-to-end n8n run | PASS - anonymized source produced the CIP workbook |
| 2026-07-15 | Five-run reproducibility test | PASS - five consistent outputs documented in `docs/images/goal2-reproducibility-outputs.png` |
| 2026-08-09 | Construction-only + YTD release-candidate run | PASS - 6,989 input rows; 133.818 seconds; 9-sheet output |
| 2026-08-09 | Instrumented validation run | PASS - 87.314 seconds; 29 tests; audit manifest and output hash verified |
| 2026-08-10 | Claude Teams comparison | PASS - same source and filters; 19 reported steps; 359 seconds plus approximately 1 minute review |
| 2026-08-10 | Reference-output reconciliation | PASS - standard Claude App skill output and skill-runner output reconcile using the same source data and filters (project-owner confirmation) |
| 2026-08-10 | Revised capstone report | COMPLETE - comparison, current validation evidence, limitations, and scaling reflection incorporated |
| 2026-08-10 | Gantt review and capstone closure | COMPLETE - current timeline reviewed; repository/reviewer-access review and final submission confirmed complete by project owner |
