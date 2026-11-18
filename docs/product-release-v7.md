# v0.7.0: scientific reproduction review workflow

## Product direction

The deliverable is an English CLI and offline evidence application. The primary workflow is prepared project → original author execution → candidate evidence → diagnosis and attributed review → optional approved lesson. Historical A/B experiments remain research evidence and are not the homepage's main workflow.

Previous B performance did not establish that lessons help. V6 also changed B's available tools, so A/B differences cannot be attributed solely to lesson text. This release does not run another 60-cell experiment or claim a success-rate improvement. A future experiment should compare matched tools, budgets, validators, and fresh tasks, with only the lesson intervention varied.

## Implemented behavior

- Product execution policy is explicit and defaults to original author code. Legacy experiment routing is retained for compatibility.
- Reference scoring is optional and separate from execution and semantic support.
- Versioned review records distinguish execution events, valid citations, successful-execution provenance, source changes, partial artifacts, optional correctness, and attributed semantic review.
- Reports have line-targeted offline evidence links, visible blockers and partial outputs, provisional diagnosis contributors, source audits, and loaded lesson provenance.
- Lessons have explicit proposal, approval, disabling, edit invalidation, development-only source eligibility, and per-run content snapshots.
- Historical run exports and experiment artifacts are preserved. The new exporter operates only on the explicitly selected product runs.

## Acceptance protocol

The selected tasks are CULP (capsule-6460826), SEM (capsule-2916503), and the Iris notebook (capsule-0940461). The first two previously supported original author execution; the third is a known external-data/network blocker. All three omit answer keys. The CULP run selects an approved development-derived lesson; the later runs omit it after disabling. All attempts remain recorded. Budgets are unchanged.

Software regression tests cover score-correct but unreviewed semantics, unsuccessful execution provenance, no answer key, absent submission, broken line citations, simultaneous network/budget contributors, attributed review import, and lesson proposal/approval/edit/disable/evaluation-source refusal. Existing controller and export tests remain part of acceptance.

Live results and delivery checks are appended after completion. They describe observed development behavior, not held-out generalization or independent human validation.

## Observed development results

| Task | Outcome | Model calls | Seconds | Estimated model cost | Reference scoring |
| --- | --- | ---: | ---: | ---: | --- |
| CULP / 6460826 | Completed; three original scripts succeeded | 7 | 27.42 | $0.006213 | Not scored |
| SEM / 2916503 | Completed; original R script succeeded | 6 | 25.93 | $0.006390 | Not scored |
| Iris notebook / 0940461 | Partial; notebook failed, wrapper succeeded, no submitted answers | 20 | 94.74 | $0.060320 | Not scored |

Total: 33 model calls, 148.09 seconds of recorded run time, approximately $0.072923 estimated model cost. These are actual development observations, not an A/B comparison. The `A1` suffix is retained legacy run naming; these product runs all used controlled original-author execution.

The notebook failed while `seaborn.load_dataset` requested the external Iris dataset in the offline sandbox. Its stderr records a name-resolution error. A subsequent author wrapper exited successfully, but that exit does not establish successful notebook computation. The agent continued inspecting and reached `Maximum model calls reached` without submitting. The product therefore preserves partial evidence and a controller-budget contributor instead of inventing answers or treating the wrapper exit as complete reproduction. No network-policy relaxation, dataset substitution, or scientific rewrite was introduced. This is a remaining agent-efficiency limitation; the report workflow successfully exposes it.

CULP and SEM have assistant-attributed semantic reviews for nine questions, with retained citations and metric/object/scale rationales. They have **not** been independently human-reviewed. The first run loaded one approved lesson from an official training run; it was disabled before the other runs. All three snapshots are retained, and no benefit claim is made from this difference.

The development runs preceded final report/diagnosis and startup-exception hardening. Those changes were checked through software regressions and report regeneration; the expensive author executions were not repeated or replaced. Original execution outputs, summaries, and failed attempts remain intact. Legacy low-level `answer_solved` fields in those raw summaries predate nullable unscored handling; the product assessment correctly records `Not scored` and must be used for interpretation.

## Validation and remaining limits

56 software tests pass, including all 48 pre-existing tests. New coverage includes a simulated runner startup failure that must still emit a report, explicit missing-reference configuration failure, and a copied historical preprocessing/render failure retaining all six changed input files and rejected candidate submissions. Historical traces are used only for software regression, not lesson generation.

The review schema conservatively leaves automatic semantic support unresolved. Attributed reviewer decisions are stored separately. File-change interpretation is conservative: the current inventory does not reliably distinguish every raw-data, generated-data, and preprocessing role. Diagnosis is signature-based and may include errors quoted in inspected source; its hypotheses require checking execution order and cited evidence. There is no universal automatic scientific-faithfulness verifier.

Browser navigation and historical-file integrity results are recorded in `reports/product-delivery-validation.json`. The English video uses actual report pages and disclosed synthetic macOS narration. Existing v0.6 video, reports, experiments, and releases remain preserved.

Final offline QA checked 487 local links and anchors with zero broken links, exercised navigation in Chrome, and verified 11,663 historical run/experiment files byte-for-byte against v0.6.0. The source distribution and wheel build successfully. The new English walkthrough is approximately 114 seconds. Regenerate delivery checks with `uv run --with playwright python scripts/validate_product_delivery.py` on the documented macOS setup.
