# v0.8.0 — local research workspace

ReproScout now exposes its original-author execution and evidence review workflow through a local browser app. The UI is backed by real project/run records and worker processes; it is not a static mockup. All product text is English.

## Delivered workflow

- Overview with actual project/run counts and separate execution/review indicators.
- Prepared-project registration and new-run forms with editable questions/types, budgets, and approved lesson selection.
- Live execution updates, retained failed steps, cooperative cancellation, and portable report export.
- Side-by-side candidate and evidence inspection with exact line selection.
- Attributed semantic review saved as new versions, preserving earlier decisions and reviewer identities.
- Lesson proposal, approval, Markdown editing, edit invalidation, disabling, and append-only transition records.
- Separate execution, source-integrity, lesson-snapshot, and visible-trace views.
- Responsive desktop/mobile layouts and keyboard-contained new-run dialogs.

Existing Inspect orchestration, offline author containers, tool boundaries, typed submissions, evidence capture, budgets, network retries, and report generation are reused. React and Lucide are frontend dependencies. shadcn/ui and Langfuse informed the layout and interaction design; their repositories were not forked and their backends are not invoked. See `frontend-references-v8.md` for boundaries and license notices.

## Browser-launched development validation

| Task | Outcome | Model calls | Seconds | Estimated model cost |
| --- | --- | ---: | ---: | ---: |
| CULP / 6460826 | Completed | 7 | 28.87 | $0.005651 |
| Iris notebook / 0940461 | Partial; known offline blocker | 13 | 67.69 | $0.031505 |
| SEM / 2916503 | Completed | 6 | 23.52 | $0.006441 |
| CULP cancellation check | Cancelled, evidence retained | 2 | 7.39 | $0.001772 |

The three execution-validation tasks used 26 model calls and approximately $0.043598 total. The cancellation check is additional and is not counted as a failed scientific task. All four attempts, including their errors and partial output, are retained in `reports/workspace-runs/` and indexed by `reports/workspace-v8.html`.

The previous v0.7 Iris attempt reached 20 calls with no submission. In this v0.8 development attempt, the author wrapper exited successfully, the notebook then failed on the unavailable external seaborn dataset, and the controller allowed two finalization generations before stopping at 13 total calls. The model still did not submit answers. The result remains partial, with exact blocker evidence and an explicit finalization-stop error. No dataset replacement, scientific rewriting, or success claim was introduced. This single development observation is not a controlled performance comparison or evidence of lesson efficacy.

Both previously successful tasks completed under the new stop policy with unchanged original inputs. The blocker detector is restricted to failed author execution stderr with an explicit network exception; generic scientific errors, inspected source text, and successful stdout do not trigger it. A subsequent conservative signature tightening was verified against the retained stderr and regression fixtures; scientific attempts were not replaced.

## Acceptance evidence

- 65 Python tests pass, including the existing 56 and new workspace tests for review-version attribution, immutable originals, cancellation, Host/origin/request-token protection, artifact path boundaries, conservative stopping, and append-only lesson history.
- TypeScript checking and the production frontend build pass.
- Real browser actions exercised launch, exact evidence preview, an assistant-attributed review, ZIP export, lesson proposal/approval/edit invalidation/disable, and cancellation.
- Final browser checks covered execution/source/trace tabs, dialog keyboard focus, and a 390-pixel layout without horizontal page overflow.
- Screenshots under `deliverables/workspace-*-v8.png` show actual application data.
- No new 60-run A/B experiment was performed. Historical experiments and portable reports remain unchanged.

## Practical limits

The workspace supports prepared CPU Python/R projects and locally cached, pinned author environments. It does not adapt arbitrary repositories or provision missing scientific data through the UI. New browser runs omit reference scoring. Missing API credentials permit browsing/review but disable execution.

Cancellation is cooperative: an already-running bounded command or API request can finish before cancellation is observed. The known-blocker allowance does not guarantee a model submission. Diagnosis and semantic review still require judgment; AI-assisted review is not independent human certification.

An independent researcher usability session has **not** been performed. Automated interaction checks are not a substitute. The next user-validation task is to have a researcher unfamiliar with the implementation register a prepared project, run it, inspect evidence, record a review, and export the report without developer help.

Final delivery checks verified 11,926 existing report files byte-for-byte against v0.7.0 and checked 490 portable links/anchors with no failures. The Python wheel and source distribution build successfully; the wheel contains the complete frontend and third-party license notices. The development proxy was also checked to preserve same-origin write protection. Detailed counts are retained in `reports/workspace-delivery-validation-v8.json`.
