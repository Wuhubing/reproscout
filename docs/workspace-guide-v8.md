# ReproScout local workspace

## Start the app

From the repository root:

```sh
uv sync --locked --extra dev
uv run reproscout serve --key-file /path/to/your/private/key.txt
```

Open **http://127.0.0.1:8765**. Alternatively set `OPENAI_API_KEY` on the host and omit `--key-file`. Without a credential the workspace still opens for browsing and review, but execution is unavailable. The server binds only to loopback. `--port` can select another local port. Only one server per repository may run at a time.

Prebuilt frontend assets are included, so Node is not needed to run the app. To develop the frontend:

```sh
npm ci --prefix frontend
npm --prefix frontend run check
npm --prefix frontend run build
```

Refresh the local workspace after a build. Source components are in `frontend/src`, and build output is in `src/reproscout/static`.

## Start a reproduction

1. Open **Projects** or **New reproduction**.
2. Select an already-prepared project. Its archive must exist under `data/`, match the manifest checksum, and use an author image pinned by digest and already cached in Docker.
3. Review or edit the questions and their answer types. Changes are saved in the new run's manifest; original code and data remain unchanged.
4. Set budgets and select approved lessons, if any. Maximums remain 20 model calls, 1,800 seconds, and $1 model cost.
5. Start the run. Progress, executed author files, retained artifacts, and model usage appear automatically.

The app does not provision arbitrary GitHub repositories or infer environments. **Import prepared manifest** registers another prepared project; it does not upload data, execute arbitrary host commands, or modify author science. Browser launches omit reference-answer scoring. The CLI still supports explicitly configured optional reference scoring.

## Blockers and cancellation

A failed original execution whose stderr demonstrates a network dependency failure in the offline sandbox produces a `blocker.json` record with exact evidence lines. Further author executions stop. The model receives at most two additional generation calls to finalize supported or null answers. A lack of submitted answers remains visible; the controller never fabricates an answer to make the report complete. Generic errors, inspected source text, and successful execution output do not trigger this rule.

**Cancel run** requests cooperative cancellation. The current bounded API request or author command can finish; no new generation starts after cancellation is observed. This preserves Inspect cleanup and source audits. Cancellation is not an instantaneous hard process kill. The report and partial evidence remain available.

## Review and export

Select a question in **Results & review**. Inspect the cited output or choose another retained artifact. Select exact line numbers, choose supported/unsupported/uncertain, explain the metric/object/units, and supply reviewer identity and type. A new version is saved without overwriting original run records or previous reviews. AI-assisted decisions must be marked **AI assistant**, not human.

**Export report** downloads a portable ZIP with the report, evidence, assessment, visible trace, source audit, and review records. Host credentials, private answer files, raw Inspect binary logs, and the Docker socket are excluded.

## Lessons

Propose only from training, development, or user-project runs, with a retained evidence artifact and an explicit action/applicability statement. A proposal is inactive. Approval names its reviewer and hashes its content. Editing invalidates approval; disabled rules cannot be selected. Each actual run retains its exact selected lesson snapshots. Loading or approving a lesson is not a demonstrated efficacy result.

## Local state and history

Workspace job state and review versions live under ignored `.reproscout/`; execution evidence stays under ignored `runs/`. The repository's portable development reports and historical experiments are preserved. The versioned lesson registry is under `lessons/registry/`. Keep the workspace and run directories when retaining local work; use report export for portable evidence.

Automated browser acceptance is documented separately. It does not substitute for an independent researcher trying the product; a first external-user usability session remains an explicit follow-up.
