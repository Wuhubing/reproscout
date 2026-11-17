# ReproScout

ReproScout runs authors' scientific code in isolated containers, submits answers
with execution evidence, and tests whether frozen development lessons help on
held-out tasks. This is an independently authored MIT 1.125 project by Weibing Wang.

It uses **Inspect AI as infrastructure**, not an existing benchmark task. It does
not fork or invoke `inspect_evals/core_bench` or the original CORE-Agent harness.
See [implementation references](docs/research-references.md).

## What works

- Independent loading of an official CORE-Bench training capsule.
- Archived author images pinned by digest; unchanged author code.
- No runtime network, privileged mode, host directory mounts, or Docker socket.
- Inspect ReAct with project-owned shell, file, image/PDF, and evidence submission tools.
- External answer scoring, per-call usage accounting, and request cost reservations.
- Original logs, controller-owned evidence snapshots, source-integrity checks,
  a SQLite event index, and portable HTML reports.
- Experiment freeze verification and resumable A/B repetition orchestration.

**Important scope:** the controller pre-provisions the author environment. This is
not an unchanged CORE-Bench Medium result. Image downloads occur before the sample
clock and are recorded separately. A successful pilot is not a benchmark-wide score.

## Install

Requirements: Python 3.12, `uv`, Docker Engine, and Docker Compose v2. The pilot uses
an amd64 author image; Apple Silicon needs Docker's amd64 emulation. Bulk preparation
also needs GnuPG. Allow substantial disk space for archived images.

```bash
git clone https://github.com/Wuhubing/reproscout.git
cd reproscout
uv sync --locked --extra dev
uv run reproscout doctor
uv run reproscout prepare
```

The preparation command downloads only the official training metadata and the
small CULP capsule, verifies checksums, excludes supplied results, and keeps
reference answers in ignored `private/`. Pull the pinned author image:

```bash
docker pull --platform linux/amd64 \
  registry.codeocean.com/published/0609cc4f-8b95-4d94-8fd0-9456d262b3a5@sha256:8627797e74cc92c24dff1abec45d299f62b842f41630be4d0a87421df24c3a5e
```

## Validate and run

```bash
uv run reproscout validate
uv run reproscout run --key-file /absolute/path/to/your-key-file
```

Alternatively, set `OPENAI_API_KEY` in the host process. The key is read in memory,
never copied into the repository or passed to the task container. Do not commit it.
The key file may contain a raw key or a single key assignment. No key is bundled.

`validate` uses a deterministic solver, not an LLM. It checks the runtime, network,
credential/socket absence, empty results, command termination, and original author
execution. `run` starts a fresh container and calls the configured model.

Every run writes a distinct directory under `runs/`. Open its `report.html`, or use
Inspect's general log viewer:

```bash
uv run inspect view --log-dir runs
```

## Understand a run

| File | Meaning |
|---|---|
| `manifest.json` | Exact task, source revision, input hashes, and image digest |
| `config.json` | Model, budget, condition, and repetition |
| `summary.json` | Sample status, scoring, elapsed time, and model costs |
| `submission.json` | Actual agent answers and evidence references |
| `artifacts/` | Controller-recorded tool outputs and image snapshots |
| `artifact-index.json` | Artifact hashes and provenance |
| `source-audit.json` | Whether original source/data changed |
| `diagnosis.json` | Provisional failure category with evidence |
| `budget.json` | Request reservations and actual returned usage |
| `logs/*.eval` | Inspect's original trajectory |
| `index.sqlite` | Rebuildable index of trajectory events |

Answer correctness, source integrity, evidence availability, and semantic support
are separate checks. The automatic evidence validator does not establish semantic
support on its own. Missing or failed runs are retained, not silently removed.

## Budget and pricing

The current configuration uses `gpt-5.4-mini-2026-03-17`, low reasoning, one model
request at a time, at most 20 calls and 30 minutes per sample. Each command has a
180-second timeout. Requests reserve a conservative cost before dispatch; retries
are disabled and unknown failed-call costs retain their reservation.

Standard API prices checked on November 17, 2026: $0.75/M uncached input tokens,
$0.075/M cached input tokens, and $4.50/M output tokens. See the
[official model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini).
Amounts are usage-based estimates, not billing receipts. Inspect reports uncached
input and cache-read tokens separately; both are included correctly in our ledger.

## Tests

```bash
uv run pytest -q
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
```

Tests cover unsafe archives, stale result exclusion, evidence boundaries, original
numeric scoring, cached-token accounting, pre-dispatch reservations, and freeze
integrity. Container checks are run separately through `validate`.

## Research and limitations

The planned intervention is a frozen, human-readable lessons file derived only
from development runs. A and B use the same model, tools, budget, and task inputs.
No held-out trace contributes new lessons during a comparison.

Failure labels are provisional operational diagnoses, not an independently
validated attribution study. The application is a local research tool, not a
multi-user service or a general promise to reproduce arbitrary papers.

- [Implementation plan](docs/implementation-plan.md)
- [Research references](docs/research-references.md)
- [AI assistance disclosure](docs/ai-disclosure.md)

Scientific capsules retain their own code/data licenses. Project code is MIT licensed.
