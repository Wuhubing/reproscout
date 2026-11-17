# ReproScout: project overview and delivery contract

## Main thread

ReproScout asks whether explicit lessons from failed scientific reproduction
attempts can improve subsequent attempts. The experiment starts with authors'
released code and data, runs that code in a controlled environment, extracts
answers, and connects each answer to recorded execution evidence. A failure is
also a useful output: it should identify what happened and where to inspect it.

This is an individual MIT 1.125 software systems project by Weibing Wang. Its
intended users are artifact reviewers, researchers reusing a baseline, and students
trying to understand a published experiment. The deliverable is an executable
research instrument and evidence report, rather than a hosted consumer product.

## Inputs and outputs

| Input | Owner and treatment |
|---|---|
| Official task prompt and questions | Visible to the agent; original question keys preserved |
| Released code and data | Prepared independently; source hashes recorded |
| Archived author image | Pulled by the controller, pinned by digest |
| Reference result runs | Host-private scorer input; never included in agent metadata or sandbox |
| API credential | Host memory only, read from an explicit file or environment |
| Model and budget configuration | Versioned and frozen before formal evaluation |
| Optional development lessons | Included only in condition B; fixed across held-out runs |

Outputs include a submitted answer for each question, references to immutable
controller-owned evidence snapshots, per-question correctness, whole-task solved
status, source-integrity audit, provisional failure diagnosis, usage/cost ledger,
original Inspect trace, SQLite event index, and a portable HTML report. A missing
submission is preserved as an unsolved attempt, not converted to a correct answer.

## Runtime flow

1. Validate an archive and prepare only code, data, environment instructions, and
   reproduction documentation. Reject unsafe paths and links; remove supplied
   results and clear stored notebook outputs without changing code-cell source.
2. Start a fresh offline author container with resource limits. Keep the answer
   key, credential, host filesystem, and Docker socket outside it.
3. Run an Inspect ReAct loop with four project-owned tools: shell, read_file,
   view_image, and submit_report. Save tool output before returning it to the model.
4. Reserve request costs before dispatch and record returned token usage. Apply
   command, call-count, context, wall-clock, and cost bounds.
5. Validate submitted evidence references, score externally against the original
   questions, audit original input hashes, and generate the report.
6. Compare baseline A with lessons condition B on frozen held-out membership,
   using two repetitions and reporting every planned cell.

## What the application looks like

The CLI prepares and runs capsules. The results homepage summarizes A/B solved
counts, cost, time, language/modality breakdowns, lessons, and recorded failures.
Each row opens a task report with question text, submitted values, correctness,
and clickable evidence. JSON files provide machine-readable manifests, budgets,
source audits, diagnoses, and the actual agent/tool conversation. Inspect View
provides a richer local trace viewer for the original logs.

No account, cloud deployment, GPU service, or multi-user interface is required.
The report can be opened locally without an API key or Docker. Rerunning scientific
experiments requires the documented runtime, capsule downloads, author image,
and an API credential.

## References versus original implementation

Inspect AI supplies general model/tool orchestration, Docker transport, logging,
and the ReAct pattern. ReproScout independently implements task preparation,
input/evidence boundaries, budgets, scoring, diagnoses, experiment freezing, and
reporting. CORE-Bench supplies scientific artifacts, split definitions, questions,
and reference results; its task harness and agents are not imported or invoked.
ExpeL is a conceptual reference for reusable natural-language lessons. This release
uses developer-curated lessons and does not claim a complete autonomous ExpeL system.
See research-references.md for the source map and attribution.

## Changes from the original proposal

The original ambition was 25 capsules and a Medium environment-building task.
The implementation uses prepared author environments. After the first fallback
release, registry recovery enabled the original target of fifteen official test
capsules, with five development tasks and the same frozen lessons. Runtime networking is disabled completely;
there is no PyPI/CRAN whitelist. One verified model handles the agent tools rather
than the unverified model lineup in the proposal. Image/PDF inspection is available,
but a vision-labelled task can also be answered by inspecting executed data output.

Registry HTTP 429 failures initially constrained the first release to two test
capsules. The expanded release recovered those images and completed preparation
of a fifteen-task cohort before freezing a new sixty-cell experiment.
The selection ledger records all considered tasks and provisioning outcomes. The
experiment neither replaces tasks based on held-out scores nor derives new rules
from held-out traces. Conclusions apply only to the selected available subset.

## Acceptance and remaining research claims

A software release is deliverable when installation is pinned, real tasks execute,
failed attempts are retained, evidence is navigable, the frozen comparison is
complete, and another reader can inspect the protocol and limitations. A positive
research result is a separate question. The original +2 solved improvement target,
80 percent agreement with independent human diagnoses, and ten adversarial model
prompts are not automatically satisfied by a working application. Report these as
unestablished unless the corresponding experiment has actually been conducted.
