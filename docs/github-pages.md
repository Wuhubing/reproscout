# GitHub Pages evidence workspace

Website: https://wuhubing.github.io/reproscout/

The published React application is a read-only view of retained real runs. It supports project browsing, run inspection, per-question evidence lines, review history, execution traces, historical experiments, and downloadable portable reports. The sample project ZIP is also downloadable.

GitHub Pages serves static files. It does not execute Docker, accept credentials, import projects, run models, or persist reviews. Run the local application for those actions: see [the local workspace guide](workspace-guide-v8.md). Published controls clearly indicate this boundary; mutation requests are rejected by the static client even if invoked programmatically.

## Build and publish

1. Install the locked Python and frontend dependencies: `uv sync --locked --extra dev --python 3.12` and `npm ci --prefix frontend`.
2. Build: `VITE_READ_ONLY=true npm --prefix frontend run build`.
3. Export public data: `uv run python scripts/export_pages.py`.
4. Serve `frontend/dist-pages` beneath `/reproscout/` to match the GitHub project-site base path.

The Pages workflow runs software tests and TypeScript checks, builds the client, exports the public snapshot, and deploys using GitHub's Pages actions on pushes to main. The generated site is not committed. Local application builds remain in `src/reproscout/static`.

The exporter reads only `reports/product-runs`, `reports/workspace-runs`, and the public lesson registry for the live workspace. It uses isolated temporary state, never local jobs, credentials, imported project registrations, or unexported review drafts. Historical reports and documentation are copied as an archive. Publish only reviewed public artifacts into these versioned directories. The existing credential-pattern check is an additional guard, not a comprehensive privacy classifier.

For a future hosted execution service, authentication, job isolation, secret storage, quotas, and durable review storage would be a separate deployment. This release does not imply those capabilities.
