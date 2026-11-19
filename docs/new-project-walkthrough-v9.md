# A new project through the complete workspace

This acceptance walkthrough used a new, unchanged upstream scientific example outside the existing task collection: scikit-learn 1.0.2's diabetes ordinary least squares example. It exercised browser import, real execution, evidence inspection, three saved reviews, and portable report download. This is an assistant-led first-use walkthrough, not an independent human usability study, a paper reproduction, or a new A/B experiment.

## Provenance and preparation

- Source: [plot_ols.py](https://github.com/scikit-learn/scikit-learn/blob/7e1e6d09bcc2eaeba98f7e737aac2ac782f0e5f1/examples/linear_model/plot_ols.py).
- Fixed commit: `7e1e6d09bcc2eaeba98f7e737aac2ac782f0e5f1`; author Jaques Grobler; BSD-3-Clause license included.
- Scientific source SHA-256: `781552d807f78ca9614bba44c75c1641b422443682e10ec99af877da1ac71761`.
- Prepared archive SHA-256: `fca78b19f7b33c1f5e2d2bfab6094c01635788747084d521c0a366b44b52a423`.
- Runtime: cached digest-pinned compatible image, with scikit-learn 1.0.2, numpy 1.21.5, scipy 1.7.3, matplotlib 3.5.1. This is not claimed to be an image published by the scikit-learn authors. The built-in diabetes dataset is fixed by the image digest, rather than downloaded at execution time.
- Four inventoried inputs: unchanged scientific source, its upstream license, and two clearly labeled preparation documents. The inventory does not separately hash every installed library or library-packaged dataset.
- No reference answers or lesson were supplied to the execution model. The acceptance coordinator viewed public example documentation; this is not a blind evaluation.

Rebuild the portable example with `uv run python scripts/prepare_external_example.py --output /tmp/reproscout-example`. The script verifies the complete result against the frozen manifest. Alternatively download `deliverables/sklearn-diabetes-ols-102.zip` and import it from Projects in the local app. The pinned container must already be available locally; importing a ZIP does not download an image or automatically adapt an arbitrary repository.

## First-use issue and fix

The initial manifest-only import failed with HTTP 400 because its prepared archive was outside the repository's data directory. That is a real onboarding obstacle: selecting a project in the browser should not require manually copying its archive into an internal directory first. The original failure is retained in `reports/new-project-import-failure-v9.json`.

The import dialog now accepts a portable ZIP containing exactly `manifest.json` and `prepared.tar`. It verifies archive and per-file SHA-256 hashes, allowed paths, inventory membership, duplicates, expanded limits, and rejection of links before registering the project. Original manifest and bundle hashes are retained. The original scientific code is never rewritten. Invalid imports roll back and duplicate imports cannot overwrite an existing project. JSON import remains available for already-local prepared archives.

After the successful ZIP import, the browser observer encountered an inspector-cache eviction while reading a response body. The application had already registered the project. We verified the persisted project and resumed from Projects, without reimporting or starting a duplicate run. This was an automation interruption, not a failed scientific execution.

## Actual execution and review

Run: `20261119T035641056702Z-sklearn-diabetes-ols-102-run-A1`.

| Measure | Observed result |
| --- | --- |
| Execution | Completed, 5 model calls |
| Time | 20.7775 seconds |
| Estimated model cost | $0.0042948; excludes host and image costs |
| Inventoried inputs | 4 unchanged |
| q1: regression coefficient | 938.23786125; stdout lines 1–2 |
| q2: test mean squared error | 2548.07; stdout line 3 |
| q3: test R-squared | 0.47; stdout line 4 |
| Review | Three supported decisions, recorded separately |
| Reference-answer score | Not supplied / not scored |

The evidence comes from the successful execution of the unchanged upstream script. Each browser review records `assistant:first-use-walkthrough`, reviewer kind `assistant`, the selected evidence and exact lines, and a question-specific rationale. MSE is not RMSE, the coefficient is not an accuracy, and R-squared is not stored as 47 percent. Execution success, unchanged inputs, semantic support, and reference correctness remain distinct.

The original example calls `plt.show()` without saving a figure. We do not claim a generated PNG or a successful figure comparison.

## Export verification

The browser downloaded the reviewed report ZIP. Its contents preserve all three review versions, original evidence files, and portable HTML. Opening the extracted report offline and following a citation reached the correct line anchor. No browser JavaScript errors were observed. The downloaded ZIP SHA-256 and verification record are retained in `reports/new-project-export-check-v9.json`.

The public portable report is in `reports/workspace-runs/20261119T035641056702Z-sklearn-diabetes-ols-102-run-A1/`. Screenshots are in `deliverables/new-project-reviewed-v9.png` and `deliverables/new-project-export-v9.png`. Previous reports and failures remain unchanged.

## Release validation

76 software tests passed, including portable import rejection/rollback and isolation of the public Pages export from local state. Ruff lint and formatting, TypeScript checking, and both local and Pages production builds passed. The static site was exercised under its real `/reproscout/` base path: evidence inspection, all three question tabs, review read-only controls, ZIP download, Projects, Lessons, and the guide passed without JavaScript errors, HTTP errors, or mutation requests.
