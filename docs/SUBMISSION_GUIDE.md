# LotLens Submission Package Guide

**Purpose:** Recommended hand-in checklist for the current Phase 2 project build.  
**Project branch:** `feature/phase-2-vertical-slice`  
**Pull request:** [PR #8](https://github.com/Deepak-Reddy-56/lotlens/pull/8)

> Follow the institution's official submission rubric first. This guide describes a complete, defensible package based on the artifacts currently present in this repository; it does not replace a required college template or prescribed file format.

## 1. Recommended primary submission

| Item | What to provide | Where it is available |
|---|---|---|
| Source code | GitHub repository URL, or a source ZIP if the portal requires an upload | Repository / feature branch |
| Project report | A formatted PDF using the institution's template, covering problem, objectives, requirements, architecture, implementation, evaluation, limitations and conclusion | Prepare from the project documentation listed below |
| Test report | Include the test coverage, execution record and limitations; PDF export if the portal accepts PDF reports | [TEST_REPORT.md](TEST_REPORT.md) |
| Setup and usage instructions | README with prerequisites, Windows PowerShell setup, environment configuration, run commands and demo flow | [README.md](../README.md) |
| Demonstration evidence | Screenshots or a short screen recording of the running application and the workflow | Capture from the actual local app; do not fabricate screens |

If the submission portal accepts only one report, integrate the test report as a dedicated testing/evaluation chapter and include the full test report as an appendix only if the page limit permits.

## 2. Supporting technical documentation

Use these as source material or appendices in the main report, rather than automatically uploading every file as a separate document:

- [Problem statement](PROBLEM_STATEMENT.md) — manufacturing problem and motivation.
- [Requirements and MVP](REQUIREMENTS.md) — scope and functional requirements.
- [Architecture](ARCHITECTURE.md) and [ADR-0002](DECISIONS/ADR-0002-first-vertical-slice-architecture.md) — system design and technology decisions.
- [Database design / ERD](DATABASE_DESIGN.md) — entities and relationships.
- [API contracts](API_CONTRACTS.md) — endpoint and payload reference.
- [Hindsight memory design](MEMORY_DESIGN.md) and [Hindsight setup](HINDSIGHT_SETUP.md) — memory model and configuration.
- [Testing strategy](TESTING_STRATEGY.md) and [test report](TEST_REPORT.md) — verification plan, automated coverage and limitations.
- [Implementation status](IMPLEMENTATION_STATUS.md) — completed scope and remaining work.

## 3. Suggested screenshots / demo sequence

Capture these from the working application if the corresponding workflow is available and verified:

1. Dashboard showing the case register and summary.
2. Case detail for a seeded synthetic case, with supplier, component, lot and defect information.
3. Investigation result showing the Hindsight synthesis and canonical historical-evidence cards.
4. Corrective-action entry and the case lifecycle after the action is recorded.
5. QA verification view showing the selected action and verification outcome.
6. Swagger/OpenAPI page at `/docs`, if API implementation evidence is requested.
7. Terminal output showing the local pytest command and final passed summary.

Use the seeded LOT-POC demo records only as synthetic examples. Label them as synthetic in the report and presentation. Capture real screenshots only after the displayed workflow has actually been run; do not use mockups as proof of execution.

## 4. Test results that can be reported

- GitHub Actions backend compile check passed.
- GitHub Actions backend pytest suite: **29 passed in 3.91 seconds**.
- Project owner confirmed the backend pytest suite also passed in the local Windows virtual environment; the local terminal transcript and exact runtime were not retained.
- GitHub Actions frontend TypeScript/Vite production build passed.

The test report explicitly identifies what remains unverified: live Hindsight smoke testing, full browser end-to-end workflow, PostgreSQL integration, and production security. Do not describe these as passed unless they are separately executed and recorded.

## 5. Files and secrets not to submit

Do **not** include:

- Root `.env`, frontend `.env`, API keys, access tokens, passwords or private credentials.
- `.venv/`, `node_modules/`, Python cache folders, `.pytest_cache/`, or build output folders unless explicitly required.
- Personal machine logs, temporary files or local database files unless the reviewer specifically requests a reproducible fixture database.
- Any real or confidential manufacturing, supplier or customer data.

Keep dependency manifests and lockfiles (such as `backend/requirements.txt`, `frontend/package.json` and `frontend/package-lock.json`) because they support reproducible setup.

## 6. Before uploading

- [ ] Confirm the official rubric, required template, file format and upload size limit.
- [ ] Open the repository and confirm the submitted branch/commit is the intended version.
- [ ] Verify the README setup instructions and environment-variable names.
- [ ] Ensure no secret files or credentials are tracked or present in the ZIP.
- [ ] Export the final report to the required PDF/DOCX format and check page numbers, figure labels and references.
- [ ] Capture actual application screenshots and the local test terminal output if evidence is required.
- [ ] Check that every claim in the report is supported by an implementation, test result or clearly labelled design proposal.
- [ ] Include known limitations rather than presenting the prototype as production-ready.

## 7. Submission recommendation

A practical package is: **(1) main project report PDF, (2) GitHub repository link or source ZIP, (3) test report PDF/appendix, and (4) a short demo video or selected screenshots if requested.** Keep the README and technical design documents inside the repository so reviewers can inspect the setup and implementation details.
