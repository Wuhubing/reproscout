# GitHub Actions execution feasibility

Checked November 19, 2026. This investigation separates technical execution, billing, data handling, and suitability as a product backend.

## Decision

Use GitHub Actions for bounded, fixed-example ReproScout integration acceptance. Do not connect arbitrary website uploads to GitHub-hosted runners as the application's production compute backend. The existing authenticated online service remains the deployment candidate; Actions does not eliminate its hosting requirement.

GitHub's [additional product terms](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#actions) limit hosted-runner activity to the associated repository's software lifecycle and explicitly caution against serverless-application use. A production service processing unrelated visitor projects does not have a sufficiently supported fit. This is our deployment decision based on the documented restrictions, not a claim that GitHub has reviewed or approved our design. A successful Docker test alone does not establish permission or suitability for that service.

## Free allowances and cost

According to the current [billing documentation](https://docs.github.com/en/billing/concepts/product-billing/github-actions):

| Item | Included usage / price |
| --- | --- |
| Public repository, standard hosted runner | Compute is free |
| GitHub Free private compute | $12/month shared included compute |
| GitHub Pro private compute | $18/month shared included compute |
| Standard Linux baseline | $0.006/minute |
| Free artifact allowance | 500 MB, shared with Packages |
| Repository cache allowance | 10 GB, separate |
| Additional artifact storage | $0.25/GB-month |

The Free included amount corresponds to about 2,000 baseline Linux minutes if nothing else consumes it. This is a conversion, not a separate dedicated allowance. Larger runners are not free merely because the repository is public. Storage accrues over time; deleting artifacts stops future accrual, not prior charges. Model API charges are external to GitHub.

The repository is public. Its observed current Actions artifact inventory was about 25.4 MB before this probe; this is not an account-wide storage or accrued-billing statement. The account billing API returned 404 and reported a missing `user` token scope. We did not expand permissions. Actual account plan, remaining included balance and spending-stop settings were therefore not verified.

For this investigation, use one owner-triggered public standard-runner test, a $0.10 maximum model reservation, no dependency cache, and one-day artifact retention. It is not a monthly service subscription or a guarantee of an account-wide $5 cap. Do not offer unlimited retries or anonymous dispatch. A future private CI setup must separately verify account budget stops and shared usage before enabling recurring runs.

## Runner and service limits

[Runner specifications](https://docs.github.com/en/actions/reference/runners/github-hosted-runners) list public `ubuntu-24.04` as x64, 4 CPU, 16 GB RAM and 14 GB SSD. Private standard Linux runners have 2 CPU and 8 GB RAM. We use the VM runner, not `ubuntu-slim`. Each run starts fresh: dependency installation and image pulls are part of the measured job, and registry availability remains an independent risk.

[Actions limits](https://docs.github.com/en/actions/reference/limits) include a six-hour hosted job maximum and account-dependent concurrency. Our test deliberately uses a 15-minute job timeout, a 300-second controller wall budget, ten model calls, and a single concurrency group. Queue time and image provisioning are not scientific execution time. Cancellation, infrastructure failure and missing outputs must remain failures, not be counted as successful experiments.

## What was implemented

- `.github/workflows/reproduction-acceptance.yml`: manual dispatch, owner-only, first attempt only, fixed public scientific example, read-only repository permission, checkout without persistent credentials, pinned action revisions.
- `scripts/actions_acceptance.py`: record Docker/Compose versions, explicitly pull the pinned amd64 image, validate/import the unchanged example ZIP, execute the actual existing controller, check source integrity and completion, and export the portable report.
- Success and failure records are uploaded with one-day retention. Raw provider `.eval` files are excluded from the portable report. Registry stdout/stderr remain available as evidence.
- A temporary dedicated CI secret is supplied only to the controller step, never to the author container or frontend. It is removed after validation. Future paid tests require the operator to intentionally provision a credential again.

This workflow accepts no project URL, arbitrary image, ZIP upload, shell command, or visitor-selected task. It is not a backend endpoint disguised as CI. A GitHub Pages visitor cannot dispatch it anonymously, and no administrator token is embedded in the page.

## Privacy and web integration

The fixed example and its evidence are already intended for publication. Public workflow logs and downloadable artifacts are not a private tenant store. Turning the repository private would change visibility and compute accounting, but would not by itself provide application authentication, per-user ownership, durable review storage, secure upload handling, or a documented exemption from Actions usage restrictions.

Consequently no website upload-to-Actions route was added. The existing website remains accurate about its read-only status. The authenticated application's upload, review and export features remain available for deployment on a suitable host. The useful output of this work is a remotely verified integration test plus a documented decision, rather than an unverified promise of free online hosting.

## Actual test results

[GitHub-hosted run 44469346488](https://github.com/Wuhubing/reproscout/actions/runs/44469346488) passed on commit `9afb261086a988acc8fcf16136e556200eab21fd`. This was one real attempt, not a local simulation or a statistical reliability study.

| Measurement | Observed |
| --- | --- |
| Full job duration, including setup/export | 96 seconds |
| Acceptance script including image provisioning | 83.80 seconds |
| Pinned image pull | 56.77 seconds |
| Controller execution | 17.51 seconds |
| Model calls | 5 |
| Estimated model charge | $0.00419205 |
| Conservative uncached cost estimate | $0.00574725 |
| Infrastructure / network-attempt failures | 0 / 0 |
| Original inventoried inputs | 4 unchanged |
| Answers | 938.23786125; 2548.07; 0.47 |

The controller executed the unchanged scientific source inside the Docker sandbox, produced typed answers and citations, and exported an actual report. Completion and source integrity passed; no independent semantic review or reference-answer score is claimed for this CI attempt. It is not a new A/B experiment.

Evidence: [acceptance record](../reports/actions-acceptance/44469346488/acceptance.json), [Docker/registry logs](../reports/actions-acceptance/44469346488/), and [portable report](../reports/actions-runs/20261119T060422381488Z-sklearn-diabetes-ols-102-run-A1/report.html). The temporary CI secret was removed after completion. The initial dispatch request returned 404 while the newly pushed workflow was registering; no run was created by that request. A subsequent dispatch created the single recorded execution. No scientific attempt was discarded or overwritten.

This test's standard-runner compute is free under the public-repository rule. Its actual model estimate is well below $5. That does not demonstrate the affordability, eligibility, privacy, or reliability of an unrestricted public compute service. The bounded CI test can be reused when an operator deliberately re-enables the credential; public execution remains pending an appropriate backend host.
